"""Embeddings via Gemini Embeddings.

All vectors are L2-normalized. Implements batching and retry logic for resilience.
"""

import math
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Sequence

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
from google import genai
from google.genai.errors import APIError

from .config import settings

_OPENROUTER_EMBED_URL = "https://openrouter.ai/api/v1/embeddings"
_DEFAULT_EMBED_MODEL = "openai/text-embedding-3-small"

_RETRYABLE = (APIError, Exception) # Catch APIError or connectivity issues

def _normalize(vec: Sequence[float]) -> list[float]:
    norm = math.sqrt(sum(float(x) * float(x) for x in vec))
    if norm == 0.0:
        return [float(x) for x in vec]
    return [float(x) / norm for x in vec]

@retry(retry=retry_if_exception_type(_RETRYABLE),
       wait=wait_exponential(multiplier=1, min=2, max=30),
       stop=stop_after_attempt(5), reraise=True)
def _embed_batch(inputs: list[str]) -> list[list[float]]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise Exception("OPENROUTER_API_KEY is missing.")

    model_name = settings.EMBED_MODEL if (hasattr(settings, "EMBED_MODEL") and settings.EMBED_MODEL) else _DEFAULT_EMBED_MODEL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    dimensions = 768
    if hasattr(settings, "EMBED_DIM") and settings.EMBED_DIM > 0:
        dimensions = settings.EMBED_DIM

    payload = {
        "model": model_name,
        "input": inputs,
    }
    
    res = requests.post(_OPENROUTER_EMBED_URL, headers=headers, json=payload)
    if not res.ok:
        raise Exception(f"OpenRouter embedding failed: {res.text}")
        
    data = res.json()
    if "data" not in data:
        raise Exception(f"Invalid OpenRouter response: {data}")
        
    vectors = []
    # Sort by index to maintain order, and truncate/normalize to required dimensions
    for d in sorted(data["data"], key=lambda x: x.get("index", 0)):
        vec = d["embedding"]
        if len(vec) > dimensions:
            # text-embedding-3-small supports Matryoshka truncation
            vec = _normalize(vec[:dimensions])
        vectors.append(vec)
        
    return vectors

def _embed_resilient(inputs: list[str]) -> list[list[float]]:
    try:
        return _embed_batch(inputs)
    except Exception as exc:
        if len(inputs) == 1:
            raise
        mid = len(inputs) // 2
        return _embed_resilient(inputs[:mid]) + _embed_resilient(inputs[mid:])

def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Embed many texts (auto-batched, concurrent), normalized, in order."""
    limit = getattr(settings, 'EMBED_MAX_CHARS', 8192)
    cleaned = [((t or " ").strip() or " ")[:limit] for t in texts]
    if not cleaned:
        return []

    batch = getattr(settings, 'EMBED_BATCH', 100)
    batches = [cleaned[i:i + batch] for i in range(0, len(cleaned), batch)]
    
    out = []
    with ThreadPoolExecutor(max_workers=getattr(settings, 'EMBED_CONCURRENCY', 5)) as ex:
        for vectors in ex.map(_embed_resilient, batches):
            out.extend(_normalize(v) for v in vectors)
    return out

def embed_query(query: str) -> list[float]:
    """Embed a single query string and return the vector."""
    res = embed_texts([query])
    return res[0] if res else []
