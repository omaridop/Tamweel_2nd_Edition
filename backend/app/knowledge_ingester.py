import os
import PyPDF2
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env file.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize the embedding model (runs locally)
print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page_text = reader.pages[page_num].extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def chunk_financial_tables(markdown_text: str):
    """
    Chunks table-heavy markdown using 'One-Row-Per-Chunk' logic.
    Do NOT use fixed character counts. Each chunk is a self-contained row fact.
    """
    raw_chunks = markdown_text.strip().split('\n\n')
    chunks = []
    for chunk in raw_chunks:
        if chunk.strip():
            chunks.append(chunk.strip())
    return chunks

def ingest_document(file_path):
    """Reads, chunks, embeds, and uploads a document to Supabase."""
    print(f"\nProcessing {file_path}...")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    filename = os.path.basename(file_path)
    
    # 1. Extract Text
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
        # Fallback to standard chunking if it's a raw PDF not explicitly pre-processed
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + 500])
            chunks.append(chunk)
            i += 500 - 50
    elif file_path.endswith('.md'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunk_financial_tables(text)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            chunks = chunk_financial_tables(text)

    if not chunks:
        print("❌ No text extracted from document.")
        return

    print(f"Created {len(chunks)} structured chunks.")

    # 3. Generate Embeddings & Upload
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i + batch_size]
        
        print(f"Generating embeddings for batch {i//batch_size + 1}...")
        embeddings = model.encode(batch_chunks).tolist()
        
        print(f"Uploading to Supabase...")
        records = []
        for j, chunk in enumerate(batch_chunks):
            # Category extraction for metadata
            category = "General"
            if "Financial Capabilities" in chunk or "financial literacy" in chunk.lower():
                category = "Financial Literacy"
            elif "consumer protection" in chunk.lower():
                category = "Consumer Protection"
                
            records.append({
                "content": chunk,
                "metadata": {"filename": filename, "chunk_index": i + j, "category": category},
                "embedding": embeddings[j]
            })
            
        try:
            supabase.table("tamweel_knowledge_base").insert(records).execute()
        except Exception as e:
            print(f"❌ Failed to upload batch: {e}")

    print(f"✅ Successfully ingested {filename} into the vector database!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest a document into Tamweel's Vector Database.")
    parser.add_argument("file_path", help="Path to the PDF or TXT file to ingest")
    args = parser.parse_args()
    
    ingest_document(args.file_path)
