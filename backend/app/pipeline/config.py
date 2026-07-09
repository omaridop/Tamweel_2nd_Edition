"""Centralized configuration for the Tamweel AI pipeline.

All settings are loaded from environment variables with sensible defaults.
This mirrors the UJ_RAG Config class, adapted for Tamweel's financial domain
and Supabase vector store (instead of ChromaDB).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class PipelineSettings:
    """Singleton-style settings — import ``settings`` from this module."""

    # ── API ─────────────────────────────────────────────────────────────────
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_REFERER: str = os.getenv("OPENROUTER_REFERER", "https://tamweel.ai")
    OPENROUTER_TITLE: str = os.getenv("OPENROUTER_TITLE", "Tamweel AI")

    # ── Models ──────────────────────────────────────────────────────────────
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "deepseek/deepseek-chat")
    CHUNK_MODEL: str = os.getenv("CHUNK_MODEL", "google/gemini-2.5-flash")
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "google/gemini-embedding-2")

    # ── Embedding ───────────────────────────────────────────────────────────
    EMBED_DIM: int = int(os.getenv("EMBED_DIM", "768"))  # 768 for Supabase pgvector (lighter than 3072)
    EMBED_BATCH: int = int(os.getenv("EMBED_BATCH", "64"))
    EMBED_CONCURRENCY: int = int(os.getenv("EMBED_CONCURRENCY", "4"))
    EMBED_TIMEOUT_S: int = int(os.getenv("EMBED_TIMEOUT_S", "90"))
    EMBED_MAX_CHARS: int = int(os.getenv("EMBED_MAX_CHARS", "6000"))

    # ── Generation ──────────────────────────────────────────────────────────
    CHAT_TEMPERATURE: float = float(os.getenv("CHAT_TEMPERATURE", "0.2"))
    CHAT_MAX_TOKENS: int = int(os.getenv("CHAT_MAX_TOKENS", "1500"))
    CHUNK_TEMPERATURE: float = float(os.getenv("CHUNK_TEMPERATURE", "0.1"))
    QA_MAX_TOKENS: int = int(os.getenv("QA_MAX_TOKENS", "32000"))

    # ── Q&A Generation ──────────────────────────────────────────────────────
    QA_VARIANTS: int = int(os.getenv("QA_VARIANTS", "5"))  # min question paraphrases per language per fact
    QA_PAGES_PER_BATCH: int = int(os.getenv("QA_PAGES_PER_BATCH", "1"))

    # ── PDF ──────────────────────────────────────────────────────────────────
    PDF_INGEST_MODE: str = os.getenv("PDF_INGEST_MODE", "native")
    PDF_ENGINE: str = os.getenv("PDF_ENGINE", "native")
    PDF_PAGES_PER_BATCH: int = int(os.getenv("PDF_PAGES_PER_BATCH", "6"))
    PDF_MAX_MB: int = int(os.getenv("PDF_MAX_MB", "50"))

    # ── Chunking (fallback) ─────────────────────────────────────────────────
    CHUNK_WINDOW_CHARS: int = int(os.getenv("CHUNK_WINDOW_CHARS", "12000"))
    CHUNK_WINDOW_OVERLAP: int = int(os.getenv("CHUNK_WINDOW_OVERLAP", "800"))
    FALLBACK_CHUNK_SIZE: int = int(os.getenv("FALLBACK_CHUNK_SIZE", "1100"))
    FALLBACK_CHUNK_OVERLAP: int = int(os.getenv("FALLBACK_CHUNK_OVERLAP", "150"))

    # ── Retrieval Config ────────────────────────────────────────────────────
    RECENCY_HALFLIFE_DAYS: float = float(os.getenv("RECENCY_HALFLIFE_DAYS", "365.0"))
    RECENCY_WEIGHT: float = float(os.getenv("RECENCY_WEIGHT", "0.15"))
    FULL_TEXT_WEIGHT: float = float(os.getenv("FULL_TEXT_WEIGHT", "1.2"))
    SEMANTIC_WEIGHT: float = float(os.getenv("SEMANTIC_WEIGHT", "1.0"))
    TOP_K: int = int(os.getenv("TOP_K", "8"))
    OVERFETCH_FACTOR: int = int(os.getenv("OVERFETCH_FACTOR", "3"))
    DIVERSITY_PENALTY: float = float(os.getenv("DIVERSITY_PENALTY", "0.95"))
    SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", "0.15"))

    # ── Timeouts ────────────────────────────────────────────────────────────
    LLM_TIMEOUT_S: int = int(os.getenv("LLM_TIMEOUT_S", "120"))
    INGEST_TIMEOUT_S: int = int(os.getenv("INGEST_TIMEOUT_S", "600"))
    INGEST_CONCURRENCY: int = int(os.getenv("INGEST_CONCURRENCY", "4"))

    # ── Supabase ────────────────────────────────────────────────────────────
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # ── Filesystem ──────────────────────────────────────────────────────────
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(Path(__file__).resolve().parent.parent.parent / "data")))
    PROCESSED_DIR: Path = DATA_DIR / "processed"

    def __repr__(self) -> str:
        return (f"<PipelineSettings CHUNK_MODEL={self.CHUNK_MODEL} "
                f"EMBED_MODEL={self.EMBED_MODEL} EMBED_DIM={self.EMBED_DIM}>")


settings = PipelineSettings()
