import asyncio
import time
from app.services.redis_cache import generate_cache_key, is_cacheable_query
from app.services.intent_classifier import IntentType

def test_document_update():
    # Test 5: Document update invalidation
    q = "What is a credit score?"
    docs_before = ["doc1", "doc2"]
    docs_after = ["doc1", "doc3"] # Knowledge base updated
    
    key1 = generate_cache_key(q, docs_before)
    key2 = generate_cache_key(q, docs_after)
    
    print(f"Update Invalidation Test:")
    print(f"Key before: {key1}")
    print(f"Key after:  {key2}")
    print(f"Match? {key1 == key2}")

def test_security():
    # Test 6: Personal financial info
    print("\nSecurity Protection Test:")
    intents_to_test = [IntentType.GENERIC, IntentType.PROFILE_LIGHT, IntentType.FINANCIAL_ADVICE]
    for intent in intents_to_test:
        allowed = is_cacheable_query(intent)
        print(f"Intent {intent.name} Cache Allowed: {allowed}")

if __name__ == '__main__':
    test_document_update()
    test_security()
