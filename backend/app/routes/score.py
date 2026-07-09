from fastapi import APIRouter, HTTPException, Depends
from app.schemas import UserFinancialData, ScoringResult
from app.main import supabase, get_current_user, engine, logger

router = APIRouter()

@router.post("/api/v1/score", response_model=ScoringResult)
async def get_credit_score(data: UserFinancialData, current_user: dict = Depends(get_current_user)):
    """
    POST user financial data to get a hybrid AI credit score.
    """
    try:
        user_data_dict = data.dict()
        
        financial_metrics = None
        # Use the authenticated user's email (from JWT) — not a guessed email from name.
        target_email = current_user.get("email", current_user.get("sub", ""))
        if supabase and target_email:
            try:
                metrics_res = supabase.rpc('calculate_financial_health', {'target_email': target_email}).execute()
                if metrics_res.data:
                    financial_metrics = metrics_res.data
            except Exception as e:
                logger.error(f"Metrics Fetch Error: {e}", exc_info=True)

        # Inject _authenticated_email so hybrid_engine.py's ownership assertion can verify
        # that the audit log is written under the correct identity.
        user_data_dict["_authenticated_email"] = target_email

        result = engine.run_pipeline(user_data_dict, financial_metrics=financial_metrics)

        
        # Ensure score_breakdown contains floats
        ml_s = result.get("ml_score", 0)
        default_sb = {
            "income_stability": round(ml_s * 0.4, 1),
            "bill_history": round(ml_s * 0.3, 1),
            "financial_health": round(ml_s * 0.3, 1)
        }
        if "score_breakdown" not in result or not result["score_breakdown"]:
            result["score_breakdown"] = default_sb
        elif isinstance(result["score_breakdown"], dict):
            # The LLM sometimes returns complex dictionaries instead of floats
            sb = result["score_breakdown"]
            cleaned_sb = {}
            for key, default_val in [("income_stability", default_sb["income_stability"]), 
                                     ("bill_history", default_sb["bill_history"]), 
                                     ("financial_health", default_sb["financial_health"])]:
                # Handle alternative key for bill_history
                lookup_key = "bill_payment_history" if key == "bill_history" and "bill_history" not in sb else key
                val = sb.get(lookup_key, default_val)
                if isinstance(val, dict):
                    val = val.get("score", default_val)
                try:
                    cleaned_sb[key] = float(val)
                except (ValueError, TypeError):
                    cleaned_sb[key] = float(default_val)
            result["score_breakdown"] = cleaned_sb
            
        return result
    except Exception as e:
        import traceback
        with open('error.log', 'w', encoding='utf-8') as f:
            f.write(traceback.format_exc())
        logger.error("Scoring Error: check error.log", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
