import os

main_path = r'C:\Users\epico\OneDrive\Documentos\Desktop\Tamweel_test\backend\app\main.py'
with open(main_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

def get_lines(start, end):
    # start and end are 1-indexed, inclusive
    return "".join(lines[start-1:end])

# Chat: 109 to 488
chat_code = get_lines(109, 488).replace("@app.", "@router.")
chat_file = '''from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.schemas import ChatRequest, ChatResponse, ImprovementPlanRequest
from app.main import supabase, get_current_user, openai_client, engine, logger

router = APIRouter()

''' + chat_code

# Auth: 490 to 607
auth_code = get_lines(490, 607).replace("@app.", "@router.")
auth_file = '''from fastapi import APIRouter, HTTPException
import jwt
from datetime import datetime, timedelta, timezone

from app.schemas import RegisterRequest, LoginRequest
from app.main import supabase, get_password_hash, verify_password, JWT_SECRET, JWT_ALGORITHM, logger

router = APIRouter()

''' + auth_code

# Score: 609 to 668
score_code = get_lines(609, 668).replace("@app.", "@router.")
score_file = '''from fastapi import APIRouter, HTTPException, Depends
from app.schemas import UserFinancialData, ScoringResult
from app.main import supabase, get_current_user, engine, logger

router = APIRouter()

''' + score_code

# Admin: 670 to 710
admin_code = get_lines(670, 710).replace("@app.", "@router.")
admin_file = '''from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File
import os
from tempfile import NamedTemporaryFile
from app.main import get_current_user, logger
from app.knowledge_ingester import ingest_document

router = APIRouter()

''' + admin_code

# Users: 712 to 834
users_code = get_lines(712, 834).replace("@app.", "@router.")
users_file = '''from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from app.schemas import TransactionCreate
from app.main import supabase, get_current_user, logger
from app.services.intelligence_cache import invalidate_intelligence, get_or_compute_intelligence

router = APIRouter()

''' + users_code

# Make routes dir
routes_dir = os.path.join(os.path.dirname(main_path), 'routes')
os.makedirs(routes_dir, exist_ok=True)
with open(os.path.join(routes_dir, '__init__.py'), 'w', encoding='utf-8') as f:
    f.write('')

# Write files
with open(os.path.join(routes_dir, 'chat.py'), 'w', encoding='utf-8') as f:
    f.write(chat_file)
with open(os.path.join(routes_dir, 'auth.py'), 'w', encoding='utf-8') as f:
    f.write(auth_file)
with open(os.path.join(routes_dir, 'score.py'), 'w', encoding='utf-8') as f:
    f.write(score_file)
with open(os.path.join(routes_dir, 'admin.py'), 'w', encoding='utf-8') as f:
    f.write(admin_file)
with open(os.path.join(routes_dir, 'users.py'), 'w', encoding='utf-8') as f:
    f.write(users_file)

# New main.py
header = get_lines(1, 108)
footer = get_lines(835, len(lines))

new_main = header + '''

from app.routes import auth, chat, score, users, admin

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(score.router)
app.include_router(users.router)
app.include_router(admin.router)
''' + footer

with open(main_path, 'w', encoding='utf-8') as f:
    f.write(new_main)

print("Refactoring complete.")
