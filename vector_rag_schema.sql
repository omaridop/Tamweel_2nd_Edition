-- SQL Script: Enable Vector RAG in Supabase
-- Run this in your Supabase SQL Editor

-- 1. Enable the pgvector extension to work with mathematical embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create a table to store your knowledge base documents
CREATE TABLE IF NOT EXISTS tamweel_knowledge_base (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,          -- The actual text chunk from your PDF
    metadata JSONB,                 -- Stores filename, page number, etc.
    embedding VECTOR(384)           -- 384 dimensions matches the 'all-MiniLM-L6-v2' model
);

-- 3. Create a Vector Similarity Search Function (Cosine Similarity)
-- The chatbot will call this function to find the most relevant paragraphs
CREATE OR REPLACE FUNCTION match_knowledge_base (
    query_embedding VECTOR(384),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        tamweel_knowledge_base.id,
        tamweel_knowledge_base.content,
        tamweel_knowledge_base.metadata,
        1 - (tamweel_knowledge_base.embedding <=> query_embedding) AS similarity
    FROM tamweel_knowledge_base
    -- Only return matches above the threshold
    WHERE 1 - (tamweel_knowledge_base.embedding <=> query_embedding) > match_threshold
    -- Order by the closest mathematical distance (Cosine distance)
    ORDER BY tamweel_knowledge_base.embedding <=> query_embedding
    LIMIT match_count;
$$;
