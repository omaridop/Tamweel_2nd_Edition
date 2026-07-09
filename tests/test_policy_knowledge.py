import pytest
import asyncio
from app.pipeline.query_rewriter import rewrite_query
from app.services.intent_classifier import classify_intent, IntentType


def test_loan_amount_knowledge_retrieval():
    """
    Validates that a generic question about loan limits correctly hits the generic RAG path,
    gets rewritten accurately, and retrieves the synthetic Tamweel credit policy document.
    """
    user_message = "What is the maximum loan amount for someone with a score of 65?"
    
    # Step 1: Intent Classification
    intent_result = classify_intent(user_message)
    intent = intent_result.intent
    assert intent == IntentType.GENERIC, f"Expected GENERIC intent, got {intent}"
    
    # Step 2: Query Rewriting
    rewritten_result = rewrite_query(user_message, [])
    # Access the string value from the RewriteResult object
    query_text = rewritten_result.rewritten_query
    
    # Should contain core concepts
    assert "loan" in query_text.lower()
    assert "amount" in query_text.lower()
    assert "65" in query_text
    
    # Step 3: Retrieval via Hybrid Engine
    # Note: Using the mock test pipeline format.
    # In hybrid_engine, predict_ml is deterministic, but this is a purely generic RAG call, 
    # so we mock the DB search directly as it would be done in chat.py
    
    from supabase import create_client
    from app.pipeline.embed import embed_texts
    from app.pipeline.config import settings
    import os
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        pytest.skip("Supabase credentials not available")
        
    supabase = create_client(supabase_url, supabase_key)
    
    # Embed the query
    query_vector = embed_texts([query_text])[0]
    
    # Execute RPC
    response = supabase.rpc(
        "hybrid_search_policy_chunks",
        {
            "query_text": query_text,
            "query_embedding": query_vector,
            "match_count": 3
        }
    ).execute()
    
    # Step 4: Validation
    assert response.data is not None
    assert len(response.data) > 0, "No chunks retrieved from knowledge base"
    
    # Ensure at least one chunk belongs to the synthetic Tamweel credit policy
    policy_found = False
    for chunk in response.data:
        policy_name = chunk.get("policy_name", "")
        if "tamweel_credit_policy" in policy_name.lower():
            policy_found = True
            break
            
    assert policy_found, "The synthetic Tamweel credit policy was not retrieved!"
