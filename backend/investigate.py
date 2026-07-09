import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.pipeline.config import PipelineSettings
from app.pipeline.embed import embed_query
from supabase import create_client

async def run_investigation():
    settings = PipelineSettings()
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    print("========================================")
    print("--- 1. Verify Ingestion ---")
    print("========================================")
    # The Arabic text has the word "عمليات التمثيل الرقمي" (digital representations)
    res = supabase.table("policy_chunks").select("id, policy_name, hierarchy_context, content").ilike("content", "%التمثيل الرقمي%").execute()
    print(f"Rows found containing 'التمثيل الرقمي': {len(res.data)}")
    
    if len(res.data) == 0:
        print("Could not find the expected paragraph in the database.")
    
    for r in res.data:
        print(f"ID: {r.get('id')}")
        print(f"Policy Name: {r.get('policy_name')}")
        print(f"Content:\n{r.get('content')}")
        
        # Verify embedding exists
        emb_res = supabase.table("policy_chunks").select("id").eq("id", r.get("id")).not_.is_("embedding", "null").execute()
        print(f"Embedding exists?: {len(emb_res.data) > 0}")
        print("-" * 20)

    print("========================================")
    print("--- 3. Run the exact vector search (English vs Arabic) ---")
    print("========================================")
    
    q_en = "Does the ban on virtual currencies include digital representations of paper currencies issued by the Central Bank?"
    q_ar = "هل يشمل حظر العملات الافتراضية عمليات التمثيل الرقمي للعملات الورقية الصادرة عن البنك المركزي؟"
    
    for q_label, q_text in [("Query 1 (English)", q_en), ("Query 2 (Arabic)", q_ar)]:
        print(f"\n[{q_label}]: {q_text}")
        query_embedding = embed_query(q_text)
        
        response = supabase.rpc(
            "hybrid_search_policy_chunks",
            {
                "query_text": q_text,
                "query_embedding": query_embedding,
                "match_count": 5
            }
        ).execute()
        
        if not response.data:
            print("No matches found.")
            continue
            
        print(f"Found {len(response.data)} matches.")
        for i, d in enumerate(response.data):
            print(f"\nMatch {i+1}:")
            print(f"Similarity: {d.get('similarity')}")
            print(f"ID: {d.get('id')}")
            print(f"Policy Name: {d.get('policy_name')}")
            print(f"Hierarchy Context: {d.get('hierarchy_context')}")
            print(f"Content (Generated Question?):\n{d.get('content')}")
            print(f"Parent Content:\n{d.get('parent_content')}")
            
            # The backend merges like this:
            text = d.get('parent_content') or d.get('content') or ""
            policy = d.get('policy_name', 'Unknown')
            print(f"Final Merged Context sent to LLM:\n[{policy}]: {text}")

if __name__ == "__main__":
    asyncio.run(run_investigation())
