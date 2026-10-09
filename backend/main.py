from fastapi import FastAPI
from typing import Optional
from database import get_connection
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, field_validator
from fastapi.middleware.cors import CORSMiddleware
import re
from datetime import date
from fastapi import HTTPException


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

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
    "https://hotel-customer-management.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)
@app.get("/")
def root():
    return {"message":"Hotel Customer API"}


@app.get("/customers")
def get_customers():
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

@app.post("/customers")
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

@app.delete("/customers/{customer_id}")
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



@app.put("/customers/{customer_id}")
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



@app.post("/customers/{customer_id}/stays")
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




@app.get("/customers/{customer_id}/stays")
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
@app.delete("/stays/{stay_id}")
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
