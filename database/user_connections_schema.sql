-- SQL Script to create the user_connections table
-- This table tracks active wallet/bank connections for users

CREATE TABLE IF NOT EXISTS user_connections (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    institution_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
