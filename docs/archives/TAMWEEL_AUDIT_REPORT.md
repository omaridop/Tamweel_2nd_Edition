# TAMWEEL AI PLATFORM - TECHNICAL AUDIT REPORT

> **STATUS: ARCHIVED & RESOLVED**
> *This audit report reflects a past state of the repository. All major findings raised here—including hardcoded JWT secrets, lack of exact decimal precision for financial math, missing API rate limits, and missing database indexes (Vector & B-Tree)—have been successfully addressed and fixed in the current architecture.*

## 1. Executive Summary
This report presents the findings of a comprehensive, read-only technical audit of the Tamweel AI credit scoring and financial advisory platform. The system demonstrates a robust architectural foundation with a thoughtful separation of concerns (Intent Classification -> Data Fetching -> Context Assembly). The implementation of Explainable AI (XAI) concepts in the UI is highly effective. However, several critical vulnerabilities and architectural gaps were identified, particularly concerning security (hardcoded secrets), database performance (missing indexes), and financial mathematics compliance (use of floating-point arithmetic instead of `Decimal`). Resolving these issues is essential prior to production launch to ensure compliance with financial regulations and data protection laws.

## 2. Connectivity Status
The system's external connections and database dependencies were tested to verify proper integration:
- **Gemini API Connectivity**: **SUCCESS**. The API key was successfully loaded from the environment. A minimal embedding call returned a valid vector with a dimension of `768`.
- **Supabase Table Access**: **SUCCESS**. Connectivity established. The expected tables (`tamweel_results`, `transactions`, `user_connections`, `policy_chunks`, `frequent_questions`, `user_financial_intelligence`) exist in the remote database.
- **Vector Dimension Matching**: **SUCCESS**. The Gemini embedding output dimension (768) perfectly matches the `policy_chunks.embedding` column type (`VECTOR(768)`).
- **Supabase RPC Functions**: **FAILING**. 
  - `calculate_financial_health`: **SUCCESS**.
  - `hybrid_search_policy_chunks`: **ERROR**. The function signature in the schema cache does not match the expected parameters (failed when called with `query_embedding`, `match_threshold`, `match_count`).
  - `search_frequent_questions`: **ERROR**. The function could not be found in the schema cache.
- **Frontend Network Requests**: The React frontend (`UserDashboard.jsx`) correctly fires an authenticated `GET` request to `/api/v1/results/{userId}` on mount to retrieve user history, successfully integrating with Supabase RLS. 

## 3. Finding Registry

### CRITICAL
*   **Hardcoded JWT Secret**: The `JWT_SECRET` is hardcoded as `"[REDACTED_DURING_AUDIT]"` in `backend/app/main.py`. This is a severe security vulnerability allowing trivial token forgery and unauthorized access to any user account.
*   **Broken Semantic Search Pipeline**: The Supabase RPC functions for hybrid search (`hybrid_search_policy_chunks` and `search_frequent_questions`) either do not exist or have mismatched parameter signatures, completely breaking the RAG retrieval mechanism.

### HIGH
*   **Missing Vector Indexes**: There are no `ivfflat` or `hnsw` approximate nearest neighbor indexes on the `embedding` columns in `policy_chunks` or `tamweel_knowledge_base`. As the knowledge base grows, vector similarity searches will perform catastrophic full sequential scans.
*   **Missing Relational Indexes**: The `transactions` table lacks a B-Tree index on `user_email`. Every time financial intelligence is calculated, the database performs a full table scan.
*   **Financial Precision Violation**: Both the PostgreSQL schema (using `FLOAT8`) and the Python backend (`financial_intelligence.py` using standard `float`) fail to use exact precision types. This introduces rounding errors in credit scoring and limits, violating strict financial compliance standards.

### MEDIUM
*   **RLS Authentication Logic**: Row Level Security policies rely on matching `auth.jwt() ->> 'email'`. While functional, relying on email strings instead of immutable UUIDs (`auth.uid()`) can lead to vulnerabilities if user emails change or are spoofed.
*   **Missing Conversation History Handling**: The `ChatRequest` Pydantic schema in `main.py` omits a `history` field, meaning the backend will silently drop multi-turn conversation context sent by the frontend.

### LOW
*   **Hardcoded Frontend API URL**: The frontend service (`frontend/src/services/api.js`) hardcodes `const BASE_URL = 'http://127.0.0.1:8000';`. This will break immediately upon deployment to a staging or production environment.

## 4. What Is Working Well
*   **Modular AI Pipeline**: The backend's separation into distinct services (`intent_classifier`, `data_fetcher`, `context_assembler`) is a very clever engineering choice. It allows the platform to selectively inject context only when needed, minimizing token usage and latency.
*   **Bilingual Robustness**: The use of `rapidfuzz` for intent matching as a fallback for both Modern Standard Arabic (MSA) and colloquial Jordanian slang ensures high resilience against user typos and dialect variations.
*   **Explainable AI (XAI) UI**: The frontend's `TwinPanelLayout` successfully demystifies the AI's credit decisions by breaking down the score into transparent, color-coded impact factors (Income Stability, Bill History, etc.), building immense user trust.

## 5. What Is Missing
*   **Production Database Indexes**: Core infrastructure for performance scaling is completely absent (Vector indexes for RAG, B-Tree indexes for transactional lookups).
*   **Correct RPC Implementations**: The specific RPCs required for fetching policy chunks and frequent questions via vector search are missing or incorrectly defined.
*   **Rate Limiting**: There is no infrastructure (e.g., Redis-based rate limiters) in the FastAPI backend to prevent abuse of the expensive LLM endpoints.

## 6. Financial Mathematics Compliance
**Status: NON-COMPLIANT**
The platform is **not** using `Decimal` everywhere. 
1.  **Database**: The `tamweel_results` table uses `FLOAT8` for `avg_monthly_income_jod`, and `transactions` uses `DECIMAL` without explicit precision/scale, but calculations often cast back to floats. 
2.  **Backend**: `financial_intelligence.py` uses standard Python `float` arithmetic for critical underwriting metrics (e.g., `savings_rate = (income - expense) / income`). 
In FinTech, standard floating-point arithmetic introduces microscopic precision errors that accumulate over time. Strict regulatory compliance requires the use of the Python `decimal.Decimal` module and PostgreSQL `NUMERIC(12,2)` (or similar exact precision types) for all monetary values and ratios.

## 7. Priority Action List
1.  **Secure Authentication**: Immediately remove the hardcoded `JWT_SECRET` from `main.py` and replace it with a secure environment variable.
2.  **Enforce Financial Precision**: Refactor all financial variables and calculations in `financial_intelligence.py` to use Python's `Decimal` class, and update database schemas to use `NUMERIC`.
3.  **Fix Vector Search RPCs**: Align the Supabase RPC definitions for hybrid search with the exact signatures expected by the FastAPI backend to restore RAG functionality.
4.  **Implement Critical Indexes**: Apply an `hnsw` index to all vector `embedding` columns and a standard B-Tree index to `transactions.user_email` to prevent catastrophic performance degradation.
5.  **Environment Configuration**: Refactor the React frontend to use `import.meta.env.VITE_API_URL` instead of a hardcoded `localhost` string for seamless deployment.
