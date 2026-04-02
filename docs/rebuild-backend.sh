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

# Remove local DB
echo "→ Removing local SQLite DB"
rm -f dev.db *.db *.sqlite *.sqlite3

# Recreate schema
echo "→ Creating database schema"
python - <<'EOF'
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)
print("✅ Database schema created")
EOF

echo "✅ Backend rebuild completed"
echo "ℹ️ Start server with: uvicorn app.main:app --reload"