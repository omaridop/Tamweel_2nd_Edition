from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.schemas import ChatRequest, ChatResponse, ImprovementPlanRequest
from app.main import supabase, get_current_user, openai_client, engine, logger

router = APIRouter()

from app.services.intent_classifier import classify_intent, IntentType
from app.services.data_fetcher import fetch_context_for_intent
from app.services.context_assembler import assemble_messages
from app.services.intelligence_cache import invalidate_intelligence, get_or_compute_intelligence

@router.post("/api/v1/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Chat with Tamweel AI about the user's specific credit score and data, or portfolio stats for sponsors.
    """
    try:
        # Extract JWT identity
        user_email = current_user.get("email", current_user.get("sub", request.user_id))
        role = current_user.get("role", request.role)

        context_data_dict = {}
        
        from app.pipeline.query_rewriter import rewrite_query
        
        # Rewrite query if there is history
        search_query = request.message
        rewritten_info = None
        if hasattr(request, "history") and request.history:
            rewrite_res = rewrite_query(request.message, request.history)
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
                context_data_dict = await fetch_context_for_intent(supabase, request.user_id, user_email, search_query, intent_result)

        # 3. Vector Search (RAG)
        rag_context = ""
        sources = []
        search_res = None
        
        needs_rag = True
        if 'intent_result' in locals() and intent_result.intent == IntentType.FINANCIAL_ADVICE:
            needs_rag = False

        if supabase and needs_rag:
            try:
                query_vector = embed_query(search_query)
                
                # Old Semantic Cache Lookup Removed (Replaced by Redis Cache after Retrieval)

                search_res = supabase.rpc(
                    'hybrid_search_policy_chunks',
                    {'query_text': search_query, 'query_embedding': query_vector, 'match_count': 3}
                ).execute()
                
                if search_res.data:
                    # 1. Deduplicate by chunk ID
                    retrieved_chunks = {}
                    for doc in search_res.data:
                        p_name = doc.get('policy_name')
                        # Use content_hash or id to prevent overwriting different chunks from the same page
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
                    
                    retrieved_parents = retrieved_chunks

                    # 3. Merge Adjacent Chunks logically
                    sorted_chunks = sorted(retrieved_parents.values(), key=lambda x: (x['policy_name'] or "", x['chunk_index'] if x['chunk_index'] is not None else 0))
                    
                    merged_contexts = []
                    current_merge = None
                    
                    for chunk in sorted_chunks:
                        if not current_merge:
                            current_merge = chunk.copy()
                        elif current_merge['policy_name'] == chunk['policy_name'] and current_merge['chunk_index'] is not None and chunk['chunk_index'] is not None and chunk['chunk_index'] == current_merge['chunk_index'] + 1:
                            # Avoid appending if parent_content is identical (e.g. duplicate DB rows)
                            if chunk['parent_content'].strip() not in current_merge['parent_content']:
                                current_merge['parent_content'] += "\n\n" + chunk['parent_content']
                            current_merge['chunk_index'] = chunk['chunk_index']
                            current_merge['similarity'] = max(current_merge['similarity'], chunk['similarity'])
                        else:
                            merged_contexts.append(current_merge)
                            current_merge = chunk.copy()
                    if current_merge:
                        merged_contexts.append(current_merge)
                    
                    # 4. Rerank and Assemble Final Context
                    merged_contexts.sort(key=lambda x: x['similarity'], reverse=True)
                    merged_contexts = merged_contexts[:3] # Keep top 3 merged sections
                    
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
            except Exception as e:
                logger.error(f"RAG Retrieval Error: {e}", exc_info=True)
        
        import time
        start_time = time.time()
        
        # --- REDIS SMART CACHE LOOKUP ---
        if 'intent_result' in locals() and is_cacheable_query(intent_result.intent):
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
        # request.history is not in ChatRequest schema in main.py? 
        # Oh, the ChatRequest only has user_id, message, role. The API actually does not send history yet, or if it does, it's not in the schema.
        # Let's pass empty history for now, or check if it exists.
        history = getattr(request, 'history', [])
        
        current_intent = intent_result.intent if 'intent_result' in locals() else IntentType.GENERIC
        messages = assemble_messages(request.message, context_data_dict, history, rag_context, intent_type=current_intent)
        
        # Inject computed confidence
        conf_display = f"{int(conf_val * 100)}% ({confidence_label})"
        if messages and messages[0]["role"] == "system":
            messages[0]["content"] = messages[0]["content"].replace("<computed_confidence>", conf_display)

        # Let's append the JSON schema instructions to the system prompt to retain the JSON response requirement
        messages[0]["content"] += """

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
        
        # 5. Call LLM via DeepSeek with OpenRouter Fallback
        import openai
        import httpx
        from fastapi.responses import JSONResponse
        from tenacity import retry, retry_if_exception_type, wait_exponential, stop_after_attempt
        
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
            except Exception as fallback_e:
                logger.error(f"Both LLM providers failed. Fallback error: {fallback_e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "success": False,
                        "message": "The AI service is temporarily unavailable. Please try again shortly."
                    }
                )
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        try:
            response_text = response.choices[0].message.content
            
            # Robust JSON boundary extraction instead of brittle markdown splitting
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                json_str = response_text[start_idx:end_idx+1]
                import json
                parsed = json.loads(json_str)
            else:
                raise ValueError("No valid JSON object boundaries found in response.")
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
        if supabase and needs_rag and 'query_vector' in locals():
            if 'intent_result' in locals() and is_cacheable_query(intent_result.intent):
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
            "confidence": confidence_label.lower() if 'confidence_label' in locals() else "unknown",
            "confidence_score": conf_val if 'conf_val' in locals() else 0.0,
            "support_score": parsed.get("support_score", 1),
            "support_summary": parsed.get("support_summary", ""),
            "missing_information": parsed.get("missing_information", "None"),
            "sources": sources,
            "retrieval_stats": retrieval_stats,
            "suggested_followups": parsed.get("suggested_followups", []),
            "rewritten_info": rewritten_info if 'rewritten_info' in locals() else None
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
async def generate_improvement_plan(request: ImprovementPlanRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a personalized, data-driven improvement plan using Claude 3.5 Sonnet based on recent transactions.
    """
    try:
        actual_email = current_user.get("email", current_user.get("sub"))
        if actual_email != request.email:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
            
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
