import os, psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'hybrid_search_policy_chunks';")
result = cur.fetchone()
if result:
    print(result[0])
else:
    print("Function not found.")
cur.close()
conn.close()
