import urllib.request
import json
import os
import jwt

# Generate JWT Token
token = jwt.encode(
    {'sub': 'anas@tamweel.ai', 'email': 'anas@tamweel.ai', 'role': 'user'},
    os.environ.get("JWT_SECRET_KEY", "test-secret-for-ci"),
    algorithm='HS256'
)

# API Request Payload
data = json.dumps({
    'user_id': 'Anas',
    'message': 'What is the maximum balance for my account?',
    'history': []
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/chat',
    method='POST',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    },
    data=data
)

try:
    response = urllib.request.urlopen(req)
    res_body = response.read().decode('utf-8')
    res_json = json.loads(res_body)
    print(json.dumps(res_json, indent=2))
except Exception as e:
    print(f"Error: {e}")
