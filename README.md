# Tamweel AI (2nd Edition) 🚀

Tamweel AI is a state-of-the-art, **Hybrid AI Credit Scoring Platform** designed specifically to empower Jordan's informal economy (gig workers, freelancers, micro-entrepreneurs). 

By analyzing alternative data (wallet transactions, bill reliability, income stability) instead of traditional credit histories, Tamweel AI bridges the financial inclusion gap.

## 🧠 Hybrid AI Architecture
This project abandons the "Black-Box" AI approach. Instead, it uses a Two-Tier system:
1. **The Math Engine (XGBoost Classifier):** Processes raw numerical alternative data to predict binary default probability and outputs a base score (0-100).
2. **The Reasoning Engine (Claude 3.5 Sonnet + Vector RAG):** Reads the ML score and uses **Retrieval-Augmented Generation (RAG)** via Supabase `pgvector` to cross-reference institutional policies and write a highly professional, transparent Arabic explanation for the decision.

## ✨ Key Features
- **Dynamic Credit Scoring:** Real-time penalties/bonuses based on live spending volatility and savings rates.
- **Role-Aware Chatbot:** A globally floating AI assistant. If an Admin logs in, it acts as a *Portfolio Risk Analyst*. If a User logs in, it acts as a *Personal Financial Advisor*.
- **Live Spending Analytics:** Interactive Recharts (Donut, Trend Lines) plotting the user's cash flow over 3 months.
- **Actionable AI Improvement Plans:** Generates a strict, personalized 3-point action plan based on exactly what the user is doing wrong (e.g., late utility bills).

## 🛠 Tech Stack
- **Frontend:** React, Vite, TailwindCSS, Zustand (State Management), Recharts.
- **Backend:** FastAPI (Python), Uvicorn, Passlib/Bcrypt.
- **Database & Vector Store:** Supabase (PostgreSQL), `pgvector`.
- **Machine Learning:** `scikit-learn`, `xgboost`, `sentence-transformers` (Local Embeddings).
- **LLM:** Anthropic API (`claude-sonnet-4-6`).

## 🚀 Setup & Installation

### 1. Database (Supabase)
Run the SQL scripts provided in your Supabase SQL Editor in the following order:
1. `supabase_schema.sql`: Creates the core credit results table (`tamweel_results`).
2. `seed_20_with_auth.sql`: Populates the database with 20 varied gig-economy users.
3. `transaction_module.sql`: Sets up transaction tables, the financial health RPC calculation, and populates mock transactions.
4. `vector_rag_schema.sql`: Enables `pgvector` and the similarity matching functions for policy RAG.

### 2. Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend (React/Vite)
```bash
cd frontend
npm install
npm run dev
```

## 🔐 Environment Variables (.env)
You will need a `.env` file in both `backend/` and `Tamweel_MVP/` directories containing:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
```
*(Never commit your real .env file!)*

---
*Built for the future of Financial Inclusion in Jordan.* 🇯🇴