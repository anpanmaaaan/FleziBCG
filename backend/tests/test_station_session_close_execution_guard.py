"""
P0-C-SESSION-RECOVERY-02 — Close Station Session Active Execution Guard

Covers SS-CLOSE-001: close_station_session must reject if active non-terminal
execution work exists under the station's scope.

Active blocker states: IN_PROGRESS, PAUSED, BLOCKED (with open downtime).
Error: StationSessionConflictError("STATION_SESSION_ACTIVE_EXECUTION") → HTTP 409.

Tests:
  T01 test_close_rejects_when_operation_is_in_progress
  T02 test_close_rejects_when_operation_is_paused
  T03 test_close_succeeds_when_no_active_execution
  T04 test_close_succeeds_after_operation_completed
  T05 test_close_rejects_wrong_scope_still_enforced
  T06 test_close_succeeds_after_open_downtime_resolves
  T07 test_start_operation_regression_session_guard_still_rejects_without_session
"""
from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import (
    ClosureStatusEnum,
    Operation,
    ProductionOrder,
    StatusEnum,
    WorkOrder,
)
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.schemas.operation import (
    OperationCompleteRequest,
    OperationPauseRequest,
    OperationStartRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    StationSessionGuardError,
    complete_operation,
    pause_operation,
    start_operation,
)
from app.services.station_session_service import (
    StationSessionConflictError,
    close_station_session,
    open_station_session,
)

_PREFIX = "TEST-P0C-SR02"
_TENANT_ID = "default"
_STATION = f"{_PREFIX}-STATION"
_ACTOR = f"{_PREFIX}-ACTOR"
_STRANGER = f"{_PREFIX}-STRANGER"  # no station scope


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


def _seed_station_scope(db, *, user_id: str, station_id: str = _STATION) -> Scope:
    role = _ensure_opr_role(db)
    scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == _TENANT_ID,
            Scope.scope_type == "station",
            Scope.scope_value == station_id,
        )
    )
    if scope is None:
        scope = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=station_id,
        )
        db.add(scope)
        db.flush()

    exists = db.scalar(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == role.id,
            UserRoleAssignment.scope_id == scope.id,
        )
    )
    if exists is None:
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
    return scope


def _seed_planned_operation(db, *, suffix: str) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="p0-sr02",
        quantity=5,
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
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name=f"sr02-op-{suffix}",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=_STATION,
        quantity=5,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


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
                db.scalars(
                    select(Operation.id).where(Operation.work_order_id.in_(wo_ids))
                )
            )
            if op_ids:
                db.execute(
                    delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids))
                )
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
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id.like(f"{_PREFIX}%")
        )
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
        _purge(db)
        db.close()


# ── T01 ─────────────────────────────────────────────────────────────────────
def test_close_rejects_when_operation_is_in_progress(db_session):
    """T01: SS-CLOSE-001 — close is rejected while an IN_PROGRESS operation exists."""
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(), station_id=_STATION)

    op = _seed_planned_operation(db, suffix="IN-PROG")
    start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    with pytest.raises(StationSessionConflictError, match="STATION_SESSION_ACTIVE_EXECUTION"):
        close_station_session(db, _identity(), session_id=session.session_id)


# ── T02 ─────────────────────────────────────────────────────────────────────
def test_close_rejects_when_operation_is_paused(db_session):
    """T02: SS-CLOSE-001 — close is rejected while a PAUSED (non-terminal) operation exists.
    PAUSED is a non-terminal state: operator must resume and complete before closing session.
    """
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(), station_id=_STATION)

    op = _seed_planned_operation(db, suffix="PAUSED")
    start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    # Reload op after start (status updated in-place)
    db.expire(op)
    db.refresh(op)

    pause_operation(
        db,
        op,
        OperationPauseRequest(reason="test pause"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    with pytest.raises(StationSessionConflictError, match="STATION_SESSION_ACTIVE_EXECUTION"):
        close_station_session(db, _identity(), session_id=session.session_id)


# ── T03 ─────────────────────────────────────────────────────────────────────
def test_close_succeeds_when_no_active_execution(db_session):
    """T03: Close succeeds when no active execution exists under the station."""
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(), station_id=_STATION)

    # No operations seeded for this station — clean state
    result = close_station_session(db, _identity(), session_id=session.session_id)

    assert result.status == "CLOSED"
    assert result.closed_at is not None


# ── T04 ─────────────────────────────────────────────────────────────────────
def test_close_succeeds_after_operation_completed(db_session):
    """T04: Close succeeds after in-progress operation is completed (terminal state)."""
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(), station_id=_STATION)

    op = _seed_planned_operation(db, suffix="COMPLETE-OK")
    start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    db.expire(op)
    db.refresh(op)

    complete_operation(
        db,
        op,
        OperationCompleteRequest(quantity_produced=5),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    # Now COMPLETED — no active blocker
    result = close_station_session(db, _identity(), session_id=session.session_id)

    assert result.status == "CLOSED"
    assert result.closed_at is not None


# ── T05 ─────────────────────────────────────────────────────────────────────
def test_close_rejects_wrong_scope_still_enforced(db_session):
    """T05: The scope guard still fires before the active execution check.
    _STRANGER has no station scope — must get PermissionError, not ConflictError.
    """
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(), station_id=_STATION)

    with pytest.raises(PermissionError, match="outside your station scope"):
        close_station_session(db, _identity(_STRANGER), session_id=session.session_id)


# ── T06 ─────────────────────────────────────────────────────────────────────
def test_close_succeeds_after_open_downtime_resolves(db_session):
    """T06: After completing an operation (which implies downtime is resolved),
    close session succeeds. This validates the BLOCKED status path indirectly:
    a COMPLETED operation is terminal and does not block closure.
    """
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(), station_id=_STATION)

    op = _seed_planned_operation(db, suffix="DT-RESOLVE")
    start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    db.expire(op)
    db.refresh(op)

    complete_operation(
        db,
        op,
        OperationCompleteRequest(quantity_produced=5),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    # No more active blockers — close must succeed
    result = close_station_session(db, _identity(), session_id=session.session_id)
    assert result.status == "CLOSED"


# ── T07 ─────────────────────────────────────────────────────────────────────
def test_start_operation_regression_session_guard_still_rejects_without_session(db_session):
    """T07: Regression — INV-004 session guard on start_operation is unchanged.
    start_operation must still reject if no open station session exists.
    """
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    # No session opened
    op = _seed_planned_operation(db, suffix="REG-NO-SESSION")

    with pytest.raises(StationSessionGuardError):
        start_operation(
            db,
            op,
            OperationStartRequest(operator_id=_ACTOR),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )
