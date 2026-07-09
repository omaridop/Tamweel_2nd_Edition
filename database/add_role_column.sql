-- ─── Role Column Migration for tamweel_results ───────────────────────────────
-- Run this in your Supabase SQL Editor.
-- This replaces the email-substring role heuristic with a proper DB column.
--
-- WHAT WAS THE OLD EXPOSURE (email-substring check):
--   role = "sponsor" if "admin" in request.email.lower() else "user"
--
--   Any user who registered with an email containing "admin" as a substring
--   (case-insensitively) would silently receive sponsor/admin privileges.
--   Examples of emails that would have passed:
--     administrator@gmail.com  → contains "admin" → sponsor
--     admin123@yahoo.com       → contains "admin" → sponsor
--     myadminmail@outlook.com  → contains "admin" → sponsor
--     ADMIN@hotmail.com        → .lower() = "admin@..." → sponsor
--
--   This affected /admin/upload-policy (RAG poisoning) and
--   /results/all_users (full portfolio data exfiltration).
--
--   The new code reads exclusively from the `role` column.
--   If the column is NULL or missing, the backend defaults to 'user'
--   and logs a warning — no email parsing occurs at all.
-- ─────────────────────────────────────────────────────────────────────────────

-- STEP 1: Add the role column (safe to run multiple times)
ALTER TABLE tamweel_results
    ADD COLUMN IF NOT EXISTS role TEXT NOT NULL DEFAULT 'user'
    CHECK (role IN ('user', 'sponsor', 'admin'));

-- STEP 2: Set existing sponsor/admin accounts explicitly
-- Edit the emails below to match your actual sponsor/admin accounts.
-- Any email NOT listed here will remain as 'user' — the safe default.
UPDATE tamweel_results
SET role = 'sponsor'
WHERE email IN (
    'admin@tamweel.ai'
    -- add more sponsor emails here, one per line:
    -- 'another-sponsor@tamweel.ai'
);

-- STEP 3: Confirm no 'admin'-substring accounts were accidentally elevated
-- Run this query and verify the results match your intention:
-- SELECT email, role FROM tamweel_results WHERE role != 'user' ORDER BY email;

-- STEP 4: (Optional) Add an index for fast role-based lookups
CREATE INDEX IF NOT EXISTS idx_tamweel_results_role ON tamweel_results (role);

-- STEP 5: Also add model_version column while we're here (for audit trail)
ALTER TABLE tamweel_results
    ADD COLUMN IF NOT EXISTS model_version TEXT DEFAULT 'xgboost-classifier-v1';
