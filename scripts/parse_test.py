from ingestion import parse_markdown_with_hierarchy
import hashlib

with open('tamweel_credit_policies.md', 'r', encoding='utf-8') as f:
    md = f.read()

chunks = parse_markdown_with_hierarchy(md)
print('\n--- Pipeline Verification Logs ---')
print('Successfully parsed structurally.')
for i, c in enumerate(chunks):
    print(f'\n--- Chunk {i+1} ---')
    print(f'Simulated Hash: {hashlib.sha256(c["content"].encode()).hexdigest()}')
    print(f'Hierarchy Context: {c["hierarchy_context"]}')
    print(f'Content Shape:\n{c["content"]}\n')
