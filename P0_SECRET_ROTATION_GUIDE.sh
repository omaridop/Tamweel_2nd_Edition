# ─── P0 Secret Rotation & Git Cleanup Guide ──────────────────────────────────
#
# Run these steps IN ORDER. Skipping any step leaves the project at risk.
# ─────────────────────────────────────────────────────────────────────────────

# STEP 1 — Rotate ALL exposed keys immediately (do this in browser dashboards)
# ──────────────────────────────────────────────────────────────────────────────
# a) Supabase service-role key:
#    Dashboard → Settings → API → Reveal service_role key → Reset
#    Also rotate the ANON key while you're there.
#
# b) OpenRouter API key:
#    https://openrouter.ai/keys → Delete old key → Create new
#
# c) Database password:
#    Supabase → Settings → Database → Reset database password
#
# d) DeepSeek API key (current value looks like a placeholder but rotate anyway):
#    https://platform.deepseek.com/api-keys → Revoke → New
#
# e) Anthropic API key (in ml_pipeline/.env):
#    https://console.anthropic.com/keys → Delete old → Create new

# STEP 2 — Generate a strong JWT secret
# ──────────────────────────────────────────────────────────────────────────────
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output → use as JWT_SECRET_KEY in your new .env

# STEP 3 — Stop tracking .env files in git
# ──────────────────────────────────────────────────────────────────────────────
git rm --cached backend/.env
git rm --cached .env
git rm --cached ml_pipeline/.env
# (run only the files that exist — ignore errors for non-tracked files)

# Confirm .env is in .gitignore (it already is per the repo .gitignore)
cat .gitignore | grep ".env"

# STEP 4 — Scrub git history (removes ALL past .env commits)
# ──────────────────────────────────────────────────────────────────────────────
# Install git-filter-repo if not present:
#   pip install git-filter-repo
#
# Remove the .env files from ALL history:
git filter-repo --path backend/.env --invert-paths --force
git filter-repo --path .env --invert-paths --force
git filter-repo --path ml_pipeline/.env --invert-paths --force

# STEP 5 — Force-push the cleaned history (COORDINATE WITH YOUR TEAM FIRST)
# ──────────────────────────────────────────────────────────────────────────────
# WARNING: This rewrites history. All collaborators must re-clone after this.
git push origin --force --all
git push origin --force --tags

# STEP 6 — Update your .env with new rotated values
# ──────────────────────────────────────────────────────────────────────────────
# Copy backend/.env.example → backend/.env
# Fill in all the new rotated keys
# Use the ANON key (not service-role) for SUPABASE_KEY
# Set JWT_SECRET_KEY to the output from Step 2

# STEP 7 — Verify no secrets remain in current files
# ──────────────────────────────────────────────────────────────────────────────
# Search for any remaining key patterns in tracked files:
git grep -r "OPENROUTER_API_KEY" -- "*.py" "*.js" "*.ts" "*.json"
git grep -r "SUPABASE_KEY" -- "*.py" "*.sql"
git grep -r "tamweel_secret_key" -- "*.py"
git grep -r "adminpassword" -- "*.py"
# All results should be empty.
