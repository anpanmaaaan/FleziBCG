from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_session import StationSession
from app.schemas.operation import (
    OperationCloseRequest,
    OperationCompleteRequest,
    OperationEndDowntimeRequest,
    OperationPauseRequest,
    OperationReopenRequest,
    OperationReportQuantityRequest,
    OperationResumeRequest,
    OperationStartDowntimeRequest,
    OperationStartRequest,
)
from app.services.operation_service import (
    close_operation,
    complete_operation,
    end_downtime,
    ensure_open_station_session_for_command,
    pause_operation,
    reopen_operation,
    report_quantity,
    resume_operation,
    start_downtime,
    start_operation,
    StationSessionGuardError,
)

_PREFIX = "TEST-P0C08C"
_TENANT_ID = "default"
_OTHER_TENANT_ID = "other-tenant"
_STATION = f"{_PREFIX}-STATION"
_OTHER_STATION = f"{_PREFIX}-OTHER-STATION"
_ACTOR = f"{_PREFIX}-ACTOR"
_OTHER_ACTOR = f"{_PREFIX}-OTHER-ACTOR"
_REASON_CODE = "MATERIAL_SHORTAGE"


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
        delete(StationSession).where(StationSession.station_id.like(f"{_PREFIX}-%"))
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


def _insert_session(
    db,
    *,
    tenant_id: str = _TENANT_ID,
    station_id: str = _STATION,
    operator_user_id: str | None = _ACTOR,
    status: str = "OPEN",
    closed: bool = False,
) -> StationSession:
    session = StationSession(
        session_id=f"{tenant_id}-{station_id}-{status}-{operator_user_id or 'none'}",
        tenant_id=tenant_id,
        station_id=station_id,
        operator_user_id=operator_user_id,
        status=status,
        opened_at=datetime.now(timezone.utc),
        closed_at=datetime.now(timezone.utc) if closed else None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _seed_operation(
    db,
    *,
    suffix: str,
    status: str,
    closure_status: str = ClosureStatusEnum.open.value,
    station_scope_value: str = _STATION,
    tenant_id: str = _TENANT_ID,
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="p0c08c",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 11, 1, 8, 0, 0),
        planned_end=datetime(2099, 11, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 11, 1, 8, 0, 0),
        planned_end=datetime(2099, 11, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c08c-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=tenant_id,
        status=status,
        closure_status=closure_status,
        station_scope_value=station_scope_value,
        quantity=10,
    )
    db.add(op)
    db.flush()

    if status in (StatusEnum.in_progress.value, StatusEnum.paused.value, StatusEnum.completed.value):
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"operator_id": _ACTOR},
                tenant_id=tenant_id,
            )
        )
    if status == StatusEnum.paused.value:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.EXECUTION_PAUSED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"paused_at": datetime(2099, 11, 1, 9, 10, 0).isoformat()},
                tenant_id=tenant_id,
            )
        )
    if status == StatusEnum.blocked.value:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"operator_id": _ACTOR},
                tenant_id=tenant_id,
            )
        )
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.DOWNTIME_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"reason_code": _REASON_CODE},
                tenant_id=tenant_id,
            )
        )
    if status == StatusEnum.completed.value:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"operator_id": _ACTOR},
                tenant_id=tenant_id,
            )
        )
    db.commit()
    db.refresh(op)
    return op


def _event_count(db, operation_id: int) -> int:
    return len(
        list(
            db.scalars(
                select(ExecutionEvent.id).where(ExecutionEvent.operation_id == operation_id)
            )
        )
    )


def test_guard_rejects_when_no_open_station_session_exists(db_session):
    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        ensure_open_station_session_for_command(
            db_session,
            tenant_id=_TENANT_ID,
            station_id=_STATION,
            operator_user_id=_ACTOR,
            command_name="start_operation",
        )


def test_guard_rejects_when_station_session_is_closed(db_session):
    _insert_session(db_session, status="CLOSED", closed=True)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_CLOSED"):
        ensure_open_station_session_for_command(
            db_session,
            tenant_id=_TENANT_ID,
            station_id=_STATION,
            operator_user_id=_ACTOR,
            command_name="start_operation",
        )


def test_guard_rejects_station_mismatch_when_operator_has_session_elsewhere(db_session):
    _insert_session(db_session, station_id=_OTHER_STATION, operator_user_id=_ACTOR)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_STATION_MISMATCH"):
        ensure_open_station_session_for_command(
            db_session,
            tenant_id=_TENANT_ID,
            station_id=_STATION,
            operator_user_id=_ACTOR,
            command_name="start_operation",
        )


def test_guard_rejects_operator_mismatch_when_station_session_owned_by_other_operator(db_session):
    _insert_session(db_session, operator_user_id=_OTHER_ACTOR)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_OPERATOR_MISMATCH"):
        ensure_open_station_session_for_command(
            db_session,
            tenant_id=_TENANT_ID,
            station_id=_STATION,
            operator_user_id=_ACTOR,
            command_name="pause_operation",
        )


def test_guard_rejects_tenant_mismatch_when_station_has_other_tenant_session(db_session):
    _insert_session(db_session, tenant_id=_OTHER_TENANT_ID, operator_user_id=_ACTOR)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_TENANT_MISMATCH"):
        ensure_open_station_session_for_command(
            db_session,
            tenant_id=_TENANT_ID,
            station_id=_STATION,
            operator_user_id=_ACTOR,
            command_name="start_operation",
        )


def test_guard_allows_matching_open_station_session(db_session):
    session = _insert_session(db_session, operator_user_id=_ACTOR)

    resolved = ensure_open_station_session_for_command(
        db_session,
        tenant_id=_TENANT_ID,
        station_id=_STATION,
        operator_user_id=_ACTOR,
        command_name="start_operation",
    )

    assert resolved.session_id == session.session_id


@pytest.mark.parametrize(
    ("command_name", "seed_status", "call"),
    [
        (
            "start_operation",
            StatusEnum.planned.value,
            lambda db, op: start_operation(
                db,
                op,
                OperationStartRequest(operator_id=_ACTOR),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
        ),
        (
            "pause_operation",
            StatusEnum.in_progress.value,
            lambda db, op: pause_operation(
                db,
                op,
                OperationPauseRequest(reason_code="BREAK", note="pause"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
        ),
        (
            "resume_operation",
            StatusEnum.paused.value,
            lambda db, op: resume_operation(
                db,
                op,
                OperationResumeRequest(note="resume"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
        ),
        (
            "report_quantity",
            StatusEnum.in_progress.value,
            lambda db, op: report_quantity(
                db,
                op,
                OperationReportQuantityRequest(good_qty=2, scrap_qty=0, operator_id=_ACTOR),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
        ),
        (
            "start_downtime",
            StatusEnum.in_progress.value,
            lambda db, op: start_downtime(
                db,
                op,
                OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="start dt"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
        ),
        (
            "end_downtime",
            StatusEnum.blocked.value,
            lambda db, op: end_downtime(
                db,
                op,
                OperationEndDowntimeRequest(note="end dt"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
        ),
        (
            "complete_operation",
            StatusEnum.in_progress.value,
            lambda db, op: complete_operation(
                db,
                op,
                OperationCompleteRequest(operator_id=_ACTOR),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
        ),
    ],
)
def test_subset_commands_reject_missing_session_and_emit_no_event(
    db_session, command_name, seed_status, call
):
    op = _seed_operation(db_session, suffix=f"FAIL-{command_name}", status=seed_status)
    before_count = _event_count(db_session, op.id)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        call(db_session, op)

    assert _event_count(db_session, op.id) == before_count


@pytest.mark.parametrize(
    ("command_name", "seed_status", "call", "expected_event"),
    [
        (
            "start_operation",
            StatusEnum.planned.value,
            lambda db, op: start_operation(
                db,
                op,
                OperationStartRequest(operator_id=_ACTOR),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
            ExecutionEventType.OP_STARTED.value,
        ),
        (
            "pause_operation",
            StatusEnum.in_progress.value,
            lambda db, op: pause_operation(
                db,
                op,
                OperationPauseRequest(reason_code="BREAK", note="pause"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
            ExecutionEventType.EXECUTION_PAUSED.value,
        ),
        (
            "resume_operation",
            StatusEnum.paused.value,
            lambda db, op: resume_operation(
                db,
                op,
                OperationResumeRequest(note="resume"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
            ExecutionEventType.EXECUTION_RESUMED.value,
        ),
        (
            "report_quantity",
            StatusEnum.in_progress.value,
            lambda db, op: report_quantity(
                db,
                op,
                OperationReportQuantityRequest(good_qty=2, scrap_qty=0, operator_id=_ACTOR),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
            ExecutionEventType.QTY_REPORTED.value,
        ),
        (
            "start_downtime",
            StatusEnum.in_progress.value,
            lambda db, op: start_downtime(
                db,
                op,
                OperationStartDowntimeRequest(reason_code=_REASON_CODE, note="start dt"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
            ExecutionEventType.DOWNTIME_STARTED.value,
        ),
        (
            "end_downtime",
            StatusEnum.blocked.value,
            lambda db, op: end_downtime(
                db,
                op,
                OperationEndDowntimeRequest(note="end dt"),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
            ExecutionEventType.DOWNTIME_ENDED.value,
        ),
        (
            "complete_operation",
            StatusEnum.in_progress.value,
            lambda db, op: complete_operation(
                db,
                op,
                OperationCompleteRequest(operator_id=_ACTOR),
                actor_user_id=_ACTOR,
                tenant_id=_TENANT_ID,
            ),
            ExecutionEventType.OP_COMPLETED.value,
        ),
    ],
)
def test_subset_commands_succeed_with_matching_open_session(
    db_session, command_name, seed_status, call, expected_event
):
    _insert_session(db_session, operator_user_id=_ACTOR)
    op = _seed_operation(db_session, suffix=f"OK-{command_name}", status=seed_status)

    detail = call(db_session, op)

    assert detail is not None
    latest_event = db_session.scalar(
        select(ExecutionEvent.event_type)
        .where(ExecutionEvent.operation_id == op.id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )
    assert latest_event == expected_event


def test_close_operation_behavior_remains_unchanged_without_station_session(db_session):
    op = _seed_operation(
        db_session,
        suffix="DEFER-CLOSE",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.open.value,
    )

    detail = close_operation(
        db_session,
        op,
        OperationCloseRequest(note="unchanged"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.closed.value


def test_reopen_operation_behavior_remains_unchanged_without_station_session(db_session):
    op = _seed_operation(
        db_session,
        suffix="DEFER-REOPEN",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    detail = reopen_operation(
        db_session,
        op,
        OperationReopenRequest(reason="unchanged"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.closure_status == ClosureStatusEnum.open.value
    assert detail.status == StatusEnum.paused.value
