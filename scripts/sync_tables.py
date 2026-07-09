import os, psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Get records from tamweel_knowledge_base
cur.execute("""
    SELECT content, metadata, embedding 
    FROM tamweel_knowledge_base 
    WHERE metadata->>'source' = 'account_limit.pdf'
""")
records = cur.fetchall()

print(f"Found {len(records)} records in tamweel_knowledge_base")

# Insert into policy_chunks
for content, metadata, embedding in records:
    policy_name = metadata.get('source')
    hierarchy_context = metadata.get('topic', '')
    import hashlib
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    cur.execute("""
        INSERT INTO policy_chunks (policy_name, hierarchy_context, content, content_hash, embedding)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (content_hash) DO NOTHING
    """, (policy_name, hierarchy_context, content, content_hash, embedding))

conn.commit()

# Verify
cur.execute("SELECT policy_name, COUNT(*) as chunk_count FROM policy_chunks GROUP BY policy_name;")
print(cur.fetchall())
cur.close()
conn.close()
