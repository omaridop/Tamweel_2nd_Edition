"""Tamweel AI — Knowledge Ingestion Pipeline (UJ_RAG Architecture).

Modules:
    config    – Centralized settings from .env
    llm       – OpenRouter client (OpenAI-compatible)
    extract   – PDF / DOCX / TXT text extraction
    doc_to_qa – LLM-driven bilingual Q&A generation (the primary strategy)
    embed     – Gemini Embedding 2 via OpenRouter, L2-normalized, batched
    ingest    – Full orchestration: extract → Q&A → embed → Supabase upsert
"""
