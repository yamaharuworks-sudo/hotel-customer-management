from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class CustomerCreate(BaseModel):
    name: str
    phone: str
    smoking_preference: str
    notes: str

class StayCreate(BaseModel):
    stay_date: str
    notes: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
    cursor = connection.cursor()
    cursor.execute(""" 
        DELETE FROM customers WHERE id = ?
        """, (customer_id,)
    )
    connection.commit()
    connection.close()
    return {"message": "customer deleted"}


@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, customer: CustomerCreate):
    connection = sqlite3.connect("hotel.db")
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
    connection.commit()
    connection.close()
    return {"message": "customer updated"}


@app.post("/customers/{customer_id}/stays")
def create_stay(customer_id: int, stay: StayCreate):
    connection = sqlite3.connect("hotel.db")
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO stays (
            customer_id,
            stay_date,
            notes
        ) VALUES(?, ?, ?)
    """, (customer_id, stay.stay_date, stay.notes)
    )
    connection.commit()
    connection.close()
    return {"message": "stay created"}


@app.get("/customers/{customer_id}/stays")
def get_stays(customer_id: int):
    connection = sqlite3.connect("hotel.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM stays WHERE customer_id = ?
        """, (customer_id,)
    )
    stays = cursor.fetchall()
    connection.close()
    return [dict(stay) for stay in stays]