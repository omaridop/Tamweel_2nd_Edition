import os
from dotenv import load_dotenv
from supabase import create_client, Client
from app.pipeline.embed import embed_query

load_dotenv('backend/.env')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

query_text = 'what is the maximum limit for e-account individual'
query_vector = embed_query(query_text)

search_res = supabase.rpc(
    'hybrid_search_policy_chunks',
    {'query_text': query_text, 'query_embedding': query_vector, 'match_count': 3}
).execute()

results = search_res.data
print(f"Number of results: {len(results)}")
if results:
    for r in results:
        print(f"Similarity: {r.get('similarity')}, Vector Sim: {r.get('vector_similarity')}, ID: {r.get('id')}")
