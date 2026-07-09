# Tamweel AI — Deployment Guide

This document explains how to deploy Tamweel AI using Docker.

## 1. Environment Variables
Before deploying, you must configure your environment variables.
Copy the `.env.example` file to `.env` in the root directory:
```bash
cp .env.example .env
```
Fill in all required API keys (e.g., Supabase, OpenRouter/Anthropic, DeepSeek).

## 2. Required Services
Tamweel AI relies on three core services managed by Docker Compose:
1. **Frontend**: React (Vite) application served via Nginx on port `5173`.
2. **Backend**: FastAPI orchestrator served on port `8000`.
3. **Redis**: Cache for LLM responses and deterministic API routing served on port `6379`.

## 3. Docker Deployment
To build and start all required services:
```bash
docker compose up --build -d
```
This will start the containers in detached mode. To view logs:
```bash
docker compose logs -f
```

## 4. Stopping the Environment
To stop the containers without destroying data:
```bash
docker compose stop
```
To bring down the containers completely:
```bash
docker compose down
```
