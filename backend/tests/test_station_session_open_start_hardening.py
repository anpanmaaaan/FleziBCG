"""
P0-C-SESSION-RECOVERY-01B — Station Session Open/Start Hardening Tests

Covers:
  T01 test_open_station_session_authorized_user_success
  T02 test_open_station_session_rejects_wrong_scope
  T03 test_open_station_session_rejects_operator_spoofing_if_payload_exists
  T04 test_start_operation_after_open_station_session_success
  T05 test_start_operation_rejects_without_valid_station_session
  T06 test_close_station_session_rejects_running_execution_if_policy_exists
       [P1 GAP — current policy does not enforce this; test documents the gap]
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
from app.schemas.operation import OperationStartRequest
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    StationSessionGuardError,
    start_operation,
)
from app.services.station_session_service import (
    StationSessionConflictError,
    close_station_session,
    open_station_session,
)

_PREFIX = "TEST-P0C-SR01B"
_TENANT_ID = "default"
_STATION = f"{_PREFIX}-STATION"
_ACTOR = f"{_PREFIX}-ACTOR"
_OTHER_ACTOR = f"{_PREFIX}-OTHER"  # eligible for station but different from _ACTOR
_STRANGER = f"{_PREFIX}-STRANGER"  # no station scope at all


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
        product_name="p0-sr01b",
        quantity=5,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 8, 1, 8, 0, 0),
        planned_end=datetime(2099, 8, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()
    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 8, 1, 8, 0, 0),
        planned_end=datetime(2099, 8, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name=f"sr01b-op-{suffix}",
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
def test_open_station_session_authorized_user_success(db_session):
    """T01: Actor with station scope opens session.
    Backend auto-derives operator from identity (BT-AGG-002).
    """
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)

    session = open_station_session(db, _identity(_ACTOR), station_id=_STATION)

    assert session.status == "OPEN"
    assert session.station_id == _STATION
    assert session.tenant_id == _TENANT_ID
    assert session.operator_user_id == _ACTOR  # auto-derived from identity


# ── T02 ─────────────────────────────────────────────────────────────────────
def test_open_station_session_rejects_wrong_scope(db_session):
    """T02: Actor with NO station scope is rejected (SS-OPEN-001 guard)."""
    db = db_session
    # _STRANGER has no station scope assignment

    with pytest.raises(PermissionError, match="outside your station scope"):
        open_station_session(db, _identity(_STRANGER), station_id=_STATION)


# ── T03 ─────────────────────────────────────────────────────────────────────
def test_open_station_session_rejects_operator_spoofing_if_payload_exists(db_session):
    """T03: Actor provides a different user as operator_user_id — spoofing rejected.
    Spoofing guard: operator_user_id must equal identity.user_id when provided.
    """
    from app.schemas.station_session import OpenStationSessionRequest

    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    _seed_station_scope(db, user_id=_OTHER_ACTOR)  # other actor eligible for station

    spoofed_payload = OpenStationSessionRequest(
        station_id=_STATION,
        operator_user_id=_OTHER_ACTOR,  # actor tries to open session as a different user
    )

    with pytest.raises(
        PermissionError,
        match="operator_user_id must match the authenticated user",
    ):
        open_station_session(
            db,
            _identity(_ACTOR),  # authenticated as _ACTOR
            station_id=_STATION,
            payload=spoofed_payload,
        )


# ── T04 ─────────────────────────────────────────────────────────────────────
def test_start_operation_after_open_station_session_success(db_session):
    """T04: Start operation succeeds after a valid open station session exists.
    After session.operator_user_id == actor, ensure_open_station_session_for_command
    passes and execution starts normally.
    """
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(_ACTOR), station_id=_STATION)
    assert session.operator_user_id == _ACTOR

    op = _seed_planned_operation(db, suffix="START-OK")

    detail = start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.in_progress.value
    assert "report_production" in detail.allowed_actions
    assert "pause_execution" in detail.allowed_actions


# ── T05 ─────────────────────────────────────────────────────────────────────
def test_start_operation_rejects_without_valid_station_session(db_session):
    """T05: Start operation is rejected when no open station session exists (INV-004)."""
    db = db_session
    # No station session opened — station scope exists but no session
    _seed_station_scope(db, user_id=_ACTOR)
    op = _seed_planned_operation(db, suffix="NO-SESSION")

    with pytest.raises(StationSessionGuardError):
        start_operation(
            db,
            op,
            OperationStartRequest(operator_id=_ACTOR),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ── T06 ─────────────────────────────────────────────────────────────────────
def test_close_station_session_rejects_running_execution_if_policy_exists(db_session):
    """T06: SS-CLOSE-001 guard — close_station_session rejects when a running execution
    exists under the session's station. Guard implemented in P0-C-SESSION-RECOVERY-02.
    """
    db = db_session
    _seed_station_scope(db, user_id=_ACTOR)
    session = open_station_session(db, _identity(_ACTOR), station_id=_STATION)

    op = _seed_planned_operation(db, suffix="CLOSE-GUARD")
    start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    # SS-CLOSE-001: must reject while active execution exists
    with pytest.raises(StationSessionConflictError, match="STATION_SESSION_ACTIVE_EXECUTION"):
        close_station_session(db, _identity(_ACTOR), session_id=session.session_id)
