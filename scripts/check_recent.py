import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv('backend/.env')
supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
res = supabase.table('policy_chunks').select('id, policy_name, created_at').order('created_at', desc=True).limit(5).execute()
for r in res.data:
    print(r['policy_name'], r['created_at'])
