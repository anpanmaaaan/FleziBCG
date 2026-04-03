#!/usr/bin/env bash
set -e

echo "=== Seed Execution Timeline Demo Data ==="

cd backend

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python -m app.db.seed_execution_timeline_demo

echo "✅ Demo data ready: PO-001 / WO-001"
echo "ℹ️ Test endpoint: GET /api/v1/work-orders/WO-001/execution-timeline"