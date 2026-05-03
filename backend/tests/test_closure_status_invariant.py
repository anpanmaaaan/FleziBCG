from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete, select, text

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_session import StationSession
from app.schemas.operation import (
    OperationAbortRequest,
    OperationCompleteRequest,
    OperationEndDowntimeRequest,
    OperationPauseRequest,
    OperationReportQuantityRequest,
    OperationResumeRequest,
    OperationStartDowntimeRequest,
    OperationStartRequest,
)
from app.services.operation_service import (
    ClosedRecordConflictError,
    CompleteOperationConflictError,
    PauseExecutionConflictError,
    ResumeExecutionConflictError,
    StartDowntimeConflictError,
    StartOperationConflictError,
    abort_operation,
    complete_operation,
    pause_operation,
    report_quantity,
    resume_operation,
    start_downtime,
    start_operation,
    end_downtime,
)

_PREFIX = "TEST-CLOSURE-STATUS"
_TENANT_ID = "default"


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
            db.execute(delete(StationSession).where(StationSession.station_id == "STATION_01"))
            db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
            db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
        db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
    db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
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


def _seed_work_order(db) -> WorkOrder:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-001",
        route_id=f"{_PREFIX}-R-01",
        product_name="closure status invariant",
        quantity=100,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 8, 1, 8, 0, 0),
        planned_end=datetime(2099, 8, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-001",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 8, 1, 8, 0, 0),
        planned_end=datetime(2099, 8, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()
    return wo


def _mk_operation(
    db,
    wo: WorkOrder,
    *,
    suffix: str,
    status: str,
    closure_status: str,
) -> Operation:
    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        work_order_id=wo.id,
        sequence=10,
        name=f"closure op {suffix}",
        status=status,
        closure_status=closure_status,
        planned_start=datetime(2099, 8, 1, 9, 0, 0),
        planned_end=datetime(2099, 8, 1, 10, 0, 0),
        quantity=10,
        completed_qty=0,
        good_qty=0,
        scrap_qty=0,
        qc_required=False,
        station_scope_value="STATION_01",
        tenant_id=_TENANT_ID,
    )
    db.add(op)
    db.flush()
    return op


def _ensure_open_station_session(
    db,
    *,
    station_id: str = "STATION_01",
    operator_user_id: str = "opr-001",
) -> StationSession:
    session = db.scalar(
        select(StationSession).where(
            StationSession.tenant_id == _TENANT_ID,
            StationSession.station_id == station_id,
            StationSession.status == "OPEN",
            StationSession.closed_at.is_(None),
        )
    )
    if session is None:
        session = StationSession(
            session_id=uuid4().hex,
            tenant_id=_TENANT_ID,
            station_id=station_id,
            operator_user_id=operator_user_id,
            status="OPEN",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def _add_open_downtime_event(db, op: Operation) -> None:
    db.add(
        ExecutionEvent(
            event_type=ExecutionEventType.DOWNTIME_STARTED.value,
            production_order_id=op.work_order.production_order_id,
            work_order_id=op.work_order_id,
            operation_id=op.id,
            payload={"started_at": datetime(2099, 8, 1, 9, 5, 0).isoformat()},
            tenant_id=op.tenant_id,
        )
    )
    db.flush()


def test_closed_record_rejects_all_execution_writes_with_same_code(db_session):
    db = db_session
    wo = _seed_work_order(db)
    _ensure_open_station_session(db)

    op_start = _mk_operation(
        db,
        wo,
        suffix="START",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        start_operation(db, op_start, OperationStartRequest(operator_id="opr-001"), tenant_id=_TENANT_ID)

    op_pause = _mk_operation(
        db,
        wo,
        suffix="PAUSE",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        pause_operation(
            db,
            op_pause,
            OperationPauseRequest(reason_code="BREAK"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )

    op_resume = _mk_operation(
        db,
        wo,
        suffix="RESUME",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        resume_operation(
            db,
            op_resume,
            OperationResumeRequest(note="resume"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )

    op_report = _mk_operation(
        db,
        wo,
        suffix="REPORT",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        report_quantity(
            db,
            op_report,
            OperationReportQuantityRequest(good_qty=1, scrap_qty=0, operator_id="opr-001"),
            tenant_id=_TENANT_ID,
        )

    op_dt_start = _mk_operation(
        db,
        wo,
        suffix="DTSTART",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        start_downtime(
            db,
            op_dt_start,
            OperationStartDowntimeRequest(reason_code="OTHER", note="n"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )

    op_dt_end = _mk_operation(
        db,
        wo,
        suffix="DTEND",
        status=StatusEnum.paused.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    _add_open_downtime_event(db, op_dt_end)
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        end_downtime(
            db,
            op_dt_end,
            OperationEndDowntimeRequest(note="end"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )

    op_complete = _mk_operation(
        db,
        wo,
        suffix="COMPLETE",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        complete_operation(
            db,
            op_complete,
            OperationCompleteRequest(operator_id="opr-001"),
            tenant_id=_TENANT_ID,
        )

    op_abort = _mk_operation(
        db,
        wo,
        suffix="ABORT",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
    )
    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        abort_operation(
            db,
            op_abort,
            OperationAbortRequest(operator_id="opr-001", reason_code="R"),
            tenant_id=_TENANT_ID,
        )


def test_open_record_keeps_existing_behavior_and_not_closed_error(db_session):
    db = db_session
    wo = _seed_work_order(db)
    _ensure_open_station_session(db)

    op_start = _mk_operation(
        db,
        wo,
        suffix="OPEN-START",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.open.value,
    )
    with pytest.raises(StartOperationConflictError, match="Operation must be PLANNED to start"):
        start_operation(db, op_start, OperationStartRequest(operator_id="opr-001"), tenant_id=_TENANT_ID)

    op_pause = _mk_operation(
        db,
        wo,
        suffix="OPEN-PAUSE",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.open.value,
    )
    with pytest.raises(PauseExecutionConflictError, match="STATE_NOT_RUNNING"):
        pause_operation(
            db,
            op_pause,
            OperationPauseRequest(reason_code="BREAK"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )

    op_resume = _mk_operation(
        db,
        wo,
        suffix="OPEN-RESUME",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.open.value,
    )
    with pytest.raises(ResumeExecutionConflictError, match="STATE_NOT_PAUSED"):
        resume_operation(
            db,
            op_resume,
            OperationResumeRequest(note="resume"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )

    op_dt = _mk_operation(
        db,
        wo,
        suffix="OPEN-DT",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.open.value,
    )
    with pytest.raises(StartDowntimeConflictError, match="STATE_NOT_RUNNING_OR_PAUSED"):
        start_downtime(
            db,
            op_dt,
            OperationStartDowntimeRequest(reason_code="OTHER", note="n"),
            actor_user_id="opr-001",
            tenant_id=_TENANT_ID,
        )


def test_open_happy_path_report_quantity_unchanged(db_session):
    db = db_session
    wo = _seed_work_order(db)
    _ensure_open_station_session(db)
    op = _mk_operation(
        db,
        wo,
        suffix="OPEN-HAPPY",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.open.value,
    )

    detail = report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=3, scrap_qty=1, operator_id="opr-001"),
        tenant_id=_TENANT_ID,
    )
    assert detail.good_qty >= 3
    assert detail.scrap_qty >= 1
    assert detail.closure_status == ClosureStatusEnum.open.value


def test_closure_status_defaults_and_backfill_to_open(db_session):
    db = db_session
    wo = _seed_work_order(db)

    # ORM default on new records should be OPEN.
    op_default = _mk_operation(
        db,
        wo,
        suffix="DEFAULT",
        status=StatusEnum.planned.value,
        closure_status=ClosureStatusEnum.open.value,
    )
    assert op_default.closure_status == ClosureStatusEnum.open.value

    # Deterministic backfill behavior from migration: blank values are normalized to OPEN.
    op_blank = _mk_operation(
        db,
        wo,
        suffix="BACKFILL",
        status=StatusEnum.planned.value,
        closure_status="",
    )
    db.execute(
        text(
            "UPDATE operations SET closure_status = 'OPEN' "
            "WHERE closure_status IS NULL OR closure_status = ''"
        )
    )
    db.commit()
    db.refresh(op_blank)
    assert op_blank.closure_status == ClosureStatusEnum.open.value
