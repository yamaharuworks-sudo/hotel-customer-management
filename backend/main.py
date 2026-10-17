from fastapi import FastAPI, Request
from typing import Optional
from database import get_connection
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, field_validator
from fastapi.middleware.cors import CORSMiddleware
import re
from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException, FastAPI, Response, Depends, Cookie
from auth import verify_password, generate_session_token, hash_session_token, get_current_admin, verify_request_origin
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    phone: str
    smoking_preference: Optional[str] = None
    notes: Optional[str] = None
    first_stay_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value.strip() == "":
            raise ValueError("氏名を入力してください")
        return value.strip()
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value.strip() == "":
            raise ValueError("電話番号を入力してください")
        elif not re.fullmatch(r"[0-9-]+", value):
            raise ValueError("電話番号は数字とハイフンのみで入力してください")
        
        digits_only = value.replace("-","")   
        if len(digits_only) != 10 and len(digits_only) != 11:
            raise ValueError("10桁または11桁の数字を入力してください")
        
        return value.strip()

class StayCreate(BaseModel):
    stay_date: date
    notes: str


class LoginRequest(BaseModel):
    email: str
    password: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",  # Nginxで配信するローカルテスト用
        "http://cpjt84zuer2u8yuqx6ki3emy.162.43.5.194.sslip.io/", 
        "https://hotel-customer-management.onrender.com",
        "https://hotel-customer-management-staging.onrender.com",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)

@app.get("/")
def root():
    return {"message":"Hotel Customer API"}


# ログイン試行回数を制限
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


@app.post("/login", dependencies=[Depends(verify_request_origin)])
@limiter.limit("5/minute")
def login(request: Request, login: LoginRequest, response: Response):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT id, email, password_hash
                FROM admin_users
                WHERE email = %s
                """,
                (login.email.strip().lower(),)
            )

            admin = cursor.fetchone()

    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="メールアドレスまたはパスワードが正しくありません"
        )
    
    # パスワードが正しいか検証
    if not verify_password(login.password, admin["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="メールアドレスまたはパスワードが正しくありません"
        )

    # セッショントークンを生成
    session_token = generate_session_token()
    # DB保存用にハッシュ化
    token_hash = hash_session_token(session_token)
    # セッションの有効期限を設定（8時間）
    expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
    # セッション情報をDBに保存
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO admin_sessions (
                    admin_id,
                    token_hash,
                    expires_at
                ) VALUES (%s, %s, %s)
                """, 
                (
                    admin["id"],
                    token_hash,
                    expires_at
                )
            )

    # is_production = os.getenv("APP_ENV") == "production"
    is_secure_environment = os.getenv("APP_ENV") in ("production", "staging")

    # cookie設定
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=is_secure_environment,
        samesite="none" if is_secure_environment else "lax",
        max_age=60 * 60 * 8,
        path="/"
    )

    return {"message": "ログイン成功"}

@app.post("/logout", dependencies=[Depends(verify_request_origin)])
def logout(
    response: Response,
    session_token: Optional[str] = Cookie(default=None)
):
    if session_token is not None:
        token_hash = hash_session_token(session_token)

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM admin_sessions
                    WHERE token_hash = %s
                    """,
                    (token_hash,)
                )

    is_secure_environment = os.getenv("APP_ENV") in ("production", "staging")
    response.delete_cookie(
        key="session_token",
        path="/",
        secure=is_secure_environment,
        samesite="none" if is_secure_environment else "lax"
    )

    return {"message": "ログアウトしました"}

@app.get("/customers")
def get_customers(admin: dict = Depends(get_current_admin)):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
    
            cursor.execute("""
                SELECT
                    customers.id,
                    customers.name,
                    customers.phone,
                    customers.smoking_preference,
                    customers.notes,
                    COUNT(stays.id) AS stay_count,
                    MAX(stays.stay_date) AS last_stayed_date
                FROM customers 
                LEFT JOIN stays
                    ON customers.id = stays.customer_id
                GROUP BY customers.id
                ORDER BY customers.id
            """)
            customers = cursor.fetchall()

    return customers

@app.post("/customers", dependencies=[Depends(get_current_admin), Depends(verify_request_origin)])
def create_customer(customer: CustomerCreate):
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                INSERT INTO customers(
                    name,
                    phone,
                    smoking_preference,
                    notes
                ) VALUES (%s, %s, %s, %s)
                RETURNING id
            """,(
                customer.name, 
                customer.phone, 
                customer.smoking_preference, 
                customer.notes,
            ))

            customer_id = cursor.fetchone()[0]

            if customer.first_stay_date is not None:
                cursor.execute("""
                    INSERT INTO stays(
                        customer_id,
                        stay_date
                    ) VALUES (%s, %s)

                """, (
                    customer_id,
                    customer.first_stay_date
                ))

    return {
        "message": "customer created",
        "customer_id": customer_id        
    }

@app.delete("/customers/{customer_id}", dependencies=[Depends(get_current_admin), Depends(verify_request_origin)])
def delete_customer(customer_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:

            # 顧客が存在するか確認
            cursor.execute(
                "SELECT id FROM customers WHERE id = %s",
                (customer_id,)
            )
            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="存在しない顧客のため削除されませんでした"
                )
            
            # 顧客の宿泊履歴を削除
            cursor.execute(
                "DELETE FROM stays WHERE customer_id = %s", 
                (customer_id,)
            )
            # 顧客情報を削除
            cursor.execute( 
                "DELETE FROM customers WHERE id = %s", 
                (customer_id,)
            )

        return {"message": "customer deleted"}



@app.put("/customers/{customer_id}", dependencies=[Depends(get_current_admin), Depends(verify_request_origin)])
def update_customer(customer_id: int, customer: CustomerCreate):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE customers 
                SET 
                    name = %s,
                    phone = %s,
                    smoking_preference = %s,
                    notes = %s
                WHERE id = %s 
            """, (
                customer.name, customer.phone, customer.smoking_preference, customer.notes, customer_id 
            ))

        update_count = cursor.rowcount

        if update_count == 0:
            raise HTTPException(
                status_code=404,
                detail="存在しない顧客のため更新されませんでした"
            )
        return {"message": "customer updated"}



@app.post("/customers/{customer_id}/stays", dependencies=[Depends(get_current_admin), Depends(verify_request_origin)])
def create_stay(customer_id: int, stay: StayCreate):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            
            # 顧客が存在するかチェック
            cursor.execute(
                "SELECT id FROM customers where id = %s" , 
                (customer_id,)
            )
            customer = cursor.fetchone()
        
            if customer is None:
                raise HTTPException(
                    status_code=404,
                    detail="顧客情報が見つかりません"
                )
                
            cursor.execute("""
                INSERT INTO stays (
                    customer_id,
                    stay_date,
                    notes
                ) VALUES(%s, %s, %s)
            """, (
                customer_id, stay.stay_date, stay.notes
            ))
        return {"message": "stay created"}




@app.get("/customers/{customer_id}/stays", dependencies=[Depends(get_current_admin)])
def get_stays(customer_id: int):
    with get_connection() as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
        
            # ① 顧客が存在するか確認
            cursor.execute(
                "SELECT id FROM customers WHERE id = %s",
                (customer_id,)
            )
            customer = cursor.fetchone()

            if customer is None:
                raise HTTPException(
                    status_code=404, 
                    detail="顧客が存在しません"
                )
            
            # ② 宿泊履歴を取得
            cursor.execute("""
                SELECT * FROM stays WHERE customer_id = %s ORDER BY stay_date DESC
                """, (customer_id,)
            )
            stays = cursor.fetchall()
        return stays


# 間違った日付で宿泊登録してしまった場合に、履歴を1件だけ削除
@app.delete("/stays/{stay_id}", dependencies=[Depends(get_current_admin), Depends(verify_request_origin)])
def delete_stay(stay_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM stays WHERE id = %s
            """, (stay_id,))

            delete_count = cursor.rowcount

            if delete_count == 0:
                raise HTTPException(
                    status_code=404,
                    detail="宿泊情報が存在せず削除できませんでした。"
                )
        return {"message": "stay deleted"}

@app.get("/me")
def get_me(admin: dict = Depends(get_current_admin)):
    return {
        "id": admin["id"],
        "email": admin["email"]
    }