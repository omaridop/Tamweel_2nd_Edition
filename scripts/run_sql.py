import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
db_url = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
ALTER TABLE transactions DROP CONSTRAINT transactions_category_check;

ALTER TABLE transactions ADD CONSTRAINT transactions_category_check 
CHECK (category IN (
  'salary', 'utilities', 'groceries', 'zaincash_transfer', 
  'business_supplies', 'rent', 'other', 'food', 'transport', 
  'entertainment', 'health', 'shopping', 'transfer'
));
""")
