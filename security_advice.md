# Security Best Practices for Keys

Currently, your `.env` file contains sensitive keys like `ANTHROPIC_API_KEY`, `SUPABASE_URL`, and `SUPABASE_KEY`. This is acceptable for local development, but not for production.

## 1. Local Development
- **Never commit `.env` to version control:** Ensure `.env` is listed in your `.gitignore` file. Your repository should only contain a `.env.example` file with placeholder values (e.g., `SUPABASE_URL=your-url-here`).

## 2. Production Deployment (Backend)
When deploying your FastAPI backend (e.g., to Heroku, AWS, Render, or DigitalOcean):
- **Do not upload the `.env` file.**
- Instead, configure these values as **Environment Variables** directly in the hosting provider's dashboard.
  - Example in Heroku: Go to Settings -> Config Vars -> Add `ANTHROPIC_API_KEY` and its value.
- Your Python code `os.getenv("ANTHROPIC_API_KEY")` will automatically read these secure variables from the host system.

## 3. Frontend Considerations
- **Do not expose backend keys in the frontend:** Your React frontend should NEVER contain the `ANTHROPIC_API_KEY` or the `SUPABASE_KEY` (unless it's the specific public anon key meant for client-side use, but here your backend handles DB access).
- Your frontend correctly only knows the `BASE_URL` of your API (`http://localhost:8000` locally, or `https://api.yourdomain.com` in production).
- When building the frontend for production, set the production URL in your Vite environment variables (`.env.production` -> `VITE_API_URL=...`).

## Summary
By keeping the heavy processing, AI calls, and database writes entirely within the FastAPI backend, you have built a secure architecture. Just remember to manage the environment variables securely on your deployment server.