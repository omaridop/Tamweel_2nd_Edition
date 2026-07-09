import requests
import json
import time

url = "http://localhost:8000/api/v1/chat"
headers = {"Content-Type": "application/json"}
data = {
    "message": "What is the maximum loan limit?",
    "role": "user",
    "user_id": "Test User"
}

print("Testing Cache Tier 2 (Vector Search + DeepSeek) + Cache Storage...")
response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2))
except Exception:
    print(response.text)

print("\nWaiting 2 seconds for background storage...")
time.sleep(2)

print("\nTesting Cache Tier 1 (Cache Hit)...")
response2 = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response2.status_code}")
try:
    print(json.dumps(response2.json(), indent=2))
except Exception:
    print(response2.text)

print("\nChecking frequent_questions table...")
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
db_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("SELECT question_text, cached_answer, hit_count FROM frequent_questions ORDER BY created_at DESC LIMIT 1;")
row = cur.fetchone()
if row:
    print(f"Table content: {row}")
else:
    print("Table is empty!")
cur.close()
conn.close()
