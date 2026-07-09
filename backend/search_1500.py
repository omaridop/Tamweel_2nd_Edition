import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

supabase = create_client(url, key)

res = supabase.table('tamweel_knowledge_base').select('id, content, metadata').execute()
for r in res.data:
    content = r['content']
    if '1,500' in content or '1500' in content or 'E-Wallet Account Policies' in str(r['metadata']):
        print(f"ID: {r['id']} Content: {content}")
        print(f"Metadata: {r['metadata']}")
