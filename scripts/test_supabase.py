import os
from dotenv import load_dotenv
from supabase import create_client

def run_tests():
    # Load environment variables
    load_dotenv("backend/.env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    print("Test 1: Connect to Supabase with credentials")
    try:
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY")
        client = create_client(url, key)
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")
        return

    print("Test 2: SELECT one row from tamweel_results")
    try:
        client.table("tamweel_results").select("*").limit(1).execute()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

    print("Test 3: SELECT one row from transactions")
    try:
        client.table("transactions").select("*").limit(1).execute()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

    print("Test 4: SELECT one row from user_connections")
    try:
        client.table("user_connections").select("*").limit(1).execute()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

    print("Test 5: SELECT one row from policy_chunks")
    try:
        client.table("policy_chunks").select("*").limit(1).execute()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

    print("Test 6: Call hybrid_search_policy_chunks RPC with dummy vector")
    try:
        dummy_vector = [0.0] * 768
        client.rpc("hybrid_search_policy_chunks", {
            "query_text": "test",
            "query_embedding": dummy_vector,
            "match_count": 1
        }).execute()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

    print("Test 7: Call calculate_financial_health RPC with test email")
    try:
        client.rpc("calculate_financial_health", {
            "target_email": "test@tamweel.ai"
        }).execute()
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    run_tests()
