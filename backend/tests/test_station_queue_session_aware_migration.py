"""
08D station queue migration tests.

These tests lock session-aware control fields while preserving
queue compatibility shape.
"""

from __future__ import annotations

from datetime import datetime

import test_station_queue_active_states as legacy_queue
from test_station_queue_active_states import station_queue_fixture  # noqa: F401

import pytest
from sqlalchemy import delete, select

from app.services.station_queue_service import get_station_queue
from app.services.station_session_service import (
    StationSessionConflictError,
    close_station_session,
    get_current_station_session,
    open_station_session,
)


def test_station_queue_includes_session_ownership_summary(station_queue_fixture):
    db, ops = station_queue_fixture

    scope_value, items = get_station_queue(db, legacy_queue._identity())
    assert scope_value == legacy_queue._STATION_SCOPE_VALUE

    by_id = legacy_queue._items_by_op_id(items)
    ownership = by_id[ops["planned"].id]["ownership"]

    assert ownership["target_owner_type"] == "station_session"
    assert ownership["has_open_session"] is True
    assert ownership["station_id"] == legacy_queue._STATION_SCOPE_VALUE
    assert ownership["session_status"] == "OPEN"
    assert ownership["operator_user_id"] == legacy_queue._USER_ID
    assert ownership["owner_state"] == "mine"
    assert ownership["session_id"] is not None


def test_station_queue_ownership_summary_handles_no_open_session(station_queue_fixture):
    db, ops = station_queue_fixture

    identity = legacy_queue._identity()
    session = get_current_station_session(
        db,
        identity,
        station_id=legacy_queue._STATION_SCOPE_VALUE,
    )
    assert session is not None
    # SS-CLOSE-001: close must be rejected while IN_PROGRESS/PAUSED/BLOCKED
    # operations exist under this station. The fixture seeds all three.
    with pytest.raises(StationSessionConflictError, match="STATION_SESSION_ACTIVE_EXECUTION"):
        close_station_session(db, identity, session_id=session.session_id)


# ── "no session" queue ownership shape ───────────────────────────────────────
# Uses a fresh minimal station (PLANNED ops only — no active execution) so the
# session can be legitimately closed, then verifies the queue ownership shape.
_PREFIX_NS = "TEST-QSA-NOSESS"
_STATION_NS = f"{_PREFIX_NS}-STATION"
_USER_NS = f"{_PREFIX_NS}-USER"
_TENANT_NS = "default"


def _setup_no_session_station(db):
    from app.db.init_db import init_db
    from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
    from app.models.rbac import Role, Scope, UserRoleAssignment
    from app.models.station_session import StationSession

    init_db()

    # purge any leftover data from previous runs
    db.execute(
        delete(StationSession).where(
            StationSession.tenant_id == _TENANT_NS,
            StationSession.station_id == _STATION_NS,
        )
    )
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX_NS}-%")
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
                db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.execute(delete(UserRoleAssignment).where(UserRoleAssignment.user_id == _USER_NS))
    db.execute(
        delete(Scope).where(
            Scope.scope_value == _STATION_NS, Scope.tenant_id == _TENANT_NS
        )
    )
    db.commit()

    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is None:
        role = Role(code="OPR", name="Operator", role_type="system", is_system=True)
        db.add(role)
        db.flush()

    scope = Scope(tenant_id=_TENANT_NS, scope_type="station", scope_value=_STATION_NS)
    db.add(scope)
    db.flush()
    db.add(UserRoleAssignment(user_id=_USER_NS, role_id=role.id, scope_id=scope.id, is_primary=True, is_active=True))

    po = ProductionOrder(
        order_number=f"{_PREFIX_NS}-PO-001",
        route_id=f"{_PREFIX_NS}-R-01",
        product_name="ns-test",
        quantity=1,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 1, 8, 0, 0),
        planned_end=datetime(2099, 10, 1, 17, 0, 0),
        tenant_id=_TENANT_NS,
    )
    db.add(po)
    db.flush()
    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX_NS}-WO-001",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 1, 8, 0, 0),
        planned_end=datetime(2099, 10, 1, 17, 0, 0),
        tenant_id=_TENANT_NS,
    )
    db.add(wo)
    db.flush()
    op = Operation(
        operation_number=f"{_PREFIX_NS}-OP-001",
        name="ns-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_NS,
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=_STATION_NS,
        quantity=1,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def test_station_queue_ownership_shows_none_state_without_session():
    """Queue ownership block shows has_open_session=False and owner_state=none
    when no station session exists. Uses a minimal station with only PLANNED ops
    (no active execution) so close_station_session legitimately succeeds.
    """
    from app.db.session import SessionLocal
    from app.security.dependencies import RequestIdentity

    identity = RequestIdentity(
        user_id=_USER_NS,
        username=_USER_NS,
        email=None,
        tenant_id=_TENANT_NS,
        role_code="OPR",
        is_authenticated=True,
    )
    db = SessionLocal()
    try:
        op = _setup_no_session_station(db)

        # Open session then close it (no active execution — succeeds per SS-CLOSE-001)
        session = open_station_session(db, identity, station_id=_STATION_NS)
        assert session.status == "OPEN"
        closed = close_station_session(db, identity, session_id=session.session_id)
        assert closed.status == "CLOSED"

        # Now query queue — no open session should exist
        _, items = get_station_queue(db, identity)
        by_id = {item["operation_id"]: item for item in items}
        ownership = by_id[op.id]["ownership"]

        assert ownership["target_owner_type"] == "station_session"
        assert ownership["has_open_session"] is False
        assert ownership["session_id"] is None
        assert ownership["station_id"] is None
        assert ownership["session_status"] is None
        assert ownership["operator_user_id"] is None
        assert ownership["owner_state"] == "none"
    finally:
        _setup_no_session_station(db)  # purge
        db.close()
