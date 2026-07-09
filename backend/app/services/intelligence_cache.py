import datetime
import logging
from app.services.financial_intelligence import compute_financial_intelligence

logger = logging.getLogger(__name__)

async def get_or_compute_intelligence(supabase, user_email: str, max_age_hours: int = 24) -> dict:
    try:
        res = supabase.table("user_financial_intelligence") \
            .select("intelligence_data, computed_at") \
            .eq("user_email", user_email) \
            .eq("is_current", True) \
            .execute()
            
        if res.data:
            record = res.data[0]
            computed_at_str = record.get("computed_at")
            if computed_at_str:
                try:
                    from app.utils import parse_iso_datetime
                    computed_at = parse_iso_datetime(computed_at_str)
                    age = datetime.datetime.now(datetime.timezone.utc) - computed_at
                    if age.total_seconds() < max_age_hours * 3600:
                        return record["intelligence_data"]
                except Exception as parse_e:
                    logger.error(f"Failed to parse intelligence cache date: {parse_e}", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to fetch financial intelligence from cache: {e}", exc_info=True)
                
    intelligence_dict = await compute_financial_intelligence(supabase, user_email, months=6)
    
    try:
        supabase.table("user_financial_intelligence") \
            .update({"is_current": False}) \
            .eq("user_email", user_email) \
            .execute()
            
        supabase.table("user_financial_intelligence") \
            .insert({
                "user_email": user_email,
                "analysis_period_months": 6,
                "intelligence_data": intelligence_dict,
                "is_current": True
            }).execute()
    except Exception as e:
        logger.error(f"Failed to cache financial intelligence: {e}", exc_info=True)
        
    return intelligence_dict

async def invalidate_intelligence(supabase, user_email: str) -> None:
    try:
        supabase.table("user_financial_intelligence") \
            .update({"is_current": False}) \
            .eq("user_email", user_email) \
            .execute()
    except Exception as e:
        logger.error(f"Failed to invalidate intelligence: {e}", exc_info=True)
