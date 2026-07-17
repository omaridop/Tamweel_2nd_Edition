from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from app.schemas import ChatRequest, ChatResponse, ImprovementPlanRequest
from app.main import supabase, get_current_user, openai_client, engine, logger, limiter

from app.services.intent_classifier import classify_intent, IntentType
from app.services.data_fetcher import fetch_context_for_intent
from app.services.context_assembler import assemble_messages
from app.services.intelligence_cache import invalidate_intelligence, get_or_compute_intelligence
from app.pipeline.embed import embed_query
from app.services.redis_cache import (
    is_cacheable_query,
    generate_cache_key,
    get_cached_response,
    set_cached_response
)

import time
import json
import openai
import httpx
from fastapi.responses import JSONResponse, StreamingResponse
from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
from app.pipeline.query_rewriter import rewrite_query

router = APIRouter()

# --- Module-level constants ---

_JSON_SCHEMA_PROMPT = """

JSON SCHEMA REQUIREMENT:
You MUST return your response as a valid JSON object matching the schema below. Do not output any other text.

JSON SCHEMA:
{
    "answer": "Your direct answer to the user's question, formatted in markdown. Use citations like [C1] where C1 is the Document ID.",
    "support_score": Integer from 1 to 5 indicating how strongly the extracts and user data support your answer (5 = explicitly stated, 1 = unsupported).,
    "support_summary": "A brief summary of how the extracts and user data support the answer.",
    "missing_information": "Any information requested by the user that was not found in the extracts or user data, or 'None'.",
    "suggested_followups": ["Follow up question 1", "Follow up question 2"]
}
"""

# --- Helper Functions for Chat Route ---

def _process_rag_results(search_data: list) -> tuple[str, list]:
    """Deduplicates, merges, and reranks RAG search results."""
    rag_context = ""
    sources = []

    # 1. Deduplicate by chunk ID
    retrieved_chunks = {}
    for doc in search_data:
        p_name = doc.get('policy_name')
        c_id = doc.get('id')
        key = (p_name, c_id)
        if key not in retrieved_chunks:
            retrieved_chunks[key] = {
                "policy_name": p_name,
                "chunk_index": doc.get('chunk_index'),
                "parent_content": doc.get('parent_content') or doc.get('content', ''),
                "similarity": doc.get('similarity', 0.0)
            }
        else:
            retrieved_chunks[key]["similarity"] = max(retrieved_chunks[key]["similarity"], doc.get('similarity', 0.0))

    # 2. Merge Adjacent Chunks logically
    sorted_chunks = sorted(retrieved_chunks.values(), key=lambda x: (x['policy_name'] or "", x['chunk_index'] if x['chunk_index'] is not None else 0))

    merged_contexts = []
    current_merge = None

    for chunk in sorted_chunks:
        if not current_merge:
            current_merge = chunk.copy()
        elif current_merge['policy_name'] == chunk['policy_name'] and current_merge['chunk_index'] is not None and chunk['chunk_index'] is not None and chunk['chunk_index'] == current_merge['chunk_index'] + 1:
            if chunk['parent_content'].strip() not in current_merge['parent_content']:
                current_merge['parent_content'] += "\n\n" + chunk['parent_content']
            current_merge['chunk_index'] = chunk['chunk_index']
            current_merge['similarity'] = max(current_merge['similarity'], chunk['similarity'])
        else:
            merged_contexts.append(current_merge)
            current_merge = chunk.copy()
    if current_merge:
        merged_contexts.append(current_merge)

    # 3. Rerank and Assemble Final Context
    merged_contexts.sort(key=lambda x: x['similarity'], reverse=True)
    merged_contexts = merged_contexts[:3]

    for idx, doc in enumerate(merged_contexts):
        if not doc['parent_content'].strip(): continue
        citation_id = f"C{idx+1}"
        rag_context += f"[{citation_id}] Source: {doc['policy_name']}\n{doc['parent_content']}\n\n"
        sources.append({
            "id": citation_id,
            "document_name": doc['policy_name'],
            "page": None,
            "similarity": doc['similarity']
        })
    return rag_context, sources

def _call_llm_with_fallback(messages: list):
    """Calls DeepSeek with retry logic, falling back to OpenRouter (GPT-4o-mini) on failure."""
    @retry(
        retry=retry_if_exception_type((httpx.RemoteProtocolError, httpx.ConnectError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        stop=stop_after_attempt(3),
        reraise=True
    )
    def call_llm_with_retry():
        return openai_client.chat.completions.create(
            model="deepseek/deepseek-chat",
            max_tokens=1024,
            messages=messages,
            response_format={"type": "json_object"}
        )

    try:
        response = call_llm_with_retry()
        return response
    except (httpx.RemoteProtocolError, httpx.ConnectError, httpx.TimeoutException) as e:
        return {
            "response": "عذراً، واجهنا مشكلة في الاتصال بالخادم. يرجى المحاولة مرة أخرى.",
            "answer": "عذراً، واجهنا مشكلة في الاتصال بالخادم. يرجى المحاولة مرة أخرى.",
            "support_score": 1,
            "support_summary": "Network connection error.",
            "missing_information": "None",
            "sources": [],
            "retrieval_stats": {"generation_time_ms": 0, "chunks_retrieved": 0, "chunks_used": 0},
            "suggested_followups": []
        }
    except (openai.AuthenticationError, openai.APIConnectionError, openai.RateLimitError, openai.APIStatusError, Exception) as e:
        if isinstance(e, openai.APIStatusError) and 400 <= e.status_code < 500:
            logger.error(f"DeepSeek 4xx logic error: {e.status_code}. Not retrying.")
        else:
            logger.warning(f"DeepSeek request failed.\nReason: {type(e).__name__}\nFalling back to OpenRouter...")

        try:
            response = openai_client.chat.completions.create(
                model="openai/gpt-4o-mini",
                max_tokens=1024,
                messages=messages,
                response_format={"type": "json_object"}
            )
            logger.info("OpenRouter fallback succeeded.")
            return response
        except Exception as fallback_e:
            logger.error(f"Both LLM providers failed. Fallback error: {fallback_e}")
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "The AI service is temporarily unavailable. Please try again shortly."
                }
            )

def _extract_and_parse_json(response_text: str) -> dict:
    """Robust JSON boundary extraction instead of brittle markdown splitting."""
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')

    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        json_str = response_text[start_idx:end_idx+1]
        return json.loads(json_str)
    else:
        raise ValueError("No valid JSON object boundaries found in response.")


@router.post("/api/v1/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_with_ai(request: Request, body: ChatRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Chat with Tamweel AI about the user's specific credit score and data, or portfolio stats for sponsors.
    """
    try:
        # Extract JWT identity
        user_email = current_user.get("email", current_user.get("sub", body.user_id))
        role = current_user.get("role") or "user"

        # Initialize all conditional variables to safe defaults to avoid 'in locals()' guards
        context_data_dict = {}
        intent_result = None
        rewritten_info = None
        query_vector = None
        conf_val = 0.0
        confidence_label = "UNKNOWN"

        # Rewrite query if there is history
        search_query = body.message
        if hasattr(body, "history") and body.history:
            rewrite_res = rewrite_query(body.message, body.history)
            if rewrite_res.rewrite_needed:
                search_query = rewrite_res.rewritten_query
                rewritten_info = rewrite_res.model_dump()

        # 1. Fetch Context based on Role
        if supabase:
            if role == "sponsor":
                # Fetch aggregated portfolio data for the sponsor
                response = supabase.table("tamweel_results").select("credit_score, risk_level, approved_amount_jod").order("generated_at", desc=True).limit(50).execute()
                if response.data:
                    avg_score = sum(r['credit_score'] for r in response.data) / len(response.data)
                    high_risk = len([r for r in response.data if r['risk_level'] == 'High'])
                    total_approved = sum(r['approved_amount_jod'] for r in response.data)
                    context_data_dict = {
                        "Portfolio Stats": {
                            "Average Credit Score": round(avg_score, 1),
                            "High Risk Borrowers": high_risk,
                            "Total Capital Approved (JOD)": total_approved
                        }
                    }
            else:
                # 2. Intent Classification and Data Fetching
                intent_result = classify_intent(search_query)
                context_data_dict = await fetch_context_for_intent(supabase, body.user_id, user_email, search_query, intent_result)

        # 3. Vector Search (RAG)
        rag_context = ""
        sources = []

        needs_rag = not (intent_result is not None and intent_result.intent == IntentType.FINANCIAL_ADVICE)

        if supabase and needs_rag:
            try:
                query_vector = embed_query(search_query)

                # Old Semantic Cache Lookup Removed (Replaced by Redis Cache after Retrieval)

                search_res = supabase.rpc(
                    'hybrid_search_policy_chunks',
                    {'query_text': search_query, 'query_embedding': query_vector, 'match_count': 3}
                ).execute()

                if search_res.data:
                    rag_context, sources = _process_rag_results(search_res.data)
            except Exception as e:
                logger.error(f"RAG Retrieval Error: {e}", exc_info=True)

        start_time = time.time()

        # --- REDIS SMART CACHE LOOKUP ---
        if intent_result is not None and is_cacheable_query(intent_result.intent):
            retrieved_doc_ids = [s['document_name'] for s in sources] if sources else []
            cache_key = generate_cache_key(search_query, retrieved_doc_ids, "v1")

            cached_response = await get_cached_response(cache_key)
            if cached_response:
                return {
                    "response": cached_response.get("answer"),
                    "answer": cached_response.get("answer"),
                    "confidence": "high",
                    "confidence_score": cached_response.get("confidence", 0.99),
                    "support_score": 5,
                    "support_summary": "Served from Redis Smart Cache.",
                    "missing_information": "None",
                    "sources": sources,
                    "retrieval_stats": {"generation_time_ms": int((time.time() - start_time) * 1000), "chunks_retrieved": len(sources), "chunks_used": len(sources)},
                    "suggested_followups": []
                }
        # --------------------------------

        # Calculate RAG confidence
        top_score = 0.0
        if sources:
            top_score = max([s.get("similarity", 0.0) for s in sources])

        confidence_label = engine.get_confidence(top_score) if sources else "UNKNOWN"
        if top_score == 0:
            conf_val = 0.0
        elif top_score < 0.1:
            conf_val = min(top_score * 50.0, 1.0)
        else:
            conf_val = min(top_score, 1.0)

        # 4. Assemble Messages for LLM
        # body.history is not in ChatRequest schema — pass empty list if absent.
        history = getattr(body, 'history', [])

        current_intent = intent_result.intent if intent_result is not None else IntentType.GENERIC
        messages = assemble_messages(body.message, context_data_dict, history, rag_context, intent_type=current_intent)

        # Inject computed confidence
        conf_display = f"{int(conf_val * 100)}% ({confidence_label})"
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = messages[0]["content"].replace("<computed_confidence>", conf_display)

        # Append the JSON schema instructions to the system prompt
        messages[0]["content"] += _JSON_SCHEMA_PROMPT

        # 5. Call LLM via DeepSeek with OpenRouter Fallback
        response = _call_llm_with_fallback(messages)
        if isinstance(response, (dict, JSONResponse)):
            return response

        generation_time_ms = int((time.time() - start_time) * 1000)

        try:
            response_text = response.choices[0].message.content
            parsed = _extract_and_parse_json(response_text)
        except Exception as e:
            logger.error(f"JSON Parse Error: {e}", exc_info=True)
            parsed = {
                "answer": response.choices[0].message.content if hasattr(response, 'choices') else "Error generating response",
                "support_score": 1,
                "support_summary": "Failed to parse structured output.",
                "missing_information": "Unknown",
                "suggested_followups": []
            }

        # --- REDIS SMART CACHE STORAGE ---
        if supabase and needs_rag and query_vector is not None:
            if intent_result is not None and is_cacheable_query(intent_result.intent):
                retrieved_doc_ids = [s['document_name'] for s in sources] if sources else []
                cache_key = generate_cache_key(search_query, retrieved_doc_ids, "v1")
                citations = retrieved_doc_ids

                background_tasks.add_task(
                    set_cached_response,
                    cache_key,
                    parsed.get("answer", ""),
                    citations,
                    conf_val
                )
        # -----------------------------

        retrieval_stats = {
            "generation_time_ms": generation_time_ms,
            "chunks_retrieved": len(sources),
            "chunks_used": len(sources)
        }

        return {
            "response": parsed.get("answer", ""),
            "answer": parsed.get("answer", ""),
            "confidence": confidence_label.lower(),
            "confidence_score": conf_val,
            "support_score": parsed.get("support_score", 1),
            "support_summary": parsed.get("support_summary", ""),
            "missing_information": parsed.get("missing_information", "None"),
            "sources": sources,
            "retrieval_stats": retrieval_stats,
            "suggested_followups": parsed.get("suggested_followups", []),
            "rewritten_info": rewritten_info
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        safe_msg = repr(e).encode('ascii', 'replace').decode('ascii')
        logger.error(f"Chat Error: {safe_msg}", exc_info=True)
        return {
            "response": "عذراً، واجهت مشكلة في معالجة طلبك. يرجى المحاولة مرة أخرى لاحقاً.",
            "answer": f"عذراً، واجهت مشكلة: {safe_msg}",
            "support_score": 1,
            "support_summary": f"Error processing request: {safe_msg}",
            "missing_information": "None",
            "sources": [],
            "retrieval_stats": {"generation_time_ms": 0, "chunks_retrieved": 0, "chunks_used": 0},
            "suggested_followups": []
        }

@router.post("/api/v1/ai/improvement-plan")
@limiter.limit("3/minute")
async def generate_improvement_plan(request: Request, body: ImprovementPlanRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a personalized, data-driven improvement plan using Claude 3.5 Sonnet based on recent transactions.
    """
    try:
        actual_email = current_user.get("email", current_user.get("sub"))
        if actual_email != body.email:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's data")

        if not supabase:
            raise HTTPException(status_code=500, detail="Database not connected")

        # 1. Fetch Financial Metrics
        metrics_res = supabase.rpc('calculate_financial_health', {'target_email': body.email}).execute()
        metrics = metrics_res.data if metrics_res.data else {}

        # 2. Fetch Recent Transactions
        tx_res = supabase.table("transactions").select("*").eq("user_email", body.email).order("created_at", desc=True).limit(15).execute()
        tx_data = tx_res.data if tx_res.data else []
        tx_summary = "\n".join([f"- {t['created_at'][:10]}: {t['type']} | {t['category']} | {t['amount']} JOD" for t in tx_data])

        # 3. Formulate System Prompt
        system_prompt = f"""
        You are a Senior Financial Advisor for Tamweel AI.
        Generate a personalized, data-driven financial improvement plan for the user.

        USER DATA:
        Name: {body.user_id}
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

        response = openai_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=300,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Please generate my personalized improvement plan based on my recent data."}
            ]
        )

        return {"plan": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Plan Generation Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate plan")


@router.post("/api/v1/ai/roadmap")
@limiter.limit("3/minute")
async def generate_90_day_roadmap(request: Request, body: ImprovementPlanRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a structured 90-day credit score improvement roadmap.
    Returns 3 monthly phases with specific actions, target score changes, and JOD amounts.
    Pulls live financial intelligence from Supabase — not hardcoded.
    """
    from app.services.financial_intelligence import compute_financial_intelligence

    try:
        actual_email = current_user.get("email", current_user.get("sub"))
        if actual_email != body.email:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's data")

        if not supabase:
            raise HTTPException(status_code=500, detail="Database not connected")

        # 1. Fetch real financial intelligence
        try:
            intel = await compute_financial_intelligence(supabase, body.email)
        except ValueError:
            intel = {}

        # 2. Pull recent credit score
        score_res = supabase.table("tamweel_results") \
            .select("credit_score, risk_level, approved_amount_jod") \
            .eq("email", body.email) \
            .order("generated_at", desc=True) \
            .limit(1).execute()
        profile = score_res.data[0] if score_res.data else {}
        current_score = profile.get("credit_score", 0)
        risk_level = profile.get("risk_level", "Unknown")

        # 3. Build data-rich context for the LLM
        spending = intel.get("spending", {})
        top_cats = spending.get("top_3_categories", [])
        savings_rate = spending.get("savings_rate_percent", 0)
        by_category = spending.get("by_category", {})
        tips = intel.get("credit_improvement_tips", [])
        alerts = intel.get("alerts", [])

        # Format category spending summary
        cat_summary = "\n".join([
            f"  - {cat}: {vals['monthly_average']:.0f} JOD/month ({vals['percentage_of_income']:.1f}% of income)"
            for cat, vals in by_category.items()
        ][:5]) or "  No category data available"

        system_prompt = f"""You are a Senior Credit Analyst at Tamweel AI.
Generate a structured 90-day credit score improvement roadmap for this user.

USER FINANCIAL PROFILE:
- Current Credit Score: {current_score}/100
- Risk Level: {risk_level}
- Savings Rate: {savings_rate:.1f}%
- Top Spending Categories: {', '.join(top_cats) if top_cats else 'Unknown'}

MONTHLY SPENDING BREAKDOWN:
{cat_summary}

ACTIVE ALERTS:
{chr(10).join(['  - ' + a for a in alerts[:4]]) if alerts else '  None'}

DATA-DRIVEN TIPS:
{chr(10).join(['  - ' + t for t in tips]) if tips else '  None'}

OUTPUT FORMAT: Return ONLY a valid JSON object matching this exact schema:
{{
  "current_score": {current_score},
  "target_score_90_days": <integer>,
  "phases": [
    {{
      "phase": 1,
      "label": "Month 1 — Foundation",
      "focus": "<one sentence focus>",
      "actions": ["<specific action with JOD amount>", "<action>", "<action>"],
      "score_impact": "+<N> points",
      "priority": "high"
    }},
    {{
      "phase": 2,
      "label": "Month 2 — Build",
      "focus": "<focus>",
      "actions": ["<action>", "<action>", "<action>"],
      "score_impact": "+<N> points",
      "priority": "medium"
    }},
    {{
      "phase": 3,
      "label": "Month 3 — Consolidate",
      "focus": "<focus>",
      "actions": ["<action>", "<action>", "<action>"],
      "score_impact": "+<N> points",
      "priority": "medium"
    }}
  ],
  "key_warning": "<the single most important risk to address>",
  "summary": "<2-sentence summary of the plan>"
}}

RULES:
- Use REAL numbers from the user's data (JOD amounts, percentages, category names).
- Score impact must be realistic (5-12 points per phase max).
- Actions must be specific and actionable (e.g., "Reduce food spending from 180 JOD to 130 JOD/month").
- Do NOT add text outside the JSON object."""

        response = openai_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=900,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate my 90-day credit score improvement roadmap."}
            ],
            response_format={"type": "json_object"}
        )

        raw_text = response.choices[0].message.content
        try:
            roadmap = _extract_and_parse_json(raw_text)
        except Exception:
            roadmap = {"raw": raw_text, "error": "Could not parse structured roadmap"}

        return {"roadmap": roadmap}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Roadmap Generation Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate roadmap")


@router.post("/api/v1/chat/stream")
@limiter.limit("10/minute")
async def chat_stream(
    request: Request,
    body: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Streaming version of /api/v1/chat.
    Returns Server-Sent Events (SSE) — each event is a JSON chunk:
      data: {"token": "..."}          <- partial text token
      data: {"done": true, "meta": {...}}  <- final event with sources/stats
    The existing /api/v1/chat endpoint is untouched and remains the fallback.
    """
    user_email = current_user.get("email", current_user.get("sub", body.user_id))
    role = current_user.get("role") or "user"

    # --- Rewrite query if history present ---
    search_query = body.message
    rewritten_info = None
    if getattr(body, "history", None):
        rewrite_res = rewrite_query(body.message, body.history)
        if rewrite_res.rewrite_needed:
            search_query = rewrite_res.rewritten_query
            rewritten_info = rewrite_res.model_dump()

    # --- Intent + context (same pipeline as /chat) ---
    context_data_dict = {}
    intent_result = None
    sources = []
    conf_val = 0.0
    confidence_label = "UNKNOWN"

    if supabase:
        if role == "sponsor":
            res = supabase.table("tamweel_results").select("credit_score, risk_level, approved_amount_jod").order("generated_at", desc=True).limit(50).execute()
            if res.data:
                avg_score = sum(r["credit_score"] for r in res.data) / len(res.data)
                high_risk = len([r for r in res.data if r["risk_level"] == "High"])
                total_approved = sum(r["approved_amount_jod"] for r in res.data)
                context_data_dict = {"Portfolio Stats": {"Average Credit Score": round(avg_score, 1), "High Risk Borrowers": high_risk, "Total Capital Approved (JOD)": total_approved}}
        else:
            intent_result = classify_intent(search_query)
            context_data_dict = await fetch_context_for_intent(supabase, body.user_id, user_email, search_query, intent_result)

    # --- RAG retrieval ---
    rag_context = ""
    needs_rag = not (intent_result is not None and intent_result.intent == IntentType.FINANCIAL_ADVICE)
    if supabase and needs_rag:
        try:
            query_vector = embed_query(search_query)
            search_res = supabase.rpc(
                "hybrid_search_policy_chunks",
                {"query_text": search_query, "query_embedding": query_vector, "match_count": 3}
            ).execute()
            if search_res.data:
                rag_context, sources = _process_rag_results(search_res.data)
        except Exception as e:
            logger.error(f"RAG Retrieval Error (stream): {e}", exc_info=True)

    # --- Confidence ---
    if sources:
        top_score = max(s.get("similarity", 0.0) for s in sources)
        confidence_label = engine.get_confidence(top_score)
        conf_val = min(top_score, 1.0) if top_score >= 0.1 else min(top_score * 50.0, 1.0)

    # --- Assemble messages ---
    current_intent = intent_result.intent if intent_result else IntentType.GENERIC
    history = getattr(body, "history", [])
    messages = assemble_messages(body.message, context_data_dict, history, rag_context, intent_type=current_intent)
    conf_display = f"{int(conf_val * 100)}% ({confidence_label})"
    if messages and messages[0]["role"] == "system":
        messages[0]["content"] = messages[0]["content"].replace("<computed_confidence>", conf_display)
    # For streaming we ask for plain text, not JSON — much faster token delivery
    messages[0]["content"] += "\n\nIMPORTANT: Reply in plain markdown text. Do NOT wrap in JSON."

    start_time = time.time()

    async def event_generator():
        """Yields SSE-formatted chunks."""
        full_text = ""
        try:
            stream = openai_client.chat.completions.create(
                model="deepseek/deepseek-chat",
                max_tokens=1024,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else ""
                if delta:
                    full_text += delta
                    payload = json.dumps({"token": delta}, ensure_ascii=False)
                    yield f"data: {payload}\n\n"
        except Exception as e:
            logger.error(f"Stream LLM error: {e}", exc_info=True)
            # Fallback: try GPT-4o-mini
            try:
                stream = openai_client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    max_tokens=1024,
                    messages=messages,
                    stream=True,
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content if chunk.choices else ""
                    if delta:
                        full_text += delta
                        payload = json.dumps({"token": delta}, ensure_ascii=False)
                        yield f"data: {payload}\n\n"
            except Exception as fallback_e:
                logger.error(f"Stream fallback also failed: {fallback_e}", exc_info=True)
                error_payload = json.dumps({"token": "عذراً، واجهنا مشكلة في الاتصال. يرجى المحاولة مرة أخرى."})
                yield f"data: {error_payload}\n\n"

        # Final metadata event
        generation_time_ms = int((time.time() - start_time) * 1000)
        done_payload = json.dumps({
            "done": True,
            "meta": {
                "sources": sources,
                "confidence": confidence_label.lower(),
                "confidence_score": conf_val,
                "rewritten_info": rewritten_info,
                "retrieval_stats": {
                    "generation_time_ms": generation_time_ms,
                    "chunks_retrieved": len(sources),
                    "chunks_used": len(sources),
                }
            }
        }, ensure_ascii=False)
        yield f"data: {done_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Connection": "keep-alive",
        }
    )
