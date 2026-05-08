from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError
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
)
from app.schemas.quality import (
    QualityDispositionRequest,
    QualityMeasurementInput,
    QualityMeasurementSubmitRequest,
)
from app.services.quality_service import (
    QualityConflictError,
    get_quality_measurement_requirements,
    list_quality_holds,
    record_quality_disposition,
    submit_qc_measurement,
)


_PREFIX = "TEST-QC-SVC"


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
    tenant_id: str,
    qc_required: bool,
    reported_good_qty: int = 0,
    reported_scrap_qty: int = 0,
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="qc-service-test",
        quantity=5,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 1, 1, 8, 0, 0),
        planned_end=datetime(2099, 1, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 1, 1, 8, 0, 0),
        planned_end=datetime(2099, 1, 1, 17, 0, 0),
        tenant_id=tenant_id,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="qc-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=tenant_id,
        status=StatusEnum.planned.value,
        quantity=5,
        completed_qty=reported_good_qty + reported_scrap_qty,
        good_qty=reported_good_qty,
        scrap_qty=reported_scrap_qty,
        qc_required=qc_required,
        station_scope_value=f"{_PREFIX}-STATION-{suffix}",
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def _all_required_measurements_pass() -> list[QualityMeasurementInput]:
    return [
        QualityMeasurementInput(item_code="DIM_A", measured_value=10.1),
        QualityMeasurementInput(item_code="DIM_B", measured_value=5.2),
        QualityMeasurementInput(item_code="SURF", measured_value=1.1),
    ]


def _all_required_measurements_with_hold() -> list[QualityMeasurementInput]:
    return [
        QualityMeasurementInput(item_code="DIM_A", measured_value=12.0),
        QualityMeasurementInput(item_code="DIM_B", measured_value=5.2),
        QualityMeasurementInput(item_code="SURF", measured_value=1.1),
    ]


def test_submit_measurement_pass_records_result_and_events(db_session):
    op = _seed_operation(db_session, suffix="PASS", tenant_id="default", qc_required=True)

    response = submit_qc_measurement(
        db_session,
        tenant_id="default",
        actor_user_id="qc-operator",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=_all_required_measurements_pass(),
        ),
    )

    assert response.quality_status == "QC_PASSED"
    assert response.review_status == "NO_REVIEW"
    assert response.hold_id is None

    event_types = list(
        db_session.scalars(
            select(ExecutionEvent.event_type).where(ExecutionEvent.operation_id == op.id)
        )
    )
    assert "qc_measurement_submitted" in event_types
    assert "qc_result_recorded" in event_types
    assert "qc_hold_applied" not in event_types


def test_submit_measurement_out_of_spec_creates_hold(db_session):
    op = _seed_operation(db_session, suffix="HOLD", tenant_id="default", qc_required=True)

    response = submit_qc_measurement(
        db_session,
        tenant_id="default",
        actor_user_id="qc-operator",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=_all_required_measurements_with_hold(),
        ),
    )

    assert response.quality_status == "QC_HOLD"
    assert response.review_status == "DECISION_PENDING"
    assert response.hold_id is not None

    hold = db_session.scalar(
        select(QualityHold).where(QualityHold.id == response.hold_id)
    )
    assert hold is not None
    assert hold.status == "ACTIVE"
    assert hold.review_status == "DECISION_PENDING"

    event_types = list(
        db_session.scalars(
            select(ExecutionEvent.event_type).where(ExecutionEvent.operation_id == op.id)
        )
    )
    assert "qc_hold_applied" in event_types


def test_submit_measurement_uses_backend_thresholds_not_client_thresholds(db_session):
    op = _seed_operation(
        db_session,
        suffix="SERVER-LIMITS",
        tenant_id="default",
        qc_required=True,
    )

    response = submit_qc_measurement(
        db_session,
        tenant_id="default",
        actor_user_id="qc-operator",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=_all_required_measurements_with_hold(),
        ),
    )

    assert response.quality_status == "QC_HOLD"
    assert response.hold_id is not None
    assert response.values[0].lower_limit == 10.0
    assert response.values[0].upper_limit == 10.5


def test_submit_measurement_rejects_unknown_backend_requirement_item(db_session):
    op = _seed_operation(
        db_session,
        suffix="UNKNOWN-ITEM",
        tenant_id="default",
        qc_required=True,
    )

    with pytest.raises(ValueError, match="Unsupported measurement item_code"):
        submit_qc_measurement(
            db_session,
            tenant_id="default",
            actor_user_id="qc-operator",
            payload=QualityMeasurementSubmitRequest(
                operation_id=op.id,
                measurements=[
                    QualityMeasurementInput(
                        item_code="DIM_X",
                        measured_value=1.0,
                    )
                ],
            ),
        )

    event_types = list(
        db_session.scalars(
            select(ExecutionEvent.event_type).where(ExecutionEvent.operation_id == op.id)
        )
    )
    assert event_types == []


def test_submit_measurement_rejects_when_required_items_missing(db_session):
    op = _seed_operation(
        db_session,
        suffix="MISSING-REQ",
        tenant_id="default",
        qc_required=True,
    )

    with pytest.raises(ValueError, match="REQUIRED_MEASUREMENTS_MISSING:DIM_B,SURF"):
        submit_qc_measurement(
            db_session,
            tenant_id="default",
            actor_user_id="qc-operator",
            payload=QualityMeasurementSubmitRequest(
                operation_id=op.id,
                measurements=[
                    QualityMeasurementInput(
                        item_code="DIM_A",
                        measured_value=10.1,
                    )
                ],
            ),
        )

    event_types = list(
        db_session.scalars(
            select(ExecutionEvent.event_type).where(ExecutionEvent.operation_id == op.id)
        )
    )
    assert event_types == []


def test_measurement_request_rejects_client_threshold_fields():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        QualityMeasurementInput.model_validate(
            {
                "item_code": "DIM_A",
                "measured_value": 10.1,
                "lower_limit": 10.0,
                "upper_limit": 10.5,
            }
        )


def test_submit_measurement_rejects_when_qc_not_required(db_session):
    op = _seed_operation(db_session, suffix="NOQC", tenant_id="default", qc_required=False)

    with pytest.raises(QualityConflictError, match="QC_NOT_REQUIRED"):
        submit_qc_measurement(
            db_session,
            tenant_id="default",
            actor_user_id="qc-operator",
            payload=QualityMeasurementSubmitRequest(
                operation_id=op.id,
                measurements=[
                    QualityMeasurementInput(
                        item_code="DIM_A",
                        measured_value=10.0,
                    )
                ],
            ),
        )


def test_get_quality_measurement_requirements_returns_backend_template(db_session):
    op = _seed_operation(
        db_session,
        suffix="REQS",
        tenant_id="default",
        qc_required=True,
    )

    response = get_quality_measurement_requirements(
        db_session,
        tenant_id="default",
        operation_id=op.id,
    )

    assert response.operation_id == op.id
    assert response.operation_number == op.operation_number
    assert response.qc_required is True
    assert response.template_code == "QLITE-STD-001"
    assert len(response.items) == 3
    assert response.items[0].item_code == "DIM_A"
    assert response.items[0].lower_limit == 10.0
    assert response.items[0].upper_limit == 10.5


def test_get_quality_measurement_requirements_returns_empty_when_qc_not_required(
    db_session,
):
    op = _seed_operation(
        db_session,
        suffix="REQS-NOQC",
        tenant_id="default",
        qc_required=False,
    )

    response = get_quality_measurement_requirements(
        db_session,
        tenant_id="default",
        operation_id=op.id,
    )

    assert response.operation_id == op.id
    assert response.qc_required is False
    assert response.template_code is None
    assert response.items == []


def test_list_quality_holds_is_tenant_isolated(db_session):
    op_a = _seed_operation(db_session, suffix="TA", tenant_id="tenant-a", qc_required=True)
    op_b = _seed_operation(db_session, suffix="TB", tenant_id="tenant-b", qc_required=True)

    submit_qc_measurement(
        db_session,
        tenant_id="tenant-a",
        actor_user_id="qa-a",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op_a.id,
            measurements=_all_required_measurements_with_hold(),
        ),
    )
    submit_qc_measurement(
        db_session,
        tenant_id="tenant-b",
        actor_user_id="qa-b",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op_b.id,
            measurements=_all_required_measurements_with_hold(),
        ),
    )

    tenant_a_holds = list_quality_holds(db_session, tenant_id="tenant-a")
    tenant_b_holds = list_quality_holds(db_session, tenant_id="tenant-b")

    assert len(tenant_a_holds) == 1
    assert len(tenant_b_holds) == 1
    assert tenant_a_holds[0].operation_id == op_a.id
    assert tenant_b_holds[0].operation_id == op_b.id


def _create_hold(db_session, *, tenant_id: str, suffix: str) -> int:
    op = _seed_operation(db_session, suffix=suffix, tenant_id=tenant_id, qc_required=True)
    response = submit_qc_measurement(
        db_session,
        tenant_id=tenant_id,
        actor_user_id="qa-source",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=[
                QualityMeasurementInput(item_code="DIM_A", measured_value=99.0),
                QualityMeasurementInput(item_code="DIM_B", measured_value=5.2),
                QualityMeasurementInput(item_code="SURF", measured_value=1.1),
            ],
        ),
    )
    assert response.hold_id is not None
    return response.hold_id


def _create_hold_with_reported_good(
    db_session,
    *,
    tenant_id: str,
    suffix: str,
    reported_good_qty: int,
) -> int:
    op = _seed_operation(
        db_session,
        suffix=suffix,
        tenant_id=tenant_id,
        qc_required=True,
        reported_good_qty=reported_good_qty,
    )
    response = submit_qc_measurement(
        db_session,
        tenant_id=tenant_id,
        actor_user_id="qa-source",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=[
                QualityMeasurementInput(item_code="DIM_A", measured_value=99.0),
                QualityMeasurementInput(item_code="DIM_B", measured_value=5.2),
                QualityMeasurementInput(item_code="SURF", measured_value=1.1),
            ],
        ),
    )
    assert response.hold_id is not None
    return response.hold_id


def test_pass_submission_releases_reported_good_quantity(db_session):
    op = _seed_operation(
        db_session,
        suffix="PASSQTY",
        tenant_id="default",
        qc_required=True,
        reported_good_qty=7,
    )

    response = submit_qc_measurement(
        db_session,
        tenant_id="default",
        actor_user_id="qc-operator",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=_all_required_measurements_pass(),
        ),
    )

    assert response.accepted_good_release_qty == 7
    assert response.held_pending_good_qty == 0

    result_event = db_session.scalar(
        select(ExecutionEvent)
        .where(
            ExecutionEvent.operation_id == op.id,
            ExecutionEvent.event_type == "qc_result_recorded",
        )
        .order_by(ExecutionEvent.id.desc())
    )
    assert result_event is not None
    assert int(result_event.payload.get("accepted_good_release_qty", -1)) == 7
    assert int(result_event.payload.get("held_pending_good_qty", -1)) == 0


def test_hold_submission_defers_reported_good_quantity(db_session):
    op = _seed_operation(
        db_session,
        suffix="HOLDQTY",
        tenant_id="default",
        qc_required=True,
        reported_good_qty=6,
    )

    response = submit_qc_measurement(
        db_session,
        tenant_id="default",
        actor_user_id="qc-operator",
        payload=QualityMeasurementSubmitRequest(
            operation_id=op.id,
            measurements=_all_required_measurements_with_hold(),
        ),
    )

    assert response.accepted_good_release_qty == 0
    assert response.held_pending_good_qty == 6

    hold_event = db_session.scalar(
        select(ExecutionEvent)
        .where(
            ExecutionEvent.operation_id == op.id,
            ExecutionEvent.event_type == "qc_hold_applied",
        )
        .order_by(ExecutionEvent.id.desc())
    )
    assert hold_event is not None
    assert int(hold_event.payload.get("held_pending_good_qty", -1)) == 6


def test_qal_can_record_quality_disposition(db_session):
    hold_id = _create_hold(db_session, tenant_id="default", suffix="DISP")

    response = record_quality_disposition(
        db_session,
        hold_id=hold_id,
        tenant_id="default",
        actor_user_id="qal-1",
        actor_role_code="QAL",
        payload=QualityDispositionRequest(disposition_code="RELEASE_QC_HOLD"),
    )

    assert response.disposition_code == "RELEASE_QC_HOLD"
    assert response.quality_status == "QC_PASSED"
    assert response.review_status == "DISPOSITION_DONE"
    assert response.hold_status == "RELEASED"

    event_types = list(
        db_session.scalars(
            select(ExecutionEvent.event_type).join(
                QualityHold, QualityHold.operation_id == ExecutionEvent.operation_id
            ).where(QualityHold.id == hold_id)
        )
    )
    assert "disposition_decision_recorded" in event_types
    assert "qc_hold_released" in event_types


def test_pmg_cannot_record_quality_disposition_by_default(db_session):
    hold_id = _create_hold(db_session, tenant_id="default", suffix="PMG")

    with pytest.raises(PermissionError, match="Only QAL"):
        record_quality_disposition(
            db_session,
            hold_id=hold_id,
            tenant_id="default",
            actor_user_id="pmg-1",
            actor_role_code="PMG",
            payload=QualityDispositionRequest(disposition_code="RELEASE_QC_HOLD"),
        )


def test_quality_disposition_is_tenant_scoped(db_session):
    hold_id = _create_hold(db_session, tenant_id="tenant-a", suffix="TENANT")

    with pytest.raises(LookupError, match="Quality hold not found"):
        record_quality_disposition(
            db_session,
            hold_id=hold_id,
            tenant_id="tenant-b",
            actor_user_id="qal-2",
            actor_role_code="QAL",
            payload=QualityDispositionRequest(disposition_code="RELEASE_QC_HOLD"),
        )


def test_released_hold_cannot_be_disposed_twice(db_session):
    hold_id = _create_hold(db_session, tenant_id="default", suffix="TWICE")
    record_quality_disposition(
        db_session,
        hold_id=hold_id,
        tenant_id="default",
        actor_user_id="qal-1",
        actor_role_code="QAL",
        payload=QualityDispositionRequest(disposition_code="RELEASE_QC_HOLD"),
    )

    with pytest.raises(QualityConflictError, match="HOLD_NOT_ACTIVE"):
        record_quality_disposition(
            db_session,
            hold_id=hold_id,
            tenant_id="default",
            actor_user_id="qal-1",
            actor_role_code="QAL",
            payload=QualityDispositionRequest(disposition_code="ACCEPT_WITH_DEVIATION"),
        )


def test_require_recheck_keeps_hold_active_and_emits_recheck_event(db_session):
    hold_id = _create_hold_with_reported_good(
        db_session,
        tenant_id="default",
        suffix="RECHECK-HOLD",
        reported_good_qty=5,
    )

    response = record_quality_disposition(
        db_session,
        hold_id=hold_id,
        tenant_id="default",
        actor_user_id="qal-1",
        actor_role_code="QAL",
        payload=QualityDispositionRequest(disposition_code="REQUIRE_RECHECK"),
    )

    hold = db_session.scalar(select(QualityHold).where(QualityHold.id == hold_id))
    assert hold is not None
    assert response.quality_status == "QC_PENDING"
    assert response.hold_status == "ACTIVE"
    assert response.review_status == "DECISION_PENDING"
    assert hold.status == "ACTIVE"
    assert hold.review_status == "DECISION_PENDING"

    event_types = list(
        db_session.scalars(
            select(ExecutionEvent.event_type)
            .where(ExecutionEvent.operation_id == hold.operation_id)
            .order_by(ExecutionEvent.id.asc())
        )
    )
    assert "disposition_decision_recorded" in event_types
    assert "qc_recheck_requested" in event_types
    assert "qc_hold_released" not in event_types


@pytest.mark.parametrize(
    ("disposition_code", "expected_release_qty", "expected_held_qty"),
    [
        ("RELEASE_QC_HOLD", 5, 0),
        ("ACCEPT_WITH_DEVIATION", 5, 0),
        ("REQUIRE_RECHECK", 0, 5),
        ("CONFIRM_SCRAP", 0, 0),
    ],
)
def test_disposition_quantity_effects_by_code(
    db_session,
    disposition_code: str,
    expected_release_qty: int,
    expected_held_qty: int,
):
    hold_id = _create_hold_with_reported_good(
        db_session,
        tenant_id="default",
        suffix=f"DISPQTY-{disposition_code}",
        reported_good_qty=5,
    )

    response = record_quality_disposition(
        db_session,
        hold_id=hold_id,
        tenant_id="default",
        actor_user_id="qal-1",
        actor_role_code="QAL",
        payload=QualityDispositionRequest(disposition_code=disposition_code),
    )

    assert response.accepted_good_release_qty == expected_release_qty
    assert response.held_pending_good_qty == expected_held_qty

    hold = db_session.scalar(select(QualityHold).where(QualityHold.id == hold_id))
    assert hold is not None

    disposition_event = db_session.scalar(
        select(ExecutionEvent)
        .where(
            ExecutionEvent.operation_id == hold.operation_id,
            ExecutionEvent.event_type == "disposition_decision_recorded",
        )
        .order_by(ExecutionEvent.id.desc())
    )
    assert disposition_event is not None
    assert (
        int(disposition_event.payload.get("accepted_good_release_qty", -1))
        == expected_release_qty
    )
    assert (
        int(disposition_event.payload.get("held_pending_good_qty", -1))
        == expected_held_qty
    )
