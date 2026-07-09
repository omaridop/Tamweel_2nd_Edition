import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv('backend/.env')
supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
res = supabase.table('policy_chunks').select('id, policy_name').ilike('policy_name', '%dummy%').execute()
print('Rows for dummy_policy.pdf:', len(res.data))
for r in res.data:
    print(r['policy_name'])
