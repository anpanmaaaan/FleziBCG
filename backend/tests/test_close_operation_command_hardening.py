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
from app.schemas.operation import OperationCloseRequest
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    CloseOperationConflictError,
    close_operation,
)
from app.services.station_session_service import open_station_session

_PREFIX = "TEST-P0C07B"
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
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="p0c07b",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 2, 8, 0, 0),
        planned_end=datetime(2099, 10, 2, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 2, 8, 0, 0),
        planned_end=datetime(2099, 10, 2, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c07b-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
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
                payload={"started_at": datetime(2099, 10, 2, 9, 0, 0).isoformat()},
                tenant_id=_TENANT_ID,
            )
        )
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"completed_at": datetime(2099, 10, 2, 9, 30, 0).isoformat()},
                tenant_id=_TENANT_ID,
            )
        )

    db.commit()
    db.refresh(op)
    return op


def _latest_event(db, operation_id: int) -> ExecutionEvent | None:
    return db.scalar(
        select(ExecutionEvent)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )


def test_close_operation_happy_path_from_completed(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-OK", status=StatusEnum.completed.value)

    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note="close for test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.completed.value
    assert detail.closure_status == ClosureStatusEnum.closed.value
    assert detail.allowed_actions == ["reopen_operation"]


def test_close_operation_rejects_invalid_runtime_state(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-NOT-COMPLETED", status=StatusEnum.in_progress.value)

    with pytest.raises(CloseOperationConflictError, match="STATE_NOT_COMPLETED"):
        close_operation(
            db,
            op,
            OperationCloseRequest(note=None),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_close_operation_rejects_already_closed(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="CLOSE-ALREADY",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(CloseOperationConflictError, match="STATE_ALREADY_CLOSED"):
        close_operation(
            db,
            op,
            OperationCloseRequest(note=None),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_close_operation_rejects_tenant_mismatch(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-TENANT", status=StatusEnum.completed.value)

    with pytest.raises(ValueError, match="does not belong to the requesting tenant"):
        close_operation(
            db,
            op,
            OperationCloseRequest(note=None),
            actor_user_id=_ACTOR,
            tenant_id="other-tenant",
        )


def test_close_operation_emits_expected_close_event(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-EVENT", status=StatusEnum.completed.value)

    close_operation(
        db,
        op,
        OperationCloseRequest(note="event check"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    last = _latest_event(db, op.id)
    assert last is not None
    assert last.event_type == ExecutionEventType.OPERATION_CLOSED_AT_STATION.value
    assert last.payload.get("actor_user_id") == _ACTOR
    assert "closed_at" in last.payload


def test_close_operation_sets_closure_status_closed(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-STATUS", status=StatusEnum.completed.value)

    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note=None),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.closed.value
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    assert db_op.closure_status == ClosureStatusEnum.closed.value


def test_close_operation_projection_detail_consistency_after_close(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-PROJ", status=StatusEnum.completed.value)

    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note=None),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.completed.value
    assert detail.closure_status == ClosureStatusEnum.closed.value
    assert detail.last_closed_by == _ACTOR
    assert detail.last_closed_at is not None


def test_close_operation_allowed_actions_after_close_backend_derived(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-ACTIONS", status=StatusEnum.completed.value)

    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note=None),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.allowed_actions == ["reopen_operation"]


def test_close_operation_without_station_session_is_allowed(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-NO-SESSION", status=StatusEnum.completed.value)

    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note=None),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.closed.value


def test_close_operation_with_open_station_session_parity(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSE-OPEN-SESSION", status=StatusEnum.completed.value)

    _seed_station_scope(db, user_id=_ACTOR, station_id=_STATION)
    session = open_station_session(
        db,
        identity=_identity(),
        station_id=_STATION,
    )
    assert session.status == "OPEN"

    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note="session parity"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.closed.value
    assert detail.allowed_actions == ["reopen_operation"]
