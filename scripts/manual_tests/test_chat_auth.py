import httpx
import json

base_url = "http://localhost:8000/api/v1"

# 1. Login
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

# 2. Chat
print("Chatting...")
try:
    chat_resp = httpx.post(
        f"{base_url}/chat",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "user_id": "Anas",
            "message": "What are the primary financial literacy and health targets the CBJ aims to reach by the end of 2028?",
            "role": "user"
        },
        timeout=120.0
    )
    with open("chat_out.txt", "w", encoding="utf-8") as f:
        f.write(f"Chat status: {chat_resp.status_code}\n")
        f.write(f"Chat response: {chat_resp.text}\n")
    print("Chat response written to chat_out.txt")
except Exception as e:
    print("Chat error:", str(e))
