import os
import asyncio
from dotenv import load_dotenv

load_dotenv('.env')

from supabase import create_client
supabase = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

from app.services.question_cache import store_in_cache, lookup_cache
from app.pipeline.embed import embed_query

async def main():
    question = "What is the maximum loan limit for personal loans?"
    answer = "The maximum loan limit is 50,000 JOD."
    
    print("Generating embedding...")
    embedding = embed_query(question)
    
    print("Testing store_in_cache...")
    await store_in_cache(supabase, question, embedding, answer)
    
    print("Testing lookup_cache...")
    from app.services.question_cache import extract_keywords
    query_keywords = extract_keywords(question)
    result = await lookup_cache(supabase, embedding, query_keywords)
    print(f"Lookup result: {result}")

asyncio.run(main())
