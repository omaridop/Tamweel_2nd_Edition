import os, psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("""
    SELECT a.attname, a.atttypmod 
    FROM pg_attribute a 
    JOIN pg_class c ON a.attrelid = c.oid 
    WHERE c.relname = 'policy_chunks' AND a.attname = 'embedding';
""")
for row in cur.fetchall():
    print(f"Column: {row[0]}, Typmod (dimension): {row[1]}")
cur.close()
conn.close()
