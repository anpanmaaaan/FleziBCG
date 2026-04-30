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
    OperationPauseRequest,
    OperationResumeRequest,
    OperationStartRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    ClosedRecordConflictError,
    PauseExecutionConflictError,
    ResumeExecutionConflictError,
    StartOperationConflictError,
    pause_operation,
    resume_operation,
    start_operation,
)
from app.services.station_session_service import open_station_session

_PREFIX = "TEST-P0C05"
_TENANT_ID = "default"
_STATION = f"{_PREFIX}-STATION"
_ACTOR = f"{_PREFIX}-ACTOR"

_IN_PROGRESS_ACTIONS = [
    "report_production",
    "pause_execution",
    "complete_execution",
    "start_downtime",
]
_PAUSED_ACTIONS = [
    "resume_execution",
    "start_downtime",
]


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
            op_ids = list(db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids))))
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
        product_name="p0c05",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 7, 1, 8, 0, 0),
        planned_end=datetime(2099, 7, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 7, 1, 8, 0, 0),
        planned_end=datetime(2099, 7, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c05-op",
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


def _latest_event_type(db, operation_id: int) -> str | None:
    return db.scalar(
        select(ExecutionEvent.event_type)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )


def _seed_paused_operation(db, *, suffix: str, station_scope_value: str = _STATION) -> Operation:
    op = _seed_operation(
        db,
        suffix=suffix,
        status=StatusEnum.planned.value,
        station_scope_value=station_scope_value,
    )
    op_detail = start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    assert op_detail.status == StatusEnum.in_progress.value
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    pause_detail = pause_operation(
        db,
        db_op,
        OperationPauseRequest(reason_code="BREAK", note="pause for test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    assert pause_detail.status == StatusEnum.paused.value
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    return db_op


def test_start_operation_happy_path_planned_emits_event_and_derives_actions(db_session):
    db = db_session
    op = _seed_operation(db, suffix="START-OK", status=StatusEnum.planned.value)

    detail = start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.in_progress.value
    assert detail.allowed_actions == _IN_PROGRESS_ACTIONS
    assert _latest_event_type(db, op.id) == ExecutionEventType.OP_STARTED.value


def test_start_operation_rejects_non_planned(db_session):
    db = db_session
    op = _seed_operation(db, suffix="START-NOT-PLANNED", status=StatusEnum.in_progress.value)

    with pytest.raises(StartOperationConflictError):
        start_operation(
            db,
            op,
            OperationStartRequest(operator_id=_ACTOR),
            tenant_id=_TENANT_ID,
        )


def test_start_operation_rejects_closed_operation(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="START-CLOSED",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        start_operation(
            db,
            op,
            OperationStartRequest(operator_id=_ACTOR),
            tenant_id=_TENANT_ID,
        )


def test_pause_operation_happy_path_in_progress_emits_event_and_derives_actions(db_session):
    db = db_session
    op = _seed_operation(db, suffix="PAUSE-OK", status=StatusEnum.planned.value)
    started = start_operation(db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID)
    assert started.status == StatusEnum.in_progress.value

    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None

    detail = pause_operation(
        db,
        db_op,
        OperationPauseRequest(reason_code="BREAK", note="pause"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.paused.value
    assert detail.allowed_actions == _PAUSED_ACTIONS
    assert _latest_event_type(db, op.id) == ExecutionEventType.EXECUTION_PAUSED.value


def test_pause_operation_rejects_non_in_progress(db_session):
    db = db_session
    op = _seed_operation(db, suffix="PAUSE-NON-RUNNING", status=StatusEnum.planned.value)

    with pytest.raises(PauseExecutionConflictError, match="STATE_NOT_RUNNING"):
        pause_operation(
            db,
            op,
            OperationPauseRequest(reason_code="BREAK", note="pause"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_pause_operation_rejects_closed_operation(db_session):
    db = db_session
    op = _seed_operation(
        db,
        suffix="PAUSE-CLOSED",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        pause_operation(
            db,
            op,
            OperationPauseRequest(reason_code="BREAK", note="pause"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_resume_operation_happy_path_paused_emits_event_and_derives_actions(db_session):
    db = db_session
    op = _seed_paused_operation(db, suffix="RESUME-OK")

    detail = resume_operation(
        db,
        op,
        OperationResumeRequest(note="resume"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.in_progress.value
    assert detail.allowed_actions == _IN_PROGRESS_ACTIONS
    assert _latest_event_type(db, op.id) == ExecutionEventType.EXECUTION_RESUMED.value


def test_resume_operation_rejects_non_paused(db_session):
    db = db_session
    op = _seed_operation(db, suffix="RESUME-NOT-PAUSED", status=StatusEnum.in_progress.value)

    with pytest.raises(ResumeExecutionConflictError, match="STATE_NOT_PAUSED"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(note="resume"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_resume_operation_rejects_open_downtime(db_session):
    db = db_session
    op = _seed_paused_operation(db, suffix="RESUME-DT-OPEN")

    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.DOWNTIME_STARTED.value,
            production_order_id=op.work_order.production_order_id,
            work_order_id=op.work_order_id,
            operation_id=op.id,
            payload={"started_at": datetime(2099, 7, 1, 9, 30, 0).isoformat()},
            tenant_id=_TENANT_ID,
        )
    )
    db.commit()

    with pytest.raises(ResumeExecutionConflictError, match="STATE_DOWNTIME_OPEN"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(note="resume"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_resume_operation_station_busy_guard_unchanged(db_session):
    db = db_session
    target = _seed_paused_operation(db, suffix="RESUME-TARGET")

    competing = _seed_operation(
        db,
        suffix="RESUME-COMPETE",
        status=StatusEnum.planned.value,
        station_scope_value=target.station_scope_value,
    )
    started_competing = start_operation(
        db,
        competing,
        OperationStartRequest(operator_id=None),
        tenant_id=_TENANT_ID,
    )
    assert started_competing.status == StatusEnum.in_progress.value

    with pytest.raises(ResumeExecutionConflictError, match="STATE_STATION_BUSY"):
        resume_operation(
            db,
            target,
            OperationResumeRequest(note="resume"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


def test_missing_station_session_does_not_change_start_pause_resume_outcome(db_session):
    db = db_session
    op = _seed_operation(db, suffix="NO-SESSION", status=StatusEnum.planned.value)

    started = start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    assert started.status == StatusEnum.in_progress.value

    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    paused = pause_operation(
        db,
        db_op,
        OperationPauseRequest(reason_code="BREAK", note="pause"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    assert paused.status == StatusEnum.paused.value

    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    resumed = resume_operation(
        db,
        db_op,
        OperationResumeRequest(note="resume"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    assert resumed.status == StatusEnum.in_progress.value


def test_open_station_session_does_not_change_start_pause_resume_outcome(db_session):
    db = db_session
    station_id = f"{_PREFIX}-OPEN-SESSION-STATION"
    _seed_station_scope(db, user_id=_ACTOR, station_id=station_id)
    open_station_session(db, _identity(), station_id=station_id)

    op = _seed_operation(
        db,
        suffix="OPEN-SESSION",
        status=StatusEnum.planned.value,
        station_scope_value=station_id,
    )

    started = start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    assert started.status == StatusEnum.in_progress.value

    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    paused = pause_operation(
        db,
        db_op,
        OperationPauseRequest(reason_code="BREAK", note="pause"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    assert paused.status == StatusEnum.paused.value

    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    resumed = resume_operation(
        db,
        db_op,
        OperationResumeRequest(note="resume"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    assert resumed.status == StatusEnum.in_progress.value
