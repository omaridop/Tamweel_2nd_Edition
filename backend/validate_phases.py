# -*- coding: utf-8 -*-
import asyncio
import os
import json
from app.services.intent_classifier import classify_intent, IntentType
from app.services.data_fetcher import fetch_context_for_intent
from app.services.context_assembler import assemble_messages
from app.pipeline.query_rewriter import rewrite_query
from app.main import supabase

async def run_phase_2():
    print("=== PHASE 2: DATABASE AND USER CONTEXT ===")
    
    # We will mock a query that triggers PROFILE_LIGHT
    q1 = "What is my credit score?"
    intent_res = classify_intent(q1)
    
    # 1. User exists (Need to check db for an existing user email, let's use 'test@example.com')
    # Actually, let's query the DB to get ANY valid email
    if not supabase:
        print("Supabase not connected. Skipping DB tests.")
        return
        
    users = supabase.table('tamweel_results').select('email').limit(1).execute()
    if not users.data:
        print("No users in DB.")
        return
        
    valid_email = users.data[0]['email']
    print(f"Testing with valid email: {valid_email}")
    
    # Test Case 1: User Exists
    ctx_exists = await fetch_context_for_intent(supabase, "test-id", valid_email, q1, intent_res)
    print("Context retrieved (User Exists):")
    print(json.dumps(ctx_exists, indent=2, ensure_ascii=False))
    
    # Test Case 2: User Does Not Exist
    ctx_not_exists = await fetch_context_for_intent(supabase, "test-id", "nonexistent@void.com", q1, intent_res)
    print("Context retrieved (User Does Not Exist):")
    print(json.dumps(ctx_not_exists, indent=2))
    
    # LLM Prompt Construction check
    messages = assemble_messages(q1, ctx_exists, [], "", intent_res.intent)
    print("\nAssembled LLM Prompt (System Instruction):")
    print(messages[0]['content'])

async def run_phase_3():
    print("\n=== PHASE 3: PRIORITY 1 COMPATIBILITY ===")
    
    # Normal question
    q_normal = "What documents are required for financing?"
    r_normal = rewrite_query(q_normal, [])
    print(f"Normal Q: {r_normal.rewrite_needed} -> {r_normal.rewritten_query}")
    
    # Follow-up
    q_follow = "What about students?"
    h_follow = [{'role': 'user', 'content': 'What are the loan requirements?'}, {'role': 'assistant', 'content': 'You need income proof.'}]
    r_follow = rewrite_query(q_follow, h_follow)
    print(f"Follow-up Q: {r_follow.rewrite_needed} -> {r_follow.rewritten_query}")

async def run_phase_4():
    print("\n=== PHASE 4: RAG PIPELINE VALIDATION ===")
    from app.main import embed_query
    
    if not supabase: return
    
    # Keyword & Vector hybrid search
    query = "What is the Central Bank's stance on Bitcoin?"
    vec = embed_query(query)
    
    res = supabase.rpc(
        'hybrid_search_policy_chunks',
        {'query_text': query, 'query_embedding': vec, 'match_count': 3}
    ).execute()
    
    print(f"Chunks retrieved: {len(res.data) if res.data else 0}")
    if res.data:
        print(f"Top match source: {res.data[0].get('policy_name')}")
        print(f"Top match score: {res.data[0].get('similarity')}")

async def main():
    await run_phase_2()
    await run_phase_3()
    await run_phase_4()

if __name__ == "__main__":
    asyncio.run(main())
