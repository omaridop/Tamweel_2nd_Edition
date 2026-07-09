import asyncio
import httpx
import jwt
import os
from datetime import datetime, timedelta

def create_mock_token(email: str):
    secret = "tamweel_secret_key_123"
    algorithm = "HS256"
    
    payload = {
        "sub": "user_id_123",
        "email": email,
        "role": "user",
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, secret, algorithm=algorithm)

async def run_e2e_test():
    print("=== STARTING END-TO-END VALIDATION (PHASE 5-9) ===")
    token = create_mock_token("anas@tamweel.ai")
    
    url = "http://localhost:8000/api/v1/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload_rag = {
        "user_id": "user_id_123",
        "message": "What is the policy on early settlement?",
        "role": "user",
        "history": []
    }
    
    print("\n--- Sending RAG Query ---")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=payload_rag, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Response Body Snippet:", str(resp.json())[:300] + "...")
                print("RAG query succeeded.")
            else:
                print("Failed:", resp.text)
        except Exception as e:
            print("Error:", e)

    payload_profile = {
        "user_id": "user_id_123",
        "message": "Can you analyze my spending habits?",
        "role": "user",
        "history": []
    }
    
    print("\n--- Sending Personal Profile Query ---")
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=payload_profile, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Response Body Snippet:", str(resp.json())[:300] + "...")
                print("Personal Profile query succeeded.")
            else:
                print("Failed:", resp.text)
        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    asyncio.run(run_e2e_test())
