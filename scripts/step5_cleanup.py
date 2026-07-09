import os, psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("""
DELETE FROM frequent_questions
WHERE cached_answer ILIKE '%retrieved context is insufficient%'
OR cached_answer ILIKE '%failed to parse%'
OR cached_answer = 'None'
OR cached_answer = '';
""")
conn.commit()
print("Deleted poisoned cache entries.")
cur.close()
conn.close()
