import asyncio
from app.pipeline.config import PipelineSettings
from supabase import create_client
import uuid

async def test_schema():
    settings = PipelineSettings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    test_id = str(uuid.uuid4())
    dummy_payload = {
        "id": test_id,
        "policy_name": "test_schema_check.txt",
        "hierarchy_context": "Test",
        "content": "test content",
        "parent_content": "test parent content",
        "chunk_index": 1,
        "metadata": {"test": True},
        "content_hash": "test_hash_12345",
        "embedding": [0.0] * 768
    }
    
    try:
        res = supabase.table("policy_chunks").insert(dummy_payload).execute()
        print("SUCCESS! Cache is updated.")
        
        # Cleanup
        supabase.table("policy_chunks").delete().eq("id", test_id).execute()
    except Exception as e:
        print(f"FAILED! Schema cache error: {e}")

if __name__ == "__main__":
    asyncio.run(test_schema())
