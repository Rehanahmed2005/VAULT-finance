import os
import psycopg2

from dotenv import load_dotenv
from models import Transaction

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

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
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM transactions")

    rows = cursor.fetchall()
    transactions = []

    for row in rows:
        transaction = Transaction(
        trans_type = row[1],
        amount = row[2],
        category = row[3],
        note = row[4],
        date = row[5]
        )
        transactions.append(transaction)

        return transactions
        cursor.close()
        connection.close() 



