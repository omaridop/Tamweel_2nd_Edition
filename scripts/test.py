import urllib.request
import json

url = 'http://localhost:8000/api/v1/chat'
headers = {'Content-Type': 'application/json'}
user_id = 'Anas'

questions = [
    'What is my credit score?',
    'What loans do I have?',
    'What documents are required for financing?',
    'Am I eligible for financing?',
    'What is the weather tomorrow?'
]

for q in questions:
    data = json.dumps({'user_id': user_id, 'message': q}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            print(f'\nQ: {q}')
            print(f'A: {res.get("answer")}')
            print(f'Missing: {res.get("missing_information")}')
    except Exception as e:
        print(f'\nError on {q}: {e}')
