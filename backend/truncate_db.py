import asyncio
from app.pipeline.config import PipelineSettings
from supabase import create_client

async def truncate():
    settings = PipelineSettings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    # Delete everything
    res = supabase.table("policy_chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("Deleted old chunks:", len(res.data) if hasattr(res, 'data') else "unknown")

if __name__ == "__main__":
    asyncio.run(truncate())
