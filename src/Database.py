import os
import psycopg2
import time

from dotenv import load_dotenv
from models import Transaction
from datetime import datetime

DEBUG_DB = False

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='disable')

def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            trans_type VARCHAR(20) NOT NULL,
            amount DECIMAL NOT NULL,
            category VARCHAR(100) NOT NULL,
            note TEXT,
            date DATE NOT NULL
        )          
    """)

    connection.commit()
    cursor.close()
    connection.close()

def load_transactions():
    start = time.time()

    connection = get_connection()

    if DEBUG_DB:
        print(f"Connection took {time.time() - start:.3f}s")

    query_start = time.time()

    cursor = connection.cursor()
    cursor.execute(
        "SELECT trans_type, amount, category, note, date FROM transactions"
    )

    rows = cursor.fetchall()

    if DEBUG_DB:
        print(f"Query took {time.time() - query_start:.3f}s")

    transactions = []

    for row in rows:
        transaction = Transaction(
            trans_type=row[0],
            amount=row[1],
            category=row[2],
            note=row[3],
            date=str(row[4])
        )
        transactions.append(transaction)

    cursor.close()
    connection.close()

    return transactions

def record_transaction(trans_type, amount, category, note):
    
    date = datetime.now().strftime("%Y-%m-%d")
    
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        INSERT INTO transactions (trans_type, amount, category, note, date)
        VALUES (%s, %s, %s, %s, %s)
    """, (trans_type, amount, category, note, date))

    connection.commit()
    cursor.close()
    connection.close()
