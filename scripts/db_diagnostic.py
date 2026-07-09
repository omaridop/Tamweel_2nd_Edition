import os
import time
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import traceback

def run_diagnostic():
    load_dotenv()
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not found in environment.")
        return

    print("Phase 1: Connection Diagnostic & Health Check")
    
    # Safely mask the connection string for logging
    masked_url = db_url
    if "@" in db_url:
        masked_url = f"***@{db_url.split('@')[-1]}"
    print(f"Testing connection to: {masked_url}")

    try:
        # Test connection pooling latency
        start_time = time.time()
        connection_pool = pool.SimpleConnectionPool(1, 5, db_url)
        pool_time = time.time() - start_time
        print(f"SUCCESS: Connection pool created in {pool_time:.4f} seconds")

        # Open a test transaction block
        conn = connection_pool.getconn()
        try:
            with conn.cursor() as cur:
                # Check vector extension
                cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
                ext = cur.fetchone()
                if ext:
                    print(f"SUCCESS: pgvector extension is active (version {ext[0]})")
                else:
                    print("ERROR: pgvector extension is NOT active!")

                # Perform a basic operation
                cur.execute("SELECT 1;")
                res = cur.fetchone()
                print(f"SUCCESS: Basic query returned {res[0]}")

                # Test transaction rollback
                cur.execute("BEGIN;")
                cur.execute("CREATE TEMPORARY TABLE diag_test (id serial primary key);")
                cur.execute("ROLLBACK;")
                print("SUCCESS: Transaction block opened and rolled back cleanly.")

        finally:
            connection_pool.putconn(conn)
            connection_pool.closeall()
            print("SUCCESS: Connection pool closed securely with no leaks.")

    except Exception as e:
        print("CRITICAL ERROR: Connection diagnostic failed!")
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnostic()
