from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.quality import (
    QualityDispositionDecision,
    QualityHold,
    QualityMeasurementRecord,
    QualityMeasurementValue,
    QualityReviewStatusEnum,
    QualityStatusEnum,
)
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.schemas.quality import QualityDispositionRequest
from app.schemas.operation import (
    OperationCompleteRequest,
    OperationPauseRequest,
    OperationResumeRequest,
    OperationStartRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    CompleteOperationConflictError,
    ResumeExecutionConflictError,
    complete_operation,
    derive_operation_detail,
    pause_operation,
    resume_operation,
    start_operation,
)
from app.services.quality_service import record_quality_disposition
from app.services.station_session_service import (
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)


_PREFIX = "TEST-QC-GATE"
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


def _purge(db) -> None:
    op_ids = list(
        db.scalars(
            select(Operation.id).where(Operation.operation_number.like(f"{_PREFIX}-%"))
        )
    )
    if op_ids:
        hold_ids = list(
            db.scalars(select(QualityHold.id).where(QualityHold.operation_id.in_(op_ids)))
        )
        if hold_ids:
            db.execute(
                delete(QualityDispositionDecision).where(
                    QualityDispositionDecision.hold_id.in_(hold_ids)
                )
            )
        db.execute(delete(QualityHold).where(QualityHold.operation_id.in_(op_ids)))
        record_ids = list(
            db.scalars(
                select(QualityMeasurementRecord.id).where(
                    QualityMeasurementRecord.operation_id.in_(op_ids)
                )
            )
        )
        if record_ids:
            db.execute(
                delete(QualityMeasurementValue).where(
                    QualityMeasurementValue.measurement_record_id.in_(record_ids)
                )
            )
            db.execute(
                delete(QualityMeasurementRecord).where(
                    QualityMeasurementRecord.id.in_(record_ids)
                )
            )

        db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))

        wo_ids = list(
            db.scalars(select(WorkOrder.id).where(WorkOrder.operations.any(Operation.id.in_(op_ids))))
        )
        db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
        if wo_ids:
            po_ids = list(
                db.scalars(
                    select(ProductionOrder.id).where(
                        ProductionOrder.work_orders.any(WorkOrder.id.in_(wo_ids))
                    )
                )
            )
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
            if po_ids:
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


def _seed_operation(db, *, suffix: str) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="qc-gate",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 11, 1, 8, 0, 0),
        planned_end=datetime(2099, 11, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 11, 1, 8, 0, 0),
        planned_end=datetime(2099, 11, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="qc-gate-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        status=StatusEnum.planned.value,
        quantity=10,
        qc_required=True,
        station_scope_value=f"{_STATION}-{suffix}",
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def _seed_active_hold(db, *, operation_id: int, suffix: str) -> QualityHold:
    record = QualityMeasurementRecord(
        operation_id=operation_id,
        submitted_by="qc-operator",
        quality_status=QualityStatusEnum.QC_HOLD.value,
        review_status=QualityReviewStatusEnum.DECISION_PENDING.value,
        tenant_id=_TENANT_ID,
    )
    db.add(record)
    db.flush()
    value = QualityMeasurementValue(
        measurement_record_id=record.id,
        item_code=f"DIM-{suffix}",
        measured_value=99.0,
        lower_limit=1.0,
        upper_limit=2.0,
        is_within_spec=False,
    )
    db.add(value)
    hold = QualityHold(
        operation_id=operation_id,
        measurement_record_id=record.id,
        status="ACTIVE",
        review_status=QualityReviewStatusEnum.DECISION_PENDING.value,
        reason="OUT_OF_SPEC_MEASUREMENT",
        created_by="qc-operator",
        tenant_id=_TENANT_ID,
    )
    db.add(hold)
    db.commit()
    db.refresh(hold)
    return hold


def test_resume_rejects_when_active_quality_hold_exists(db_session):
    db = db_session
    op = _seed_operation(db, suffix="RESUME")
    _ensure_open_station_session(db, station_id=op.station_scope_value)

    start_operation(db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID)
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    pause_operation(
        db,
        db_op,
        OperationPauseRequest(reason_code="BREAK", note="pause"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    _seed_active_hold(db, operation_id=op.id, suffix="RESUME")
    paused_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert paused_op is not None

    with pytest.raises(ResumeExecutionConflictError, match="STATE_QC_HOLD_ACTIVE"):
        resume_operation(
            db,
            paused_op,
            OperationResumeRequest(note="resume"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )

    detail = derive_operation_detail(db, paused_op)
    assert "resume_execution" not in detail.allowed_actions


def test_complete_rejects_when_active_quality_hold_exists(db_session):
    db = db_session
    op = _seed_operation(db, suffix="COMPLETE")
    _ensure_open_station_session(db, station_id=op.station_scope_value)

    start_operation(db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID)
    _seed_active_hold(db, operation_id=op.id, suffix="COMPLETE")

    in_progress_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert in_progress_op is not None

    with pytest.raises(CompleteOperationConflictError, match="STATE_QC_HOLD_ACTIVE"):
        complete_operation(
            db,
            in_progress_op,
            OperationCompleteRequest(operator_id=_ACTOR),
            tenant_id=_TENANT_ID,
        )

    detail = derive_operation_detail(db, in_progress_op)
    assert "complete_execution" not in detail.allowed_actions


def test_require_recheck_keeps_resume_blocked(db_session):
    db = db_session
    op = _seed_operation(db, suffix="RECHECK-RESUME")
    _ensure_open_station_session(db, station_id=op.station_scope_value)

    start_operation(db, op, OperationStartRequest(operator_id=_ACTOR), tenant_id=_TENANT_ID)
    db_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert db_op is not None
    pause_operation(
        db,
        db_op,
        OperationPauseRequest(reason_code="BREAK", note="pause"),
        actor_user_id=_ACTOR,
        tenant_id=_TENANT_ID,
    )

    hold = _seed_active_hold(db, operation_id=op.id, suffix="RECHECK-RESUME")
    record_quality_disposition(
        db,
        hold_id=hold.id,
        tenant_id=_TENANT_ID,
        actor_user_id="qal-1",
        actor_role_code="QAL",
        payload=QualityDispositionRequest(disposition_code="REQUIRE_RECHECK"),
    )

    paused_op = db.scalar(select(Operation).where(Operation.id == op.id))
    assert paused_op is not None

    with pytest.raises(ResumeExecutionConflictError, match="STATE_QC_HOLD_ACTIVE"):
        resume_operation(
            db,
            paused_op,
            OperationResumeRequest(note="resume"),
            actor_user_id=_ACTOR,
            tenant_id=_TENANT_ID,
        )

    detail = derive_operation_detail(db, paused_op)
    assert detail.quality_hold_open is True
    assert "resume_execution" not in detail.allowed_actions