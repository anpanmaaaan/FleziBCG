from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.execution import ExecutionEvent
from app.models.master import (
    ClosureStatusEnum,
    Operation,
    ProductionOrder,
    StatusEnum,
    WorkOrder,
)
from app.models.quality import (
    QualityDispositionDecision,
    QualityHold,
    QualityMeasurementRecord,
    QualityMeasurementValue,
)
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.schemas.operation import (
    OperationCompleteRequest,
    OperationReportQuantityRequest,
    OperationStartRequest,
)
from app.schemas.quality import (
    QualityDispositionRequest,
    QualityMeasurementInput,
    QualityMeasurementSubmitRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import (
    CompleteOperationConflictError,
    complete_operation,
    derive_operation_detail,
    report_quantity,
    start_operation,
)
from app.services.quality_service import (
    record_quality_disposition,
    submit_qc_measurement,
)
from app.services.station_session_service import (
    get_current_station_session,
    open_station_session,
)


_PREFIX = f"TEST-PILOT-GOLDEN-{uuid4().hex[:8]}"
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
    return session


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
            db.scalars(
                select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
            )
        )
        op_ids = list(
            db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids)))
        )

        if op_ids:
            hold_ids = list(
                db.scalars(
                    select(QualityHold.id).where(QualityHold.operation_id.in_(op_ids))
                )
            )
            if hold_ids:
                db.execute(
                    delete(QualityDispositionDecision).where(
                        QualityDispositionDecision.hold_id.in_(hold_ids)
                    )
                )
                db.execute(delete(QualityHold).where(QualityHold.id.in_(hold_ids)))

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

            db.execute(
                delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids))
            )
            db.commit()

        if wo_ids:
            db.execute(delete(Operation).where(Operation.work_order_id.in_(wo_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
            db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))
            db.commit()

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
    qc_required: bool,
    status: str = StatusEnum.planned.value,
    closure_status: str = ClosureStatusEnum.open.value,
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="pilot-golden",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 12, 1, 8, 0, 0),
        planned_end=datetime(2099, 12, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 12, 1, 8, 0, 0),
        planned_end=datetime(2099, 12, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="pilot-golden-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        status=status,
        closure_status=closure_status,
        station_scope_value=_STATION,
        quantity=10,
        qc_required=qc_required,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def _complete_operation(db, op: Operation):
    return complete_operation(
        db,
        op,
        OperationCompleteRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )


def test_pilot_golden_path_happy_path_smoke(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(db, suffix="HAPPY", qc_required=False)

    started = start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    assert started.status == StatusEnum.in_progress.value
    assert started.allowed_actions == [
        "report_production",
        "pause_execution",
        "complete_execution",
        "start_downtime",
    ]

    reported = report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=4, scrap_qty=1, operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    assert reported.status == StatusEnum.in_progress.value
    assert reported.good_qty == 4
    assert reported.scrap_qty == 1
    assert reported.allowed_actions == [
        "report_production",
        "pause_execution",
        "complete_execution",
        "start_downtime",
    ]

    completed = complete_operation(
        db,
        op,
        OperationCompleteRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    assert completed.status == StatusEnum.completed.value
    assert completed.allowed_actions == ["close_operation"]


def test_pilot_golden_path_quality_hold_release_smoke(db_session):
    db = db_session
    _ensure_open_station_session(db)
    op = _seed_operation(db, suffix="QUALITY", qc_required=True)

    start_operation(
        db,
        op,
        OperationStartRequest(operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )
    report_quantity(
        db,
        op,
        OperationReportQuantityRequest(good_qty=5, scrap_qty=0, operator_id=_ACTOR),
        tenant_id=_TENANT_ID,
    )

    hold_response = submit_qc_measurement(
        db,
        tenant_id=_TENANT_ID,
        actor_user_id=_ACTOR,
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=[
                QualityMeasurementInput(item_code="DIM_A", measured_value=11.0),
                QualityMeasurementInput(item_code="DIM_B", measured_value=5.2),
                QualityMeasurementInput(item_code="SURF", measured_value=3.0),
            ],
        ),
    )
    assert hold_response.quality_status == "QC_HOLD"
    assert hold_response.hold_id is not None

    held_detail = derive_operation_detail(db, op)
    assert held_detail.quality_hold_open is True
    assert "complete_execution" not in held_detail.allowed_actions

    with pytest.raises(CompleteOperationConflictError, match="STATE_QC_HOLD_ACTIVE"):
        _complete_operation(db, op)

    disposition = record_quality_disposition(
        db,
        hold_id=hold_response.hold_id,
        tenant_id=_TENANT_ID,
        actor_user_id="QAL-DECIDER",
        actor_role_code="QAL",
        payload=QualityDispositionRequest(disposition_code="RELEASE_QC_HOLD"),
    )
    assert disposition.hold_status == "RELEASED"
    assert disposition.quality_status == "QC_PASSED"

    released_detail = derive_operation_detail(db, op)
    assert released_detail.quality_hold_open is False
    assert "complete_execution" in released_detail.allowed_actions

    completed = _complete_operation(db, op)
    assert completed.status == StatusEnum.completed.value
    assert completed.allowed_actions == ["close_operation"]
