-- 1. Add full text search column to policy_chunks
ALTER TABLE policy_chunks ADD COLUMN IF NOT EXISTS fts tsvector;
UPDATE policy_chunks SET fts = to_tsvector('english', content);

-- Create index for sparse search
CREATE INDEX IF NOT EXISTS idx_policy_chunks_fts ON policy_chunks USING GIN (fts);

-- 2. Create the Hybrid Search RPC (Reciprocal Rank Fusion)
CREATE OR REPLACE FUNCTION hybrid_search_policy_chunks(
    query_text TEXT,
    query_embedding VECTOR(768),
    match_count INT,
    full_text_weight FLOAT DEFAULT 1.0,
    semantic_weight FLOAT DEFAULT 1.0,
    rrf_k INT DEFAULT 50
) RETURNS TABLE (
    id UUID,
    policy_name VARCHAR,
    hierarchy_context VARCHAR,
    content TEXT,
    parent_content TEXT,
    chunk_index INT,
    metadata JSONB,
    similarity FLOAT
) LANGUAGE sql AS $$
WITH semantic_search AS (
    SELECT id, 
           RANK() OVER (ORDER BY embedding <=> query_embedding) as semantic_rank
    FROM policy_chunks
    ORDER BY embedding <=> query_embedding
    LIMIT match_count
),
fulltext_search AS (
    SELECT id, 
           RANK() OVER (ORDER BY ts_rank_cd(fts, websearch_to_tsquery('english', query_text)) DESC) as fulltext_rank
    FROM policy_chunks
    WHERE fts @@ websearch_to_tsquery('english', query_text)
    ORDER BY ts_rank_cd(fts, websearch_to_tsquery('english', query_text)) DESC
    LIMIT match_count
)
SELECT 
    p.id,
    p.policy_name,
    p.hierarchy_context,
    p.content,
    p.parent_content,
    p.chunk_index,
    p.metadata,
    COALESCE(1.0 / (rrf_k + ss.semantic_rank), 0.0) * semantic_weight + 
    COALESCE(1.0 / (rrf_k + fs.fulltext_rank), 0.0) * full_text_weight AS similarity
FROM policy_chunks p
LEFT JOIN semantic_search ss ON p.id = ss.id
LEFT JOIN fulltext_search fs ON p.id = fs.id
WHERE ss.id IS NOT NULL OR fs.id IS NOT NULL
ORDER BY similarity DESC
LIMIT match_count;
$$;
