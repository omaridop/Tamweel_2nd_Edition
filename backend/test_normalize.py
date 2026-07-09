import sys
from app.services.redis_cache import normalize_query

test_cases = [
    "What documents are needed?",
    "what documents do I need?",
    "Documents required for financing?",
    "ما هي متطلبات التمويل؟",
    "ما هى متطلبات التمويل؟"
]

for t in test_cases:
    print(f"'{t}' -> '{normalize_query(t)}'")
