#!/usr/bin/env bash
set -e

echo "==============================="
echo "🚀 Rebuilding MES Full System"
echo "==============================="

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Frontend
$SCRIPT_DIR/rebuild-frontend.sh

# Backend
$SCRIPT_DIR/rebuild-backend.sh

echo "✅ System rebuild completed"
echo ""
echo "Next steps:"
echo "  Backend: uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"