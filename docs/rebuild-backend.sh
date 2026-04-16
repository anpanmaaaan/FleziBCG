#!/usr/bin/env bash
set -e

echo "=== Rebuilding Backend (FastAPI) ==="

cd backend

# Activate venv
if [ -d ".venv" ]; then
  source .venv/bin/activate
else
  echo "❌ .venv not found. Please create virtualenv first."
  exit 1
fi

# Create database schema via PostgreSQL (Docker-based)
echo "→ Creating database schema"
echo "ℹ️ Note: Ensure Docker-based PostgreSQL is running (docker compose -f docker/docker-compose.db.yml up -d)"
python -m app.db.init_db
echo "✅ Backend rebuild completed"
echo "ℹ️ Seed data: python -m scripts.seed.seed_all"
echo "ℹ️ Start server with: uvicorn app.main:app --reload"