import os
import sys
import logging
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
try:
    from supabase import create_client, Client
except Exception:
    create_client = None
    Client = None
from app.schemas import UserFinancialData, ScoringResult, ChatRequest, ChatResponse, RegisterRequest, LoginRequest, ImprovementPlanRequest, TransactionCreate
import json
from openai import OpenAI
import bcrypt

JWT_SECRET = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET_KEY environment variable is not set. Refusing to start.")
JWT_ALGORITHM = "HS256"

from app.pipeline.embed import embed_query
from app.knowledge_ingester import ingest_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from tempfile import NamedTemporaryFile

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

from app.ml.hybrid_engine import TamweelHybridEngine

app = FastAPI(title="Tamweel AI Backend", version="1.0.0")

# CORS configuration
# Origins are read from the CORS_ALLOWED_ORIGINS environment variable (comma-separated).
# In production set: CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
# For local development this defaults to localhost/127.0.0.1 on ports 5173 and 3000.
_raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
try:
    if create_client and SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception as e:
    logger.error(f"⚠️ Supabase Connection Failed: {e}", exc_info=True)
    supabase = None

# Initialize the Hybrid Engine
engine = TamweelHybridEngine()

# Initialize OpenAI Client to point to OpenRouter
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Initialize DeepSeek Client
deepseek_client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

from app.services.redis_cache import is_cacheable_query, generate_cache_key, get_cached_response, set_cached_response

@app.get("/")
async def root():
    return {"message": "Welcome to Tamweel AI Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "supabase": "connected" if supabase else "disconnected"}

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



from app.routes import auth, chat, score, users, admin

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(score.router)
app.include_router(users.router)
app.include_router(admin.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
