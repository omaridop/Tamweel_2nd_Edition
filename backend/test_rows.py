import asyncio
from app.pipeline.config import PipelineSettings
from supabase import create_client
async def check():
    settings = PipelineSettings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    try:
        res = supabase.table("policy_chunks").select("id, policy_name").execute()
        print("Total rows:", len(res.data))
        if len(res.data) > 0:
            print("First row:", res.data[0])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(check())
