-- SQL Script: Upgrade Vector RAG Schema for Gemini 768-dim Embeddings & Semantic Cache
-- Run this in your Supabase SQL Editor

-- 1. Drop old tables/functions if they exist
DROP FUNCTION IF EXISTS match_knowledge_base(vector, double precision, integer);
DROP FUNCTION IF EXISTS match_semantic_cache(vector, double precision, integer);
DROP TABLE IF EXISTS tamweel_knowledge_base;
DROP TABLE IF EXISTS tamweel_semantic_cache;

-- 2. Create the new knowledge base table with 768 dimensions
CREATE TABLE tamweel_knowledge_base (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(768)  -- Updated for Gemini embeddings
);

-- 3. Create the updated Vector Similarity Search Function
CREATE OR REPLACE FUNCTION match_knowledge_base (
    query_embedding VECTOR(768),
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
    WHERE 1 - (tamweel_knowledge_base.embedding <=> query_embedding) > match_threshold
    ORDER BY tamweel_knowledge_base.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 4. Create Semantic Cache Table (Step 3)
CREATE TABLE tamweel_semantic_cache (
    id BIGSERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    question_hash VARCHAR(64) UNIQUE,
    answer TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(768)
);

-- 5. Create Semantic Cache Match Function
CREATE OR REPLACE FUNCTION match_semantic_cache (
    query_embedding VECTOR(768),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id BIGINT,
    question TEXT,
    answer TEXT,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        tamweel_semantic_cache.id,
        tamweel_semantic_cache.question,
        tamweel_semantic_cache.answer,
        1 - (tamweel_semantic_cache.embedding <=> query_embedding) AS similarity
    FROM tamweel_semantic_cache
    WHERE 1 - (tamweel_semantic_cache.embedding <=> query_embedding) > match_threshold
    ORDER BY tamweel_semantic_cache.embedding <=> query_embedding
    LIMIT match_count;
$$;
