import json

# Tool Schemas for OpenRouter / OpenAI
FETCH_TRANSACTIONS_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_recent_transactions",
        "description": "Fetch the user's recent spending transactions from the database. Use this when the user asks about their recent spending, grocery bills, expenses, or asks to see their transactions.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "The number of recent transactions to fetch. Default is 5, max is 20.",
                    "default": 5
                }
            },
            "required": []
        }
    }
}

def execute_fetch_transactions(supabase_client, email: str, args_json: str) -> str:
    """Executes the fetch_transactions tool against Supabase."""
    if not supabase_client:
        return "Error: Database not connected."
        
    try:
        args = json.loads(args_json)
        limit = min(args.get("limit", 5), 20)
        
        response = supabase_client.table("transactions").select("*").eq("user_email", email).order("created_at", desc=True).limit(limit).execute()
        
        if not response.data:
            return "No recent transactions found for this user."
            
        summary = "Recent Transactions:\n"
        for t in response.data:
            summary += f"- Date: {t['created_at'][:10]}, Type: {t['type']}, Category: {t['category']}, Amount: {t['amount']} JOD\n"
            
        return summary
    except Exception as e:
        print(f"Tool Execution Error (fetch_recent_transactions): {e}")
        return f"Database error occurred while fetching transactions: {str(e)}"

FETCH_TOP_USERS_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_top_users",
        "description": "Fetch the users with the highest credit scores from the database. Use this when the admin/sponsor asks about top users, highest scores, or rankings.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "The number of top users to fetch. Default is 3.",
                    "default": 3
                }
            },
            "required": []
        }
    }
}

def execute_fetch_top_users(supabase_client, email: str, args_json: str) -> str:
    """Executes the fetch_top_users tool against Supabase."""
    if not supabase_client:
        return "Error: Database not connected."
        
    try:
        args = json.loads(args_json)
        limit = min(args.get("limit", 3), 20)
        
        response = supabase_client.table("tamweel_results").select("name, email, credit_score, risk_level, approved_amount_jod").order("credit_score", desc=True).limit(limit).execute()
        
        if not response.data:
            return "No users found in the database."
            
        summary = f"Top {limit} Users by Credit Score:\n"
        for i, u in enumerate(response.data):
            summary += f"{i+1}. {u.get('name', 'Unknown')} ({u.get('email', '')}) | Score: {u.get('credit_score')} | Risk: {u.get('risk_level')} | Approved: {u.get('approved_amount_jod')} JOD\n"
            
        return summary
    except Exception as e:
        print(f"Tool Execution Error (fetch_top_users): {e}")
        return f"Database error occurred while fetching top users: {str(e)}"

# A dictionary mapping tool names to their python functions
AVAILABLE_TOOLS = {
    "fetch_recent_transactions": execute_fetch_transactions,
    "fetch_top_users": execute_fetch_top_users
}
