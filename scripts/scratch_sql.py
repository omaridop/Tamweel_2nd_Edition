import os, psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT proname, pg_get_function_arguments(oid) FROM pg_proc WHERE proname IN ('hybrid_search_policy_chunks', 'search_frequent_questions', 'calculate_financial_health');")
for row in cur.fetchall():
    print(row)
cur.close()
conn.close()
