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

    try:
        # users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        #user_identities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_identities (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id BIGINT NOT NULL,
                provider VARCHAR(30) NOT NULL,
                provider_user_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                UNIQUE (provider, provider_user_id)
            )
        """)

        #Create index for user identity lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_identities_user_id
            ON user_identities(user_id)
        """)

        # 4. Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                user_id BIGINT NOT NULL,
                trans_type VARCHAR(20) NOT NULL,
                amount NUMERIC(15, 2) NOT NULL,
                category VARCHAR(100) NOT NULL,
                note TEXT,
                transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        #composite index for transaction queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_transactions_user_date
            ON transactions(user_id, transaction_date DESC)
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
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
