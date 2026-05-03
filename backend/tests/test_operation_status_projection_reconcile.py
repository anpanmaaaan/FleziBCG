from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.repositories.execution_event_repository import create_execution_event
from app.services.operation_service import (
    derive_operation_detail,
    derive_operation_runtime_projection_for_ids,
    detect_operation_status_projection_mismatches,
    reconcile_operation_status_projection,
)

_PREFIX = "TEST-STATUS-RECONCILE"
_TENANT_ID = "default"


def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if not po_ids:
        db.commit()
        return

    wo_ids = list(
        db.scalars(
            select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
        )
    )
    if wo_ids:
        op_ids = list(
            db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids)))
        )
        if op_ids:
            db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
        db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.commit()


def test_reconcile_runtime_repair_event_updates_snapshot_projection():
    db = SessionLocal()
    try:
        _purge(db)

        po = ProductionOrder(
            order_number=f"{_PREFIX}-PO-001",
            route_id=f"{_PREFIX}-R-01",
            product_name="status projection reconcile",
            quantity=10,
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(po)
        db.flush()

        wo = WorkOrder(
            production_order_id=po.id,
            work_order_number=f"{_PREFIX}-WO-001",
            status=StatusEnum.planned.value,
            planned_start=datetime(2099, 6, 1, 8, 0, 0),
            planned_end=datetime(2099, 6, 1, 17, 0, 0),
            tenant_id=_TENANT_ID,
        )
        db.add(wo)
        db.flush()

        op = Operation(
            operation_number=f"{_PREFIX}-OP-001",
            work_order_id=wo.id,
            sequence=10,
            name="projection mismatch op",
            status=StatusEnum.paused.value,
            planned_start=datetime(2099, 6, 1, 9, 15, 0),
            planned_end=datetime(2099, 6, 1, 11, 15, 0),
            quantity=10,
            completed_qty=0,
            good_qty=0,
            scrap_qty=0,
            qc_required=False,
            station_scope_value="STATION_RECONCILE",
            tenant_id=_TENANT_ID,
        )
        db.add(op)
        db.flush()

        # Base history: started then paused.
        create_execution_event(
            db=db,
            event_type=ExecutionEventType.OP_STARTED.value,
            production_order_id=po.id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"started_at": "2099-06-01T09:15:00"},
            tenant_id=_TENANT_ID,
        )
        create_execution_event(
            db=db,
            event_type=ExecutionEventType.EXECUTION_PAUSED.value,
            production_order_id=po.id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"paused_at": "2099-06-01T09:20:00", "actor_user_id": "seed"},
            tenant_id=_TENANT_ID,
        )

        # Simulated maintenance repair appends execution_resumed but forgets
        # to synchronize operation.status projection.
        create_execution_event(
            db=db,
            event_type=ExecutionEventType.EXECUTION_RESUMED.value,
            production_order_id=po.id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={
                "resumed_at": "2099-06-01T09:25:00",
                "actor_user_id": "system_data_repair_paused_orphan",
            },
            tenant_id=_TENANT_ID,
        )
        db.commit()
        db.refresh(op)

        assert op.status == StatusEnum.paused.value

        mismatches_before = detect_operation_status_projection_mismatches(
            db,
            tenant_id=_TENANT_ID,
            operation_ids=[op.id],
        )
        assert len(mismatches_before) == 1
        assert mismatches_before[0]["snapshot_status"] == StatusEnum.paused.value
        assert mismatches_before[0]["derived_status"] == StatusEnum.in_progress.value

        reconcile_operation_status_projection(
            db,
            operation=op,
            tenant_id=_TENANT_ID,
        )
        db.refresh(op)

        assert op.status == StatusEnum.in_progress.value

        mismatches_after = detect_operation_status_projection_mismatches(
            db,
            tenant_id=_TENANT_ID,
            operation_ids=[op.id],
        )
        assert mismatches_after == []
    finally:
        db.rollback()
        _purge(db)
        db.close()


def _seed_operation_with_event_types(
    db,
    *,
    suffix: str,
    snapshot_status: str,
    event_types: list[str],
    closure_status: str = "OPEN",
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="projection parity",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        work_order_id=wo.id,
        sequence=10,
        name=f"projection-parity-{suffix}",
        status=snapshot_status,
        closure_status=closure_status,
        planned_start=datetime(2099, 6, 1, 9, 15, 0),
        planned_end=datetime(2099, 6, 1, 11, 15, 0),
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=False,
        station_scope_value="STATION_RECONCILE",
        tenant_id=_TENANT_ID,
    )
    db.add(op)
    db.flush()

    for event_type in event_types:
        create_execution_event(
            db=db,
            event_type=event_type,
            production_order_id=po.id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"seed": suffix, "event_type": event_type},
            tenant_id=_TENANT_ID,
        )
    db.commit()
    db.refresh(op)
    return op


def _assert_detail_bulk_parity(db, op: Operation, expected_status: str, expected_downtime_open: bool):
    detail = derive_operation_detail(db, op)
    bulk_projection = derive_operation_runtime_projection_for_ids(
        db,
        tenant_id=_TENANT_ID,
        operation_ids=[op.id],
    )[op.id]
    assert detail.status == expected_status
    assert bulk_projection.status == expected_status
    assert detail.downtime_open is expected_downtime_open
    assert bulk_projection.downtime_open is expected_downtime_open


def test_projection_parity_reopen_resume_complete_is_completed():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_event_types(
            db,
            suffix="PARITY-01",
            snapshot_status=StatusEnum.planned.value,
            event_types=[
                ExecutionEventType.OP_STARTED.value,
                ExecutionEventType.OP_COMPLETED.value,
                ExecutionEventType.OPERATION_REOPENED.value,
                ExecutionEventType.EXECUTION_RESUMED.value,
                ExecutionEventType.OP_COMPLETED.value,
            ],
        )
        _assert_detail_bulk_parity(
            db,
            op,
            expected_status=StatusEnum.completed.value,
            expected_downtime_open=False,
        )
    finally:
        db.rollback()
        _purge(db)
        db.close()


def test_projection_parity_aborted_is_consistent():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_event_types(
            db,
            suffix="PARITY-02",
            snapshot_status=StatusEnum.planned.value,
            event_types=[
                ExecutionEventType.OP_STARTED.value,
                ExecutionEventType.OP_ABORTED.value,
            ],
        )
        _assert_detail_bulk_parity(
            db,
            op,
            expected_status=StatusEnum.aborted.value,
            expected_downtime_open=False,
        )
    finally:
        db.rollback()
        _purge(db)
        db.close()


def test_projection_parity_downtime_open_is_blocked():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_event_types(
            db,
            suffix="PARITY-03",
            snapshot_status=StatusEnum.planned.value,
            event_types=[
                ExecutionEventType.OP_STARTED.value,
                ExecutionEventType.DOWNTIME_STARTED.value,
            ],
        )
        _assert_detail_bulk_parity(
            db,
            op,
            expected_status=StatusEnum.blocked.value,
            expected_downtime_open=True,
        )
    finally:
        db.rollback()
        _purge(db)
        db.close()


def test_projection_parity_downtime_ended_is_paused_until_resume():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_event_types(
            db,
            suffix="PARITY-04",
            snapshot_status=StatusEnum.planned.value,
            event_types=[
                ExecutionEventType.OP_STARTED.value,
                ExecutionEventType.DOWNTIME_STARTED.value,
                ExecutionEventType.DOWNTIME_ENDED.value,
            ],
        )
        _assert_detail_bulk_parity(
            db,
            op,
            expected_status=StatusEnum.paused.value,
            expected_downtime_open=False,
        )
    finally:
        db.rollback()
        _purge(db)
        db.close()


def test_projection_parity_closed_detail_actions_are_reopen_only():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_event_types(
            db,
            suffix="PARITY-05",
            snapshot_status=StatusEnum.completed.value,
            closure_status="CLOSED",
            event_types=[
                ExecutionEventType.OP_STARTED.value,
                ExecutionEventType.OP_COMPLETED.value,
                ExecutionEventType.OPERATION_CLOSED_AT_STATION.value,
            ],
        )
        detail = derive_operation_detail(db, op)
        bulk_projection = derive_operation_runtime_projection_for_ids(
            db,
            tenant_id=_TENANT_ID,
            operation_ids=[op.id],
        )[op.id]
        assert detail.status == bulk_projection.status == StatusEnum.completed.value
        assert detail.allowed_actions == ["reopen_operation"]
    finally:
        db.rollback()
        _purge(db)
        db.close()
