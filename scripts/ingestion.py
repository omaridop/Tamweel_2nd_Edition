import os
import re
import hashlib
import psycopg2
from pgvector.psycopg2 import register_vector
# In a real environment, uncomment to use the OpenAI Python SDK
# from openai import OpenAI

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from app.pipeline.embed import embed_texts

def get_embedding(text, model="google/gemini-embedding-2"):
    """
    Generates a 768-dimensional vector embedding for the text chunk using the Gemini model.
    """
    return embed_texts([text])[0] 

def parse_markdown_with_hierarchy(md_content):
    """
    Parses markdown and chunks it structurally by header levels (H1 -> H2 -> H3).
    Returns chunks with the prepended hierarchical context.
    """
    lines = md_content.split('\n')
    current_hierarchy = {1: "", 2: "", 3: "", 4: "", 5: "", 6: ""}
    chunks = []
    current_chunk_text = []
    
    def save_chunk():
        # If we have accumulated text for a section, save it
        if current_chunk_text and "".join(current_chunk_text).strip():
            # Build the "[Chapter > Section > Subsection]" string
            active_levels = [current_hierarchy[i] for i in range(1, 7) if current_hierarchy[i]]
            hierarchy_str = " > ".join(active_levels)
            hierarchy_context = f"[{hierarchy_str}]" if hierarchy_str else "[Document Introduction]"
            
            raw_content = "\n".join(current_chunk_text).strip()
            
            # Prepend hierarchical context to the chunk content so the LLM explicitly sees it
            enriched_content = f"{hierarchy_context}\n\n{raw_content}"
            
            chunks.append({
                "hierarchy_context": hierarchy_context,
                "content": enriched_content
            })
        current_chunk_text.clear()

    for line in lines:
        header_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if header_match:
            # A new header means the previous section has ended
            save_chunk()
            
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            
            # Update current hierarchy level and clear any deeper nested levels
            current_hierarchy[level] = title
            for i in range(level + 1, 7):
                current_hierarchy[i] = ""
        else:
            current_chunk_text.append(line)
            
    # Save the final chunk at the end of the document
    save_chunk()
    return chunks

def ingest_policy(file_path, db_conn_str, policy_name):
    print(f"Reading policy file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    chunks = parse_markdown_with_hierarchy(md_content)
    print(f"Successfully parsed {len(chunks)} structural chunks.")
    
    # Connect to PostgreSQL and register the vector extension with psycopg2
    conn = psycopg2.connect(db_conn_str)
    register_vector(conn)
    cur = conn.cursor()
    
    try:
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}: {chunk['hierarchy_context']}")
            
            # 1. Generate Embedding
            embedding = get_embedding(chunk['content'])
            
            # 2. Hash the content to enable clean, idempotent upserts
            content_hash = hashlib.sha256(chunk['content'].encode('utf-8')).hexdigest()
            
            # 3. Clean Upsert into pgvector
            cur.execute("""
                INSERT INTO policy_chunks (policy_name, hierarchy_context, content, content_hash, embedding)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (content_hash) DO UPDATE 
                SET updated_at = NOW(),
                    hierarchy_context = EXCLUDED.hierarchy_context,
                    policy_name = EXCLUDED.policy_name
            """, (policy_name, chunk['hierarchy_context'], chunk['content'], content_hash, embedding))
            
        conn.commit()
        print("✅ Ingestion and Upsert complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during ingestion: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Example Database Connection String
    DB_URL = os.getenv("DATABASE_URL", "postgresql://localhost/tamweel")
    
    # Creating a dummy markdown file to demonstrate structural parsing
    dummy_md = """# Chapter 1: Introduction
Welcome to the Tamweel Retail Credit Policy.

## Section 1.1: Scope
This policy covers retail banking and personal loan originations.

# Chapter 2: Risk Assessment
## Section 2.1: Income Verification
Applicants must provide a minimum of 3 months of bank statements to verify consistent salary deposits.

### Section 2.1.1: Debt-to-Income (DTI) Calculation
The total Debt-to-Income (DTI) ratio must not exceed 40% for personal loans."""
    
    with open("sample_policy.md", "w", encoding='utf-8') as f:
        f.write(dummy_md)
        
    ingest_policy("sample_policy.md", DB_URL, "Retail Credit Policy v1.0")
