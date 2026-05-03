"""
P0-C-04C / P0-C-04D — Command Context Diagnostic Integration Tests.

Purpose:
- Verify that guarded execution commands reject without an OPEN StationSession.
- Verify that execution commands produce expected outcomes with a matching
    OPEN StationSession.
- Verify that StationSession diagnostic context IS accessible from the same
  tenant/station context that execution commands use.
- Prove that existing rejection codes are unchanged.
- Prove that cross-tenant and CLOSED sessions do not create false positives.

Contract:
- Diagnostic result (session_ctx) remains informational only.
- Guarded commands require a matching OPEN StationSession before later state
    validations run.
- OperationDetail API response shape is unchanged.
- Claim compatibility regression must remain green.
"""
from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.schemas.operation import (
    OperationPauseRequest,
    OperationStartRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    StartOperationConflictError,
    PauseExecutionConflictError,
    StationSessionGuardError,
    start_operation,
    pause_operation,
)
from app.services.station_session_diagnostic import (
    SessionReadiness,
    get_station_session_diagnostic,
)
from app.services.station_session_service import (
    close_station_session,
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

_PREFIX = "TEST-CMD-CTX"
_TENANT_ID = "default"
_OTHER_TENANT_ID = "cmd-ctx-tenant-b"
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
            StationSession.station_id == _STATION,
            StationSession.tenant_id.in_([_TENANT_ID, _OTHER_TENANT_ID]),
        )
    )
    db.execute(
        delete(UserRoleAssignment).where(UserRoleAssignment.user_id == _ACTOR)
    )
    db.execute(
        delete(Scope).where(
            Scope.scope_value == _STATION,
            Scope.tenant_id.in_([_TENANT_ID, _OTHER_TENANT_ID]),
        )
    )
    db.commit()


def _seed_station_scope(db) -> None:
    opr_role = _ensure_opr_role(db)
    scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == _TENANT_ID,
            Scope.scope_type == "station",
            Scope.scope_value == _STATION,
        )
    )
    if scope is None:
        scope = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=_STATION,
        )
        db.add(scope)
        db.flush()

    assignment = db.scalar(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == _ACTOR,
            UserRoleAssignment.role_id == opr_role.id,
            UserRoleAssignment.scope_id == scope.id,
        )
    )
    if assignment is None:
        db.add(
            UserRoleAssignment(
                user_id=_ACTOR,
                role_id=opr_role.id,
                scope_id=scope.id,
                is_primary=True,
                is_active=True,
            )
        )
    db.commit()


def _ensure_open_station_session(db) -> StationSession:
    identity = _identity()
    session = get_current_station_session(db, identity, station_id=_STATION)
    if session is None:
        session = open_station_session(db, identity, station_id=_STATION)
    if session.operator_user_id != _ACTOR:
        session = identify_operator_at_station(
            db,
            identity,
            session_id=session.session_id,
            operator_user_id=_ACTOR,
        )
    return session


def _seed_planned_op(db, suffix: str) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R",
        product_name="cmd ctx product",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()
    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="cmd ctx op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=_STATION,
        quantity=10,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def _seed_running_op(db, suffix: str) -> Operation:
    """Seeds a PLANNED op then starts it; returns the refreshed operation."""
    op = _seed_planned_op(db, suffix)
    _ensure_open_station_session(db)
    start_operation(
        db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID
    )
    # Re-load ORM object
    from app.repositories.operation_repository import get_operation_by_id
    reloaded = get_operation_by_id(db, op.id)
    assert reloaded is not None
    return reloaded


@pytest.fixture
def cmd_fixture():
    """Combined fixture: DB initialised, RBAC seeded, cleanup guaranteed."""
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        _seed_station_scope(db)
        yield db
    finally:
        _purge(db)
        db.close()


# ---------------------------------------------------------------------------
# CMD-T1: start_operation unchanged — no StationSession
# ---------------------------------------------------------------------------

def test_start_operation_requires_session(cmd_fixture):
    """CMD-T1: start_operation rejects when no StationSession exists."""
    db = cmd_fixture
    op = _seed_planned_op(db, "t1-no-sess")

    # Confirm no session exists before command
    diag = get_station_session_diagnostic(db, tenant_id=_TENANT_ID, station_id=_STATION)
    assert diag.readiness == SessionReadiness.NO_ACTIVE_SESSION

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        start_operation(
            db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID
        )


# ---------------------------------------------------------------------------
# CMD-T2: start_operation unchanged — with OPEN StationSession
# ---------------------------------------------------------------------------

def test_start_operation_unchanged_with_open_session(cmd_fixture):
    """CMD-T2: start_operation succeeds (same outcome) when OPEN StationSession exists."""
    db = cmd_fixture
    op = _seed_planned_op(db, "t2-with-sess")

    _ensure_open_station_session(db)

    diag = get_station_session_diagnostic(db, tenant_id=_TENANT_ID, station_id=_STATION)
    assert diag.readiness == SessionReadiness.OPEN

    detail = start_operation(
        db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID
    )
    # Outcome is identical regardless of session presence
    assert detail.status == StatusEnum.in_progress.value


# ---------------------------------------------------------------------------
# CMD-T3: pause_operation unchanged — no StationSession
# ---------------------------------------------------------------------------

def test_pause_operation_requires_session(cmd_fixture):
    """CMD-T3: pause_operation rejects when no StationSession exists."""
    db = cmd_fixture
    op = _seed_planned_op(db, "t3-no-sess")
    op.status = StatusEnum.in_progress.value
    db.add(op)
    db.commit()

    diag = get_station_session_diagnostic(db, tenant_id=_TENANT_ID, station_id=_STATION)
    assert diag.readiness == SessionReadiness.NO_ACTIVE_SESSION

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        pause_operation(
            db,
            op,
            OperationPauseRequest(reason_code=None, note=None),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# CMD-T4: pause_operation unchanged — with OPEN StationSession
# ---------------------------------------------------------------------------

def test_pause_operation_unchanged_with_open_session(cmd_fixture):
    """CMD-T4: pause_operation succeeds (same outcome) when OPEN StationSession exists."""
    db = cmd_fixture
    _ensure_open_station_session(db)
    op = _seed_running_op(db, "t4-with-sess")

    diag = get_station_session_diagnostic(db, tenant_id=_TENANT_ID, station_id=_STATION)
    assert diag.readiness == SessionReadiness.OPEN

    detail = pause_operation(
        db,
        op,
        OperationPauseRequest(reason_code=None, note=None),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    assert detail.status == StatusEnum.paused.value


# ---------------------------------------------------------------------------
# CMD-T5: existing rejection unchanged — start on IN_PROGRESS op
# ---------------------------------------------------------------------------

def test_start_operation_rejection_unchanged_with_no_session(cmd_fixture):
    """CMD-T5: start_operation still rejects IN_PROGRESS operation with same error code."""
    db = cmd_fixture
    _ensure_open_station_session(db)
    # Seed a PLANNED op with no operator_id so no operator-conflict guard fires
    op = _seed_planned_op(db, "t5-reject")
    # Start it (no operator_id avoids the per-operator running check)
    start_operation(db, op, OperationStartRequest(operator_id=None), tenant_id=_TENANT_ID)
    from app.repositories.operation_repository import get_operation_by_id
    op = get_operation_by_id(db, op.id)
    assert op is not None
    assert op.status == StatusEnum.in_progress.value

    # Attempting to start an IN_PROGRESS op must raise the same conflict (unchanged rejection)
    with pytest.raises(StartOperationConflictError):
        start_operation(
            db, op, OperationStartRequest(operator_id=None), tenant_id=_TENANT_ID
        )


# ---------------------------------------------------------------------------
# CMD-T6: diagnostic is accessible from command context
# ---------------------------------------------------------------------------

def test_diagnostic_accessible_from_command_context(cmd_fixture):
    """CMD-T6: Given tenant_id + operation.station_scope_value, diagnostic returns OPEN."""
    db = cmd_fixture
    op = _seed_planned_op(db, "t6-diag")

    # Open a session for the same station
    _ensure_open_station_session(db)

    # The same context that a command has (tenant_id + operation.station_scope_value)
    # can derive diagnostic readiness
    diag = get_station_session_diagnostic(
        db,
        tenant_id=op.tenant_id,
        station_id=op.station_scope_value,
    )
    assert diag.readiness == SessionReadiness.OPEN
    assert diag.session_id is not None


# ---------------------------------------------------------------------------
# CMD-T7: CLOSED session is not active diagnostic context
# ---------------------------------------------------------------------------

def test_closed_session_not_active_context_from_command_context(cmd_fixture):
    """CMD-T7: Only CLOSED sessions present — diagnostic returns NO_ACTIVE_SESSION."""
    db = cmd_fixture
    op = _seed_planned_op(db, "t7-closed-sess")

    session = _ensure_open_station_session(db)
    close_station_session(db, _identity(), session_id=session.session_id)

    diag = get_station_session_diagnostic(
        db,
        tenant_id=op.tenant_id,
        station_id=op.station_scope_value,
    )
    assert diag.readiness == SessionReadiness.NO_ACTIVE_SESSION

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_CLOSED"):
        start_operation(
            db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID
        )


# ---------------------------------------------------------------------------
# CMD-T8: cross-tenant session does not create false positive
# ---------------------------------------------------------------------------

def test_cross_tenant_session_no_false_positive(cmd_fixture):
    """CMD-T8: Session for other tenant does not appear in diagnostic for this tenant."""
    db = cmd_fixture
    op = _seed_planned_op(db, "t8-cross-tenant")

    # Open session for THIS tenant
    _ensure_open_station_session(db)

    # Diagnostic for OTHER tenant must return NO_ACTIVE_SESSION
    diag = get_station_session_diagnostic(
        db,
        tenant_id=_OTHER_TENANT_ID,
        station_id=_STATION,
    )
    assert diag.readiness == SessionReadiness.NO_ACTIVE_SESSION

    # This-tenant command is not affected
    detail = start_operation(
        db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID
    )
    assert detail.status == StatusEnum.in_progress.value


# ---------------------------------------------------------------------------
# CMD-T9: pause rejection unchanged (PauseExecutionConflictError on non-running)
# ---------------------------------------------------------------------------

def test_pause_rejection_unchanged_no_session(cmd_fixture):
    """CMD-T9 (variant): pause on PLANNED op still rejects with same error code."""
    db = cmd_fixture
    _ensure_open_station_session(db)
    op = _seed_planned_op(db, "t9-pause-reject")
    # op is PLANNED — cannot pause

    with pytest.raises(PauseExecutionConflictError):
        pause_operation(
            db,
            op,
            OperationPauseRequest(reason_code=None, note=None),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )
