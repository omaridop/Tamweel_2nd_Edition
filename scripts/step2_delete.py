import os, psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("""
DELETE FROM policy_chunks
WHERE policy_name IN (
    'account_limit.pdf',
    'consumer_empowerment_and_market_conduct_wg_action_plan-0.pdf',
    'tmp7xhv2ama.pdf',
    'tmp18emanrw.pdf'
);
""")
conn.commit()
cur.execute("SELECT COUNT(*) FROM policy_chunks;")
print(cur.fetchone()[0])
cur.close()
conn.close()
