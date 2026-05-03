#!/usr/bin/env python3
"""
Seed production orders linked to master data products and routings.

This creates production orders that reference the products and routings
created by seed_products_and_routing.py.

Usage:
  cd backend
    .venv\\Scripts\\python scripts/seed/seed_production_orders_with_master_data.py

Prerequisites:
  - seed_products_and_routing.py must be run first

Database: localhost:5432/mes (Docker postgres_data volume)
"""

from datetime import datetime
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.product import Product
from app.models.routing import Routing


TENANT_ID = "default"
def seed_production_orders_for_widgets():
    """
    Create production orders for WIDGET-A and WIDGET-B using master data.

    PO-1: WIDGET-A × 100 units
      - R-WIDGET-A routing with 3 operations
      - Distributed across STATION-A, STATION-B, STATION-C

    PO-2: WIDGET-B × 50 units (premium)
      - R-WIDGET-B routing with 4 operations
      - Distributed across STATION-A, STATION-B
    """
    db = SessionLocal()
    try:
        print("\n=== PRODUCTION ORDERS (WITH MASTER DATA) ===")

        # Get products and routings
        widget_a = db.scalar(
            select(Product).where(
                Product.product_code == "WIDGET-A", Product.tenant_id == TENANT_ID
            )
        )
        widget_b = db.scalar(
            select(Product).where(
                Product.product_code == "WIDGET-B", Product.tenant_id == TENANT_ID
            )
        )
        routing_a = db.scalar(
            select(Routing).where(
                Routing.routing_code == "R-WIDGET-A", Routing.tenant_id == TENANT_ID
            )
        )
        routing_b = db.scalar(
            select(Routing).where(
                Routing.routing_code == "R-WIDGET-B", Routing.tenant_id == TENANT_ID
            )
        )

        if not all([widget_a, widget_b, routing_a, routing_b]):
            print("  ⚠ Products or routings not found")
            print("  → Run seed_products_and_routing.py first")
            return

        # PO-1: WIDGET-A
        po_a = _create_or_get_production_order(
            db,
            order_number="PRD-WIDGET-A-001",
            route_id=routing_a.routing_id,
            product_name=widget_a.product_name,
            quantity=100,
            planned_start="2099-07-01 08:00:00",
            planned_end="2099-07-02 17:00:00",
        )

        if po_a:
            _create_work_order_with_operations(
                db,
                production_order_id=po_a.id,
                wo_number="WO-WIDGET-A-001",
                routing=routing_a,
                quantity=100,
                stations=["STATION-A", "STATION-B", "STATION-C"],
            )

        # PO-2: WIDGET-B (Premium)
        po_b = _create_or_get_production_order(
            db,
            order_number="PRD-WIDGET-B-001",
            route_id=routing_b.routing_id,
            product_name=widget_b.product_name,
            quantity=50,
            planned_start="2099-07-03 08:00:00",
            planned_end="2099-07-04 17:00:00",
        )

        if po_b:
            _create_work_order_with_operations(
                db,
                production_order_id=po_b.id,
                wo_number="WO-WIDGET-B-001",
                routing=routing_b,
                quantity=50,
                stations=["STATION-A", "STATION-B"],
            )

        db.commit()

    finally:
        db.close()


def seed_production_orders_for_frames():
    """
    Create production order for FRAME-001 (semi-finished).

    PO-3: FRAME-001 × 150 units
      - R-FRAME routing with 2 operations
      - STATION-D for cutting, STATION-E for welding
    """
    db = SessionLocal()
    try:
        print("\n=== PRODUCTION ORDERS FOR SEMI-FINISHED ===")

        # Get product and routing
        frame = db.scalar(
            select(Product).where(
                Product.product_code == "FRAME-001", Product.tenant_id == TENANT_ID
            )
        )
        routing_frame = db.scalar(
            select(Routing).where(
                Routing.routing_code == "R-FRAME", Routing.tenant_id == TENANT_ID
            )
        )

        if not all([frame, routing_frame]):
            print("  ⚠ Frame product or routing not found")
            return

        # PO-3: FRAME-001
        po_frame = _create_or_get_production_order(
            db,
            order_number="PRD-FRAME-001-001",
            route_id=routing_frame.routing_id,
            product_name=frame.product_name,
            quantity=150,
            planned_start="2099-07-05 06:00:00",
            planned_end="2099-07-07 18:00:00",
        )

        if po_frame:
            _create_work_order_with_operations(
                db,
                production_order_id=po_frame.id,
                wo_number="WO-FRAME-001-001",
                routing=routing_frame,
                quantity=150,
                stations=["STATION-D", "STATION-E"],
            )

        db.commit()

    finally:
        db.close()


def _create_or_get_production_order(
    db,
    order_number: str,
    route_id: str,
    product_name: str,
    quantity: int,
    planned_start: str,
    planned_end: str,
) -> ProductionOrder | None:
    """Create or get a production order."""
    existing = db.scalar(
        select(ProductionOrder).where(
            ProductionOrder.order_number == order_number,
            ProductionOrder.tenant_id == TENANT_ID,
        )
    )
    if existing:
        print(f"  ✓ {order_number} (existing)")
        return existing

    po = ProductionOrder(
        order_number=order_number,
        route_id=route_id,
        product_name=product_name,
        quantity=quantity,
        status=StatusEnum.planned.value,
        planned_start=_parse_datetime(planned_start),
        planned_end=_parse_datetime(planned_end),
        tenant_id=TENANT_ID,
    )
    db.add(po)
    db.flush()
    print(f"  ✓ {order_number}: {product_name} (qty: {quantity})")
    return po


def _create_work_order_with_operations(
    db,
    production_order_id: str,
    wo_number: str,
    routing,
    quantity: int,
    stations: list[str],
):
    """Create work order and distribute operations across stations."""
    existing = db.scalar(
        select(WorkOrder).where(
            WorkOrder.work_order_number == wo_number,
            WorkOrder.tenant_id == TENANT_ID,
        )
    )
    if existing:
        print(f"    → {wo_number} (existing)")
        return

    wo = WorkOrder(
        production_order_id=production_order_id,
        work_order_number=wo_number,
        status=StatusEnum.planned.value,
        planned_start=_parse_datetime("2099-07-01 08:00:00"),
        planned_end=_parse_datetime("2099-07-02 17:00:00"),
        tenant_id=TENANT_ID,
    )
    db.add(wo)
    db.flush()

    # Create operations for each routing operation
    for i, routing_op in enumerate(routing.operations):
        station = stations[i % len(stations)]
        op = Operation(
            operation_number=f"{wo_number}-{routing_op.operation_code}",
            work_order_id=wo.id,
            sequence=routing_op.sequence_no,
            name=routing_op.operation_name,
            status=StatusEnum.planned.value,
            planned_start=_parse_datetime("2099-07-01 09:00:00"),
            planned_end=_parse_datetime("2099-07-01 17:00:00"),
            quantity=quantity,
            completed_qty=0,
            good_qty=0,
            scrap_qty=0,
            qc_required=(routing_op.sequence_no >= 30),  # QC ops require QC
            station_scope_value=station,
            tenant_id=TENANT_ID,
        )
        db.add(op)
        db.flush()

    print(f"    → {wo_number} ({len(routing.operations)} ops across {len(set(stations))} stations)")


def _parse_datetime(value: str) -> datetime:
    """Parse datetime string."""
    return datetime.fromisoformat(value)


def main():
    """Run all seed operations."""
    print("\n" + "=" * 60)
    print("SEED PRODUCTION ORDERS WITH MASTER DATA")
    print("=" * 60)
    print("\nCreating production orders linked to products & routings...")

    init_db_module = None
    try:
        from app.db.init_db import init_db as init_db_func
        init_db_module = init_db_func
        init_db_module()
    except ImportError:
        pass

    seed_production_orders_for_widgets()
    seed_production_orders_for_frames()

    print("\n" + "=" * 60)
    print("✓ PRODUCTION ORDERS SEEDED SUCCESSFULLY")
    print("=" * 60)
    print("\nData Summary:")
    print("- PO-1: PRD-WIDGET-A-001 (100 units, 3 operations)")
    print("  Stations: STATION-A, STATION-B, STATION-C")
    print("- PO-2: PRD-WIDGET-B-001 (50 units, 4 operations)")
    print("  Stations: STATION-A, STATION-B")
    print("- PO-3: PRD-FRAME-001-001 (150 units, 2 operations)")
    print("  Stations: STATION-D, STATION-E")
    print("\nAll operations are ready for execution workflow testing")
    print()


if __name__ == "__main__":
    main()
