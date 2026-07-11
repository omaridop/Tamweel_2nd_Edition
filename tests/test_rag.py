import sys
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

os.environ["JWT_SECRET_KEY"] = "mock"

from app.main import app, JWT_SECRET
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta, timezone

client = TestClient(app)

@patch("app.routes.chat.set_cached_response", new_callable=AsyncMock)
@patch("app.routes.chat.get_cached_response", new_callable=AsyncMock)
@patch("app.routes.chat.supabase")
@patch("app.routes.chat.openai_client")
@patch("app.routes.chat.embed_query")
def test_retrieval_returns_docs_and_citations(mock_embed, mock_openai, mock_supabase, mock_get_cache, mock_set_cache):
    """Assert retrieval returns docs, citations exist in the RAG pipeline."""
    # Setup mock token
    token = jwt.encode({"sub": "test@test.com", "email": "test@test.com", "role": "user", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, JWT_SECRET, algorithm="HS256")
    
    # Mock cache
    mock_get_cache.return_value = None
    
    # Mock embeddings
    mock_embed.return_value = [0.1] * 1536
    
    # Mock Supabase RPC for RAG
    mock_rpc = MagicMock()
    mock_rpc.execute.return_value.data = [
        {"policy_name": "Risk Policy 2026", "chunk_index": 0, "parent_content": "Requires 500 JOD minimum.", "similarity": 0.95}
    ]
    mock_supabase.rpc.return_value = mock_rpc
    
    # Mock LLM JSON return
    mock_openai.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content='{"answer": "You need 500 JOD minimum [C1].", "support_score": 5, "support_summary": "Matched policy.", "missing_information": "None", "suggested_followups": []}'))
    ]
    
    response = client.post(
        "/api/v1/chat",
        json={"user_id": "test", "message": "What is the minimum?", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Assert RAG docs returned
    assert "sources" in data
    assert len(data["sources"]) > 0
    assert data["sources"][0]["document_name"] == "Risk Policy 2026"
    
    # Assert Citation is present in answer
    assert "[C1]" in data["answer"]
