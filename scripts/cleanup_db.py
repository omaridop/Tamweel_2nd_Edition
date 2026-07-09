import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

if not db_url:
    print("No DATABASE_URL found in .env")
    exit(1)

def run():
    print(f"Connecting to {db_url.split('@')[1]}...")
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # 1. Delete duplicate transactions safely
        print("Cleaning up duplicate transactions...")
        cursor.execute("""
            DELETE FROM transactions
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY user_email, amount, category, type, (created_at AT TIME ZONE 'UTC')::DATE
                               ORDER BY id
                           ) AS rnum
                    FROM transactions
                ) t
                WHERE t.rnum > 1
            );
        """)
        print(f"Deleted {cursor.rowcount} duplicate transactions.")

        # 2. Add composite unique index for idempotency
        print("Creating unique index idx_transactions_idempotency...")
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_transactions_idempotency 
            ON transactions (user_email, amount, category, type, ((created_at AT TIME ZONE 'UTC')::DATE));
        """)
        print("Successfully created unique index.")

    except Exception as e:
        print(f"Error during execution: {e}")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run()
