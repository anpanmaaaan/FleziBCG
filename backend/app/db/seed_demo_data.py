"""Seed realistic MES demo data for local development.

Creates a few production orders with work orders, operations, and execution events.
Safe to re-run: previously seeded demo records are removed first.
"""

from datetime import datetime

from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import Operation, ProductionOrder, WorkOrder

TENANT_ID = "default"
DEMO_PREFIX = "PO-DEMO-"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def reset_demo_data() -> None:
    """Remove previously inserted demo dataset."""
    with SessionLocal() as db:
        demo_po_ids = list(
            db.scalars(
                select(ProductionOrder.id).where(ProductionOrder.order_number.like(f"{DEMO_PREFIX}%"))
            )
        )

        if not demo_po_ids:
            db.commit()
            return

        demo_wo_ids = list(
            db.scalars(select(WorkOrder.id).where(WorkOrder.production_order_id.in_(demo_po_ids)))
        )

        if demo_wo_ids:
            db.execute(delete(ExecutionEvent).where(ExecutionEvent.work_order_id.in_(demo_wo_ids)))
            db.execute(delete(Operation).where(Operation.work_order_id.in_(demo_wo_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(demo_wo_ids)))

        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(demo_po_ids)))
        db.commit()


def _add_event(
    db,
    *,
    event_type: str,
    production_order: ProductionOrder,
    work_order: WorkOrder,
    operation: Operation,
    payload: dict,
) -> None:
    db.add(
        ExecutionEvent(
            event_type=event_type,
            production_order_id=production_order.id,
            work_order_id=work_order.id,
            operation_id=operation.id,
            payload=payload,
            tenant_id=TENANT_ID,
        )
    )


def seed_demo_data() -> None:
    """Insert a deterministic demo dataset that exercises MES read/write screens."""
    with SessionLocal() as db:
        po_1001 = ProductionOrder(
            order_number="PO-DEMO-1001",
            route_id="DMES-R8",
            product_name="Engine Block Type A",
            quantity=120,
            status="IN_PROGRESS",
            planned_start=_dt("2026-04-01T06:00:00"),
            planned_end=_dt("2026-04-02T18:00:00"),
            tenant_id=TENANT_ID,
        )

        wo_1001_a = WorkOrder(
            production_order=po_1001,
            work_order_number="WO-DEMO-1001-A",
            status="COMPLETED",
            planned_start=_dt("2026-04-01T06:00:00"),
            planned_end=_dt("2026-04-01T13:30:00"),
            actual_start=_dt("2026-04-01T06:00:00"),
            actual_end=_dt("2026-04-01T13:10:00"),
            tenant_id=TENANT_ID,
        )
        wo_1001_b = WorkOrder(
            production_order=po_1001,
            work_order_number="WO-DEMO-1001-B",
            status="IN_PROGRESS",
            planned_start=_dt("2026-04-02T06:00:00"),
            planned_end=_dt("2026-04-02T16:00:00"),
            actual_start=_dt("2026-04-02T06:10:00"),
            actual_end=None,
            tenant_id=TENANT_ID,
        )

        po_1002 = ProductionOrder(
            order_number="PO-DEMO-1002",
            route_id="DMES-R9",
            product_name="Cylinder Head Type B",
            quantity=80,
            status="PENDING",
            planned_start=_dt("2026-04-03T07:00:00"),
            planned_end=_dt("2026-04-03T18:00:00"),
            tenant_id=TENANT_ID,
        )

        wo_1002_a = WorkOrder(
            production_order=po_1002,
            work_order_number="WO-DEMO-1002-A",
            status="PENDING",
            planned_start=_dt("2026-04-03T07:00:00"),
            planned_end=_dt("2026-04-03T12:00:00"),
            actual_start=None,
            actual_end=None,
            tenant_id=TENANT_ID,
        )
        wo_1002_b = WorkOrder(
            production_order=po_1002,
            work_order_number="WO-DEMO-1002-B",
            status="LATE",
            planned_start=_dt("2026-04-03T12:30:00"),
            planned_end=_dt("2026-04-03T18:00:00"),
            actual_start=_dt("2026-04-03T13:15:00"),
            actual_end=None,
            tenant_id=TENANT_ID,
        )

        po_1003 = ProductionOrder(
            order_number="PO-DEMO-1003",
            route_id="DMES-R12",
            product_name="Pump Housing Type C",
            quantity=60,
            status="COMPLETED",
            planned_start=_dt("2026-03-31T06:00:00"),
            planned_end=_dt("2026-03-31T15:00:00"),
            tenant_id=TENANT_ID,
        )

        wo_1003_a = WorkOrder(
            production_order=po_1003,
            work_order_number="WO-DEMO-1003-A",
            status="COMPLETED",
            planned_start=_dt("2026-03-31T06:00:00"),
            planned_end=_dt("2026-03-31T15:00:00"),
            actual_start=_dt("2026-03-31T06:00:00"),
            actual_end=_dt("2026-03-31T14:45:00"),
            tenant_id=TENANT_ID,
        )

        operations = [
            Operation(
                operation_number="OP-DEMO-1001A-010",
                work_order=wo_1001_a,
                sequence=10,
                name="Material Preparation",
                description="Stage raw castings and tooling.",
                status="COMPLETED",
                planned_start=_dt("2026-04-01T06:00:00"),
                planned_end=_dt("2026-04-01T07:00:00"),
                actual_start=_dt("2026-04-01T06:00:00"),
                actual_end=_dt("2026-04-01T06:50:00"),
                quantity=120,
                completed_qty=120,
                good_qty=120,
                scrap_qty=0,
                qc_required=False,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1001A-020",
                work_order=wo_1001_a,
                sequence=20,
                name="Rough Machining",
                description="Rough cut main faces and bore centers.",
                status="COMPLETED",
                planned_start=_dt("2026-04-01T07:00:00"),
                planned_end=_dt("2026-04-01T09:30:00"),
                actual_start=_dt("2026-04-01T07:05:00"),
                actual_end=_dt("2026-04-01T09:20:00"),
                quantity=120,
                completed_qty=120,
                good_qty=118,
                scrap_qty=2,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1001A-030",
                work_order=wo_1001_a,
                sequence=30,
                name="Finish Machining",
                description="Final bore finishing and thread cutting.",
                status="COMPLETED",
                planned_start=_dt("2026-04-01T09:45:00"),
                planned_end=_dt("2026-04-01T11:45:00"),
                actual_start=_dt("2026-04-01T09:40:00"),
                actual_end=_dt("2026-04-01T11:30:00"),
                quantity=120,
                completed_qty=118,
                good_qty=118,
                scrap_qty=0,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1001A-040",
                work_order=wo_1001_a,
                sequence=40,
                name="Final Inspection",
                description="Verify dimensional and visual quality.",
                status="COMPLETED",
                planned_start=_dt("2026-04-01T11:50:00"),
                planned_end=_dt("2026-04-01T13:30:00"),
                actual_start=_dt("2026-04-01T11:45:00"),
                actual_end=_dt("2026-04-01T13:10:00"),
                quantity=118,
                completed_qty=118,
                good_qty=117,
                scrap_qty=1,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1001B-010",
                work_order=wo_1001_b,
                sequence=10,
                name="Material Preparation",
                description="Prepare batch for second shift execution.",
                status="COMPLETED",
                planned_start=_dt("2026-04-02T06:00:00"),
                planned_end=_dt("2026-04-02T07:00:00"),
                actual_start=_dt("2026-04-02T06:10:00"),
                actual_end=_dt("2026-04-02T06:55:00"),
                quantity=120,
                completed_qty=120,
                good_qty=120,
                scrap_qty=0,
                qc_required=False,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1001B-020",
                work_order=wo_1001_b,
                sequence=20,
                name="Bore Drilling",
                description="Current in-progress machining step.",
                status="IN_PROGRESS",
                planned_start=_dt("2026-04-02T07:00:00"),
                planned_end=_dt("2026-04-02T11:30:00"),
                actual_start=_dt("2026-04-02T07:20:00"),
                actual_end=None,
                quantity=120,
                completed_qty=57,
                good_qty=54,
                scrap_qty=3,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1001B-030",
                work_order=wo_1001_b,
                sequence=30,
                name="Surface Treatment",
                description="Pending downstream coating step.",
                status="PENDING",
                planned_start=_dt("2026-04-02T11:45:00"),
                planned_end=_dt("2026-04-02T13:30:00"),
                actual_start=None,
                actual_end=None,
                quantity=120,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=False,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1001B-040",
                work_order=wo_1001_b,
                sequence=40,
                name="Final Inspection",
                description="Pending quality release.",
                status="PENDING",
                planned_start=_dt("2026-04-02T13:45:00"),
                planned_end=_dt("2026-04-02T16:00:00"),
                actual_start=None,
                actual_end=None,
                quantity=120,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1002A-010",
                work_order=wo_1002_a,
                sequence=10,
                name="Casting Prep",
                description="Pending release for cylinder head batch.",
                status="PENDING",
                planned_start=_dt("2026-04-03T07:00:00"),
                planned_end=_dt("2026-04-03T08:30:00"),
                quantity=80,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=False,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1002A-020",
                work_order=wo_1002_a,
                sequence=20,
                name="Valve Seat Machining",
                description="Pending machining release.",
                status="PENDING",
                planned_start=_dt("2026-04-03T08:45:00"),
                planned_end=_dt("2026-04-03T10:45:00"),
                quantity=80,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1002A-030",
                work_order=wo_1002_a,
                sequence=30,
                name="Leak Test",
                description="Pending validation.",
                status="PENDING",
                planned_start=_dt("2026-04-03T11:00:00"),
                planned_end=_dt("2026-04-03T12:00:00"),
                quantity=80,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1002B-010",
                work_order=wo_1002_b,
                sequence=10,
                name="Surface Cleanup",
                description="Late-start cleanup operation.",
                status="COMPLETED",
                planned_start=_dt("2026-04-03T12:30:00"),
                planned_end=_dt("2026-04-03T13:30:00"),
                actual_start=_dt("2026-04-03T13:15:00"),
                actual_end=_dt("2026-04-03T14:05:00"),
                quantity=80,
                completed_qty=80,
                good_qty=79,
                scrap_qty=1,
                qc_required=False,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1002B-020",
                work_order=wo_1002_b,
                sequence=20,
                name="Pressure Fit Assembly",
                description="Late work order currently running.",
                status="IN_PROGRESS",
                planned_start=_dt("2026-04-03T13:30:00"),
                planned_end=_dt("2026-04-03T16:30:00"),
                actual_start=_dt("2026-04-03T14:20:00"),
                actual_end=None,
                quantity=80,
                completed_qty=32,
                good_qty=30,
                scrap_qty=2,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1002B-030",
                work_order=wo_1002_b,
                sequence=30,
                name="Leak Test",
                description="Blocked by upstream delay.",
                status="PENDING",
                planned_start=_dt("2026-04-03T16:45:00"),
                planned_end=_dt("2026-04-03T18:00:00"),
                quantity=80,
                completed_qty=0,
                good_qty=0,
                scrap_qty=0,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1003A-010",
                work_order=wo_1003_a,
                sequence=10,
                name="Blank Preparation",
                description="Prepare pump housing blanks.",
                status="COMPLETED",
                planned_start=_dt("2026-03-31T06:00:00"),
                planned_end=_dt("2026-03-31T07:00:00"),
                actual_start=_dt("2026-03-31T06:00:00"),
                actual_end=_dt("2026-03-31T06:45:00"),
                quantity=60,
                completed_qty=60,
                good_qty=60,
                scrap_qty=0,
                qc_required=False,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1003A-020",
                work_order=wo_1003_a,
                sequence=20,
                name="CNC Machining",
                description="Machine pump housing to tolerance.",
                status="COMPLETED",
                planned_start=_dt("2026-03-31T07:10:00"),
                planned_end=_dt("2026-03-31T11:30:00"),
                actual_start=_dt("2026-03-31T07:05:00"),
                actual_end=_dt("2026-03-31T11:10:00"),
                quantity=60,
                completed_qty=60,
                good_qty=59,
                scrap_qty=1,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
            Operation(
                operation_number="OP-DEMO-1003A-030",
                work_order=wo_1003_a,
                sequence=30,
                name="Final Test",
                description="Final dimensional and leak verification.",
                status="COMPLETED",
                planned_start=_dt("2026-03-31T11:45:00"),
                planned_end=_dt("2026-03-31T15:00:00"),
                actual_start=_dt("2026-03-31T11:40:00"),
                actual_end=_dt("2026-03-31T14:45:00"),
                quantity=59,
                completed_qty=59,
                good_qty=59,
                scrap_qty=0,
                qc_required=True,
                tenant_id=TENANT_ID,
            ),
        ]

        db.add_all([po_1001, wo_1001_a, wo_1001_b, po_1002, wo_1002_a, wo_1002_b, po_1003, wo_1003_a, *operations])
        db.flush()

        operations_by_number = {operation.operation_number: operation for operation in operations}

        completed_runs = [
            (po_1001, wo_1001_a, "OP-DEMO-1001A-010", "2026-04-01T06:00:00", (120, 0), "2026-04-01T06:50:00", "DEMO-OP-01"),
            (po_1001, wo_1001_a, "OP-DEMO-1001A-020", "2026-04-01T07:05:00", (118, 2), "2026-04-01T09:20:00", "DEMO-OP-02"),
            (po_1001, wo_1001_a, "OP-DEMO-1001A-030", "2026-04-01T09:40:00", (118, 0), "2026-04-01T11:30:00", "DEMO-OP-03"),
            (po_1001, wo_1001_a, "OP-DEMO-1001A-040", "2026-04-01T11:45:00", (117, 1), "2026-04-01T13:10:00", "QC-OP-01"),
            (po_1001, wo_1001_b, "OP-DEMO-1001B-010", "2026-04-02T06:10:00", (120, 0), "2026-04-02T06:55:00", "DEMO-OP-04"),
            (po_1002, wo_1002_b, "OP-DEMO-1002B-010", "2026-04-03T13:15:00", (79, 1), "2026-04-03T14:05:00", "DEMO-OP-05"),
            (po_1003, wo_1003_a, "OP-DEMO-1003A-010", "2026-03-31T06:00:00", (60, 0), "2026-03-31T06:45:00", "DEMO-OP-06"),
            (po_1003, wo_1003_a, "OP-DEMO-1003A-020", "2026-03-31T07:05:00", (59, 1), "2026-03-31T11:10:00", "DEMO-OP-07"),
            (po_1003, wo_1003_a, "OP-DEMO-1003A-030", "2026-03-31T11:40:00", (59, 0), "2026-03-31T14:45:00", "QC-OP-02"),
        ]

        for production_order, work_order, operation_number, started_at, qty, completed_at, operator_id in completed_runs:
            operation = operations_by_number[operation_number]
            _add_event(
                db,
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order=production_order,
                work_order=work_order,
                operation=operation,
                payload={"started_at": started_at, "operator_id": operator_id},
            )
            _add_event(
                db,
                event_type=ExecutionEventType.QTY_REPORTED.value,
                production_order=production_order,
                work_order=work_order,
                operation=operation,
                payload={"good_qty": qty[0], "scrap_qty": qty[1], "operator_id": operator_id},
            )
            _add_event(
                db,
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order=production_order,
                work_order=work_order,
                operation=operation,
                payload={"completed_at": completed_at, "operator_id": operator_id},
            )

        _add_event(
            db,
            event_type=ExecutionEventType.OP_STARTED.value,
            production_order=po_1001,
            work_order=wo_1001_b,
            operation=operations_by_number["OP-DEMO-1001B-020"],
            payload={"started_at": "2026-04-02T07:20:00", "operator_id": "DEMO-OP-08"},
        )
        _add_event(
            db,
            event_type=ExecutionEventType.QTY_REPORTED.value,
            production_order=po_1001,
            work_order=wo_1001_b,
            operation=operations_by_number["OP-DEMO-1001B-020"],
            payload={"good_qty": 54, "scrap_qty": 3, "operator_id": "DEMO-OP-08"},
        )

        _add_event(
            db,
            event_type=ExecutionEventType.OP_STARTED.value,
            production_order=po_1002,
            work_order=wo_1002_b,
            operation=operations_by_number["OP-DEMO-1002B-020"],
            payload={"started_at": "2026-04-03T14:20:00", "operator_id": "DEMO-OP-09"},
        )
        _add_event(
            db,
            event_type=ExecutionEventType.QTY_REPORTED.value,
            production_order=po_1002,
            work_order=wo_1002_b,
            operation=operations_by_number["OP-DEMO-1002B-020"],
            payload={"good_qty": 30, "scrap_qty": 2, "operator_id": "DEMO-OP-09"},
        )

        db.commit()


def main() -> None:
    init_db()
    reset_demo_data()
    seed_demo_data()
    print("Seeded MES demo data: 3 production orders / 5 work orders / 17 operations")


if __name__ == "__main__":
    main()