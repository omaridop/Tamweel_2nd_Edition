import sys
import os
import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

os.environ["JWT_SECRET_KEY"] = "test_super_secret_key"

from app.main import app

client = TestClient(app)

def test_jwt_token_validation():
    """Assert JWT token validation works correctly."""
    # Test with invalid signature
    bad_token = jwt.encode({"sub": "test@test.com", "role": "user", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "wrong_key", algorithm="HS256")
    res1 = client.get("/api/v1/results/all_users", headers={"Authorization": f"Bearer {bad_token}"})
    assert res1.status_code == 401

    # Test with expired token
    expired_token = jwt.encode({"sub": "test@test.com", "role": "user", "exp": datetime.now(timezone.utc) - timedelta(hours=1)}, "test_super_secret_key", algorithm="HS256")
    res2 = client.get("/api/v1/results/all_users", headers={"Authorization": f"Bearer {expired_token}"})
    assert res2.status_code == 401

def test_sensitive_financial_constraints():
    """Assert IDOR and role-based financial constraints are enforced."""
    token = jwt.encode({"sub": "user1@test.com", "email": "user1@test.com", "role": "user", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "test_super_secret_key", algorithm="HS256")
    
    # 1. User1 trying to access User2's insights (IDOR prevention)
    res_insights = client.get("/api/v1/insights/user2@test.com", headers={"Authorization": f"Bearer {token}"})
    assert res_insights.status_code == 403
    
    # 2. User trying to access Sponsor Dashboard (Role-based access control)
    res_sponsor = client.get("/api/v1/results/all_users", headers={"Authorization": f"Bearer {token}"})
    assert res_sponsor.status_code == 403
