from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel, Field, field_validator
from fastapi.middleware.cors import CORSMiddleware
import re
from datetime import date
from fastapi import HTTPException

class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    phone: str
    smoking_preference: str
    notes: str

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
    "https://hotel-customer-api.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)
@app.get("/")
def root():
    return {"message":"Hotel Customer API"}



connection = sqlite3.connect("hotel.db")
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    smoking_preference TEXT,
    notes TEXT)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    stay_date TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
""")

connection.commit()


@app.get("/customers")
def get_customers():
    connection = sqlite3.connect("hotel.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            customers.id,
            customers.name,
            customers.phone,
            customers.smoking_preference,
            customers.notes,
            COUNT(stays.id) AS stay_count,
            MAX(stays.stay_date) AS last_stayed_date
        FROM customers LEFT JOIN stays
            ON customers.id = stays.customer_id
        GROUP BY customers.id
    """)
    customers = cursor.fetchall()
    connection.close()
    return [dict(customer) for customer in customers]

@app.post("/customers")
def create_customer(customer: CustomerCreate):
    connection = sqlite3.connect("hotel.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO customers(
            name,
            phone,
            smoking_preference,
            notes
        ) VALUES (?, ?, ?, ?)
    """,
    (
        customer.name, 
        customer.phone, 
        customer.smoking_preference, 
        customer.notes
    )
    )
    connection.commit()
    connection.close()
    return {"message": "customer created"}

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    connection = sqlite3.connect("hotel.db")
    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM stays WHERE customer_id = ?
        """, (customer_id,))
        cursor.execute(""" 
            DELETE FROM customers WHERE id = ?
            """, (customer_id,)
        )
        # rowcount = 1 顧客がいた　rowcount = 0 存在しない顧客エラーを出す
        delete_count = cursor.rowcount
        if delete_count == 0:
            raise HTTPException(
                status_code=404,
                detail="存在しない顧客のため削除されませんでした"
            )
        connection.commit()
        return {"message": "customer deleted"}
    finally:
        connection.close()


@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: CustomerCreate):
    connection = sqlite3.connect("hotel.db")
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE customers 
            SET 
                name = ?,
                phone = ?,
                smoking_preference = ?,
                notes = ?
            WHERE id = ? """, 
            (customer.name, customer.phone, customer.smoking_preference, customer.notes, customer_id )
        )

        update_count = cursor.rowcount
        if update_count == 0:
            raise HTTPException(
                status_code=404,
                detail="存在しない顧客のため更新されませんでした"
            )
        connection.commit()
        return {"message": "customer updated"}

    finally:
        connection.close()


@app.post("/customers/{customer_id}/stays")
def create_stay(customer_id: int, stay: StayCreate):
    connection = sqlite3.connect("hotel.db")
    try:
        cursor = connection.cursor()

        # 顧客が存在するかチェック
        cursor.execute(
            "SELECT id FROM customers where id = ?" , (customer_id,))
        customer = cursor.fetchone()
        
        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="顧客情報が見つかりません")
            
        cursor.execute("""
            INSERT INTO stays (
                customer_id,
                stay_date,
                notes
            ) VALUES(?, ?, ?)
        """, (customer_id, stay.stay_date.isoformat(), stay.notes)
        )
        connection.commit()
        return {"message": "stay created"}

    finally:
        connection.close()



@app.get("/customers/{customer_id}/stays")
def get_stays(customer_id: int):
    connection = sqlite3.connect("hotel.db")
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM customers WHERE id = ?"
            , (customer_id,)
        )
        customer = cursor.fetchone()

        if customer is None:
            raise HTTPException(status_code=404, detail="顧客が存在しません")
        
        cursor.execute("""
            SELECT * FROM stays WHERE customer_id = ? ORDER BY stay_date DESC
            """, (customer_id,)
        )
        stays = cursor.fetchall()
        return [dict(stay) for stay in stays]

    finally:
        connection.close()


# 間違った日付で宿泊登録してしまった場合に、履歴を1件だけ削除
@app.delete("/stays/{stay_id}")
def delete_stay(stay_id: int):
    
    connection = sqlite3.connect("hotel.db")

    try:
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM stays WHERE id = ?
        """, (stay_id,)
        )
        delete_count = cursor.rowcount
        if delete_count == 0:
            raise HTTPException(
                status_code=404,
                detail="宿泊情報が存在せず削除できませんでした。"
            )
        connection.commit()
        return {"message": "stay deleted"}

    finally:
        connection.close()
    
    