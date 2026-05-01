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
from app.schemas.operation import (
    OperationCloseRequest,
    OperationPauseRequest,
    OperationReopenRequest,
    OperationResumeRequest,
)
from app.services.operation_service import (
    CloseOperationConflictError,
    ClosedRecordConflictError,
    ReopenOperationConflictError,
    close_operation,
    derive_operation_detail,
    pause_operation,
    reopen_operation,
    resume_operation,
)
from app.security.dependencies import RequestIdentity
from app.services.station_session_service import (
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

_PREFIX = "TEST-CLOSE-REOPEN"
_TENANT_ID = "default"


def _identity(user_id: str) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username=user_id,
        email=None,
        tenant_id=_TENANT_ID,
        role_code="OPR",
        is_authenticated=True,
    )


def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if not po_ids:
        db.commit()
        return
    wo_ids = list(
        db.scalars(select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids)))
    )
    if wo_ids:
        op_ids = list(db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids))))
        if op_ids:
            db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
            db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
    db.execute(delete(StationSession).where(StationSession.station_id.like("TEST_CLOSE_REOPEN%")))
    db.execute(delete(UserRoleAssignment).where(UserRoleAssignment.user_id == "opr-001"))
    db.execute(delete(Scope).where(Scope.scope_value.like("TEST_CLOSE_REOPEN%")))
    db.commit()


def _ensure_opr_role(db) -> Role:
    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is not None:
        return role
    role = Role(code="OPR", name="Operator", role_type="system", is_system=True)
    db.add(role)
    db.flush()
    return role


def _ensure_open_station_session(db, *, user_id: str, station_id: str) -> StationSession:
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

    identity = _identity(user_id)
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


def _seed_wo(db, suffix: str) -> WorkOrder:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="close reopen foundation",
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
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    return wo


def _mk_op(
    db,
    wo: WorkOrder,
    *,
    suffix: str,
    status: str,
    closure_status: str,
    station_scope_value: str = "STATION_01",
) -> Operation:
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        work_order_id=wo.id,
        sequence=10,
        name=f"op {suffix}",
        status=status,
        closure_status=closure_status,
        station_scope_value=station_scope_value,
        quantity=10,
        tenant_id=_TENANT_ID,
    )
    db.add(op)
    db.flush()
    return op


def _event_count(db, operation_id: int) -> int:
    return len(
        list(
            db.scalars(
                select(ExecutionEvent.id).where(ExecutionEvent.operation_id == operation_id)
            )
        )
    )


def _event_types(db, operation_id: int) -> list[str]:
    return list(
        db.scalars(
            select(ExecutionEvent.event_type)
            .where(ExecutionEvent.operation_id == operation_id)
            .order_by(ExecutionEvent.id.asc())
        )
    )


def test_close_operation_success_sets_closed_and_appends_event(db_session):
    db = db_session
    wo = _seed_wo(db, "CLOSE-OK")
    op = _mk_op(
        db,
        wo,
        suffix="CLOSE-OK",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.open.value,
    )
    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.OP_STARTED.value,
            production_order_id=wo.production_order_id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"started_at": datetime(2099, 9, 1, 9, 0, 0).isoformat()},
            tenant_id=_TENANT_ID,
        )
    )
    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.OP_COMPLETED.value,
            production_order_id=wo.production_order_id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"completed_at": datetime(2099, 9, 1, 9, 30, 0).isoformat()},
            tenant_id=_TENANT_ID,
        )
    )
    db.commit()

    before_count = _event_count(db, op.id)
    detail = close_operation(
        db,
        op,
        OperationCloseRequest(note="close for station handoff"),
        actor_user_id="sup-001",
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.closed.value
    assert detail.last_closed_by == "sup-001"
    assert detail.last_closed_at is not None
    assert _event_count(db, op.id) == before_count + 1
    assert _event_types(db, op.id)[-1] == ExecutionEventType.OPERATION_CLOSED_AT_STATION.value


def test_close_operation_rejects_already_closed_and_non_completed(db_session):
    db = db_session
    wo = _seed_wo(db, "CLOSE-REJECT")

    closed_op = _mk_op(
        db,
        wo,
        suffix="ALREADY-CLOSED",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(CloseOperationConflictError, match="STATE_ALREADY_CLOSED"):
        close_operation(
            db,
            closed_op,
            OperationCloseRequest(note=None),
            actor_user_id="sup-001",
            tenant_id=_TENANT_ID,
        )

    running_op = _mk_op(
        db,
        wo,
        suffix="NOT-COMPLETED",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.open.value,
    )
    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.OP_STARTED.value,
            production_order_id=wo.production_order_id,
            work_order_id=wo.id,
            operation_id=running_op.id,
            payload={"started_at": datetime(2099, 9, 1, 9, 0, 0).isoformat()},
            tenant_id=_TENANT_ID,
        )
    )
    db.commit()

    with pytest.raises(CloseOperationConflictError, match="STATE_NOT_COMPLETED"):
        close_operation(
            db,
            running_op,
            OperationCloseRequest(note=None),
            actor_user_id="sup-001",
            tenant_id=_TENANT_ID,
        )


def test_reopen_operation_success_updates_metadata_appends_event_and_projects_paused(db_session):
    db = db_session
    wo = _seed_wo(db, "REOPEN-OK")
    op = _mk_op(
        db,
        wo,
        suffix="REOPEN-OK",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value="TEST_CLOSE_REOPEN_STATION",
    )
    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.OP_STARTED.value,
            production_order_id=wo.production_order_id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"started_at": datetime(2099, 9, 1, 9, 0, 0).isoformat()},
            tenant_id=_TENANT_ID,
        )
    )
    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.OP_COMPLETED.value,
            production_order_id=wo.production_order_id,
            work_order_id=wo.id,
            operation_id=op.id,
            payload={"completed_at": datetime(2099, 9, 1, 9, 30, 0).isoformat()},
            tenant_id=_TENANT_ID,
        )
    )
    db.commit()

    closed = close_operation(
        db,
        op,
        OperationCloseRequest(note="close before reopen"),
        actor_user_id="sup-001",
        tenant_id=_TENANT_ID,
    )
    assert closed.closure_status == ClosureStatusEnum.closed.value

    # Closed invariant blocks execution writes while CLOSED.
    _ensure_open_station_session(db, user_id="opr-001", station_id="TEST_CLOSE_REOPEN_STATION")
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        pause_operation(
            db,
            op,
            OperationPauseRequest(reason_code="CHECK"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )

    count_before_reopen = _event_count(db, op.id)
    reopened_detail = reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="Material recheck required"),
        actor_user_id="sup-001",
        tenant_id=_TENANT_ID,
    )

    assert reopened_detail.closure_status == ClosureStatusEnum.open.value
    assert reopened_detail.reopen_count == 1
    assert reopened_detail.last_reopened_by == "sup-001"
    assert reopened_detail.last_reopened_at is not None
    assert _event_count(db, op.id) == count_before_reopen + 1
    assert _event_types(db, op.id)[-1] == ExecutionEventType.OPERATION_REOPENED.value

    # Reopened runtime projection is controlled non-running state.
    assert reopened_detail.status == StatusEnum.paused.value

    # After reopen, closed invariant no longer blocks execution writes.
    reopened_live = get_operation(db, op.id)
    _ensure_open_station_session(db, user_id="opr-001", station_id="TEST_CLOSE_REOPEN_STATION")
    resumed = resume_operation(
        db,
        reopened_live,
        OperationResumeRequest(note="resume after controlled reopen"),
        actor_user_id="opr-001",
        tenant_id=_TENANT_ID,
    )
    assert resumed.status == StatusEnum.in_progress.value

    # Append-only proof: event count increases by add-only writes and no deletions.
    assert len(_event_types(db, op.id)) >= 4


def test_reopen_operation_rejects_not_closed_and_missing_reason(db_session):
    db = db_session
    wo = _seed_wo(db, "REOPEN-REJECT")
    op = _mk_op(
        db,
        wo,
        suffix="REOPEN-REJECT",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.open.value,
    )

    with pytest.raises(ReopenOperationConflictError, match="STATE_NOT_CLOSED"):
        reopen_operation(
            db,
            op,
            OperationReopenRequest(reason="valid"),
            actor_user_id="sup-001",
            tenant_id=_TENANT_ID,
        )

    op.closure_status = ClosureStatusEnum.closed.value
    db.add(op)
    db.commit()

    with pytest.raises(ReopenOperationConflictError, match="REOPEN_REASON_REQUIRED"):
        reopen_operation(
            db,
            op,
            OperationReopenRequest(reason="   "),
            actor_user_id="sup-001",
            tenant_id=_TENANT_ID,
        )


def get_operation(db, operation_id: int) -> Operation:
    operation = db.scalar(select(Operation).where(Operation.id == operation_id))
    assert operation is not None
    return operation
