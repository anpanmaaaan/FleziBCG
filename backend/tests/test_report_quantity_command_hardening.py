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
    OperationReportQuantityRequest,
    OperationStartRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    ClosedRecordConflictError,
    report_quantity,
    StationSessionGuardError,
    start_operation,
)
from app.services.station_session_service import (
    close_station_session,
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

_PREFIX = "TEST-P0C06A"
_TENANT_ID = "default"
_STATION = f"{_PREFIX}-STATION"
_ACTOR = f"{_PREFIX}-ACTOR"

_IN_PROGRESS_ACTIONS = [
    "report_production",
    "pause_execution",
    "complete_execution",
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
        product_name="p0c06a",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 8, 1, 8, 0, 0),
        planned_end=datetime(2099, 8, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 8, 1, 8, 0, 0),
        planned_end=datetime(2099, 8, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c06a-op",
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


def _latest_event_type(db, operation_id: int) -> str | None:
    return db.scalar(
        select(ExecutionEvent.event_type)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )


# ---------------------------------------------------------------------------
# T1 — Happy path: good_qty only, status stays IN_PROGRESS
# ---------------------------------------------------------------------------

def test_report_quantity_happy_path_good_qty_only(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="RPT-GOOD-ONLY")

    detail = report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=5, scrap_qty=0, operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.in_progress.value
    assert detail.allowed_actions == _IN_PROGRESS_ACTIONS
    assert _latest_event_type(db, op.id) == ExecutionEventType.QTY_REPORTED.value


# ---------------------------------------------------------------------------
# T2 — Happy path: mixed good + scrap qty, accumulates in projection
# ---------------------------------------------------------------------------

def test_report_quantity_happy_path_mixed_qty_accumulates(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="RPT-MIXED")

    detail = report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=3, scrap_qty=2, operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.in_progress.value
    assert detail.good_qty == 3
    assert detail.scrap_qty == 2


# ---------------------------------------------------------------------------
# T3 — Rejects non-IN_PROGRESS (PLANNED)
# ---------------------------------------------------------------------------

def test_report_quantity_rejects_planned_operation(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(db, suffix="RPT-PLANNED", status=StatusEnum.planned.value)

    with pytest.raises(ValueError, match="IN_PROGRESS"):
        report_quantity(
            db,
            op,
            OperationReportQuantityRequest(good_qty=5, scrap_qty=0),
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T4 — Rejects non-IN_PROGRESS (PAUSED) — must start then pause first
# ---------------------------------------------------------------------------

def test_report_quantity_rejects_paused_operation(db_session):
    db = db_session
    from app.schemas.operation import OperationPauseRequest
    from app.services.operation_service import pause_operation

    op = _seed_in_progress_operation(db, suffix="RPT-PAUSED")
    pause_operation(
        db,
        op,
        OperationPauseRequest(reason_code="BREAK", note="p0c06a pause test"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    assert db_op.status == StatusEnum.paused.value

    with pytest.raises(ValueError, match="IN_PROGRESS"):
        report_quantity(
            db,
            db_op,
            OperationReportQuantityRequest(good_qty=5, scrap_qty=0),
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T5 — Rejects CLOSED (closure_status = closed) operation
# ---------------------------------------------------------------------------

def test_report_quantity_rejects_closed_operation(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(
        db,
        suffix="RPT-CLOSED",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.closed.value,
    )

    with pytest.raises(ClosedRecordConflictError, match="STATE_CLOSED_RECORD"):
        report_quantity(
            db,
            op,
            OperationReportQuantityRequest(good_qty=5, scrap_qty=0),
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T6 — Rejects negative good_qty
# ---------------------------------------------------------------------------

def test_report_quantity_rejects_negative_good_qty(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="RPT-NEG-GOOD")

    with pytest.raises(ValueError, match="non-negative"):
        report_quantity(
            db,
            op,
            OperationReportQuantityRequest(good_qty=-1, scrap_qty=0),
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T7 — Rejects negative scrap_qty
# ---------------------------------------------------------------------------

def test_report_quantity_rejects_negative_scrap_qty(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="RPT-NEG-SCRAP")

    with pytest.raises(ValueError, match="non-negative"):
        report_quantity(
            db,
            op,
            OperationReportQuantityRequest(good_qty=0, scrap_qty=-1),
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T8 — Rejects zero-sum (both good_qty=0 and scrap_qty=0)
# ---------------------------------------------------------------------------

def test_report_quantity_rejects_zero_sum(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="RPT-ZERO-SUM")

    with pytest.raises(ValueError, match="greater than zero"):
        report_quantity(
            db,
            op,
            OperationReportQuantityRequest(good_qty=0, scrap_qty=0),
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T9 — Cumulative quantity: two reports accumulate in projection
# ---------------------------------------------------------------------------

def test_report_quantity_cumulative_across_two_reports(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="RPT-CUMUL")

    report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=3, scrap_qty=1, operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    # Re-fetch operation after first report
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None

    detail = report_quantity(
        db,
        db_op,
        OperationReportQuantityRequest(good_qty=2, scrap_qty=1, operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    # Projection accumulates both reports: good=3+2=5, scrap=1+1=2
    assert detail.good_qty == 5
    assert detail.scrap_qty == 2
    assert detail.status == StatusEnum.in_progress.value

    # Two QTY_REPORTED events should exist
    qty_event_count = db.query(ExecutionEvent).filter(
        ExecutionEvent.operation_id == op.id,
        ExecutionEvent.event_type == ExecutionEventType.QTY_REPORTED.value,
    ).count()
    assert qty_event_count == 2


# ---------------------------------------------------------------------------
# T10 — Allowed actions after report remain correct
# ---------------------------------------------------------------------------

def test_report_quantity_allowed_actions_after_report(db_session):
    db = db_session
    op = _seed_in_progress_operation(db, suffix="RPT-ACTIONS")

    detail = report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=5, scrap_qty=0, operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    assert detail.allowed_actions == _IN_PROGRESS_ACTIONS


# ---------------------------------------------------------------------------
# T11 — No-session outcome parity: missing StationSession does not change outcome
# ---------------------------------------------------------------------------

def test_report_quantity_no_session_rejects(db_session):
    db = db_session
    op = _seed_operation(db, suffix="RPT-NO-SESSION", status=StatusEnum.in_progress.value)

    with pytest.raises(StationSessionGuardError, match="STATION_SESSION_REQUIRED"):
        report_quantity(
            db,
            op,
            OperationReportQuantityRequest(good_qty=4, scrap_qty=1, operator_id=_ACTOR),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )


# ---------------------------------------------------------------------------
# T12 — OPEN-session outcome parity: active StationSession does not change outcome
# ---------------------------------------------------------------------------

def test_report_quantity_open_session_parity(db_session):
    db = db_session
    _ensure_open_station_session(db)

    op = _seed_in_progress_operation(db, suffix="RPT-OPEN-SESSION")

    detail = report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=4, scrap_qty=1, operator_id=_ACTOR),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    assert detail.status == StatusEnum.in_progress.value
    assert detail.allowed_actions == _IN_PROGRESS_ACTIONS
    assert _latest_event_type(db, op.id) == ExecutionEventType.QTY_REPORTED.value
