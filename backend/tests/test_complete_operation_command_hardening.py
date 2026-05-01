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
from app.schemas.operation import OperationCompleteRequest, OperationStartRequest
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    ClosedRecordConflictError,
    CompleteOperationConflictError,
    complete_operation,
    StationSessionGuardError,
    start_operation,
)
from app.services.station_session_service import (
    close_station_session,
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

_PREFIX = "TEST-P0C07A"
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

    assignment = db.scalar(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == role.id,
            UserRoleAssignment.scope_id == scope.id,
        )
    )
    if assignment is None:
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


def _ensure_open_station_session(
    db,
    *,
    user_id: str = _ACTOR,
    station_id: str = _STATION,
) -> StationSession:
    _seed_station_scope(db, user_id=user_id, station_id=station_id)
    identity = _identity(user_id=user_id)
    session = get_current_station_session(db, identity, station_id=station_id)
    if session is None:
        session = open_station_session(db, identity, station_id=station_id)
    if session.operator_user_id != user_id:
        session = identify_operator_at_station(
            db,
            identity,
            session_id=session.session_id,
            operator_user_id=user_id,
        )
    return session


def _close_open_station_session(
    db,
    *,
    user_id: str = _ACTOR,
    station_id: str = _STATION,
) -> None:
    identity = _identity(user_id=user_id)
    session = get_current_station_session(db, identity, station_id=station_id)
    if session is not None:
        close_station_session(db, identity, session_id=session.session_id)


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
        product_name="p0c07a",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 1, 8, 0, 0),
        planned_end=datetime(2099, 10, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 10, 1, 8, 0, 0),
        planned_end=datetime(2099, 10, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c07a-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        status=status,
        closure_status=closure_status,
        station_scope_value=station_scope_value,
        quantity=10,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def _seed_in_progress_operation(db, *, suffix: str, station_scope_value: str = _STATION) -> Operation:
    _ensure_open_station_session(db, station_id=station_scope_value)
    op = _seed_operation(db, suffix=suffix, status=StatusEnum.planned.value, station_scope_value=station_scope_value)
    start_operation(db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID)
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    assert db_op.status == StatusEnum.in_progress.value
    return db_op


def _latest_event(db, operation_id: int) -> ExecutionEvent | None:
    return db.scalar(
        select(ExecutionEvent)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )


def test_complete_operation_happy_path_from_in_progress(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="COMPLETE-OK")

    detail = complete_operation(
        db,
        op,
        OperationCompleteRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.completed.value
    assert detail.closure_status == ClosureStatusEnum.open.value
    assert detail.allowed_actions == ["close_operation"]
    assert detail.downtime_open is False


def test_complete_operation_rejects_invalid_runtime_state(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(db, suffix="COMPLETE-PLANNED", status=StatusEnum.planned.value)

    with pytest.raises(CompleteOperationConflictError, match="IN_PROGRESS"):
        complete_operation(
            db,
            op,
            OperationCompleteRequest(operator_id=_ACTOR),
            tenant_id=_TENANT_ID,
        )


def test_complete_operation_rejects_already_completed(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(db, suffix="COMPLETE-ALREADY", status=StatusEnum.completed.value)

    with pytest.raises(CompleteOperationConflictError, match="already completed"):
        complete_operation(
            db,
            op,
            OperationCompleteRequest(operator_id=_ACTOR),
            tenant_id=_TENANT_ID,
        )


def test_complete_operation_rejects_closed_record(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(
        db,
        suffix="COMPLETE-CLOSED",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        complete_operation(
            db,
            op,
            OperationCompleteRequest(operator_id=_ACTOR),
            tenant_id=_TENANT_ID,
        )


def test_complete_operation_rejects_tenant_mismatch(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="COMPLETE-TENANT")

    with pytest.raises(ValueError, match="does not belong to the requesting tenant"):
        complete_operation(
            db,
            op,
            OperationCompleteRequest(operator_id=_ACTOR),
            tenant_id="other-tenant",
        )


def test_complete_operation_emits_op_completed_event(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="COMPLETE-EVENT")

    complete_operation(
        db,
        op,
        OperationCompleteRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    last = _latest_event(db, op.id)
    assert last is not None
    assert last.event_type == ExecutionEventType.OP_COMPLETED.value
    assert last.payload.get("operator_id") == _ACTOR
    assert "completed_at" in last.payload


def test_complete_operation_projection_after_complete_is_event_derived_completed(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="COMPLETE-PROJ")

    detail = complete_operation(
        db,
        op,
        OperationCompleteRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    assert db_op.status == StatusEnum.completed.value
    assert detail.status == StatusEnum.completed.value


def test_complete_operation_allowed_actions_after_complete_backend_derived(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="COMPLETE-ACTIONS")

    detail = complete_operation(
        db,
        op,
        OperationCompleteRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    assert detail.allowed_actions == ["close_operation"]


def test_complete_operation_without_station_session_rejects(db_session):
    db = db_session
    op = _seed_operation(db, suffix="COMPLETE-NO-SESSION", status=StatusEnum.in_progress.value)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        complete_operation(
            db,
            op,
            OperationCompleteRequest(operator_id=_ACTOR),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_complete_operation_with_open_station_session_parity(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="COMPLETE-OPEN-SESSION")

    session = _ensure_open_station_session(db)
    assert session.status == "OPEN"

    detail = complete_operation(
        db,
        op,
        OperationCompleteRequest(operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.completed.value
    assert detail.allowed_actions == ["close_operation"]
