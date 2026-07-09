# Tamweel AI — API & Health Check Documentation

This document outlines the core APIs and health monitoring endpoints available in the Tamweel AI platform.

## 1. OpenAPI / Swagger UI
FastAPI automatically generates comprehensive API documentation. When the backend is running locally, you can access the interactive Swagger UI here:
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Alternative**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 2. Health Checks

### Backend Health Check
The backend exposes a lightweight `GET /health` endpoint used by Docker and load balancers to verify service availability.
```http
GET /health
```
**Response (200 OK)**
```json
{
  "status": "healthy"
}
```

### Redis Status
The system utilizes Redis for caching LLM responses and query routing. The Docker container healthcheck pings Redis directly:
```bash
redis-cli ping
```
*Expected output: `PONG`*

### Database Connection Status
Database connections are handled via the Supabase client inside the FastAPI app. Any failure to connect to Supabase will be raised as a `500 Internal Server Error` during credit scoring or fetching endpoints.

## 3. Core API Endpoints

### Authentication
- `POST /api/v1/auth/register`: Registers a new user.
- `POST /api/v1/auth/login`: Authenticates a user and returns a JWT.

### Credit Scoring
- `POST /api/v1/score`: Submits an application and returns the deterministic ML score combined with the LLM explanation.

### Chat & AI
- `POST /api/v1/chat`: Conversational interface for interacting with financial policies via RAG.

### User Data
- `GET /api/v1/analytics/spending-patterns/{user_email}`: Fetches transaction analytics.
- `POST /api/v1/transactions`: Submits a new transaction.
