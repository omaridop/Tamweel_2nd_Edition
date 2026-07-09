import os
from dotenv import load_dotenv
from supabase import create_client
import urllib.request
import json

load_dotenv('backend/.env')
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')

print('--- Supabase policy_chunks test ---')
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    res = supabase.table('policy_chunks').select('id, policy_name, content_hash').limit(5).execute()
    print('Rows in policy_chunks:', len(res.data))
    for r in res.data:
        print(f" - {r['policy_name']} (Hash: {r['content_hash']})")
else:
    print('Missing Supabase credentials')

print('\n--- OpenRouter Embeddings Test ---')
openrouter_key = os.environ.get('OPENROUTER_API_KEY')
if openrouter_key:
    url = "https://openrouter.ai/api/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }
    
    models_to_test = ['google/text-embedding-004', 'openai/text-embedding-3-small']
    for model in models_to_test:
        data = {
            "model": model,
            "input": "This is a test document."
        }
        req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode('utf-8'))
        try:
            with urllib.request.urlopen(req) as response:
                print(f"Model {model}: Status {response.getcode()}")
        except urllib.error.HTTPError as e:
            print(f"Model {model}: HTTP {e.getcode()} - {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"Model {model}: Error {e}")
