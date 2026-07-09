import os, psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT column_name, data_type, udt_name FROM information_schema.columns WHERE table_name = 'policy_chunks';")
for row in cur.fetchall():
    print(row)
cur.close()
conn.close()
