import os
import sys
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client
from app.schemas import UserFinancialData, ScoringResult, ChatRequest, ChatResponse, RegisterRequest, LoginRequest, ImprovementPlanRequest
import json
from anthropic import Anthropic
import bcrypt
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    # Initialize the local embedding model
    print("Loading SentenceTransformer model...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    embedder = None
    print("SentenceTransformers not installed. Vector RAG disabled.")

def get_password_hash(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # Fallback for old plaintext passwords from the SQL seed script
        return plain_password == hashed_password

# Add Tamweel_MVP to sys.path to import the engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Tamweel_MVP")))
from hybrid_engine import TamweelHybridEngine

load_dotenv()

app = FastAPI(title="Tamweel AI Backend", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"⚠️ Supabase Connection Failed: {e}")
    supabase = None

# Initialize the Hybrid Engine
engine = TamweelHybridEngine()

# Initialize Anthropic Client
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@app.get("/")
async def root():
    return {"message": "Welcome to Tamweel AI Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "supabase": "connected" if supabase else "disconnected"}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Chat with Tamweel AI about the user's specific credit score and data, or portfolio stats for sponsors.
    """
    try:
        context_data = "No historical data found."
        
        # 1. Fetch Context based on Role
        if supabase:
            if request.role == "sponsor":
                # Fetch aggregated portfolio data for the sponsor
                response = supabase.table("tamweel_results").select("credit_score, risk_level, approved_amount_jod").order("generated_at", desc=True).limit(50).execute()
                if response.data:
                    avg_score = sum(r['credit_score'] for r in response.data) / len(response.data)
                    high_risk = len([r for r in response.data if r['risk_level'] == 'High'])
                    total_approved = sum(r['approved_amount_jod'] for r in response.data)
                    context_data = f"""
                    Portfolio Stats (Based on last {len(response.data)} applications):
                    - Average Credit Score: {avg_score:.1f}/100
                    - High Risk Borrowers: {high_risk}
                    - Total Capital Approved: {total_approved} JOD
                    """
            else:
                # Fetch specific user data
                response = supabase.table("tamweel_results").select("*").eq("name", request.user_id).order("generated_at", desc=True).limit(1).execute()
                if response.data:
                    latest = response.data[0]
                    context_data = f"""
                    User: {latest['name']}
                    Latest Credit Score: {latest['credit_score']}
                    Risk Level: {latest['risk_level']}
                    Decision: {latest['decision']}
                    Approved Amount: {latest['approved_amount_jod']} JOD
                    Profession: {latest['profession']}
                    Avg Monthly Income: {latest['avg_monthly_income_jod']} JOD
                    """
                
        # 2. Vector Search (RAG)
        rag_context = ""
        if supabase and embedder:
            try:
                query_vector = embedder.encode(request.message).tolist()
                search_res = supabase.rpc(
                    'match_knowledge_base',
                    {'query_embedding': query_vector, 'match_threshold': 0.3, 'match_count': 3}
                ).execute()
                
                if search_res.data:
                    for doc in search_res.data:
                        rag_context += f"- {doc['content']}\n"
            except Exception as e:
                print(f"RAG Retrieval Error: {e}")
        
        # 3. Formulate System Prompt based on Persona
        if request.role == "sponsor":
            system_prompt = f"""
            You are a Senior Financial Policy Advisor. You provide answers based strictly and exclusively on the provided KNOWLEDGE BASE EXTRACTS.

            CONSTRAINTS:
            - Length: Responses must be strictly concise. Limit all answers to 1 to 3 lines maximum.
            - Tone: Use a professional, academic, and direct tone.
            - No Emojis: Strictly prohibit the use of any emojis or informal symbols.
            - Directness: Start your answer IMMEDIATELY with the core fact. NEVER use phrases like "Based on the Tamweel knowledge base", "According to the documents", or "Here is what I found". Do not attribute the information to the system.
            - Hallucination: If the answer is not contained in the extracts, output exactly: "Data not available in the current financial context."

            EXAMPLE OUTPUT:
            User: "What is the 2028 financial literacy target?"
            Assistant: "The target is to increase the average financial literacy score from 42% in 2023 to 50% by the end of 2028."
            
            KNOWLEDGE BASE EXTRACTS:
            {rag_context}
            
            PORTFOLIO DATA:
            {context_data}
            """
        else:
            system_prompt = f"""
            You are Tamweel AI Chatbot, a highly analytical financial assistant for users in Jordan.
            
            You have access to the user's latest credit assessment data:
            {context_data}
            
            {rag_context}
            
            CONSTRAINTS:
            - Length: Keep responses strictly between 1 to 3 lines.
            - Tone: Use a professional, direct, and encouraging tone.
            - No Emojis: Strictly prohibit the use of any emojis or informal symbols.
            - Directness: Start your answer IMMEDIATELY. NEVER use filler phrases like "Based on your data", "According to the knowledge base", or "I can see that".
            - Personalization: If the user asks about their score, you MUST use their specific data (e.g., mention their specific income, late bills count, or wallet volume) to explain exactly WHY they have that score.
            - Improvement: Provide 1 or 2 concrete, data-backed steps on how to improve (e.g., "Pay your bills regularly" if they have late bills, or "Increase wallet transactions").
            
            Speak in the user's language (mix of English and Arabic if natural, or just professional Arabic as requested).
            """
        
        # 4. Call Anthropic Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": request.message}
            ]
        )
        
        return {"response": response.content[0].text}
    except Exception as e:
        print(f"Chat Error: {e}")
        return {"response": "عذراً، واجهت مشكلة في معالجة طلبك. يرجى المحاولة مرة أخرى لاحقاً."}

@app.post("/api/v1/ai/improvement-plan")
async def generate_improvement_plan(request: ImprovementPlanRequest):
    """
    Generate a personalized, data-driven improvement plan using Claude 3.5 Sonnet based on recent transactions.
    """
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not connected")
        
        # 1. Fetch Financial Metrics
        metrics_res = supabase.rpc('calculate_financial_health', {'target_email': request.email}).execute()
        metrics = metrics_res.data if metrics_res.data else {}
        
        # 2. Fetch Recent Transactions
        tx_res = supabase.table("transactions").select("*").eq("user_email", request.email).order("created_at", desc=True).limit(15).execute()
        tx_data = tx_res.data if tx_res.data else []
        tx_summary = "\n".join([f"- {t['created_at'][:10]}: {t['type']} | {t['category']} | {t['amount']} JOD" for t in tx_data])

        # 3. Formulate System Prompt
        system_prompt = f"""
        You are a Senior Financial Advisor for Tamweel AI.
        Generate a personalized, data-driven financial improvement plan for the user.
        
        USER DATA:
        Name: {request.user_id}
        Savings Rate: {metrics.get('savings_rate', 0)}
        Spending Volatility: {metrics.get('volatility', 0)}
        Top Expense Category: {metrics.get('top_category', 'None')}
        
        RECENT TRANSACTIONS:
        {tx_summary}
        
        CONSTRAINTS:
        - Format: Output exactly 3 actionable bullet points.
        - Length: Each bullet point must be strictly 1-2 lines.
        - Tone: Professional, direct, authoritative.
        - Emojis: NO EMOJIS OR SYMBOLS ALLOWED.
        - Data: You MUST cite specific numbers from their recent transactions or metrics (e.g., "Reduce spending in your top category: rent").
        """

        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": "Please generate my personalized improvement plan based on my recent data."}]
        )
        
        return {"plan": response.content[0].text}
    except Exception as e:
        print(f"Plan Generation Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate plan")

@app.post("/api/v1/auth/register")
async def register_user(request: RegisterRequest):
    """
    Register a new user and insert into Supabase with hashed password.
    """
    try:
        from datetime import datetime
        if not supabase:
            # For prototype if supabase is down, just return success
            return {"message": "User registered (Mock Mode)", "user": {"name": request.name, "email": request.email}}

        # 1. Check if email exists
        existing = supabase.table("tamweel_results").select("id").eq("email", request.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")

        # 2. Hash password
        hashed_password = get_password_hash(request.password)

        # 3. Insert new record
        new_user = {
            "name": request.name,
            "email": request.email,
            "password": hashed_password,
            "profession": "New User",
            "profession_category": "pending",
            "avg_monthly_income_jod": 0,
            "credit_score": 0,
            "risk_level": "Pending",
            "decision": "Pending",
            "approved_amount_jod": 0,
            "generated_at": datetime.now().isoformat()
        }
        
        response = supabase.table("tamweel_results").insert(new_user).execute()
        return {"message": "User registered successfully", "user": {"name": request.name, "email": request.email}}
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Registration Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during registration")

@app.post("/api/v1/auth/login")
async def login_user(request: LoginRequest):
    """
    Login user by verifying credentials against Supabase.
    """
    try:
        if not supabase:
            # Fallback for prototype if supabase is down
            if request.email == "anas@tamweel.ai" and request.password == "password123":
                 return {"user": {"id": "1", "name": "Anas", "email": request.email}, "role": "user"}
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Fetch user by email only
        response = supabase.table("tamweel_results").select("*").eq("email", request.email).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_record = response.data[0]
        stored_password = user_record.get('password')

        # Check password
        # Support both plaintext (from initial seed) and hashed passwords for prototype transitioning
        is_valid = False
        try:
             is_valid = verify_password(request.password, stored_password)
        except ValueError:
             # Fallback for old plaintext passwords from the seed script
             if request.password == stored_password:
                 is_valid = True

        if not is_valid:
             raise HTTPException(status_code=401, detail="Invalid credentials")
        
        role = "sponsor" if "admin" in request.email.lower() else "user"
        
        return {
            "user": {
                "id": str(user_record.get('id')),
                "name": user_record.get('name'),
                "email": user_record.get('email')
            },
            "role": role
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Login Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during login")

@app.post("/api/v1/score", response_model=ScoringResult)
async def get_credit_score(data: UserFinancialData):
    """
    POST user financial data to get a hybrid AI credit score.
    """
    try:
        user_data_dict = data.dict()
        
        financial_metrics = None
        # Retrieve Transaction Insights from Supabase if connected
        if supabase:
            # We assume user_data contains the user's name which we matched to email for prototyping, or we can fetch by name
            # Let's map name to email or just fetch directly. The prompt assumes target_email, but for safety in the prototype:
            # We'll use a hardcoded fallback to the anas@tamweel.ai email if name matches, or fetch properly.
            target_email = "anas@tamweel.ai" if "anas" in user_data_dict['name'].lower() else f"{user_data_dict['name'].lower().replace(' ', '')}@tamweel.ai"
            try:
                metrics_res = supabase.rpc('calculate_financial_health', {'target_email': target_email}).execute()
                if metrics_res.data:
                    financial_metrics = metrics_res.data
            except Exception as e:
                print(f"Metrics Fetch Error: {e}")

        result = engine.run_pipeline(user_data_dict, financial_metrics=financial_metrics)
        return result
    except Exception as e:
        print(f"Scoring Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/spending-patterns/{user_email}")
async def get_spending_patterns(user_email: str):
    """
    Fetch comprehensive spending analytics and raw transactions.
    """
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Database not connected")
            
        metrics_res = supabase.rpc('calculate_financial_health', {'target_email': user_email}).execute()
        tx_res = supabase.table("transactions").select("*").eq("user_email", user_email).order("created_at", desc=False).execute()
        
        return {
            "metrics": metrics_res.data,
            "transactions": tx_res.data
        }
    except Exception as e:
        print(f"Analytics Fetch Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/results/all_users")
async def get_all_results():
    """
    Fetch all credit assessments from Supabase for the Sponsor Dashboard.
    """
    try:
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
        print(f"Get All Results Error: {e}")
        return []

@app.get("/api/v1/results/{user_id}")
async def get_user_results(user_id: str):
    """
    Fetch previous results from Supabase for a specific user.
    """
    try:
        if supabase:
            response = supabase.table("tamweel_results").select("*").eq("name", user_id).execute()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
