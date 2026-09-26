from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class CustomerCreate(BaseModel):
    name: str
    phone: str
    smoking_preference: str
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
    SELECT * FROM customers
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