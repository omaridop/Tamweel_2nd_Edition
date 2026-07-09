import os
import psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("No DATABASE_URL found")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b"adminpassword", salt).decode('utf-8')

    cursor.execute("UPDATE tamweel_results SET password = %s WHERE email = 'admin@tamweel.ai';", (hashed,))
    print("Updated admin password.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
