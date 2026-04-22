"""
Covers the DB-backed downtime reason master path.

Scope:
- valid start_downtime with reason_code (seeded master row)
- invalid reason_code rejected
- inactive reason rejected
- start_downtime still blocked in invalid runtime states
- end_downtime still returns execution to PAUSED
- resume blocked while downtime open
- complete blocked while downtime open (indirect: BLOCKED state guard)
- close/reopen behavior unaffected by the refactor
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.downtime_reason import DowntimeReason
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.schemas.operation import (
    OperationCloseRequest,
    OperationCompleteRequest,
    OperationEndDowntimeRequest,
    OperationReopenRequest,
    OperationResumeRequest,
    OperationStartDowntimeRequest,
)
from app.services.operation_service import (
    CompleteOperationConflictError,
    ResumeExecutionConflictError,
    StartDowntimeConflictError,
    close_operation,
    complete_operation,
    end_downtime,
    reopen_operation,
    resume_operation,
    start_downtime,
)


_PREFIX = "TEST-DT-REASON-MASTER"
_TENANT_ID = "default"


def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if po_ids:
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
                db.execute(
                    delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids))
                )
                db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    db.execute(
        delete(DowntimeReason).where(
            DowntimeReason.tenant_id == _TENANT_ID,
            DowntimeReason.reason_code.like(f"{_PREFIX}-%"),
        )
    )
    db.commit()


@pytest.fixture
def db_session():
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        yield db
    finally:
        _purge(db)
        db.close()


def _seed_wo(db) -> WorkOrder:
    unique = uuid4().hex[:6].upper()
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{unique}",
        route_id=f"R-{unique}",
        product_name="downtime reason master",
        quantity=10,
        status=StatusEnum.planned.value,
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()
    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{unique}",
        status=StatusEnum.in_progress.value,
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    return wo


def _mk_op(
    db,
    wo: WorkOrder,
    *,
    status: str,
    closure_status: str = ClosureStatusEnum.open.value,
) -> Operation:
    unique = uuid4().hex[:6].upper()
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{unique}",
        work_order_id=wo.id,
        sequence=10,
        name="reason master op",
        status=status,
        closure_status=closure_status,
        planned_start=datetime(2099, 8, 1, 9, 0, 0),
        planned_end=datetime(2099, 8, 1, 10, 0, 0),
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=False,
        station_scope_value="STATION_01",
        tenant_id=_TENANT_ID,
    )
    db.add(op)
    db.flush()
    # Append an OP_STARTED event so the event-driven derivations agree with
    # the snapshot for IN_PROGRESS / PAUSED / BLOCKED fixtures.
    if status in (
        StatusEnum.in_progress.value,
        StatusEnum.paused.value,
        StatusEnum.blocked.value,
    ):
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=wo.production_order_id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"operator_id": None, "started_at": "2099-08-01T09:00:00"},
                tenant_id=_TENANT_ID,
            )
        )
        db.flush()
    return op


def _seed_inactive_reason(db) -> DowntimeReason:
    r = DowntimeReason(
        tenant_id=_TENANT_ID,
        reason_code=f"{_PREFIX}-INACTIVE",
        reason_name="Inactive test reason",
        reason_group="OTHER",
        planned_flag=False,
        default_block_mode="BLOCK",
        requires_comment=False,
        requires_supervisor_review=False,
        active_flag=False,
        sort_order=0,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


# ─── 1. valid start_downtime with seeded reason_code ────────────────────────
def test_start_downtime_with_valid_reason_code_persists_master_fields(db_session):
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.in_progress.value)

    detail = start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code="MATERIAL_SHORTAGE", note="n"),
        actor_user_id="opr-001",
        tenant_id=_TENANT_ID,
    )
    assert detail.downtime_open is True
    assert detail.status == StatusEnum.blocked.value

    events = list(
        db.scalars(
            select(ExecutionEvent).where(
                ExecutionEvent.operation_id == op.id,
                ExecutionEvent.event_type == ExecutionEventType.DOWNTIME_STARTED.value,
            )
        )
    )
    assert len(events) == 1
    payload = events[0].payload
    assert payload["reason_code"] == "MATERIAL_SHORTAGE"
    assert payload["reason_group"] == "MATERIAL"
    assert payload["reason_name"] == "Material shortage"
    assert payload["planned_flag"] is False
    # Classification is server-derived from master data; no legacy client input
    # field should appear on the event payload.
    assert "reason_class" not in payload


# ─── 2. invalid reason_code rejected ────────────────────────────────────────
def test_start_downtime_rejects_unknown_reason_code(db_session):
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.in_progress.value)

    with pytest.raises(StartDowntimeConflictError, match="INVALID_REASON_CODE"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code=f"{_PREFIX}-NOT-THERE"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )


# ─── 3. inactive reason rejected ────────────────────────────────────────────
def test_start_downtime_rejects_inactive_reason(db_session):
    db = db_session
    _seed_inactive_reason(db)
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.in_progress.value)

    with pytest.raises(StartDowntimeConflictError, match="INACTIVE_REASON"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code=f"{_PREFIX}-INACTIVE"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )


# ─── 4. start_downtime blocked in invalid runtime state ─────────────────────
def test_start_downtime_blocked_in_planned_state(db_session):
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.planned.value)

    with pytest.raises(StartDowntimeConflictError, match="STATE_NOT_RUNNING_OR_PAUSED"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code="MATERIAL_SHORTAGE"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )


# ─── 5. end_downtime returns execution to PAUSED ────────────────────────────
def test_end_downtime_transitions_blocked_to_paused(db_session):
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.in_progress.value)

    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code="BREAKDOWN_GENERIC"),
        actor_user_id="opr-001",
        tenant_id=_TENANT_ID,
    )
    db.refresh(op)
    assert op.status == StatusEnum.blocked.value

    detail = end_downtime(
        db,
        op,
        OperationEndDowntimeRequest(note="fixed"),
        actor_user_id="opr-001",
        tenant_id=_TENANT_ID,
    )
    db.refresh(op)
    assert op.status == StatusEnum.paused.value
    assert detail.status == StatusEnum.paused.value
    assert detail.downtime_open is False


# ─── 6. resume blocked while downtime open ──────────────────────────────────
def test_resume_blocked_while_downtime_open(db_session):
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.in_progress.value)

    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code="BREAKDOWN_GENERIC"),
        actor_user_id="opr-001",
        tenant_id=_TENANT_ID,
    )
    db.refresh(op)
    with pytest.raises(ResumeExecutionConflictError, match="STATE_DOWNTIME_OPEN"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(note="try resume"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )


# ─── 7. complete blocked while downtime open (indirect via state guard) ─────
def test_complete_blocked_while_downtime_open(db_session):
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.in_progress.value)

    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code="BREAKDOWN_GENERIC"),
        actor_user_id="opr-001",
        tenant_id=_TENANT_ID,
    )
    db.refresh(op)
    # Snapshot is BLOCKED, so complete_operation rejects via STATE_NOT_IN_PROGRESS
    # (policy PMD-EXEC-005 — complete with open downtime disallowed).
    with pytest.raises(
        CompleteOperationConflictError, match="must be IN_PROGRESS to complete"
    ):
        complete_operation(
            db,
            op,
            OperationCompleteRequest(operator_id="opr-001"),
            tenant_id=_TENANT_ID,
        )


# ─── 8. close/reopen behavior unaffected by refactor ────────────────────────
def test_close_reopen_flow_unchanged_with_new_reason_path(db_session):
    """
    Seeds a COMPLETED snapshot + OP_COMPLETED event directly (the refactor
    does not touch completion wiring) and confirms close -> reopen still
    transitions closure_status as the baseline does. The downtime refactor
    must not alter this baseline guarantee.
    """
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.completed.value)

    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.OP_COMPLETED.value,
            production_order_id=wo.production_order_id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"completed_at": "2099-08-01T11:00:00"},
            tenant_id=_TENANT_ID,
        )
    )
    db.commit()
    db.refresh(op)

    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note="done"),
        actor_user_id="sup-001",
        tenant_id=_TENANT_ID,
    )
    assert detail.closure_status == ClosureStatusEnum.closed.value

    op = db.get(Operation, op.id)
    detail = reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="rework needed"),
        actor_user_id="sup-001",
        tenant_id=_TENANT_ID,
    )
    assert detail.closure_status == ClosureStatusEnum.open.value
    assert detail.status == StatusEnum.paused.value


# ─── 9. legacy reason_class compat path still writes an event ───────────────
def test_legacy_reason_class_compat_path_still_works(db_session):
    db = db_session
    wo = _seed_wo(db)
    op = _mk_op(db, wo, status=StatusEnum.in_progress.value)

    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_class=DowntimeReasonClass.BREAKDOWN),
        actor_user_id="opr-001",
        tenant_id=_TENANT_ID,
    )
    db.refresh(op)
    assert op.status == StatusEnum.blocked.value

    event = db.scalar(
        select(ExecutionEvent)
        .where(
            ExecutionEvent.operation_id == op.id,
            ExecutionEvent.event_type == ExecutionEventType.DOWNTIME_STARTED.value,
        )
        .order_by(ExecutionEvent.id.desc())
    )
    assert event is not None
    # Legacy compat payload: reason_group is populated, reason_code is absent.
    assert event.payload["reason_group"] == "BREAKDOWN"
    assert event.payload.get("reason_class") == "BREAKDOWN"
    assert "reason_code" not in event.payload
