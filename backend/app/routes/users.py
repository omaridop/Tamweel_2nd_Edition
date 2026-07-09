from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from app.schemas import TransactionCreate
from app.main import supabase, get_current_user, logger
from app.services.intelligence_cache import invalidate_intelligence, get_or_compute_intelligence

router = APIRouter()

@router.get("/api/v1/analytics/spending-patterns/{user_email}")
async def get_spending_patterns(user_email: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch comprehensive spending analytics and raw transactions.
    """
    try:
        actual_email = current_user.get("email", current_user.get("sub"))
        if actual_email != user_email:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
            
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not connected")
            
        metrics_res = supabase.rpc('calculate_financial_health', {'target_email': user_email}).execute()
        tx_res = supabase.table("transactions").select("*").eq("user_email", user_email).order("created_at", desc=False).execute()
        
        return {
            "metrics": metrics_res.data,
            "transactions": tx_res.data
        }
    except Exception as e:
        logger.error(f"Analytics Fetch Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/results/all_users")
async def get_all_results(current_user: dict = Depends(get_current_user)):
    """
    Fetch all credit assessments from Supabase for the Sponsor Dashboard.
    Requires sponsor/admin role.
    """
    try:
        if current_user.get("role") != "sponsor":
            raise HTTPException(status_code=403, detail="Sponsor access required.")

        if supabase:
            response = supabase.table("tamweel_results").select("*").order("generated_at", desc=True).execute()
            return response.data
        else:
            # Mock data fallback for Sponsor Dashboard
            return [
                { "name": "Anas", "credit_score": 75, "approved_amount_jod": 600, "risk_level": "Low", "generated_at": "2026-06-17T08:00:00" },
                { "name": "Samer", "credit_score": 86, "approved_amount_jod": 1000, "risk_level": "Low", "generated_at": "2026-06-16T10:00:00" },
                { "name": "Rana", "credit_score": 50, "approved_amount_jod": 300, "risk_level": "Medium", "generated_at": "2026-06-15T12:00:00" },
                { "name": "Khaled", "credit_score": 17, "approved_amount_jod": 0, "risk_level": "High", "generated_at": "2026-06-14T14:00:00" },
            ]
    except Exception as e:
        logger.error(f"Get All Results Error: {e}", exc_info=True)
        return []

@router.post("/api/v1/transactions")
async def create_transaction(transaction: TransactionCreate, current_user: dict = Depends(get_current_user)):
    """
    Create a new transaction and invalidate the financial intelligence cache.
    Only the authenticated user may create transactions for their own account.
    """
    try:
        # Ownership check: the authenticated user can only create their own transactions
        actual_email = current_user.get("email", current_user.get("sub"))
        if actual_email != transaction.user_email:
            raise HTTPException(status_code=403, detail="Not authorized to create transactions for another user.")

        if not supabase:
            raise HTTPException(status_code=500, detail="Database not connected")
            
        data = transaction.dict()
        data["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Insert into transactions table
        res = supabase.table("transactions").insert(data).execute()
        
        # Invalidate intelligence cache
        await invalidate_intelligence(supabase, transaction.user_email)
        
        return {"message": "Transaction created successfully", "transaction": res.data[0] if res.data else None}
    except Exception as e:
        logger.error(f"Create Transaction Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/insights/{user_email}")
async def get_insights(user_email: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch proactive AI insights for the dashboard.
    Ignores the path parameter and uses the authenticated user's sub claim for security.
    """
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # Security requirement: Extract email from token to prevent IDOR
        actual_email = current_user.get("email", current_user.get("sub"))
        print(f"get_insights called for: {actual_email}")
        
        intelligence_data = await get_or_compute_intelligence(supabase, actual_email)
        return intelligence_data
    except Exception as e:
        print(f"Get Insights Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/results/{user_id}")
async def get_user_results(user_id: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch previous results from Supabase for a specific user.
    """
    try:
        actual_email = current_user.get("email", current_user.get("sub"))
        if actual_email != user_id and current_user.get("role") != "sponsor":
             raise HTTPException(status_code=403, detail="Not authorized to access this user's results")
             
        if supabase:
            response = supabase.table("tamweel_results").select("*").eq("email", user_id).execute()
            return response.data
        else:
            # Mock data fallback for User Dashboard
            if user_id == "Anas":
                return [
                    { "name": "Anas", "credit_score": 75, "approved_amount_jod": 600, "risk_level": "Low", "generated_at": "2026-06-17T08:00:00" },
                    { "name": "Anas", "credit_score": 62, "approved_amount_jod": 500, "risk_level": "Low", "generated_at": "2026-06-01T08:00:00" },
                    { "name": "Anas", "credit_score": 58, "approved_amount_jod": 300, "risk_level": "Medium", "generated_at": "2026-05-15T08:00:00" },
                ]
            return []
    except Exception as e:
        print(f"Get User Results Error: {e}")
        return []
