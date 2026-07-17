import json
import re
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from openai import APIError
from .config import settings
from .llm import ProviderResponseError, first_choice_content, get_client

def _retrieval_prompt() -> str:
    return (
        "You are an expert bilingual financial archivist. Your job is to analyze the provided text chunk "
        "and generate a comprehensive retrieval representation to maximize semantic search accuracy in both Arabic and English.\n"
        "You must return STRICT JSON exactly in this format:\n"
        "{\n"
        '  "questions_en": ["3 to 8 English questions this text answers"],\n'
        '  "questions_ar": ["3 to 8 Arabic questions this text answers"],\n'
        '  "keywords_en": ["list of English keywords"],\n'
        '  "keywords_ar": ["list of Arabic keywords"],\n'
        '  "aliases": ["common aliases, acronyms, or financial terminology related to the text"]\n'
        "}"
    )

@retry(retry=retry_if_exception_type((APIError, ProviderResponseError, json.JSONDecodeError)),
       wait=wait_exponential(multiplier=1, min=2, max=20),
       stop=stop_after_attempt(3), reraise=True)
def generate_bilingual_representation(text: str) -> dict:
    messages = [
        {"role": "system", "content": _retrieval_prompt()},
        {"role": "user", "content": text}
    ]
    kwargs = {
        "model": settings.CHUNK_MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"}
    }
    resp = get_client().chat.completions.create(
        timeout=float(settings.INGEST_TIMEOUT_S), **kwargs)
    
    content = first_choice_content(resp)
    
    # parse json
    s = content.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s).strip()
    
    data = json.loads(s)
    return {
        "questions_en": data.get("questions_en", []),
        "questions_ar": data.get("questions_ar", []),
        "keywords_en": data.get("keywords_en", []),
        "keywords_ar": data.get("keywords_ar", []),
        "aliases": data.get("aliases", [])
    }
