import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env')
db_url = os.environ.get('DATABASE_URL')

if not db_url:
    print("No DATABASE_URL found.")
    exit(1)

conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

sql_rpc = """
CREATE OR REPLACE FUNCTION search_frequent_questions(
    query_embedding VECTOR,
    similarity_threshold FLOAT DEFAULT 0.98,
    match_count INT DEFAULT 1
)
RETURNS TABLE (
    id UUID,
    question_text TEXT,
    cached_answer TEXT,
    question_keywords TEXT[],
    similarity FLOAT
)
LANGUAGE sql STABLE AS $$
    SELECT
        id,
        question_text,
        cached_answer,
        question_keywords,
        1 - (question_embedding <=> query_embedding) AS similarity
    FROM frequent_questions
    WHERE 1 - (question_embedding <=> query_embedding) >= similarity_threshold
    ORDER BY question_embedding <=> query_embedding
    LIMIT match_count;
$$;
"""

try:
    cur.execute(sql_rpc)
    print("RPC function created.")
except Exception as e:
    print("Error:", e)
finally:
    cur.close()
    conn.close()
