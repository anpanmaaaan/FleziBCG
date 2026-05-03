"""
P0-C-04C Diagnostic Session Context Bridge Tests.

Behavior contract:
- Missing StationSession produces diagnostic readiness signal.
- Missing StationSession now rejects guarded execution commands.
- Matching OPEN StationSession preserves normal command outcomes.
- Diagnostic output is backend-derived (tenant_id + station_scope_value from
  verified context, not from user input).
- No new domain events are introduced in this slice.
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
from app.schemas.operation import OperationStartRequest
from app.security.dependencies import RequestIdentity
from app.services.operation_service import StationSessionGuardError, start_operation
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

_PREFIX = "TEST-BRIDGE"
_TENANT_ID = "default"
_OTHER_TENANT_ID = "bridge-tenant-b"
_STATION = f"{_PREFIX}-STATION-01"
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


def _purge_sessions(db) -> None:
    db.execute(
        delete(StationSession).where(
            StationSession.station_id == _STATION,
            StationSession.tenant_id.in_([_TENANT_ID, _OTHER_TENANT_ID]),
        )
    )


def _purge_rbac(db) -> None:
    db.execute(
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id == _ACTOR
        )
    )
    db.execute(
        delete(Scope).where(
            Scope.scope_value == _STATION,
            Scope.tenant_id.in_([_TENANT_ID, _OTHER_TENANT_ID]),
        )
    )


def _purge_operations(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if not po_ids:
        return
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


def _purge(db) -> None:
    _purge_sessions(db)
    _purge_rbac(db)
    _purge_operations(db)
    db.commit()


def _seed_station_scope(db, tenant_id: str = _TENANT_ID) -> Scope:
    opr_role = _ensure_opr_role(db)
    scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == tenant_id,
            Scope.scope_type == "station",
            Scope.scope_value == _STATION,
        )
    )
    if scope is None:
        scope = Scope(
            tenant_id=tenant_id,
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
    return scope


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


def _seed_operation(db, suffix: str = "01") -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="bridge test product",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()
    wo = WorkOrder(
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        production_order_id=po.id,
        tenant_id=_TENANT_ID,
        status=StatusEnum.planned.value,
    )
    db.add(wo)
    db.flush()
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="Bridge Test Operation",
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


@pytest.fixture
def bridge_fixture():
    """Combined fixture: DB initialised, RBAC seeded, cleanup guaranteed."""
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        _seed_station_scope(db)
        yield db
    finally:
        db.rollback()
        _purge(db)
        db.close()


# ---------------------------------------------------------------------------
# Diagnostic detection tests
# ---------------------------------------------------------------------------


def test_diagnostic_no_active_session_returns_no_active_session(bridge_fixture):
    """BRIDGE-T4: diagnostic detects missing session."""
    db = bridge_fixture

    result = get_station_session_diagnostic(
        db,
        tenant_id=_TENANT_ID,
        station_id=_STATION,
    )

    assert result.readiness == SessionReadiness.NO_ACTIVE_SESSION
    assert result.session_id is None
    assert result.operator_user_id is None


def test_diagnostic_open_session_returns_open(bridge_fixture):
    """BRIDGE-T3: diagnostic detects matching OPEN session."""
    db = bridge_fixture

    session = open_station_session(db, _identity(), station_id=_STATION)

    result = get_station_session_diagnostic(
        db,
        tenant_id=_TENANT_ID,
        station_id=_STATION,
    )

    assert result.readiness == SessionReadiness.OPEN
    assert result.session_id == session.session_id


def test_diagnostic_closed_session_treated_as_no_active_session(bridge_fixture):
    """BRIDGE-T5: diagnostic ignores CLOSED session — returns NO_ACTIVE_SESSION."""
    db = bridge_fixture

    session = open_station_session(db, _identity(), station_id=_STATION)
    close_station_session(db, _identity(), session_id=session.session_id)

    result = get_station_session_diagnostic(
        db,
        tenant_id=_TENANT_ID,
        station_id=_STATION,
    )

    assert result.readiness == SessionReadiness.NO_ACTIVE_SESSION
    assert result.session_id is None


def test_diagnostic_tenant_mismatch_no_false_positive(bridge_fixture):
    """BRIDGE-T6: session for one tenant does not appear for another tenant."""
    db = bridge_fixture

    # Open a session for the test tenant
    open_station_session(db, _identity(), station_id=_STATION)

    # Diagnostic query for a different tenant should find nothing
    result = get_station_session_diagnostic(
        db,
        tenant_id=_OTHER_TENANT_ID,
        station_id=_STATION,
    )

    assert result.readiness == SessionReadiness.NO_ACTIVE_SESSION
    assert result.session_id is None


# ---------------------------------------------------------------------------
# Command behavior-unchanged tests
# ---------------------------------------------------------------------------


def test_start_operation_requires_session(bridge_fixture):
    """BRIDGE-T1: start_operation rejects when no StationSession exists."""
    db = bridge_fixture
    op = _seed_operation(db, suffix="no-session")

    # Verify no session exists
    diagnostic = get_station_session_diagnostic(
        db, tenant_id=_TENANT_ID, station_id=_STATION
    )
    assert diagnostic.readiness == SessionReadiness.NO_ACTIVE_SESSION

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        start_operation(
            db,
            op,
            OperationStartRequest(operator_id=_ACTOR, started_at=None),
            tenant_id=_TENANT_ID,
        )


def test_start_operation_proceeds_with_open_session(bridge_fixture):
    """BRIDGE-T2: start_operation succeeds when a matching OPEN StationSession exists."""
    db = bridge_fixture
    op = _seed_operation(db, suffix="with-session")

    _ensure_open_station_session(db)

    diagnostic = get_station_session_diagnostic(
        db, tenant_id=_TENANT_ID, station_id=_STATION
    )
    assert diagnostic.readiness == SessionReadiness.OPEN

    # Command outcome identical to no-session case
    detail = start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR, started_at=None),
        tenant_id=_TENANT_ID,
    )
    assert detail.status == StatusEnum.in_progress.value


def test_diagnostic_result_has_operator_context_when_identified(bridge_fixture):
    """Diagnostic returns operator_user_id when session has an identified operator."""
    db = bridge_fixture

    from app.services.station_session_service import identify_operator_at_station

    session = open_station_session(db, _identity(), station_id=_STATION)
    # Seed operator scope so identify works
    opr_role = _ensure_opr_role(db)
    # Reuse existing scope for _ACTOR as operator (simplification)
    scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == _TENANT_ID,
            Scope.scope_value == _STATION,
        )
    )
    # _ACTOR already has scope; use _ACTOR as operator too
    identify_operator_at_station(
        db, _identity(), session_id=session.session_id, operator_user_id=_ACTOR
    )

    result = get_station_session_diagnostic(
        db, tenant_id=_TENANT_ID, station_id=_STATION
    )

    assert result.readiness == SessionReadiness.OPEN
    assert result.operator_user_id == _ACTOR
