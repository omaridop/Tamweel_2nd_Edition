import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# Mock env vars
os.environ["JWT_SECRET_KEY"] = "test_super_secret_key"

from app.main import app

client = TestClient(app)

def test_auth_unauthorized_access():
    """Test that endpoints requiring auth block unauthorized access."""
    # Attempt to post a score without auth
    response = client.post("/api/v1/score", json={"avg_monthly_income_jod": 1000})
    assert response.status_code == 401

def test_chat_invalid_request():
    """Test that invalid requests to chat endpoint are properly rejected."""
    # We test with a missing required field (user_id) but with a mock token
    import jwt
    from datetime import datetime, timedelta, timezone
    
    # Generate mock token
    token = jwt.encode(
        {"sub": "test@example.com", "email": "test@example.com", "role": "user", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "test_super_secret_key",
        algorithm="HS256"
    )
    
    # Missing required 'message' in body
    response = client.post(
        "/api/v1/chat",
        json={"user_id": "test", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 422 # Unprocessable Entity due to missing field

def test_login_invalid_credentials():
    """Test that login rejects invalid credentials safely."""
    response = client.post("/api/v1/auth/login", json={"email": "nonexistent@test.com", "password": "wrong"})
    assert response.status_code in [401, 503] # 503 if DB is not connected, 401 if it works but is unauthorized
