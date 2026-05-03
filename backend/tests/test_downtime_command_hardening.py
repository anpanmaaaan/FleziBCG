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
    OperationEndDowntimeRequest,
    OperationResumeRequest,
    OperationStartDowntimeRequest,
    OperationStartRequest,
    OperationPauseRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    ClosedRecordConflictError,
    EndDowntimeConflictError,
    ResumeExecutionConflictError,
    StationSessionGuardError,
    StartDowntimeConflictError,
    end_downtime,
    pause_operation,
    resume_operation,
    start_downtime,
    start_operation,
)
from app.services.station_session_service import (
    close_station_session,
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

_PREFIX = "TEST-P0C06B"
_TENANT_ID = "default"
_STATION = f"{_PREFIX}-STATION"
_ACTOR = f"{_PREFIX}-ACTOR"

# MATERIAL_SHORTAGE is seeded by migration 0012_downtime_reason_master.sql
# for tenant_id='default' and is active by default.
_REASON_CODE = "MATERIAL_SHORTAGE"


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
        product_name="p0c06b",
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

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c06b-op",
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


def _seed_paused_operation(db, *, suffix: str, station_scope_value: str = _STATION) -> Operation:
    op = _seed_in_progress_operation(db, suffix=suffix, station_scope_value=station_scope_value)
    pause_operation(
        db,
        op,
        OperationPauseRequest(reason_code="BREAK", note="pause for downtime test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    assert db_op.status == StatusEnum.paused.value
    return db_op


def _seed_blocked_operation(db, *, suffix: str, station_scope_value: str = _STATION) -> Operation:
    """Start downtime from IN_PROGRESS → operation becomes BLOCKED."""
    op = _seed_in_progress_operation(db, suffix=suffix, station_scope_value=station_scope_value)
    start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="block for test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    assert db_op.status == StatusEnum.blocked.value
    return db_op


def _latest_event_type(db, operation_id: int) -> str | None:
    return db.scalar(
        select(ExecutionEvent.event_type)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )


def _events_of_type(db, operation_id: int, event_type: str) -> list:
    return list(
        db.scalars(
            select(ExecutionEvent)
            .where(
                ExecutionEvent.operation_id == operation_id,
                ExecutionEvent.event_type == event_type,
            )
        )
    )


# ---------------------------------------------------------------------------
# T1 — Happy path: start_downtime from IN_PROGRESS → BLOCKED
# ---------------------------------------------------------------------------

def test_start_downtime_happy_path_from_in_progress(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="DT-START-IP")

    detail = start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.blocked.value
    assert detail.downtime_open is True
    assert detail.allowed_actions == ["end_downtime"]
    assert _latest_event_type(db, op.id) == ExecutionEventType.DOWNTIME_STARTED.value


# ---------------------------------------------------------------------------
# T2 — Happy path: start_downtime from PAUSED → stays PAUSED with downtime open
# ---------------------------------------------------------------------------

def test_start_downtime_happy_path_from_paused(db_session):
    db = db_session
    op = _seed_paused_operation(db, suffix="DT-START-PAUSED")

    detail = start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    # Service comment "If PAUSED, stay PAUSED" refers to the snapshot column only.
    # The event-derived projection (_derive_status) returns BLOCKED whenever
    # downtime_started_count > downtime_ended_count, independent of snapshot.
    # So derive_operation_detail.status == BLOCKED and downtime_open == True.
    assert detail.status == StatusEnum.blocked.value
    assert detail.downtime_open is True
    assert detail.allowed_actions == ["end_downtime"]
    assert _latest_event_type(db, op.id) == ExecutionEventType.DOWNTIME_STARTED.value


# ---------------------------------------------------------------------------
# T3 — Rejects non-IN_PROGRESS/PAUSED state (PLANNED)
# ---------------------------------------------------------------------------

def test_start_downtime_rejects_planned_operation(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(db, suffix="DT-START-PLANNED", status=StatusEnum.planned.value)

    with pytest.raises(StartDowntimeConflictError, match="STATE_NOT_RUNNING_OR_PAUSED"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code=_REASON_CODE),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T4 — Rejects CLOSED operation
# ---------------------------------------------------------------------------

def test_start_downtime_rejects_closed_operation(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(
        db,
        suffix="DT-START-CLOSED",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code=_REASON_CODE),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T5 — Rejects duplicate open downtime
# ---------------------------------------------------------------------------

def test_start_downtime_rejects_duplicate_open_downtime(db_session):
    db = db_session
    # First downtime opens: IN_PROGRESS → BLOCKED
    op = _seed_blocked_operation(db, suffix="DT-START-DUP")

    # Operation is now BLOCKED (snapshot) but start_downtime also checks events
    # for open downtime; the state guard rejects BLOCKED before we even get there
    # (not in_progress or paused). Verify it's caught somewhere reasonable.
    # NOTE: source checks status first, so BLOCKED raises STATE_NOT_RUNNING_OR_PAUSED.
    with pytest.raises(StartDowntimeConflictError):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="second"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T5b — Rejects DOWNTIME_ALREADY_OPEN when snapshot is IN_PROGRESS but
#        events show open downtime (edge case: status check passes, event check fires)
# ---------------------------------------------------------------------------

def test_start_downtime_rejects_downtime_already_open_event_count_guard(db_session):
    db = db_session
    _ensure_open_station_session(db)
    # Seed IN_PROGRESS operation with manual event-level open downtime
    # (status snapshot intentionally left as in_progress to bypass status guard).
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-DT-EDGE",
        route_id=f"{_PREFIX}-R-DT-EDGE",
        product_name="p0c06b",
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
        work_order_number=f"{_PREFIX}-WO-DT-EDGE",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 9, 1, 8, 0, 0),
        planned_end=datetime(2099, 9, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    op = Operation(
        operation_number=f"{_PREFIX}-OP-DT-EDGE",
        name="p0c06b-edge",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        # Snapshot is intentionally IN_PROGRESS so the status guard passes;
        # we manually inject a DOWNTIME_STARTED event so the event-count guard fires.
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=_STATION,
        quantity=10,
    )
    db.add(op)
    db.flush()
    # Inject OP_STARTED and DOWNTIME_STARTED events directly
    from app.repositories.execution_event_repository import create_execution_event
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.OP_STARTED.value,
        production_order_id=po.id,
        work_order_id=wo.id,
        operation_id=op.id,
        payload={"operator_id": _ACTOR},
        tenant_id=_TENANT_ID,
    )
    create_execution_event(
        db=db,
        event_type=ExecutionEventType.DOWNTIME_STARTED.value,
        production_order_id=po.id,
        work_order_id=wo.id,
        operation_id=op.id,
        payload={"actor_user_id": _ACTOR, "reason_code": _REASON_CODE},
        tenant_id=_TENANT_ID,
    )
    db.commit()
    db.refresh(op)

    with pytest.raises(StartDowntimeConflictError, match="DOWNTIME_ALREADY_OPEN"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="should fail"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T6 — Rejects unknown/invalid reason code
# ---------------------------------------------------------------------------

def test_start_downtime_rejects_invalid_reason_code(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="DT-START-BADCODE")

    with pytest.raises(StartDowntimeConflictError, match="INVALID_REASON_CODE"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code="NO_SUCH_REASON_XYZ"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T7 — Happy path: end_downtime → BLOCKED→PAUSED, downtime_open=False
# ---------------------------------------------------------------------------

def test_end_downtime_happy_path_blocked_to_paused(db_session):
    db = db_session
    op = _seed_blocked_operation(db, suffix="DT-END-OK")

    detail = end_downtime(
        db,
        op,
        OperationEndDowntimeRequest(note="end test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.paused.value
    assert detail.downtime_open is False
    assert detail.allowed_actions == ["resume_execution", "start_downtime"]
    assert _latest_event_type(db, op.id) == ExecutionEventType.DOWNTIME_ENDED.value


# ---------------------------------------------------------------------------
# T8 — end_downtime does NOT auto-resume (no EXECUTION_RESUMED emitted)
# ---------------------------------------------------------------------------

def test_end_downtime_does_not_auto_resume(db_session):
    db = db_session
    op = _seed_blocked_operation(db, suffix="DT-END-NO-RESUME")

    end_downtime(
        db,
        op,
        OperationEndDowntimeRequest(note="no-resume-test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    resumed_events = _events_of_type(db, op.id, ExecutionEventType.EXECUTION_RESUMED.value)
    assert len(resumed_events) == 0, (
        "end_downtime must not auto-resume: no EXECUTION_RESUMED event should be emitted"
    )


# ---------------------------------------------------------------------------
# T9 — end_downtime rejects when no open downtime
# ---------------------------------------------------------------------------

def test_end_downtime_rejects_when_no_open_downtime(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="DT-END-NONE")

    with pytest.raises(EndDowntimeConflictError, match="STATE_NO_OPEN_DOWNTIME"):
        end_downtime(
            db,
            op,
            OperationEndDowntimeRequest(note="should fail"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T10 — end_downtime rejects CLOSED operation
# ---------------------------------------------------------------------------

def test_end_downtime_rejects_closed_operation(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(
        db,
        suffix="DT-END-CLOSED",
        status=StatusEnum.blocked.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        end_downtime(
            db,
            op,
            OperationEndDowntimeRequest(note="should fail"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T11 — resume_operation rejected while downtime is open
# ---------------------------------------------------------------------------

def test_resume_blocked_while_downtime_open(db_session):
    db = db_session
    op = _seed_blocked_operation(db, suffix="DT-RESUME-BLOCKED")

    with pytest.raises(ResumeExecutionConflictError, match="STATE_DOWNTIME_OPEN"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T12 — No-session outcome parity
# ---------------------------------------------------------------------------

def test_start_downtime_no_session_rejects(db_session):
    db = db_session
    op = _seed_operation(db, suffix="DT-NO-SESSION", status=StatusEnum.in_progress.value)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        start_downtime(
            db,
            op,
            OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="no-session"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T13 — OPEN-session outcome parity
# ---------------------------------------------------------------------------

def test_start_downtime_open_session_parity(db_session):
    db = db_session
    _ensure_open_station_session(db)

    op = _seed_in_progress_operation(db, suffix="DT-OPEN-SESSION")

    detail = start_downtime(
        db,
        op,
        OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="open-session"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.blocked.value
    assert detail.downtime_open is True
    assert detail.allowed_actions == ["end_downtime"]
    assert _latest_event_type(db, op.id) == ExecutionEventType.DOWNTIME_STARTED.value
