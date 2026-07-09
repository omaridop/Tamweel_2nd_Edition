"""
# Tamweel Chat Pipeline Architecture Map

## Current Flow
1. **Request Receipt**: The endpoint `/api/v1/chat` receives `ChatRequest` with `user_id`, `message`, `role`, and `history`.
2. **Data Fetching**:
   - Queries `tamweel_results` fetching ALL columns for the user (`SELECT *`).
   - Determines `user_email` from the result or falls back to a derived string.
   - Queries `user_connections` to get active wallets.
   - Queries `transactions` fetching the latest 10 transactions.
3. **Context Serialization**: Builds a massive `<USER_FINANCIAL_PROFILE>` string block containing email, credit score, risk level, income, active wallets, and all 10 recent transactions.
4. **Condensation Step**: Condenses the user query using `condense_question` (LLM call).
5. **RAG Search**: Performs a hybrid search on `policy_chunks` table using the condensed query, extracting policy texts into `rag_context`.
6. **System Prompt Formulation**: Prepends the full system prompt, `<USER_FINANCIAL_PROFILE>`, and `rag_context`.
7. **Message Assembly**: Appends the last 4 chat history messages and the new user message.
8. **LLM Invocation**: Calls the LLM via `get_client().chat.completions.create` and returns the generated answer.

## Problem
- This full sequence runs for every chat turn regardless of intent, blowing up context window and cost, adding latency with unnecessary database calls and LLM condensation calls.

## Proposed Optimization Flow
1. **Intent Classification (`intent_classifier.py`)**: Synchronously evaluate the user's message using keywords to determine if the turn is GENERIC, PROFILE_LIGHT, TRANSACTIONS, DTI_ANALYSIS, or FULL_REVIEW. Also extracts filters like transaction categories.
2. **Gating Logic**:
   - **RAG & Condensation Gating**: Skip `condense_question` and `policy_chunks` search unless intent is DTI_ANALYSIS or FULL_REVIEW, OR message contains ["policy", "law", "regulation", "eligible", "rule", "allowed", "limit", "comply", "legal"].
   - **Wallet Query Gating**: Skip `user_connections` query unless intent is PROFILE_LIGHT, DTI_ANALYSIS, or FULL_REVIEW, OR message contains ["wallet", "account", "balance", "connected"].
3. **Column Audit & Tiered Data Fetcher (`data_fetcher.py`)**: 
   - Before any queries are made, columns from `tamweel_results` are mapped to intent tiers (e.g. `credit_score` for PROFILE_LIGHT, etc.) and documented in `data_fetcher.py`.
   - Perform targeted async Supabase queries based entirely on the classified intent, limiting SELECT fields according to the column audit. Implements the conditional wallet query logic.
4. **Context Assembler (`context_assembler.py`)**: Format the fetched dict into a minified JSON `<FP>` block. Select the appropriate system prompt length, and append a sliding window of `max_turns=6` for the chat history.
5. **Integration (`main.py`)**: Rewire the `/api/v1/chat` endpoint to call these layers sequentially with the new gating conditions before hitting the LLM.
"""
