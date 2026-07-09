import os
import jwt
import requests
from dotenv import load_dotenv

load_dotenv('backend/.env')

token = jwt.encode({"sub": "anas@tamweel.ai"}, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

url = "http://127.0.0.1:8000/api/v1/chat"
payload = {
    "message": "what is the maximum limit for e-account individual",
    "user_email": "anas@tamweel.ai",
    "user_id": "1",
    "history": []
}
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status:", response.status_code)
    print("Response:")
    import json
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
