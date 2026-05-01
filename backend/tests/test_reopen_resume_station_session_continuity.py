from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_session import StationSession
from app.schemas.operation import OperationReopenRequest, OperationResumeRequest
from app.services.operation_service import (
    StationSessionGuardError,
    reopen_operation,
    resume_operation,
)

_PREFIX = "TEST-P0C08E"
_TENANT_ID = "default"
_STATION = f"{_PREFIX}-STATION"
_OTHER_STATION = f"{_PREFIX}-OTHER-STATION"
_SUPERVISOR = f"{_PREFIX}-SUP"
_OPERATOR = f"{_PREFIX}-OPR"
_OTHER_OPERATOR = f"{_PREFIX}-OTHER-OPR"


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


def _seed_operation(db, *, suffix: str) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="p0c08e",
        quantity=10,
        status=StatusEnum.planned.value,
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        work_order_id=wo.id,
        sequence=10,
        name=f"op {suffix}",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.closed.value,
        station_scope_value=_STATION,
        quantity=10,
        tenant_id=_TENANT_ID,
    )
    db.add(op)
    db.flush()

    db.add_all(
        [
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"started_at": datetime(2099, 11, 2, 9, 0, 0).isoformat()},
                tenant_id=_TENANT_ID,
            ),
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"completed_at": datetime(2099, 11, 2, 9, 30, 0).isoformat()},
                tenant_id=_TENANT_ID,
            ),
        ]
    )
    db.commit()
    db.refresh(op)
    return op


def _insert_station_session(
    db,
    *,
    station_id: str,
    operator_user_id: str | None,
    status: str,
    closed: bool = False,
) -> StationSession:
    session = StationSession(
        session_id=f"{station_id}-{status}-{operator_user_id or 'none'}",
        tenant_id=_TENANT_ID,
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


def _event_count(db, operation_id: int) -> int:
    return len(
        list(
            db.scalars(
                select(ExecutionEvent.id).where(ExecutionEvent.operation_id == operation_id)
            )
        )
    )


def test_reopen_sets_open_and_paused_without_session_guard(db_session):
    db = db_session
    op = _seed_operation(db, suffix="REOPEN")

    reopened = reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="continuity replacement"),
        actor_user_id=_SUPERVISOR,
        tenant_id=_TENANT_ID,
    )

    assert reopened.closure_status == ClosureStatusEnum.open.value
    assert reopened.status == StatusEnum.paused.value


def test_resume_after_reopen_succeeds_with_matching_open_station_session(db_session):
    db = db_session
    op = _seed_operation(db, suffix="RESUME-SUCCESS")

    reopened = reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="resume path"),
        actor_user_id=_SUPERVISOR,
        tenant_id=_TENANT_ID,
    )
    assert reopened.status == StatusEnum.paused.value

    _insert_station_session(
        db,
        station_id=_STATION,
        operator_user_id=_OPERATOR,
        status="OPEN",
    )

    resumed = resume_operation(
        db,
        op,
        OperationResumeRequest(note="resume from paused"),
        actor_user_id=_OPERATOR,
        tenant_id=_TENANT_ID,
    )
    assert resumed.status == StatusEnum.in_progress.value


def test_resume_after_reopen_rejects_without_open_station_session(db_session):
    db = db_session
    op = _seed_operation(db, suffix="NO-SESSION")
    reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="must enforce session"),
        actor_user_id=_SUPERVISOR,
        tenant_id=_TENANT_ID,
    )

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(note="should fail"),
            actor_user_id=_OPERATOR,
            tenant_id=_TENANT_ID,
        )


def test_resume_after_reopen_rejects_closed_station_session_and_does_not_append_event(db_session):
    db = db_session
    op = _seed_operation(db, suffix="CLOSED-SESSION")
    reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="closed station session"),
        actor_user_id=_SUPERVISOR,
        tenant_id=_TENANT_ID,
    )

    _insert_station_session(
        db,
        station_id=_STATION,
        operator_user_id=_OPERATOR,
        status="CLOSED",
        closed=True,
    )

    before = _event_count(db, op.id)
    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_CLOSED"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(note="should fail"),
            actor_user_id=_OPERATOR,
            tenant_id=_TENANT_ID,
        )
    after = _event_count(db, op.id)
    assert after == before


def test_resume_after_reopen_rejects_operator_and_station_mismatch(db_session):
    db = db_session
    op = _seed_operation(db, suffix="MISMATCH")
    reopen_operation(
        db,
        op,
        OperationReopenRequest(reason="mismatch checks"),
        actor_user_id=_SUPERVISOR,
        tenant_id=_TENANT_ID,
    )

    _insert_station_session(
        db,
        station_id=_STATION,
        operator_user_id=_OTHER_OPERATOR,
        status="OPEN",
    )
    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_OPERATOR_MISMATCH"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(note="should fail operator"),
            actor_user_id=_OPERATOR,
            tenant_id=_TENANT_ID,
        )

    db.execute(
        delete(StationSession).where(
            StationSession.tenant_id == _TENANT_ID,
            StationSession.station_id == _STATION,
        )
    )
    db.commit()

    _insert_station_session(
        db,
        station_id=_OTHER_STATION,
        operator_user_id=_OPERATOR,
        status="OPEN",
    )
    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_STATION_MISMATCH"):
        resume_operation(
            db,
            op,
            OperationResumeRequest(note="should fail station"),
            actor_user_id=_OPERATOR,
            tenant_id=_TENANT_ID,
        )
