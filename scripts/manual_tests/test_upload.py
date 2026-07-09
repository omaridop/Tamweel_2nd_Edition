import urllib.request
import json
import os
import time
from dotenv import load_dotenv
from supabase import create_client

with open('dummy_policy.pdf', 'rb') as f:
    pdf_content = f.read()

load_dotenv('backend/.env')
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
client = create_client(url, key)

res = client.table('policy_chunks').select('*', count='exact').execute()
initial_count = res.count
print('Initial policy_chunks count:', initial_count)

import urllib.parse
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="dummy_policy.pdf"\r\n'
    f'Content-Type: application/pdf\r\n\r\n'
).encode('utf-8') + pdf_content + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/admin/upload-policy',
    data=body,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body))
    }
)

try:
    resp = urllib.request.urlopen(req)
    print('Upload response status:', resp.getcode())
    print('Upload response json:', json.loads(resp.read().decode('utf-8')))
except Exception as e:
    print('Upload failed:', e)

print('Waiting for background processing...')
for i in range(15):
    time.sleep(2)
    res = client.table('policy_chunks').select('*', count='exact').execute()
    new_count = res.count
    print(f'Checking count: {new_count}')
    if new_count > initial_count:
        print('Success! New chunks added.')
        break
else:
    print('Failed: No new chunks were added within the timeout.')
