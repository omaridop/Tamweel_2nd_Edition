import requests

url = "http://127.0.0.1:8000/api/v1/admin/upload-policy"
files = {'file': open('backend/account_limit.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())
