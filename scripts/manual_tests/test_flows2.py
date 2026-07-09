import urllib.request
import urllib.parse
import json
import uuid

BASE_URL = 'http://127.0.0.1:8000/api/v1'

def request(method, path, data=None, token=None):
    url = BASE_URL + path
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.getcode(), json.loads(e.read().decode('utf-8'))
    except Exception as e:
        return 0, str(e)

test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
test_password = "Password123!"

request('POST', '/auth/register', {'name': 'Test User', 'email': test_email, 'password': test_password})
code, resp = request('POST', '/auth/login', {'email': test_email, 'password': test_password})
print("Login Status:", code)
print("Login Response:", resp)
