"""Document extraction utilities for Tamweel AI.

Provides helper functions for handling PDFs and text files before passing them to the LLM.
"""

from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def _pdf_batch_bytes(path: Path, start: int, end: int) -> bytes:
    """Extracts a page range from a PDF as a new mini-PDF in memory."""
    if not fitz:
        raise ImportError("PyMuPDF (fitz) is not installed. Run: pip install PyMuPDF")
        
    with fitz.open(str(path)) as src:
        dest = fitz.open()
        dest.insert_pdf(src, from_page=start, to_page=end - 1)
        pdf_bytes = dest.write()
        dest.close()
    return pdf_bytes

def _pages_text(path: Path, start: int, end: int) -> str:
    """Extracts raw text from a PDF page range (fallback for vision failure)."""
    if not fitz:
        return ""
    try:
        with fitz.open(str(path)) as d:
            pages = []
            for i in range(start, min(end, d.page_count)):
                pages.append(d[i].get_text("text"))
            return "\n\n".join(pages)
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}", exc_info=True)
        return ""
