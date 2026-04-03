#!/usr/bin/env bash
set -e

echo "=== Seeding Database ==="

cd backend

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python -m app.db.seed_demo_data

echo "✅ Demo data created"
echo "ℹ️ Demo production orders: PO-DEMO-1001, PO-DEMO-1002, PO-DEMO-1003"
echo "ℹ️ Example work order timeline: GET /api/v1/work-orders/WO-DEMO-1001-B/execution-timeline"