import asyncio
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.intent_classifier import classify_intent, IntentType
from app.services.data_fetcher import fetch_context_for_intent
from app.services.context_assembler import assemble_messages

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
else:
    supabase = None

async def run_test(message):
    print(f"Testing message: {message}")
    intent_result = classify_intent(message)
    print(f"Intent classified as: {intent_result.intent.name}")
    
    # fetch context
    user_email = "anas@tamweel.ai"
    context = await fetch_context_for_intent(supabase, "user_id_123", user_email, message, intent_result)
    
    needs_rag = True
    if intent_result.intent == IntentType.FINANCIAL_ADVICE:
        needs_rag = False
    print(f"Needs RAG? {needs_rag}")
    
    messages = assemble_messages(message, context, [], "", intent_type=intent_result.intent)
    
    # print the system prompt
    print("\n--- SYSTEM PROMPT ---")
    print(messages[0]["content"])
    print("---------------------\n")
    
if __name__ == "__main__":
    asyncio.run(run_test("What can I do to save more money?"))
    asyncio.run(run_test("كيف أوفر فلوس؟"))
    asyncio.run(run_test("How do I improve my credit score?"))
