import json
from openai import OpenAI
from pydantic import BaseModel, Field
from app.pipeline.config import PipelineSettings
import logging

logger = logging.getLogger(__name__)

class LLMRewriteOutput(BaseModel):
    original_query: str
    rewritten_query: str
    rewrite_needed: bool
    reason: str = Field(description="Explanation of why a rewrite was needed or not.")

class RewriteResult(BaseModel):
    original_query: str
    rewritten_query: str
    rewrite_needed: bool
    reason: str = ""
    history_messages_used: int = 0
    rewrite_latency_ms: int = 0

REWRITE_PROMPT = """
You are a Query Rewriter for a bilingual (Arabic/English) financial AI assistant.
Your task is to analyze the user's current message in the context of the previous conversation history, and rewrite it into a standalone query IF it is an ambiguous follow-up.

Rules:
- Do not answer the question.
- Do not add new information.
- Only transform ambiguous follow-up questions (e.g. "What about for freelancers?", "هل ينطبق على الموظفين؟", "Why?").
- Preserve user intent exactly.
- Keep financial terminology accurate.
- Output the exact same language as the user's current query.
- If the current query is already perfectly standalone and unambiguous, set rewrite_needed to false and rewritten_query to the original_query.
- NEVER rewrite complete personal questions like "What is the minimum income requirement?", "My credit score is low, why?", or "What is my approved amount?". Protect user-specific financial queries.

Examples:
History: User: "ما هي شروط التمويل؟" -> Assistant: "شروط التمويل هي 1 و 2..."
Current Query: "وماذا عن الموظفين؟"
Output rewritten_query: "ما هي شروط التمويل للموظفين؟"

History: User: "What documents are required for a loan?" -> Assistant: "You need ID and salary slip."
Current Query: "What about freelancers?"
Output rewritten_query: "What documents are required for freelancers applying for a loan?"

History: User: "What is my credit score?" -> Assistant: "Your score is 600."
Current Query: "Why is it low?"
Output rewritten_query: "Why is my credit score low?" (MUST rewrite ambiguous pronouns so keywords are preserved for intent classification)

History: User: "My credit score is 600."
Current Query: "My credit score is low, why?"
Output rewritten_query: "My credit score is low, why?" (set rewrite_needed to false because the query is ALREADY a fully complete personal question)
"""

def rewrite_query(current_query: str, history: list) -> RewriteResult:
    if not history:
        return RewriteResult(
            original_query=current_query,
            rewritten_query=current_query,
            rewrite_needed=False
        )

    # Keep only the last 5 messages to avoid large token usage and preserve relevance
    recent_history = history[-5:] if len(history) > 5 else history

    # Format history for prompt
    history_text = ""
    for msg in recent_history:
        # Expected format from frontend: {"role": "user" or "assistant", "content": "..."}
        # or just passing a list of messages. We'll handle dicts.
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", str(msg))
            history_text += f"{role.capitalize()}: {content}\n"
        else:
            history_text += f"{msg}\n"
            
    if not history_text.strip():
        return RewriteResult(
            original_query=current_query,
            rewritten_query=current_query,
            rewrite_needed=False
        )

    user_prompt = f"""
Conversation History:
{history_text}

Current Query:
{current_query}
"""

    settings = PipelineSettings()
    client = OpenAI(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        default_headers={"HTTP-Referer": settings.OPENROUTER_REFERER}
    )

    import time
    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",  # using gpt-4o-mini via OpenRouter for fast json structured output
            messages=[
                {"role": "system", "content": REWRITE_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_schema", "json_schema": {
                "name": "rewrite_result",
                "schema": LLMRewriteOutput.model_json_schema()
            }},
            temperature=0.0
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        result_json = json.loads(response.choices[0].message.content)
        llm_out = LLMRewriteOutput(**result_json)
        
        return RewriteResult(
            original_query=llm_out.original_query,
            rewritten_query=llm_out.rewritten_query,
            rewrite_needed=llm_out.rewrite_needed,
            reason=llm_out.reason,
            history_messages_used=len(recent_history),
            rewrite_latency_ms=latency_ms
        )
    except Exception as e:
        logger.error(f"Query rewrite failed: {e}", exc_info=True)
        return RewriteResult(
            original_query=current_query,
            rewritten_query=current_query,
            rewrite_needed=False,
            reason=f"Error: {e}",
            history_messages_used=len(recent_history),
            rewrite_latency_ms=int((time.time() - start_time) * 1000)
        )
