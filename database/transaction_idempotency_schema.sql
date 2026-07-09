-- 1. Create Idempotency Cache Table
CREATE TABLE IF NOT EXISTS idempotency_cache (
    idempotency_key VARCHAR(255) PRIMARY KEY,
    user_email TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours'
);

-- 2. Create RPC for safe transaction insertion with Strict Isolation
CREATE OR REPLACE FUNCTION process_safe_transaction(
    p_idempotency_key VARCHAR,
    p_user_email TEXT,
    p_amount DECIMAL,
    p_type VARCHAR,
    p_category VARCHAR,
    p_description TEXT
) RETURNS JSON AS $$
DECLARE
    v_id UUID;
BEGIN
    -- Insert Idempotency Key atomically
    INSERT INTO idempotency_cache (idempotency_key, user_email)
    VALUES (p_idempotency_key, p_user_email)
    ON CONFLICT (idempotency_key) DO NOTHING;

    -- Check if insertion was successful
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Idempotency conflict: Duplicate request';
    END IF;

    -- Insert Transaction
    INSERT INTO transactions (user_email, amount, type, category, description)
    VALUES (p_user_email, p_amount, p_type, p_category, p_description)
    RETURNING id INTO v_id;

    RETURN json_build_object('success', true, 'transaction_id', v_id);
END;
$$ LANGUAGE plpgsql;
