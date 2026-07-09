import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

supabase = create_client(url, key)

res = supabase.table('tamweel_documents').select('content, metadata').execute()
for doc in res.data:
    print(f"Source: {doc['metadata'].get('source')}")
    print(doc['content'][:200])
    print('-'*50)
