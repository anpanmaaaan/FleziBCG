#!/usr/bin/env bash
set -e

echo "=== Seeding Database ==="

cd backend
source .venv/bin/activate

python - <<'EOF'
from app.db.session import engine
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(text("""
        INSERT INTO production_orders (order_number, product_name, quantity, status, tenant_id)
        VALUES ('PO-DEMO', 'DEMO PRODUCT', 100, 'PENDING', 'default')
    """))
    conn.execute(text("""
        INSERT INTO work_orders (production_order_id, work_order_number, status, tenant_id)
        VALUES (1, 'WO-DEMO', 'PENDING', 'default')
    """))
    conn.execute(text("""
        INSERT INTO operations (operation_number, work_order_id, sequence, name, status, quantity,
                                completed_qty, good_qty, scrap_qty, qc_required, tenant_id)
        VALUES ('OP-DEMO', 1, 1, 'Demo Operation', 'PENDING', 100, 0, 0, 0, 0, 'default')
    """))

print("✅ Seed data created")
EOF