import httpx
import json

base_url = "http://localhost:8000/api/v1"

print("Logging in...")
try:
    login_resp = httpx.post(f"{base_url}/auth/login", json={
        "email": "anas@tamweel.ai",
        "password": "password123"
    }, timeout=10.0)
    print("Login status:", login_resp.status_code)
    token = login_resp.json().get("access_token")
    if not token:
        print("No token:", login_resp.text)
        exit(1)
except Exception as e:
    print("Login error:", str(e))
    exit(1)

print("Triggering Insights...")
try:
    insights_resp = httpx.get(
        f"{base_url}/insights/anas@tamweel.ai",
        headers={"Authorization": f"Bearer {token}"},
        timeout=120.0
    )
    print("Insights status:", insights_resp.status_code)
    print("Insights response:")
    print(json.dumps(insights_resp.json(), indent=2))
except Exception as e:
    print("Insights error:", str(e))
