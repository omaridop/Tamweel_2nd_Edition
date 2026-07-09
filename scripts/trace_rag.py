import sys
import os
import asyncio
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.main import supabase
from app.services.intent_classifier import classify_intent, IntentType
from app.pipeline.query_rewriter import rewrite_query
from app.pipeline.embed import embed_query

async def run_trace():
    query = "What is the maximum loan amount you can approve for someone with a score of 65?"
    
    print("--- 1. Intent Classification ---")
    intent_res = classify_intent(query)
    print(f"Intent: {intent_res.intent}")
    
    print("\n--- 2. Query Rewriter ---")
    rewritten_result = rewrite_query(query, [])
    rewritten_query = rewritten_result.rewritten_query
    print(f"Original: {query}")
    print(f"Rewritten: {rewritten_query}")
    
    print("\n--- 3. Retrieval Layer ---")
    # Generate embedding
    print("Generating embedding for rewritten query...")
    query_vector = embed_query(rewritten_query)
    print(f"Vector length: {len(query_vector)}")
    
    if supabase:
        print("Executing hybrid search against Supabase...")
        # Check actual logic in chat.py or hybrid_engine.py
        # Let's call the RPC
        response = supabase.rpc(
            "hybrid_search_policy_chunks",
            {
                "query_text": rewritten_query,
                "query_embedding": query_vector,
                "match_count": 5
            }
        ).execute()
        
        data = response.data
        print(f"Returned chunks: {len(data)}")
        for i, chunk in enumerate(data):
            print(f"\n[Chunk {i+1}] ID: {chunk.get('id')} | Score: {chunk.get('score')} | Parent Doc: {chunk.get('document_id')}")
            content = chunk.get('content', '')
            print(f"Content preview: {content[:200]}...")
            
    print("\n--- 4. Knowledge Base Inspection ---")
    if supabase:
        # Let's search all documents
        doc_res = supabase.table("tamweel_policy_pages").select("id, policy_name, url").execute()
        print(f"Documents found: {len(doc_res.data)}")
        for d in doc_res.data:
            print(f"- {d.get('policy_name')} ({d.get('url')})")
            
        # Search for exact phrases "65", "maximum loan", "approval" in chunks using wildcard search
        phrase_res = supabase.table("tamweel_policy_chunks").select("id, content_text").execute()
        chunks = phrase_res.data
        matches = [c for c in chunks if "loan amount" in c.get('content_text', '').lower() or "score" in c.get('content_text', '').lower()]
        print(f"\nFound {len(matches)} chunks mentioning 'loan amount' or 'score' in entire DB.")
        for m in matches:
            print(f"Match ID {m.get('id')}: {m.get('content_text')[:150]}...")

if __name__ == "__main__":
    asyncio.run(run_trace())
