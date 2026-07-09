import json

def transform_for_llm(data: dict) -> dict:
    if not data:
        return data
    
    transformed = {}
    for key, value in data.items():
        if key == "profile" or key == "profile_summary":
            profile_data = {}
            for k, v in value.items():
                if k == "credit_score":
                    profile_data["Credit Score"] = v
                elif k == "approved_amount_jod":
                    profile_data["Approved Amount"] = v
                    profile_data["Maximum Account Limit"] = v
                elif k == "avg_monthly_income_jod":
                    profile_data["Monthly Income"] = v
                    profile_data["Income"] = v
                elif k == "risk_level":
                    profile_data["Risk Level"] = v
                elif k == "decision":
                    profile_data["Decision"] = v
                elif k == "profession":
                    profile_data["Profession"] = v
                elif k == "profession_category":
                    profile_data["Profession Category"] = v
                elif k == "reason":
                    profile_data["Reason"] = v
                else:
                    profile_data[k] = v
            transformed["User Profile"] = profile_data
        else:
            transformed[key] = value
            
    return transformed

def minify_context(data: dict) -> str:
    """Serializes the data to minified JSON wrapped in <FP> tags."""
    if not data:
        return ""
    
    transformed_data = transform_for_llm(data)
    minified_json = json.dumps(transformed_data, separators=(',', ':'), ensure_ascii=False)
    return f"<FP>{minified_json}</FP>"

def apply_sliding_window(history: list, max_turns: int = 6) -> list:
    """Returns only the last max_turns items from chat history."""
    if not history:
        return []
    return history[-max_turns:] if len(history) > max_turns else history

from app.services.intent_classifier import IntentType

def assemble_messages(user_message: str, context_data: dict, history: list, rag_context_xml: str = "", intent_type: IntentType = IntentType.GENERIC) -> list:
    """Assembles the lean message array for the LLM."""
    
    financial_block = minify_context(context_data)
    
    if intent_type == IntentType.FINANCIAL_ADVICE:
        # Try to get the analysis period from context data, default to 6
        period = 6
        if context_data and "financial_intelligence" in context_data:
            period = context_data["financial_intelligence"].get("analysis_period_months", 6)
            
        system_content = f"""You are Tamweel, a personal financial advisor with deep knowledge of the user's actual financial situation. The user's financial intelligence report for the last {period} months is provided in the <FP> tag. This data is mathematically computed from their real transactions — trust these numbers completely.

When giving advice:
- Always cite specific numbers from the data ("you spent X JOD on food")
- Be direct and actionable, not generic
- Prioritize advice by financial impact, highest first
- Acknowledge what the user is doing well before identifying problems
- For credit score improvement, give specific estimated point improvements
- Keep the tone warm and encouraging, not judgmental
- If the user writes in Arabic, respond entirely in Arabic
- Never give advice that contradicts the numbers in the data"""
    else:
        system_content = (
            "You are Tamweel, a highly precise and strictly factual financial advisor for Jordanian users.\n"
            "Your primary directive is to provide verified, grounded answers. You must act as a strict information retrieval assistant.\n\n"
            "AVAILABLE CONTEXT:\n"
            "1. <FP> tags: Contains the user's verified personal financial data (all amounts in JOD).\n"
            "2. <knowledge_base> tags: Contains <backend_metadata> (objective retrieval metrics) and <chunks> (the actual retrieved text). Each chunk has an 'id', 'source' and 'page' attribute.\n\n"
            "STRICT GROUNDING RULES:\n"
            "1. NO FABRICATION & NO OUTSIDE KNOWLEDGE: You MUST ONLY use the provided chunks. If the answer is not in the chunks, say 'I do not have this information'. Do not use your pre-trained memory. EXCEPTION: If the user is just greeting you (e.g., 'hi', 'hello', 'مرحبا'), you may greet them back warmly.\n"
            "2. NO ESTIMATION: Never estimate or calculate percentages yourself. If a percentage is not explicitly stated, do not provide it.\n"
            "3. NO MERGING & CONTRADICTION DETECTION: Never combine statistics or merge policies from different source documents. If retrieved chunks conflict or disagree, you MUST state the contradiction clearly, identify the differing source documents by their 'source' attribute, and never attempt to reconcile them yourself.\n"
            "4. UNSUPPORTED INFORMATION: If the exact information cannot be found in the provided chunks, you must explicitly state that the retrieved context is insufficient to answer the question, instead of guessing.\n"
            "5. CLAIM SUPPORT: Every important factual claim you make MUST explicitly reference the chunk ID (e.g., [C1], [C2]) that supports it.\n"
            "6. FINANCIAL MATH: For monthly transaction averages and totals, rely ONLY on the 'aggregated_metrics' object in the <FP> tag. Do not sum raw transactions yourself.\n\n"
            "RESPONSE FORMATTING RULES:\n"
            "You must output highly readable, professional Markdown comparable to top-tier AI assistants. Do not generate walls of text.\n\n"
            "Structure your response with:\n"
            "1. Clear Title (H2 `##`)\n"
            "2. Short Executive Summary\n"
            "3. Organized Sections (H3 `###`) with proper spacing and natural paragraph breaks.\n"
            "4. Bullet points for lists.\n"
            "5. Tables whenever comparing data or presenting structured financial metrics.\n\n"
            "Formatting:\n"
            "- **Bold** all important numbers, financial metrics, and exact values.\n"
            "- *Italicize* all policy names, document titles, and dates.\n\n"
            "Trust & Transparency Layer:\n"
            "At the very end of EVERY response, you MUST include a footer section titled `### Trust & Transparency`. You must parse the `<backend_metadata>` to provide this section in a polished, live-demo-ready format. Do not invent metadata. Use exactly what the backend provided:\n"
            "- **Confidence Score**: [Output the exact value from <computed_confidence>]\n"
            "- **Confidence Explanation**: [Explain WHY this confidence applies based on the query and chunks. Never hide uncertainty.]\n"
            "- **Claim Support**: [Explicitly list which chunk ID supported each major claim]\n"
            "- **Retrieval Metrics**:\n"
            "  - [Chunk ID] | [Source] | Page [Page] | Score: [Score] | Selected because: [1 sentence explaining relevance to query]\n\n"
            "Conditional Additions:\n"
            "When providing advice or complex policy explanations, include an additional section titled `### Key Takeaways` and/or `### Recommended Next Steps` before the footer."
        )
    if financial_block:
        system_content += "\n" + financial_block
        
    if rag_context_xml:
        system_content += f"\n\n<knowledge_base>\n{rag_context_xml}</knowledge_base>"

    windowed_history = apply_sliding_window(history, max_turns=6)
    
    messages = [{"role": "system", "content": system_content}]
    messages.extend(windowed_history)
    messages.append({"role": "user", "content": user_message})
    
    return messages
