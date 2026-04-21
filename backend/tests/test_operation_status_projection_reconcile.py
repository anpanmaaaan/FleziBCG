from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.repositories.execution_event_repository import create_execution_event
from app.services.operation_service import (
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
            db.execute(
                delete(OperationClaimAuditLog).where(
                    OperationClaimAuditLog.operation_id.in_(op_ids)
                )
            )
            db.execute(
                delete(OperationClaim).where(OperationClaim.operation_id.in_(op_ids))
            )
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
        _purge(db)
        db.close()
