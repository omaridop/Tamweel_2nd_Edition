# -*- coding: utf-8 -*-
from app.pipeline.query_rewriter import rewrite_query
from app.services.intent_classifier import classify_intent

cases = [
    {"q": "What is my credit score?", "h": []},
    {"q": "Why is it low?", "h": [{'role': 'assistant', 'content': 'Your credit score is 620.'}]},
    {"q": "What is my approved loan amount?", "h": []},
    {"q": "What about students?", "h": [{'role': 'user', 'content': 'What are financing requirements?'}]},
    {"q": "وماذا عن الموظفين؟", "h": [{'role': 'user', 'content': 'ما هي شروط التمويل؟'}]},
    {"q": "What is the minimum income requirement?", "h": []},
    {"q": "My credit score is low, why?", "h": []}
]

for c in cases:
    res = rewrite_query(c["q"], c["h"])
    intent = classify_intent(res.rewritten_query)
    print(f"Q: '{c['q']}' | RW: {res.rewrite_needed} -> '{res.rewritten_query}' | INTENT: {intent.intent}")
