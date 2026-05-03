"""P0-C-07C — Reopen Operation / Claim Continuity Hardening

Focused hardening suite for reopen_operation guards, event emission,
projection/detail consistency, allowed_actions derivation, claim
continuity, and StationSession diagnostic non-interference.

Existing coverage in:
  - test_close_reopen_operation_foundation.py (4 tests)
  - test_reopen_resumability_claim_continuity.py (4 tests)

This file adds focused coverage for:
  T1  — happy path snapshot + return value
  T2  — rejects non-CLOSED (OPEN) operation
  T3  — rejects blank reason
  T4  — rejects None reason
  T5  — rejects tenant mismatch
  T6  — emits OPERATION_REOPENED event with expected payload
  T7  — closure_status becomes OPEN in detail and snapshot
  T8  — projection/detail after reopen is consistent (PAUSED + OPEN)
  T9  — allowed_actions after reopen = ["resume_execution", "start_downtime"]
  T10 — missing StationSession does not change reopen outcome
  T11 — matching OPEN StationSession does not change reopen outcome
  T12 — PAUSED non-closed operation rejects reopen
  T13 — reopen_count increments on first reopen
"""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.schemas.operation import OperationReopenRequest
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    ReopenOperationConflictError,
    derive_operation_detail,
    reopen_operation,
)
from app.services.station_session_service import open_station_session

_PREFIX = "TEST-P0C07C"
_TENANT_ID = "default"
_STATION = f"{_PREFIX}-STATION"
_ACTOR = f"{_PREFIX}-ACTOR"


def _identity(user_id: str = _ACTOR, tenant_id: str = _TENANT_ID) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username=user_id,
        email=None,
        tenant_id=tenant_id,
        role_code="OPR",
        acting_role_code=None,
        is_authenticated=True,
    )


def _ensure_opr_role(db) -> Role:
    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is not None:
        return role
    role = Role(code="OPR", name="Operator", role_type="system", is_system=True)
    db.add(role)
    db.flush()
    return role


def _seed_station_scope(db, *, user_id: str, station_id: str = _STATION) -> None:
    role = _ensure_opr_role(db)
    scope = Scope(
        tenant_id=_TENANT_ID,
        scope_type="station",
        scope_value=station_id,
    )
    db.add(scope)
    db.flush()
    db.add(
        UserRoleAssignment(
            user_id=user_id,
            role_id=role.id,
            scope_id=scope.id,
            is_primary=True,
            is_active=True,
        )
    )
    db.commit()


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
            db.scalars(select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids)))
        )
        if wo_ids:
            op_ids = list(
                db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids)))
            )
            if op_ids:
                db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
                db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    db.execute(
        delete(StationSession).where(
            StationSession.tenant_id == _TENANT_ID,
            StationSession.station_id.like(f"{_PREFIX}-%"),
        )
    )
    db.execute(
        delete(UserRoleAssignment).where(UserRoleAssignment.user_id.like(f"{_PREFIX}%"))
    )
    db.execute(
        delete(Scope).where(
            Scope.tenant_id == _TENANT_ID,
            Scope.scope_type == "station",
            Scope.scope_value.like(f"{_PREFIX}-%"),
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
        db.rollback()
        _purge(db)
        db.close()


def _seed_operation(
    db,
    *,
    suffix: str,
    status: str,
    closure_status: str = ClosureStatusEnum.open.value,
    station_scope_value: str = _STATION,
    tenant_id: str = _TENANT_ID,
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="p0c07c",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 3, 8, 0, 0),
        planned_end=datetime(2099, 10, 3, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 3, 8, 0, 0),
        planned_end=datetime(2099, 10, 3, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c07c-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=tenant_id,
        status=status,
        closure_status=closure_status,
        station_scope_value=station_scope_value,
        quantity=10,
    )
    db.add(op)
    db.flush()

    if status in (StatusEnum.completed.value, StatusEnum.completed_late.value):
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"started_at": datetime(2099, 10, 3, 9, 0, 0).isoformat()},
                tenant_id=tenant_id,
            )
        )
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"completed_at": datetime(2099, 10, 3, 9, 30, 0).isoformat()},
                tenant_id=tenant_id,
            )
        )

    if status == StatusEnum.paused.value:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"started_at": datetime(2099, 10, 3, 9, 0, 0).isoformat()},
                tenant_id=tenant_id,
            )
        )
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.EXECUTION_PAUSED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"paused_at": datetime(2099, 10, 3, 9, 15, 0).isoformat()},
                tenant_id=tenant_id,
            )
        )

    db.commit()
    db.refresh(op)
    return op


def _reopen_request(reason: str | None = "quality recheck required") -> OperationReopenRequest:
    return OperationReopenRequest(reason=reason)


def _latest_event(db, operation_id: int) -> ExecutionEvent | None:
    return db.scalar(
        select(ExecutionEvent)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
    )


def _event_count(db, operation_id: int) -> int:
    return db.scalar(
        select(ExecutionEvent.id).where(
            ExecutionEvent.operation_id == operation_id
        ).count()  # type: ignore[attr-defined]
    ) or len(
        list(
            db.scalars(
                select(ExecutionEvent.id).where(ExecutionEvent.operation_id == operation_id)
            )
        )
    )


def _count_events(db, operation_id: int) -> int:
    return len(
        list(
            db.scalars(
                select(ExecutionEvent.id).where(ExecutionEvent.operation_id == operation_id)
            )
        )
    )


# ---------------------------------------------------------------------------
# T1 — Happy path from CLOSED completed operation
# ---------------------------------------------------------------------------

def test_reopen_operation_happy_path_from_closed_completed(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="HAPPY",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    detail = reopen_operation(
        db,
        op,
        _reopen_request("verified: batch correction required"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.open.value
    assert detail.status == StatusEnum.paused.value
    assert detail.last_reopened_by == _ACTOR
    assert detail.last_reopened_at is not None


# ---------------------------------------------------------------------------
# T2 — Rejects non-CLOSED (OPEN) operation
# ---------------------------------------------------------------------------

def test_reopen_operation_rejects_non_closed_open_operation(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="REJECT-OPEN",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.open.value,
    )

    with pytest.raises(ReopenOperationConflictError, match="STATE_NOT_CLOSED"):
        reopen_operation(
            db,
            op,
            _reopen_request(),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T3 — Rejects blank reason
# ---------------------------------------------------------------------------

def test_reopen_operation_rejects_blank_reason(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="REJECT-BLANK",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ReopenOperationConflictError, match="REOPEN_REASON_REQUIRED"):
        reopen_operation(
            db,
            op,
            _reopen_request("   "),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T4 — Schema rejects None reason (Pydantic schema-level guard)
# ---------------------------------------------------------------------------

def test_reopen_request_schema_rejects_none_reason():
    # OperationReopenRequest validates reason as a required string.
    # None is rejected at schema boundary before service is called.
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        OperationReopenRequest(reason=None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# T5 — Rejects tenant mismatch
# ---------------------------------------------------------------------------

def test_reopen_operation_rejects_tenant_mismatch(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="TENANT-MISMATCH",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ValueError, match="does not belong to the requesting tenant"):
        reopen_operation(
            db,
            op,
            _reopen_request(),
            actor_user_id=_ACTOR,
            tenant_id="other-tenant",
        )


# ---------------------------------------------------------------------------
# T6 — Emits OPERATION_REOPENED event with expected payload fields
# ---------------------------------------------------------------------------

def test_reopen_operation_emits_operation_reopened_event_with_payload(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="EVENT-PAYLOAD",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    before_count = _count_events(db, op.id)

    reopen_operation(
        db,
        op,
        _reopen_request("quality check"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    after_count = _count_events(db, op.id)
    assert after_count == before_count + 1

    latest = _latest_event(db, op.id)
    assert latest is not None
    assert latest.event_type == ExecutionEventType.OPERATION_REOPENED.value

    payload = latest.payload if isinstance(latest.payload, dict) else {}
    assert payload.get("actor_user_id") == _ACTOR
    assert payload.get("reason") == "quality check"
    assert "reopened_at" in payload


# ---------------------------------------------------------------------------
# T7 — closure_status becomes OPEN in detail and snapshot
# ---------------------------------------------------------------------------

def test_reopen_operation_closure_status_becomes_open(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="CLOSURE-OPEN",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    assert op.closure_status == ClosureStatusEnum.closed.value

    detail = reopen_operation(
        db,
        op,
        _reopen_request(),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.open.value

    # Verify snapshot is persisted
    db.refresh(op)
    assert op.closure_status == ClosureStatusEnum.open.value


# ---------------------------------------------------------------------------
# T8 — Projection/detail after reopen is consistent (PAUSED + OPEN)
# ---------------------------------------------------------------------------

def test_reopen_operation_projection_detail_consistent(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="PROJ-DETAIL",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    detail = reopen_operation(
        db,
        op,
        _reopen_request(),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    # Projection must agree: reopened → PAUSED runtime
    assert detail.status == StatusEnum.paused.value
    assert detail.closure_status == ClosureStatusEnum.open.value

    # Detail is backend-derived: re-derive independently and verify consistency
    db.refresh(op)
    recomputed = derive_operation_detail(db, op)
    assert recomputed.status == detail.status
    assert recomputed.closure_status == detail.closure_status


# ---------------------------------------------------------------------------
# T9 — allowed_actions after reopen = ["resume_execution", "start_downtime"]
# ---------------------------------------------------------------------------

def test_reopen_operation_allowed_actions_backend_derived(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="ALLOWED-ACTIONS",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    detail = reopen_operation(
        db,
        op,
        _reopen_request(),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert "resume_execution" in detail.allowed_actions
    assert "start_downtime" in detail.allowed_actions
    assert "reopen_operation" not in detail.allowed_actions
    assert "close_operation" not in detail.allowed_actions


# ---------------------------------------------------------------------------
# T10 — Missing StationSession does not change reopen outcome
# ---------------------------------------------------------------------------

def test_reopen_operation_without_station_session_is_allowed(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="NO-SESSION",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    # No StationSession created — diagnostic is non-blocking
    detail = reopen_operation(
        db,
        op,
        _reopen_request(),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.open.value
    assert detail.status == StatusEnum.paused.value


# ---------------------------------------------------------------------------
# T11 — Matching OPEN StationSession does not change reopen outcome
# ---------------------------------------------------------------------------

def test_reopen_operation_with_open_station_session_parity(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="OPEN-SESSION",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    _seed_station_scope(db, user_id=_ACTOR, station_id=_STATION)
    session = open_station_session(
        db,
        identity=_identity(),
        station_id=_STATION,
    )
    assert session.status == "OPEN"

    detail = reopen_operation(
        db,
        op,
        _reopen_request("session-parity reopen"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.open.value
    assert detail.status == StatusEnum.paused.value
    assert "resume_execution" in detail.allowed_actions


# ---------------------------------------------------------------------------
# T12 — PAUSED non-closed operation rejects reopen
# ---------------------------------------------------------------------------

def test_reopen_operation_rejects_paused_non_closed_operation(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="PAUSED-REJECT",
        status=StatusEnum.paused.value,
        closure_status=ClosureStatusEnum.open.value,
    )

    with pytest.raises(ReopenOperationConflictError, match="STATE_NOT_CLOSED"):
        reopen_operation(
            db,
            op,
            _reopen_request(),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T13 — reopen_count increments on first reopen
# ---------------------------------------------------------------------------

def test_reopen_operation_increments_reopen_count(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="REOPEN-COUNT",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    assert (op.reopen_count or 0) == 0

    detail = reopen_operation(
        db,
        op,
        _reopen_request(),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.reopen_count == 1
