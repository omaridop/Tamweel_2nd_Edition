-- 1. Enable the pgvector extension (requires superuser privileges in some environments)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the table for structurally chunked policies
-- We use 768 dimensions as the default for Gemini-based embeddings
CREATE TABLE IF NOT EXISTS policy_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_name VARCHAR(255) NOT NULL,
    hierarchy_context VARCHAR(512) NOT NULL,
    content TEXT NOT NULL,
    parent_content TEXT,
    chunk_index INT,
    metadata JSONB,
    content_hash VARCHAR(64) UNIQUE, -- Enforces idempotency for clean upserts
    embedding VECTOR(768) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Create a HNSW (Hierarchical Navigable Small World) index
-- This is critical for fast approximate nearest neighbor (ANN) search at scale.
-- vector_cosine_ops is ideal for text embeddings using cosine similarity.
CREATE INDEX IF NOT EXISTS idx_policy_chunks_embedding 
ON policy_chunks 
USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);
