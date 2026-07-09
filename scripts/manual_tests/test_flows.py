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

print('--- Phase 3.1: User Panel Flow ---')
test_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
test_password = "Password123!"
test_name = "Test User"

# 1. Registration
print(f"Registering user {test_email}...")
import time
for i in range(3):
    code, resp = request('POST', '/auth/register', {'name': test_name, 'email': test_email, 'password': test_password})
    if code == 200:
        break
    time.sleep(1)
print("Registration Status:", code)

# 2. Login
print(f"Logging in user {test_email}...")
code, resp = request('POST', '/auth/login', {'email': test_email, 'password': test_password})
print("Login Status:", code)
token = resp.get('access_token')

if token:
    # 3. Dashboard load (Score history)
    # The frontend fetches by 'name' mapped to user_id in the url
    print(f"Fetching score history for user {test_name}...")
    code, resp = request('GET', f'/results/{urllib.parse.quote(test_name)}', token=token)
    print("Dashboard History Status:", code)

    # 4. AI Simulator (Scoring Flow)
    print("Running AI Simulator scoring flow...")
    score_payload = {
        'name': test_name,
        'profession': 'Developer',
        'profession_category': 'salaried',
        'avg_monthly_income_jod': 5000,
        'income_stability_score': 0.9,
        'income_source_count': 1,
        'late_bills_count': 0,
        'bill_reliability_pct': 100.0,
        'total_bills_checked': 12,
        'current_balance_jod': 1000,
        'wallet_tx_count': 50,
        'wallet_total_volume_jod': 5000,
        'balance_to_income_ratio': 0.2,
        'existing_loans': 0
    }
    code, resp = request('POST', '/score', score_payload, token=token)
    print("Scoring Status:", code)
    print("Scoring result contains score:", "final_score" in resp)

    # 5. AI Simulator (Chat Flow)
    print("Running AI Chat...")
    chat_payload = {
        'message': 'What is my credit score?',
        'history': [],
        'user_id': test_name,
        'role': 'user'
    }
    code, resp = request('POST', '/chat', chat_payload, token=token)
    print("Chat Status:", code)
    print("Chat Response answer:", str(resp)[:200])

print('\n--- Phase 3.2: Admin Panel Flow ---')
print("Uploading policy as admin...")
with open('dummy_policy.pdf', 'rb') as f:
    pdf_content = f.read()

import urllib.parse
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\\r\\n'
    f'Content-Disposition: form-data; name="file"; filename="dummy_policy.pdf"\\r\\n'
    f'Content-Type: application/pdf\\r\\n\\r\\n'
).encode('utf-8') + pdf_content + f'\\r\\n--{boundary}--\\r\\n'.encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/admin/upload-policy',
    data=body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body)),
        'Authorization': f'Bearer {token}'
    }
)
try:
    resp = urllib.request.urlopen(req)
    print('Upload response status:', resp.getcode())
except urllib.error.HTTPError as e:
    print('Upload response status:', e.getcode())
