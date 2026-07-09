"""Document -> chunked knowledge base for Tamweel AI.

This module replaces the LLM Q&A generator with a robust LLM Markdown Transcriber + chunker.
This preserves exact numerical values, percentages, and tabular constraints.
"""

import base64
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

try:
    import fitz
except ImportError:
    fitz = None

from openai import APIError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .config import settings
from .llm import ProviderResponseError, first_choice_content, get_client
from .extract import _pdf_batch_bytes, _pages_text
from .retrieval_generator import generate_bilingual_representation

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 300) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            match = re.search(r'\n\s*\n', text[end - overlap:end])
            if match:
                end = (end - overlap) + match.end()
            else:
                match = re.search(r'\.\s', text[end - overlap:end])
                if match:
                    end = (end - overlap) + match.end()
        chunks.append(text[start:end].strip())
        start = end - overlap
        if start >= len(text) or end >= len(text):
            break
    return [c for c in chunks if c]

def _system_prompt() -> str:
    return (
        "You are an expert OCR and document transcriber. "
        "Transcribe the provided document pages into accurate, structured Markdown. "
        "You MUST preserve all text, tables, numbers, targets, and constraints exactly as they appear. "
        "Do NOT summarize, paraphrase, or omit any information. "
        "Return STRICT JSON exactly in this format: {\"markdown\": \"full transcribed markdown text here\"}"
    )

def _loads_markdown(content: str) -> str:
    s = (content or "").strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s).strip()
    try:
        data = json.loads(s)
        return data.get("markdown", "")
    except json.JSONDecodeError:
        return s

@retry(retry=retry_if_exception_type((APIError, ProviderResponseError)),
       wait=wait_exponential(multiplier=1, min=2, max=20),
       stop=stop_after_attempt(3), reraise=True)
def _request(messages: list[dict], *, json_mode: bool, plugins: Optional[list]) -> str:
    kwargs: dict = {
        "model": settings.CHUNK_MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 4000,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if plugins:
        kwargs["extra_body"] = {"plugins": plugins}
        
    resp = get_client().chat.completions.create(
        timeout=float(settings.INGEST_TIMEOUT_S), **kwargs)
    return first_choice_content(resp)

def _call(messages: list[dict], *, plugins: Optional[list] = None) -> str:
    try:
        content = _request(messages, json_mode=True, plugins=plugins)
    except APIError as exc:
        if getattr(exc, "status_code", None) in (400, 404, 422):
            content = _request(messages, json_mode=False, plugins=plugins)
        else:
            raise
    return _loads_markdown(content)

def _qa_batch(path: Path, start: int, end: int, total: int) -> tuple[list[dict], str]:
    logger.info(f"Transcribing pages {start+1}-{end} of {total}...")
    plugins = [{"id": "file-parser", "pdf": {"engine": settings.PDF_ENGINE}}]
    parent_text = _pages_text(path, start, end)

    try:
        b64 = base64.b64encode(_pdf_batch_bytes(path, start, end)).decode("ascii")
        messages = [
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": [
                {"type": "text", "text": "Transcribe the following document exactly as requested."},
                {"type": "file", "file": {
                    "filename": f"{path.stem}_p{start + 1}-{end}.pdf",
                    "file_data": f"data:application/pdf;base64,{b64}",
                }},
            ]},
        ]
        markdown_text = _call(messages, plugins=plugins)
    except Exception as exc:
        logger.warning(f"Vision read failed for pages {start+1}-{end}: {exc}. Trying text fallback...")
        markdown_text = parent_text

    units = []
    if markdown_text.strip():
        chunks = chunk_text(markdown_text)
        for c in chunks:
            rep = generate_bilingual_representation(c)
            # Combine the representation into a single text block for embedding
            answer_content = (
                f"Questions (EN):\n{chr(10).join(rep['questions_en'])}\n\n"
                f"Questions (AR):\n{chr(10).join(rep['questions_ar'])}\n\n"
                f"Keywords (EN): {', '.join(rep['keywords_en'])}\n"
                f"Keywords (AR): {', '.join(rep['keywords_ar'])}\n"
                f"Aliases: {', '.join(rep['aliases'])}"
            )
            units.append({
                "page": start,
                "topic": "Document Excerpt",
                "questions_en": rep["questions_en"],
                "answer_en": answer_content,
                "questions_ar": rep["questions_ar"],
                "answer_ar": "",
                "parent_text": c
            })
    return units, markdown_text

def generate_qa(path: str | Path, file_type: str) -> list[dict]:
    path = Path(path)
    if file_type == "pdf":
        if not fitz:
            raise ImportError("PyMuPDF required for PDF reading.")
        with fitz.open(str(path)) as d:
            total = d.page_count
        batch = settings.QA_PAGES_PER_BATCH
        spans = [(s, min(s + batch, total)) for s in range(0, total, batch)]
        units = []
        with ThreadPoolExecutor(max_workers=settings.INGEST_CONCURRENCY) as ex:
            for batch_units, parent_text in ex.map(lambda se: _qa_batch(path, se[0], se[1], total), spans):
                for u in batch_units:
                    u["parent_text"] = parent_text
                units.extend(batch_units)
        return units
    else:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            units = []
            if text.strip():
                chunks = chunk_text(text)
                for c in chunks:
                    rep = generate_bilingual_representation(c)
                    answer_content = (
                        f"Questions (EN):\n{chr(10).join(rep['questions_en'])}\n\n"
                        f"Questions (AR):\n{chr(10).join(rep['questions_ar'])}\n\n"
                        f"Keywords (EN): {', '.join(rep['keywords_en'])}\n"
                        f"Keywords (AR): {', '.join(rep['keywords_ar'])}\n"
                        f"Aliases: {', '.join(rep['aliases'])}"
                    )
                    units.append({
                        "page": 0,
                        "topic": "Document Excerpt",
                        "questions_en": rep["questions_en"],
                        "answer_en": answer_content,
                        "questions_ar": rep["questions_ar"],
                        "answer_ar": "",
                        "parent_text": c
                    })
            return units
