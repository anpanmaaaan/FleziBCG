from __future__ import annotations

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.execution import ExecutionEvent
from app.models.master import (
    ClosureStatusEnum,
    Operation,
    ProductionOrder,
    StatusEnum,
    WorkOrder,
)
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.security_event import SecurityEventLog
from app.models.station_session import StationSession
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.station_session_service import open_station_session

_PREFIX = "TEST-SS-CLOSE-API"
_TENANT_ID = "default"
_ACTOR = f"{_PREFIX}-ACTOR"
_STATION = f"{_PREFIX}-STATION"

client = TestClient(app)


def _identity() -> RequestIdentity:
    return RequestIdentity(
        user_id=_ACTOR,
        username=_ACTOR,
        email=None,
        tenant_id=_TENANT_ID,
        role_code="OPR",
        acting_role_code=None,
        is_authenticated=True,
        session_id=f"{_PREFIX}-AUTH-SESSION",
    )


@pytest.fixture(autouse=True)
def override_auth_identity():
    app.dependency_overrides[require_authenticated_identity] = _identity
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_authenticated_identity, None)


def _ensure_opr_role(db) -> Role:
    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is not None:
        return role
    role = Role(code="OPR", name="Operator", role_type="system", is_system=True)
    db.add(role)
    db.flush()
    return role


def _seed_station_scope(db) -> None:
    role = _ensure_opr_role(db)
    scope = Scope(
        tenant_id=_TENANT_ID,
        scope_type="station",
        scope_value=_STATION,
    )
    db.add(scope)
    db.flush()
    db.add(
        UserRoleAssignment(
            user_id=_ACTOR,
            role_id=role.id,
            scope_id=scope.id,
            is_primary=True,
            is_active=True,
        )
    )
    db.commit()


def _seed_operation(db, *, status: str) -> Operation:
    production_order = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{status}",
        route_id=f"{_PREFIX}-R-{status}",
        product_name="station-session-close-api",
        quantity=5,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(production_order)
    db.flush()

    work_order = WorkOrder(
        production_order_id=production_order.id,
        work_order_number=f"{_PREFIX}-WO-{status}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(work_order)
    db.flush()

    operation = Operation(
        operation_number=f"{_PREFIX}-OP-{status}",
        name=f"station-session-close-api-{status.lower()}",
        sequence=10,
        work_order_id=work_order.id,
        tenant_id=_TENANT_ID,
        status=status,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=_STATION,
        quantity=5,
    )
    db.add(operation)
    db.commit()
    db.refresh(operation)
    return operation


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
                db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
                db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    db.execute(
        delete(SecurityEventLog).where(
            SecurityEventLog.actor_user_id.like(f"{_PREFIX}%")
        )
    )
    db.execute(
        delete(StationSession).where(
            StationSession.tenant_id == _TENANT_ID,
            StationSession.station_id == _STATION,
        )
    )
    db.execute(
        delete(UserRoleAssignment).where(UserRoleAssignment.user_id.like(f"{_PREFIX}%"))
    )
    db.execute(
        delete(Scope).where(
            Scope.tenant_id == _TENANT_ID,
            Scope.scope_type == "station",
            Scope.scope_value == _STATION,
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


def _closed_event_count(db, session_id: str) -> int:
    return len(
        list(
            db.scalars(
                select(SecurityEventLog.id).where(
                    SecurityEventLog.resource_type == "station_session",
                    SecurityEventLog.resource_id == session_id,
                    SecurityEventLog.event_type == "STATION_SESSION.CLOSED",
                )
            )
        )
    )


def test_close_session_api_rejects_active_execution_without_closing_or_event(
    db_session,
):
    _seed_station_scope(db_session)
    session = open_station_session(db_session, _identity(), station_id=_STATION)
    _seed_operation(db_session, status=StatusEnum.in_progress.value)

    before_closed_events = _closed_event_count(db_session, session.session_id)

    response = client.post(f"/api/v1/station/sessions/{session.session_id}/close")

    assert response.status_code == 409
    assert response.json()["detail"] == "STATION_SESSION_ACTIVE_EXECUTION"
    assert _closed_event_count(db_session, session.session_id) == before_closed_events

    db_session.expire_all()
    current = db_session.get(StationSession, session.session_id)
    assert current is not None
    assert current.status == "OPEN"
    assert current.closed_at is None


def test_close_session_api_succeeds_without_active_execution_and_emits_closed_event(
    db_session,
):
    _seed_station_scope(db_session)
    session = open_station_session(db_session, _identity(), station_id=_STATION)

    response = client.post(f"/api/v1/station/sessions/{session.session_id}/close")

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session.session_id
    assert payload["status"] == "CLOSED"
    assert payload["closed_at"] is not None
    assert _closed_event_count(db_session, session.session_id) == 1

    db_session.expire_all()
    current = db_session.get(StationSession, session.session_id)
    assert current is not None
    assert current.status == "CLOSED"
    assert current.closed_at is not None
