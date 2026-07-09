"""Semantic Memory Cache.

Provides fast, LLM-free responses for exact or highly similar questions
that were previously asked and answered.
"""

from typing import Optional

def lookup_semantic(supabase_client, query_embedding: list[float], threshold: float = 0.98) -> Optional[str]:
    """Check if the semantic cache has a highly similar question already answered."""
    if not supabase_client:
        return None
        
    try:
        res = supabase_client.rpc(
            'match_semantic_cache',
            {'query_embedding': query_embedding, 'match_threshold': threshold, 'match_count': 1}
        ).execute()
        
        if res.data and len(res.data) > 0:
            # We have a high-confidence match!
            hit = res.data[0]
            print(f"[CACHE] Semantic Cache Hit! Similarity: {hit['similarity']:.3f}")
            return hit['answer']
    except Exception as e:
        print(f"Semantic Cache Lookup Error: {e}")
        
    return None

import hashlib

def add_to_cache(supabase_client, question: str, answer: str, query_embedding: list[float]):
    """Add a new question and its generated answer to the cache."""
    if not supabase_client:
        return
        
    try:
        normalized_q = question.strip().lower()
        q_hash = hashlib.sha256(normalized_q.encode('utf-8')).hexdigest()
        
        supabase_client.table("tamweel_semantic_cache").upsert({
            "question": question,
            "question_hash": q_hash,
            "answer": answer,
            "embedding": query_embedding,
            "metadata": {"auto_cached": True}
        }, on_conflict="question_hash").execute()
        print("[CACHE] Saved response to Semantic Cache.")
    except Exception as e:
        print(f"Semantic Cache Insert Error: {e}")
