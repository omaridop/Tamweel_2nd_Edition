import requests
import json

url = "http://127.0.0.1:8000/api/v1/chat"
payload = {
    "message": "what is the maximum limit for e-account individual",
    "user_email": "anas@tamweel.ai",
    "history": []
}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status:", response.status_code)
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
