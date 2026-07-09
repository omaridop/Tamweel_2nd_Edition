"""OpenAI-compatible client for OpenRouter."""

import json
from openai import OpenAI, APIError
from .config import settings

# Global client singleton
_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set.")
        _client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": settings.OPENROUTER_REFERER,
                "X-Title": settings.OPENROUTER_TITLE,
            },
            timeout=float(settings.LLM_TIMEOUT_S),
            max_retries=0,  # We handle retries via tenacity in the specific modules
        )
    return _client

class ProviderResponseError(Exception):
    """Raised when the provider (e.g. Gemini via OpenRouter) returns an invalid response."""
    pass

def first_choice_content(resp) -> str:
    """Extracts the first choice content from a chat completion response."""
    if not resp or not hasattr(resp, "choices") or not resp.choices:
        raise ProviderResponseError("No choices in LLM response.")
    return resp.choices[0].message.content or ""
