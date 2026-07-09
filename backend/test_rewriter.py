# -*- coding: utf-8 -*-
import asyncio
from app.pipeline.query_rewriter import rewrite_query

cases = [
    {'name': 'Test 1: Normal question', 'query': 'What are the financing requirements?', 'history': []},
    {'name': 'Test 2: Follow-up question', 'query': 'What about employees?', 'history': [{'role': 'user', 'content': 'What are financing requirements?'}]},
    {'name': 'Test 3: Arabic follow-up', 'query': 'وماذا عن الموظفين؟', 'history': [{'role': 'user', 'content': 'ما هي شروط التمويل؟'}]},
    {'name': 'Test 4: Mixed language', 'query': 'What about students?', 'history': [{'role': 'user', 'content': 'ما هي شروط التمويل؟'}]},
    {'name': 'Test 5: Personal credit question', 'query': 'Why is it low?', 'history': [{'role': 'user', 'content': 'What is my credit score?'}], 'expected_rewrite': False},
    {'name': 'Test 6: Long conversation', 'query': 'What are the required documents?', 'history': [{'role': 'user', 'content': f'Message {i}'} for i in range(50)]}
]

for case in cases:
    res = rewrite_query(case['query'], case['history'])
    output = f"{case['name']}:\n"
    output += f"  rewrite_needed={res.rewrite_needed}\n"
    output += f"  rewritten_query='{res.rewritten_query}'\n"
    output += f"  reason='{res.reason}'\n"
    output += f"  history_messages_used={res.history_messages_used}\n"
    output += f"  rewrite_latency_ms={res.rewrite_latency_ms}\n"
    print(output.encode('cp1256', errors='replace').decode('cp1256'))
