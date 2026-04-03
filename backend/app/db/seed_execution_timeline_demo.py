"""Seed deterministic demo data for execution timeline visualization.

Dev/PoC only.
"""

from datetime import datetime

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import Operation, ProductionOrder, WorkOrder

TENANT_ID = "default"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def reset_demo_data() -> None:
    """Remove timeline demo records if they already exist."""
    with SessionLocal() as db:
        po = db.scalar(select(ProductionOrder).where(ProductionOrder.order_number == "PO-001"))
        if not po:
            db.commit()
            return

        work_order_ids = [wo.id for wo in po.work_orders]

        if work_order_ids:
            db.execute(delete(ExecutionEvent).where(ExecutionEvent.work_order_id.in_(work_order_ids)))
            db.execute(delete(Operation).where(Operation.work_order_id.in_(work_order_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(work_order_ids)))

        db.execute(delete(ProductionOrder).where(ProductionOrder.id == po.id))
        db.commit()


def seed_demo_data() -> None:
    """Create WO-001 with 4 operations and event-driven execution timeline state."""
    with SessionLocal() as db:
        production_order = ProductionOrder(
            order_number="PO-001",
            route_id="DMES-R8",
            product_name="Engine Block Type A",
            quantity=50,
            status="IN_PROGRESS",
            planned_start=_dt("2024-04-15T07:00:00"),
            planned_end=_dt("2024-04-15T23:00:00"),
            tenant_id=TENANT_ID,
        )

        work_order = WorkOrder(
            production_order=production_order,
            work_order_number="WO-001",
            status="IN_PROGRESS",
            planned_start=_dt("2024-04-15T07:00:00"),
            planned_end=_dt("2024-04-15T23:00:00"),
            tenant_id=TENANT_ID,
        )

        # Projection/snapshot baseline (planned schedule only).
        op010 = Operation(
            operation_number="OP-010",
            work_order=work_order,
            sequence=10,
            name="Material Preparation",
            status="COMPLETED",
            planned_start=_dt("2024-04-15T07:00:00"),
            planned_end=_dt("2024-04-15T08:30:00"),
            quantity=50,
            completed_qty=50,
            good_qty=50,
            scrap_qty=0,
            qc_required=False,
            tenant_id=TENANT_ID,
            actual_start=None,
            actual_end=None,
        )

        op020 = Operation(
            operation_number="OP-020",
            work_order=work_order,
            sequence=20,
            name="Machining - Bore Drilling",
            status="IN_PROGRESS",
            planned_start=_dt("2024-04-15T08:30:00"),
            planned_end=_dt("2024-04-15T13:00:00"),
            quantity=50,
            completed_qty=0,
            good_qty=0,
            scrap_qty=0,
            qc_required=True,
            tenant_id=TENANT_ID,
            actual_start=None,
            actual_end=None,
        )

        op030 = Operation(
            operation_number="OP-030",
            work_order=work_order,
            sequence=30,
            name="Surface Treatment",
            status="PENDING",
            planned_start=_dt("2024-04-15T13:00:00"),
            planned_end=_dt("2024-04-15T18:00:00"),
            quantity=50,
            completed_qty=0,
            good_qty=0,
            scrap_qty=0,
            qc_required=False,
            tenant_id=TENANT_ID,
            actual_start=None,
            actual_end=None,
        )

        op040 = Operation(
            operation_number="OP-040",
            work_order=work_order,
            sequence=40,
            name="Quality Inspection",
            status="PENDING",
            planned_start=_dt("2024-04-15T18:00:00"),
            planned_end=_dt("2024-04-15T23:00:00"),
            quantity=50,
            completed_qty=0,
            good_qty=0,
            scrap_qty=0,
            qc_required=True,
            tenant_id=TENANT_ID,
            actual_start=None,
            actual_end=None,
        )

        db.add_all([production_order, work_order, op010, op020, op030, op040])
        db.flush()

        # OP-010 started exactly at planned start.
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=production_order.id,
                work_order_id=work_order.id,
                operation_id=op010.id,
                payload={"started_at": "2024-04-15T07:00:00", "operator_id": "DEMO-OP-01"},
                tenant_id=TENANT_ID,
            )
        )

        # OP-010 completed at 08:15 (15 minutes early versus planned end 08:30).
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=production_order.id,
                work_order_id=work_order.id,
                operation_id=op010.id,
                payload={"completed_at": "2024-04-15T08:15:00", "operator_id": "DEMO-OP-01"},
                tenant_id=TENANT_ID,
            )
        )

        # OP-020 started at 08:35 (5 minutes after planned start 08:30), still running.
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=production_order.id,
                work_order_id=work_order.id,
                operation_id=op020.id,
                payload={"started_at": "2024-04-15T08:35:00", "operator_id": "DEMO-OP-02"},
                tenant_id=TENANT_ID,
            )
        )

        # No events for OP-030/040 to keep them pending / not started.
        db.commit()


def main() -> None:
    reset_demo_data()
    seed_demo_data()
    print("Seeded execution timeline demo data: PO-001 / WO-001 / OP-010..040")


if __name__ == "__main__":
    main()