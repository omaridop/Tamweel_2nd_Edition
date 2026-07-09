import asyncio
from app.main import supabase

res = supabase.table('frequent_questions').select('*').limit(1).execute()
if res.data:
    print(res.data[0].keys())
else:
    print("No data in frequent_questions")
