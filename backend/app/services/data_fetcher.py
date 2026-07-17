"""
COLUMN AUDIT MAPPING (tamweel_results):
The existing codebase selects '*' from tamweel_results but actively uses:
- email
- credit_score
- risk_level
- avg_monthly_income_jod
- name (only for email fallback)

Mapped to Intent Tiers:
- GENERIC: None
- PROFILE_LIGHT: credit_score, avg_monthly_income_jod, risk_level
- TRANSACTIONS: avg_monthly_income_jod
- DTI_ANALYSIS: credit_score, avg_monthly_income_jod, risk_level, approved_amount_jod
- FULL_REVIEW: email, credit_score, risk_level, avg_monthly_income_jod, profession, profession_category, decision, approved_amount_jod, reason
"""

from collections import defaultdict

from app.services.intent_classifier import IntentResult, IntentType
from app.services.intelligence_cache import get_or_compute_intelligence
import logging

logger = logging.getLogger(__name__)

ALLOWED_PROFILE_FIELDS = frozenset([
    "name",
    "email",
    "credit_score", 
    "avg_monthly_income_jod", 
    "risk_level", 
    "approved_amount_jod", 
    "profession", 
    "profession_category", 
    "decision", 
    "reason"
])

async def fetch_context_for_intent(supabase, user_id: str, user_email: str, message: str, intent_result: IntentResult) -> dict:
    if not supabase:
        return {}

    intent = intent_result.intent
    if intent == IntentType.GENERIC:
        return {}

    # Step 1: Base query to find the user's latest record
    
    # Aggressively fetch all relevant profile data for ANY personalized intent
    select_fields = "name, email, credit_score, avg_monthly_income_jod, risk_level, approved_amount_jod, profession, profession_category, decision, reason"
    
    # 1. Fetch Financial Intelligence (which contains DTI, savings rate, top categories, etc.)
    try:
        intelligence_dict = await get_or_compute_intelligence(supabase, user_email)
    except Exception as e:
        logger.error(f"Failed to fetch financial intelligence: {e}", exc_info=True)
        intelligence_dict = {}

    if intent == IntentType.FINANCIAL_ADVICE:
        return {
            "financial_intelligence": intelligence_dict,
            "user_email": user_email
        }

    profile_res = supabase.table("tamweel_results").select(select_fields).eq("email", user_email).order("generated_at", desc=True).limit(1).execute()
    
    if not profile_res.data:
        return {}
        
    user_record = profile_res.data[0]
    result_data = {}
    
    # Extract profile summary dict based on intent
    profile_dict = {k: v for k, v in user_record.items() if k in ALLOWED_PROFILE_FIELDS}
    if intent == IntentType.PROFILE_LIGHT:
        result_data["profile_summary"] = profile_dict
    else:
        result_data["profile"] = profile_dict

    
    # Include Financial Intelligence
    if intelligence_dict:
        result_data["financial_intelligence"] = intelligence_dict

    # Transaction fetching for all personalized intents
    if intent != IntentType.GENERIC:
        limit = 25
        tx_query = supabase.table("transactions").select("amount, category, type, description, created_at").eq("user_email", user_email).order("created_at", desc=True)
        
        if intent == IntentType.TRANSACTIONS and "category" in intent_result.filters:
            tx_query = tx_query.eq("category", intent_result.filters["category"])
            
        tx_query = tx_query.limit(limit)
        tx_res = tx_query.execute()
        
        tx_list = []
        if tx_res.data:
            monthly_aggregates = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
            
            for tx in tx_res.data:
                amt = float(tx.get("amount") or 0.0)
                tx_type = str(tx.get("type", "expense")).lower()
                date_str = tx.get("created_at", "")[:7] if tx.get("created_at") else "unknown"
                
                if date_str != "unknown":
                    if tx_type == "income":
                        monthly_aggregates[date_str]["income"] += amt
                    else:
                        monthly_aggregates[date_str]["expense"] += amt

                # rename created_at to date for LLM compactness
                tx_list.append({
                    "amount": amt,
                    "type": tx_type,
                    "category": tx.get("category", ""),
                    "description": tx.get("description", ""),
                    "date": tx.get("created_at", "")[:10] if tx.get("created_at") else ""
                })
            
            if monthly_aggregates:
                total_months = len(monthly_aggregates)
                avg_inc = sum(m["income"] for m in monthly_aggregates.values()) / total_months
                avg_exp = sum(m["expense"] for m in monthly_aggregates.values()) / total_months
                result_data["aggregated_metrics"] = {
                    "monthly_totals": dict(monthly_aggregates),
                    "avg_monthly_income": round(avg_inc, 2),
                    "avg_monthly_expense": round(avg_exp, 2)
                }
        
        if intent == IntentType.TRANSACTIONS:
            result_data["transactions"] = tx_list
            result_data["monthly_income"] = user_record.get("avg_monthly_income_jod")
        else:
            result_data["recent_transactions"] = tx_list

    # Wallet Query Gating
    msg_lower = message.lower()
    wallet_keywords = ["wallet", "account", "balance", "connected"]
    needs_wallet = intent in [IntentType.PROFILE_LIGHT, IntentType.DTI_ANALYSIS, IntentType.FULL_REVIEW]
    
    if needs_wallet or any(kw in msg_lower for kw in wallet_keywords):
        try:
            wallet_res = supabase.table("user_connections").select("institution_name").eq("user_email", user_email).execute()
            if wallet_res.data:
                result_data["active_wallets"] = [w['institution_name'] for w in wallet_res.data]
            else:
                result_data["active_wallets"] = []
        except Exception as e:
            logger.warning(f"Failed to fetch active wallets: {e}")
            result_data["active_wallets"] = []

    return result_data
