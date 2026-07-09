import os
import psycopg2
from ingestion import ingest_policy
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Dynamically fetch the Supabase (or any PostgreSQL) connection string
# Expected format: postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres
DB_URL = os.environ.get("DATABASE_URL")

if not DB_URL:
    print("❌ ERROR: DATABASE_URL environment variable is not set.")
    print("Please set it in your backend environment or a local .env file.")
    exit(1)

# Mask the password for safe logging
safe_db_url = DB_URL.split('@')[-1] if '@' in DB_URL else "[hidden credentials]"
print(f"Connecting to database at {safe_db_url}...")

try:
    # 1. Execute schema.sql to ensure Supabase has the tables and vector extension
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    with open("schema.sql", "r", encoding="utf-8") as f:
        schema_sql = f.read()
    print("Executing schema.sql...")
    cur.execute(schema_sql)
    print("Schema executed successfully.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Database setup error: {e}")
    print("Please ensure your Supabase connection string is correct and accessible.")
    exit(1)

# 2. Run ingestion
print("\nStarting ingestion...")
ingest_policy("tamweel_credit_policies.md", DB_URL, "Alternative Data Underwriting")

# 3. Verify
print("\n--- Verification Logs ---")
try:
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT hierarchy_context, content, content_hash FROM policy_chunks ORDER BY hierarchy_context ASC;")
    rows = cur.fetchall()
    for i, r in enumerate(rows):
        print(f"--- Chunk {i+1} ---")
        print(f"Hash: {r[2]}")
        print(f"Hierarchy Context: {r[0]}")
        print(f"Content Shape:\n{r[1]}\n")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Verification failed: {e}")
