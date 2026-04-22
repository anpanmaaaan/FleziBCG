from __future__ import annotations

from datetime import datetime
from io import StringIO

from sqlalchemy import delete, func as sa_func, select

from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.repositories.execution_event_repository import create_execution_event
from scripts.reconcile_operation_status_projection import run_status_projection_reconcile

_PREFIX = "TEST-RECONCILE-CMD"
_TENANT_A = "tenant-a"
_TENANT_B = "tenant-b"


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
            db.execute(
                delete(OperationClaimAuditLog).where(
                    OperationClaimAuditLog.operation_id.in_(op_ids)
                )
            )
            db.execute(delete(OperationClaim).where(OperationClaim.operation_id.in_(op_ids)))
            db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
        db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.commit()


def _seed_operation_with_runtime_mismatch(
    db,
    *,
    tenant_id: str,
    suffix: str,
    snapshot_status: str,
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="reconcile command",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 6, 1, 8, 0, 0),
        planned_end=datetime(2099, 6, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        work_order_id=wo.id,
        sequence=10,
        name=f"op-{suffix}",
        status=snapshot_status,
        planned_start=datetime(2099, 6, 1, 9, 15, 0),
        planned_end=datetime(2099, 6, 1, 11, 15, 0),
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=False,
        station_scope_value="STATION_01",
        tenant_id=tenant_id,
    )
    db.add(op)
    db.flush()

    # Maintenance-style runtime truth: OP_STARTED + EXECUTION_RESUMED -> IN_PROGRESS.
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OP_STARTED.value,
        production_order_id=po.id,
        work_order_id=wo.id,
        operation_id=op.id,
        payload={"started_at": "2099-06-01T09:15:00"},
        tenant_id=tenant_id,
    )
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.EXECUTION_RESUMED.value,
        production_order_id=po.id,
        work_order_id=wo.id,
        operation_id=op.id,
        payload={
            "resumed_at": "2099-06-01T09:20:00",
            "actor_user_id": "system_data_repair_paused_orphan",
        },
        tenant_id=tenant_id,
    )
    db.commit()
    db.refresh(op)
    return op


def test_reconcile_command_detect_only_reports_without_mutating_snapshot():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_runtime_mismatch(
            db,
            tenant_id=_TENANT_A,
            suffix="A1",
            snapshot_status=StatusEnum.paused.value,
        )

        out = StringIO()
        result = run_status_projection_reconcile(
            tenant_id=_TENANT_A,
            apply=False,
            out=out,
        )

        db.refresh(op)
        assert result["mismatch_count"] == 1
        assert result["reconciled_count"] == 0
        assert op.status == StatusEnum.paused.value
        assert "mismatches:" in out.getvalue()
    finally:
        _purge(db)
        db.close()


def test_reconcile_command_apply_mode_reconciles_and_clears_mismatch():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_runtime_mismatch(
            db,
            tenant_id=_TENANT_A,
            suffix="A2",
            snapshot_status=StatusEnum.paused.value,
        )

        detect = run_status_projection_reconcile(tenant_id=_TENANT_A, apply=False)
        assert detect["mismatch_count"] == 1

        apply_result = run_status_projection_reconcile(tenant_id=_TENANT_A, apply=True)
        assert apply_result["mismatch_count"] == 1
        assert apply_result["reconciled_count"] == 1

        db.refresh(op)
        assert op.status == StatusEnum.in_progress.value

        after = run_status_projection_reconcile(tenant_id=_TENANT_A, apply=False)
        assert after["mismatch_count"] == 0
    finally:
        _purge(db)
        db.close()


def test_reconcile_command_clean_dataset_returns_zero_mismatch():
    db = SessionLocal()
    try:
        _purge(db)
        _seed_operation_with_runtime_mismatch(
            db,
            tenant_id=_TENANT_A,
            suffix="A3",
            snapshot_status=StatusEnum.paused.value,
        )
        run_status_projection_reconcile(tenant_id=_TENANT_A, apply=True)

        result = run_status_projection_reconcile(tenant_id=_TENANT_A, apply=False)
        assert result["mismatch_count"] == 0
        assert result["reconciled_count"] == 0
    finally:
        _purge(db)
        db.close()


def test_reconcile_command_respects_tenant_scope():
    db = SessionLocal()
    try:
        _purge(db)
        op_tenant_a = _seed_operation_with_runtime_mismatch(
            db,
            tenant_id=_TENANT_A,
            suffix="A4",
            snapshot_status=StatusEnum.paused.value,
        )
        op_tenant_b = _seed_operation_with_runtime_mismatch(
            db,
            tenant_id=_TENANT_B,
            suffix="B1",
            snapshot_status=StatusEnum.paused.value,
        )

        run_status_projection_reconcile(tenant_id=_TENANT_A, apply=True)
        db.refresh(op_tenant_a)
        db.refresh(op_tenant_b)

        assert op_tenant_a.status == StatusEnum.in_progress.value
        assert op_tenant_b.status == StatusEnum.paused.value

        tenant_b_detect = run_status_projection_reconcile(tenant_id=_TENANT_B, apply=False)
        assert tenant_b_detect["mismatch_count"] == 1
    finally:
        _purge(db)
        db.close()


def test_reconcile_command_does_not_mutate_event_history():
    db = SessionLocal()
    try:
        _purge(db)
        op = _seed_operation_with_runtime_mismatch(
            db,
            tenant_id=_TENANT_A,
            suffix="A5",
            snapshot_status=StatusEnum.paused.value,
        )

        count_before = db.scalar(
            select(sa_func.count())
            .select_from(ExecutionEvent)
            .where(ExecutionEvent.operation_id == op.id)
        )

        apply_result = run_status_projection_reconcile(tenant_id=_TENANT_A, apply=True)
        assert apply_result["reconciled_count"] == 1

        count_after = db.scalar(
            select(sa_func.count())
            .select_from(ExecutionEvent)
            .where(ExecutionEvent.operation_id == op.id)
        )

        assert count_before == count_after

        db.refresh(op)
        assert op.status == StatusEnum.in_progress.value
    finally:
        _purge(db)
        db.close()
