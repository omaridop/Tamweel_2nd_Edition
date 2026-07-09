import os
import argparse
from supabase import create_client, Client
from dotenv import load_dotenv
from app.pipeline.doc_to_qa import generate_qa
from app.pipeline.embed import embed_texts

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[Error] Missing Supabase credentials in .env file.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

import re
from pathlib import Path
from app.pipeline.llm import get_client, first_choice_content
from app.pipeline.config import settings

def extract_doc_date(file_path: str) -> str:
    """Attempts to extract a YYYY-MM-DD date from the document. Uses a simple LLM call on the first page."""
    try:
        from app.pipeline.extract import _pages_text
        text = _pages_text(Path(file_path), 0, 3)
        if not text:
            return ""
            
        client = get_client()
        prompt = (
            "Extract the primary publication, effective, or release date from the following text snippet of a document. "
            "Return ONLY the date in YYYY-MM-DD format. If no clear date is found, output nothing. Text:\n\n" + text[:2000]
        )
        resp = client.chat.completions.create(
            model=settings.GEMINI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        date_str = first_choice_content(resp).strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return date_str
    except Exception as e:
        print(f"[Warning] Failed to automatically extract date: {e}")
    return ""

def qa_units_to_prepared(units: list[dict], filename: str, doc_date: str) -> list[dict]:
    """Converts the raw JSON QA units into flat records ready for embedding."""
    prepared = []
    for ui, unit in enumerate(units):
        page = unit.get("page", 0)
        topic = unit.get("topic", "")
        parent_text = unit.get("parent_text", "")
        # answer_en contains the full generated retrieval representation (Questions, Keywords, Aliases)
        representation_text = unit.get("answer_en", "").strip()
        
        if not representation_text:
            continue
            
        prepared.append({
            "embed_text": representation_text,
            "content": representation_text,
            "parent_text": parent_text,
            "chunk_index": page,
            "metadata": {
                "document_id": filename,
                "document_name": filename,
                "page_number": page,
                "chunk_id": f"{filename}_p{page}_{ui}",
                "section": topic,
                "heading": topic,
                "policy_name": filename,
                "embedding_model": settings.EMBED_MODEL,
                "upload_date": doc_date,
                "type": "bilingual_retrieval_chunk"
            },
        })
    return prepared

def ingest_document(file_path, cli_date=None):
    """Reads, generates QA, embeds, and uploads a document to Supabase."""
    print(f"\nProcessing {file_path} using Vision QA Pipeline...")
    
    if not os.path.exists(file_path):
        print(f"[Error] File not found: {file_path}")
        return

    filename = os.path.basename(file_path)
    file_type = "pdf" if file_path.lower().endswith(".pdf") else "txt"
    
    # Extract temporal metadata
    doc_date = cli_date
    if not doc_date:
        print("Attempting to auto-extract document date...")
        doc_date = extract_doc_date(file_path)
        if doc_date:
            print(f"Auto-extracted date: {doc_date}")
        else:
            print("No date extracted. Recency weighting will be bypassed for this document.")
    
    # 1. Generate Synthetic Q&A
    print("Generating Synthetic Q&A (Vision + LLM)...")
    qa_units = generate_qa(file_path, file_type)
    
    if not qa_units:
        print("[Error] No Q&A units extracted from document.")
        return
        
    print(f"Generated {len(qa_units)} fundamental QA facts.")
    
    # 2. Flatten into embedding records
    prepared_records = qa_units_to_prepared(qa_units, filename, doc_date)
    print(f"Flattened into {len(prepared_records)} distinct vector records (Questions + Answers).")
    
    # 3. Generate Embeddings & Upload
    batch_size = 64
    for i in range(0, len(prepared_records), batch_size):
        batch = prepared_records[i:i + batch_size]
        
        print(f"Generating embeddings for batch {i//batch_size + 1}...")
        texts_to_embed = [rec["embed_text"] for rec in batch]
        embeddings = embed_texts(texts_to_embed)
        
        print(f"Uploading to Supabase...")
        db_records = []
        import hashlib
        seen_hashes = set()
        for j, rec in enumerate(batch):
            content_str = rec["content"]
            global_index = i + j
            
            # Deterministic hash: Hash of (filename + global_index) instead of the LLM content itself
            raw_id = f"{filename}_{global_index}"
            content_hash = hashlib.sha256(raw_id.encode('utf-8')).hexdigest()
            
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)
            import json
            safe_metadata = rec["metadata"]
            db_records.append({
                "policy_name": filename,
                "hierarchy_context": rec["metadata"].get("section", "General"),
                "content": content_str,
                "content_hash": content_hash,
                "embedding": embeddings[j],
                "parent_content": rec.get("parent_text", ""),
                "chunk_index": rec.get("chunk_index", 0),
                "metadata": safe_metadata
            })
            
        try:
            if db_records:
                supabase.table("policy_chunks").insert(db_records).execute()
        except Exception as e:
            print(f"[Error] Failed to upload batch: {e}")

    print(f"Successfully ingested {filename} into the vector database using UJ_RAG Architecture!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a document into Tamweel's Vector Database.")
    parser.add_argument("file_path", help="Path to the PDF or TXT file to ingest")
    parser.add_argument("--date", help="Manual override for the document publication date (YYYY-MM-DD)", default=None)
    args = parser.parse_args()
    
    ingest_document(args.file_path, args.date)
