from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.execution import ExecutionEvent
from app.models.master import Operation
from app.models.quality import (
    QualityDeviationRequestStatusEnum,
    QualityGateDefinitionStatusEnum,
    QualityGateInstanceStatusEnum,
    QualityGateTypeEnum,
    QualityHoldStatusEnum,
    QualityReviewStatusEnum,
    QualityStatusEnum,
)
from app.repositories.operation_repository import get_operation_by_id
from app.repositories.quality_repository import (
    create_quality_gate_definition,
    create_quality_gate_instance,
    create_disposition_decision,
    create_measurement_record,
    create_measurement_values,
    create_quality_hold,
    get_active_quality_gate_instance_for_operation,
    get_quality_gate_instance_by_id,
    get_quality_gate_definition_by_id,
    get_hold_by_id,
    get_open_deviation_request_for_hold,
    get_deviation_request_by_id,
    get_measurement_record_by_id,
    list_quality_gate_definitions as list_quality_gate_definitions_repo,
    list_active_holds,
    create_deviation_request,
    create_nonconformance,
    list_nonconformances_by_hold,
    get_nonconformance_by_code,
    list_nonconformances as list_nonconformances_repo,
    list_deviation_requests as list_deviation_requests_repo,
)
from app.schemas.quality import (
    QualityGateDefinitionCreateRequest,
    QualityGateDefinitionResponse,
    QualityGateInstanceOpenRequest,
    QualityGateInstanceResponse,
    QualityDispositionRequest,
    QualityDispositionResponse,
    QualityHoldItem,
    QualityMeasurementSubmitRequest,
    QualityMeasurementSubmitResponse,
    QualityOperationRequirementsResponse,
    QualityRequirementItem,
    QualityMeasurementValueResult,
    QualityDeviationRequestCreate,
    QualityDeviationResolveRequest,
    QualityDeviationRequestItem,
    QualityNonconformanceCreateRequest,
    QualityNonconformanceItem,
)
from app.services.security_event_service import record_security_event


class QualityConflictError(ValueError):
    pass


_DISPOSITION_STATUS_MAP: dict[str, str] = {
    "RELEASE_QC_HOLD": QualityStatusEnum.QC_PASSED.value,
    "ACCEPT_WITH_DEVIATION": QualityStatusEnum.QC_PASSED.value,
    "REQUIRE_RECHECK": QualityStatusEnum.QC_PENDING.value,
    "CONFIRM_SCRAP": QualityStatusEnum.QC_FAILED.value,
}

_BASELINE_TEMPLATE_CODE = "QLITE-STD-001"
_BASELINE_TEMPLATE_NAME = "Quality Lite Baseline Inspection"
_BASELINE_TEMPLATE_VERSION = "v1"
_BASELINE_REQUIREMENT_ITEMS: tuple[dict[str, object], ...] = (
    {
        "item_code": "DIM_A",
        "label": "Dimension A",
        "input_type": "number",
        "required": True,
        "unit": "mm",
        "lower_limit": 10.0,
        "upper_limit": 10.5,
    },
    {
        "item_code": "DIM_B",
        "label": "Dimension B",
        "input_type": "number",
        "required": True,
        "unit": "mm",
        "lower_limit": 5.0,
        "upper_limit": 5.5,
    },
    {
        "item_code": "SURF",
        "label": "Surface Variation",
        "input_type": "number",
        "required": True,
        "unit": None,
        "lower_limit": None,
        "upper_limit": 2.0,
    },
)


def _get_requirement_items_for_operation(
    operation: Operation,
) -> tuple[dict[str, object], ...]:
    if not operation.qc_required:
        return ()
    return _BASELINE_REQUIREMENT_ITEMS


def _get_requirement_map_for_operation(
    operation: Operation,
) -> dict[str, dict[str, object]]:
    return {
        str(item["item_code"]): item
        for item in _get_requirement_items_for_operation(operation)
    }


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _resolve_operation_for_tenant(
    db: Session, *, operation_id: int, tenant_id: str
) -> Operation:
    operation = get_operation_by_id(db, operation_id)
    if operation is None or operation.tenant_id != tenant_id:
        raise ValueError("Operation not found")
    return operation


def create_quality_gate_definition_service(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: QualityGateDefinitionCreateRequest,
) -> QualityGateDefinitionResponse:
    gate_type = payload.gate_type.strip().upper()
    if gate_type not in {v.value for v in QualityGateTypeEnum}:
        raise ValueError(f"Unsupported gate_type={gate_type!r}")

    existing = [
        row
        for row in list_quality_gate_definitions_repo(db, tenant_id=tenant_id)
        if row.code == payload.code
    ]
    if existing:
        raise ValueError("Duplicate quality gate code in tenant")

    row = create_quality_gate_definition(
        db,
        code=payload.code,
        name=payload.name,
        status=QualityGateDefinitionStatusEnum.DRAFT.value,
        gate_type=gate_type,
        rule_set_version=payload.rule_set_version,
        applicability_scope_type=payload.applicability_scope_type,
        applicability_scope_value=payload.applicability_scope_value,
        tenant_id=tenant_id,
        created_by=actor_user_id,
    )

    db.commit()
    db.refresh(row)

    return QualityGateDefinitionResponse(
        gate_definition_id=row.id,
        code=row.code,
        name=row.name,
        status=row.status,
        gate_type=row.gate_type,
        rule_set_version=row.rule_set_version,
        applicability_scope_type=row.applicability_scope_type,
        applicability_scope_value=row.applicability_scope_value,
        tenant_id=row.tenant_id,
        created_by=row.created_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def list_quality_gate_definitions_service(
    db: Session,
    *,
    tenant_id: str,
) -> list[QualityGateDefinitionResponse]:
    rows = list_quality_gate_definitions_repo(db, tenant_id=tenant_id)
    return [
        QualityGateDefinitionResponse(
            gate_definition_id=row.id,
            code=row.code,
            name=row.name,
            status=row.status,
            gate_type=row.gate_type,
            rule_set_version=row.rule_set_version,
            applicability_scope_type=row.applicability_scope_type,
            applicability_scope_value=row.applicability_scope_value,
            tenant_id=row.tenant_id,
            created_by=row.created_by,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def open_quality_gate_instance_service(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: QualityGateInstanceOpenRequest,
) -> QualityGateInstanceResponse:
    gate_definition = get_quality_gate_definition_by_id(
        db,
        gate_definition_id=payload.gate_definition_id,
        tenant_id=tenant_id,
    )
    if gate_definition is None:
        raise LookupError("Quality gate definition not found")
    if gate_definition.status not in (
        QualityGateDefinitionStatusEnum.ACTIVE.value,
        QualityGateDefinitionStatusEnum.DRAFT.value,
    ):
        raise ValueError("Quality gate definition is not openable")

    operation = _resolve_operation_for_tenant(
        db,
        operation_id=payload.operation_id,
        tenant_id=tenant_id,
    )

    active_gate = get_active_quality_gate_instance_for_operation(
        db,
        operation_id=operation.id,
        tenant_id=tenant_id,
    )
    if active_gate is not None:
        raise QualityConflictError("QUALITY_GATE_INSTANCE_ALREADY_ACTIVE")

    instance = create_quality_gate_instance(
        db,
        gate_definition_id=payload.gate_definition_id,
        operation_id=operation.id,
        status=QualityGateInstanceStatusEnum.PENDING_MEASUREMENT.value,
        review_status=QualityReviewStatusEnum.NO_REVIEW.value,
        opened_by=actor_user_id,
        tenant_id=tenant_id,
    )

    db.add(
        ExecutionEvent(
            event_type="quality_gate_instance_opened",
            production_order_id=operation.work_order.production_order_id,
            work_order_id=operation.work_order_id,
            operation_id=operation.id,
            payload={
                "gate_instance_id": instance.id,
                "gate_definition_id": instance.gate_definition_id,
                "status": instance.status,
                "opened_by": actor_user_id,
            },
            tenant_id=tenant_id,
        )
    )
    db.commit()
    db.refresh(instance)

    return QualityGateInstanceResponse(
        gate_instance_id=instance.id,
        gate_definition_id=instance.gate_definition_id,
        operation_id=instance.operation_id,
        status=instance.status,
        review_status=instance.review_status,
        opened_by=instance.opened_by,
        closed_by=instance.closed_by,
        tenant_id=instance.tenant_id,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
    )


def _derive_quantity_effects(
    *,
    reported_good_qty: int,
    hold_active: bool,
    disposition_code: str | None = None,
) -> tuple[int, int]:
    safe_reported_good = max(int(reported_good_qty), 0)
    if not hold_active:
        return safe_reported_good, 0

    if disposition_code is None:
        return 0, safe_reported_good

    if disposition_code in ("RELEASE_QC_HOLD", "ACCEPT_WITH_DEVIATION"):
        return safe_reported_good, 0
    if disposition_code == "REQUIRE_RECHECK":
        return 0, safe_reported_good
    return 0, 0


def _evaluate_values(
    payload_measurements,
    *,
    requirement_map: dict[str, dict[str, object]],
) -> list[dict]:
    evaluated: list[dict] = []
    for row in payload_measurements:
        item_code = row.item_code.strip()
        requirement = requirement_map.get(item_code)
        if requirement is None:
            raise ValueError(f"Unsupported measurement item_code={item_code!r}")

        lower_limit = requirement.get("lower_limit")
        upper_limit = requirement.get("upper_limit")
        is_within_spec = True
        if lower_limit is not None and row.measured_value < float(lower_limit):
            is_within_spec = False
        if upper_limit is not None and row.measured_value > float(upper_limit):
            is_within_spec = False

        evaluated.append(
            {
                "item_code": item_code,
                "measured_value": row.measured_value,
                "lower_limit": lower_limit,
                "upper_limit": upper_limit,
                "is_within_spec": is_within_spec,
            }
        )
    return evaluated


def get_quality_measurement_requirements(
    db: Session,
    *,
    tenant_id: str,
    operation_id: int,
) -> QualityOperationRequirementsResponse:
    operation = _resolve_operation_for_tenant(
        db,
        operation_id=operation_id,
        tenant_id=tenant_id,
    )

    if not operation.qc_required:
        return QualityOperationRequirementsResponse(
            operation_id=operation.id,
            operation_number=operation.operation_number,
            operation_name=operation.name,
            qc_required=False,
            items=[],
        )

    return QualityOperationRequirementsResponse(
        operation_id=operation.id,
        operation_number=operation.operation_number,
        operation_name=operation.name,
        qc_required=True,
        template_code=_BASELINE_TEMPLATE_CODE,
        template_name=_BASELINE_TEMPLATE_NAME,
        template_version=_BASELINE_TEMPLATE_VERSION,
        items=[
            QualityRequirementItem(**item)
            for item in _get_requirement_items_for_operation(operation)
        ],
    )


def submit_qc_measurement(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: QualityMeasurementSubmitRequest,
) -> QualityMeasurementSubmitResponse:
    operation = _resolve_operation_for_tenant(
        db, operation_id=payload.operation_id, tenant_id=tenant_id
    )
    if not operation.qc_required:
        raise QualityConflictError("QC_NOT_REQUIRED")

    requirement_map = _get_requirement_map_for_operation(operation)
    active_gate_instance = get_active_quality_gate_instance_for_operation(
        db,
        operation_id=operation.id,
        tenant_id=tenant_id,
    )

    gate_instance_id = payload.gate_instance_id
    gate_instance = None
    if gate_instance_id is None and active_gate_instance is not None:
        raise QualityConflictError("QUALITY_GATE_INSTANCE_CONTEXT_REQUIRED")
    if gate_instance_id is not None:
        gate_instance = get_quality_gate_instance_by_id(
            db,
            gate_instance_id=gate_instance_id,
            tenant_id=tenant_id,
        )
        if gate_instance is None:
            raise LookupError("Quality gate instance not found")
        if gate_instance.operation_id != operation.id:
            raise QualityConflictError("QUALITY_GATE_INSTANCE_OPERATION_MISMATCH")
        if (
            active_gate_instance is not None
            and active_gate_instance.id != gate_instance.id
        ):
            raise QualityConflictError("QUALITY_GATE_INSTANCE_OPERATION_MISMATCH")
        if gate_instance.status not in (
            QualityGateInstanceStatusEnum.PENDING_MEASUREMENT.value,
            QualityGateInstanceStatusEnum.RECHECK_REQUIRED.value,
        ):
            raise QualityConflictError("QUALITY_GATE_INSTANCE_NOT_MEASURABLE")

        gate_instance.status = QualityGateInstanceStatusEnum.PENDING_EVALUATION.value
        gate_instance.review_status = QualityReviewStatusEnum.NO_REVIEW.value
    evaluated = _evaluate_values(
        payload.measurements,
        requirement_map=requirement_map,
    )
    required_item_codes = {
        str(item["item_code"])
        for item in _get_requirement_items_for_operation(operation)
        if bool(item.get("required", True))
    }
    measured_item_codes = {str(row["item_code"]) for row in evaluated}
    missing_required_codes = sorted(required_item_codes - measured_item_codes)
    if missing_required_codes:
        missing_csv = ",".join(missing_required_codes)
        raise ValueError(f"REQUIRED_MEASUREMENTS_MISSING:{missing_csv}")

    has_out_of_spec = any(not row["is_within_spec"] for row in evaluated)
    reported_good_qty = max(int(operation.good_qty or 0), 0)

    quality_status = (
        QualityStatusEnum.QC_HOLD.value
        if has_out_of_spec
        else QualityStatusEnum.QC_PASSED.value
    )
    review_status = (
        QualityReviewStatusEnum.DECISION_PENDING.value
        if has_out_of_spec
        else QualityReviewStatusEnum.NO_REVIEW.value
    )
    accepted_good_release_qty, held_pending_good_qty = _derive_quantity_effects(
        reported_good_qty=reported_good_qty,
        hold_active=has_out_of_spec,
    )

    record = create_measurement_record(
        db,
        operation_id=operation.id,
        gate_instance_id=gate_instance_id,
        submitted_by=actor_user_id,
        quality_status=quality_status,
        review_status=review_status,
        tenant_id=tenant_id,
    )
    values = create_measurement_values(
        db,
        measurement_record_id=record.id,
        values=evaluated,
    )

    hold_id: int | None = None
    if has_out_of_spec:
        hold = create_quality_hold(
            db,
            operation_id=operation.id,
            measurement_record_id=record.id,
            status=QualityHoldStatusEnum.ACTIVE.value,
            review_status=QualityReviewStatusEnum.DECISION_PENDING.value,
            reason="OUT_OF_SPEC_MEASUREMENT",
            created_by=actor_user_id,
            tenant_id=tenant_id,
        )
        hold_id = hold.id

    submitted_at = _utcnow()
    db.add(
        ExecutionEvent(
            event_type="qc_measurement_submitted",
            production_order_id=operation.work_order.production_order_id,
            work_order_id=operation.work_order_id,
            operation_id=operation.id,
            payload={
                "measurement_record_id": record.id,
                "submitted_by": actor_user_id,
                "submitted_at": submitted_at.isoformat(),
            },
            tenant_id=tenant_id,
        )
    )
    db.add(
        ExecutionEvent(
            event_type="qc_result_recorded",
            production_order_id=operation.work_order.production_order_id,
            work_order_id=operation.work_order_id,
            operation_id=operation.id,
            payload={
                "measurement_record_id": record.id,
                "quality_status": quality_status,
                "review_status": review_status,
                "reported_good_qty": reported_good_qty,
                "accepted_good_release_qty": accepted_good_release_qty,
                "held_pending_good_qty": held_pending_good_qty,
            },
            tenant_id=tenant_id,
        )
    )

    if hold_id is not None:
        if gate_instance is not None:
            gate_instance.status = QualityGateInstanceStatusEnum.HOLD_ACTIVE.value
            gate_instance.review_status = QualityReviewStatusEnum.DECISION_PENDING.value
        db.add(
            ExecutionEvent(
                event_type="qc_hold_applied",
                production_order_id=operation.work_order.production_order_id,
                work_order_id=operation.work_order_id,
                operation_id=operation.id,
                payload={
                    "measurement_record_id": record.id,
                    "hold_id": hold_id,
                    "reason": "OUT_OF_SPEC_MEASUREMENT",
                    "review_status": QualityReviewStatusEnum.DECISION_PENDING.value,
                    "held_pending_good_qty": held_pending_good_qty,
                },
                tenant_id=tenant_id,
            )
        )
    elif gate_instance is not None:
        gate_instance.status = QualityGateInstanceStatusEnum.PASSED.value
        gate_instance.review_status = QualityReviewStatusEnum.NO_REVIEW.value

    db.commit()
    db.refresh(record)

    return QualityMeasurementSubmitResponse(
        measurement_record_id=record.id,
        operation_id=record.operation_id,
        gate_instance_id=record.gate_instance_id,
        quality_status=quality_status,
        review_status=review_status,
        accepted_good_release_qty=accepted_good_release_qty,
        held_pending_good_qty=held_pending_good_qty,
        hold_id=hold_id,
        submitted_at=record.submitted_at,
        values=[
            QualityMeasurementValueResult(
                item_code=value.item_code,
                measured_value=value.measured_value,
                lower_limit=value.lower_limit,
                upper_limit=value.upper_limit,
                is_within_spec=value.is_within_spec,
            )
            for value in values
        ],
    )


def list_quality_holds(db: Session, *, tenant_id: str) -> list[QualityHoldItem]:
    rows = list_active_holds(db, tenant_id=tenant_id)
    return [
        QualityHoldItem(
            hold_id=hold.id,
            operation_id=hold.operation_id,
            operation_number=operation.operation_number,
            measurement_record_id=hold.measurement_record_id,
            status=hold.status,
            review_status=hold.review_status,
            reason=hold.reason,
            created_by=hold.created_by,
            created_at=hold.created_at,
        )
        for hold, operation in rows
    ]


def request_quality_deviation(
    db: Session,
    *,
    hold_id: int,
    tenant_id: str,
    actor_user_id: str,
    payload: QualityDeviationRequestCreate,
) -> QualityDeviationRequestItem:
    hold = get_hold_by_id(db, hold_id=hold_id, tenant_id=tenant_id)
    if hold is None:
        raise LookupError("Quality hold not found")
    if hold.status != QualityHoldStatusEnum.ACTIVE.value:
        raise QualityConflictError("HOLD_NOT_ACTIVE")

    existing = get_open_deviation_request_for_hold(
        db,
        hold_id=hold_id,
        tenant_id=tenant_id,
    )
    if existing is not None:
        raise QualityConflictError("DEVIATION_REQUEST_ALREADY_OPEN")

    measurement_record = get_measurement_record_by_id(
        db,
        measurement_record_id=hold.measurement_record_id,
        tenant_id=tenant_id,
    )
    if measurement_record is None:
        raise LookupError("Quality measurement record not found")
    operation = _resolve_operation_for_tenant(
        db,
        operation_id=measurement_record.operation_id,
        tenant_id=tenant_id,
    )

    row = create_deviation_request(
        db,
        hold_id=hold.id,
        gate_instance_id=measurement_record.gate_instance_id,
        requested_by=actor_user_id,
        reason=payload.reason,
        tenant_id=tenant_id,
    )

    db.add(
        ExecutionEvent(
            event_type="quality_deviation_requested",
            production_order_id=operation.work_order.production_order_id,
            work_order_id=operation.work_order_id,
            operation_id=operation.id,
            payload={
                "hold_id": hold.id,
                "deviation_request_id": row.id,
                "requested_by": actor_user_id,
                "reason": payload.reason,
            },
            tenant_id=tenant_id,
        )
    )
    db.commit()
    db.refresh(row)

    return QualityDeviationRequestItem(
        deviation_request_id=row.id,
        hold_id=row.hold_id,
        gate_instance_id=row.gate_instance_id,
        status=row.status,
        requested_by=row.requested_by,
        reason=row.reason,
        requested_at=row.requested_at,
        resolved_by=row.resolved_by,
        resolved_at=row.resolved_at,
        resolution_comment=row.resolution_comment,
    )


def list_quality_deviation_requests(
    db: Session,
    *,
    tenant_id: str,
) -> list[QualityDeviationRequestItem]:
    rows = list_deviation_requests_repo(db, tenant_id=tenant_id)
    return [
        QualityDeviationRequestItem(
            deviation_request_id=row.id,
            hold_id=row.hold_id,
            gate_instance_id=row.gate_instance_id,
            status=row.status,
            requested_by=row.requested_by,
            reason=row.reason,
            requested_at=row.requested_at,
            resolved_by=row.resolved_by,
            resolved_at=row.resolved_at,
            resolution_comment=row.resolution_comment,
        )
        for row in rows
    ]


def resolve_quality_deviation(
    db: Session,
    *,
    deviation_request_id: int,
    tenant_id: str,
    actor_user_id: str,
    actor_role_code: str | None,
    payload: QualityDeviationResolveRequest,
) -> QualityDeviationRequestItem:
    if (actor_role_code or "").upper() != "QAL":
        raise PermissionError("Only QAL may resolve quality deviation by default")

    row = get_deviation_request_by_id(
        db,
        deviation_request_id=deviation_request_id,
        tenant_id=tenant_id,
    )
    if row is None:
        raise LookupError("Quality deviation request not found")
    if row.status != QualityDeviationRequestStatusEnum.OPEN.value:
        raise QualityConflictError("DEVIATION_REQUEST_NOT_OPEN")

    resolution_status = payload.resolution_status.strip().upper()
    if resolution_status not in {
        QualityDeviationRequestStatusEnum.APPROVED.value,
        QualityDeviationRequestStatusEnum.REJECTED.value,
        QualityDeviationRequestStatusEnum.CLOSED.value,
    }:
        raise ValueError(f"Unsupported resolution_status={resolution_status!r}")

    hold = get_hold_by_id(db, hold_id=row.hold_id, tenant_id=tenant_id)
    if hold is None:
        raise LookupError("Quality hold not found")
    measurement_record = get_measurement_record_by_id(
        db,
        measurement_record_id=hold.measurement_record_id,
        tenant_id=tenant_id,
    )
    if measurement_record is None:
        raise LookupError("Quality measurement record not found")
    operation = _resolve_operation_for_tenant(
        db,
        operation_id=measurement_record.operation_id,
        tenant_id=tenant_id,
    )

    row.status = resolution_status
    row.resolved_by = actor_user_id
    row.resolution_comment = payload.resolution_comment
    row.resolved_at = _utcnow()

    if row.gate_instance_id is not None:
        gate_instance = get_quality_gate_instance_by_id(
            db,
            gate_instance_id=row.gate_instance_id,
            tenant_id=tenant_id,
        )
        if (
            gate_instance is not None
            and resolution_status == QualityDeviationRequestStatusEnum.APPROVED.value
        ):
            gate_instance.status = QualityGateInstanceStatusEnum.DEVIATION_PENDING.value
            gate_instance.review_status = QualityReviewStatusEnum.DECISION_PENDING.value

    db.add(
        ExecutionEvent(
            event_type="quality_deviation_resolved",
            production_order_id=operation.work_order.production_order_id,
            work_order_id=operation.work_order_id,
            operation_id=operation.id,
            payload={
                "deviation_request_id": row.id,
                "hold_id": row.hold_id,
                "resolution_status": row.status,
                "resolved_by": actor_user_id,
            },
            tenant_id=tenant_id,
        )
    )
    db.commit()
    db.refresh(row)

    return QualityDeviationRequestItem(
        deviation_request_id=row.id,
        hold_id=row.hold_id,
        gate_instance_id=row.gate_instance_id,
        status=row.status,
        requested_by=row.requested_by,
        reason=row.reason,
        requested_at=row.requested_at,
        resolved_by=row.resolved_by,
        resolved_at=row.resolved_at,
        resolution_comment=row.resolution_comment,
    )


def create_quality_nonconformance(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: QualityNonconformanceCreateRequest,
) -> QualityNonconformanceItem:
    operation = _resolve_operation_for_tenant(
        db,
        operation_id=payload.operation_id,
        tenant_id=tenant_id,
    )

    if payload.hold_id is not None:
        hold = get_hold_by_id(db, hold_id=payload.hold_id, tenant_id=tenant_id)
        if hold is None:
            raise LookupError("Quality hold not found")
        if hold.operation_id != operation.id:
            raise QualityConflictError("NONCONFORMANCE_HOLD_OPERATION_MISMATCH")

    existing = get_nonconformance_by_code(
        db,
        nc_code=payload.nc_code,
        tenant_id=tenant_id,
    )
    if existing is not None:
        raise ValueError("Duplicate nonconformance code in tenant")

    row = create_nonconformance(
        db,
        nc_code=payload.nc_code,
        operation_id=operation.id,
        hold_id=payload.hold_id,
        severity=payload.severity.strip().upper(),
        description=payload.description,
        reported_by=actor_user_id,
        tenant_id=tenant_id,
    )

    db.add(
        ExecutionEvent(
            event_type="quality_nonconformance_recorded",
            production_order_id=operation.work_order.production_order_id,
            work_order_id=operation.work_order_id,
            operation_id=operation.id,
            payload={
                "nonconformance_id": row.id,
                "nc_code": row.nc_code,
                "hold_id": row.hold_id,
                "severity": row.severity,
                "reported_by": actor_user_id,
            },
            tenant_id=tenant_id,
        )
    )
    db.commit()
    db.refresh(row)

    return QualityNonconformanceItem(
        nonconformance_id=row.id,
        nc_code=row.nc_code,
        operation_id=row.operation_id,
        hold_id=row.hold_id,
        status=row.status,
        severity=row.severity,
        description=row.description,
        disposition_code=row.disposition_code,
        reported_by=row.reported_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def list_quality_nonconformances(
    db: Session,
    *,
    tenant_id: str,
) -> list[QualityNonconformanceItem]:
    rows = list_nonconformances_repo(db, tenant_id=tenant_id)
    return [
        QualityNonconformanceItem(
            nonconformance_id=row.id,
            nc_code=row.nc_code,
            operation_id=row.operation_id,
            hold_id=row.hold_id,
            status=row.status,
            severity=row.severity,
            description=row.description,
            disposition_code=row.disposition_code,
            reported_by=row.reported_by,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def record_quality_disposition(
    db: Session,
    *,
    hold_id: int,
    tenant_id: str,
    actor_user_id: str,
    actor_role_code: str | None,
    payload: QualityDispositionRequest,
) -> QualityDispositionResponse:
    if (actor_role_code or "").upper() != "QAL":
        raise PermissionError("Only QAL may record quality disposition by default")

    disposition_code = payload.disposition_code.strip().upper()
    if disposition_code not in _DISPOSITION_STATUS_MAP:
        raise ValueError(f"Unsupported disposition_code={disposition_code!r}")

    hold = get_hold_by_id(db, hold_id=hold_id, tenant_id=tenant_id)
    if hold is None:
        raise LookupError("Quality hold not found")
    if hold.status != QualityHoldStatusEnum.ACTIVE.value:
        raise QualityConflictError("HOLD_NOT_ACTIVE")

    record = get_measurement_record_by_id(
        db,
        measurement_record_id=hold.measurement_record_id,
        tenant_id=tenant_id,
    )
    if record is None:
        raise LookupError("Quality measurement record not found")
    operation = _resolve_operation_for_tenant(
        db,
        operation_id=record.operation_id,
        tenant_id=tenant_id,
    )
    gate_instance = None
    if record.gate_instance_id is not None:
        gate_instance = get_quality_gate_instance_by_id(
            db,
            gate_instance_id=record.gate_instance_id,
            tenant_id=tenant_id,
        )
    reported_good_qty = max(int(operation.good_qty or 0), 0)
    accepted_good_release_qty, held_pending_good_qty = _derive_quantity_effects(
        reported_good_qty=reported_good_qty,
        hold_active=True,
        disposition_code=disposition_code,
    )

    decision = create_disposition_decision(
        db,
        hold_id=hold.id,
        disposition_code=disposition_code,
        decided_by=actor_user_id,
        comment=payload.comment,
        tenant_id=tenant_id,
    )

    linked_ncs = list_nonconformances_by_hold(
        db,
        hold_id=hold.id,
        tenant_id=tenant_id,
    )
    for nc in linked_ncs:
        nc.disposition_code = disposition_code
        nc.status = "DISPOSITIONED"

    record.quality_status = _DISPOSITION_STATUS_MAP[disposition_code]

    if disposition_code == "REQUIRE_RECHECK":
        hold.status = QualityHoldStatusEnum.ACTIVE.value
        hold.review_status = QualityReviewStatusEnum.DECISION_PENDING.value
        record.review_status = QualityReviewStatusEnum.DECISION_PENDING.value
        if gate_instance is not None:
            gate_instance.status = QualityGateInstanceStatusEnum.RECHECK_REQUIRED.value
            gate_instance.review_status = QualityReviewStatusEnum.DECISION_PENDING.value
    else:
        hold.status = QualityHoldStatusEnum.RELEASED.value
        hold.review_status = QualityReviewStatusEnum.DISPOSITION_DONE.value
        record.review_status = QualityReviewStatusEnum.DISPOSITION_DONE.value
        if gate_instance is not None:
            gate_instance.status = QualityGateInstanceStatusEnum.RELEASED.value
            gate_instance.review_status = QualityReviewStatusEnum.DISPOSITION_DONE.value

    db.add(
        ExecutionEvent(
            event_type="disposition_decision_recorded",
            production_order_id=operation.work_order.production_order_id,
            work_order_id=operation.work_order_id,
            operation_id=record.operation_id,
            payload={
                "hold_id": hold.id,
                "disposition_decision_id": decision.id,
                "disposition_code": disposition_code,
                "decided_by": actor_user_id,
                "reported_good_qty": reported_good_qty,
                "accepted_good_release_qty": accepted_good_release_qty,
                "held_pending_good_qty": held_pending_good_qty,
            },
            tenant_id=tenant_id,
        )
    )
    if linked_ncs:
        db.add(
            ExecutionEvent(
                event_type="quality_nonconformance_disposition_linked",
                production_order_id=operation.work_order.production_order_id,
                work_order_id=operation.work_order_id,
                operation_id=record.operation_id,
                payload={
                    "hold_id": hold.id,
                    "disposition_code": disposition_code,
                    "nonconformance_ids": [nc.id for nc in linked_ncs],
                },
                tenant_id=tenant_id,
            )
        )
    if disposition_code == "REQUIRE_RECHECK":
        db.add(
            ExecutionEvent(
                event_type="qc_recheck_requested",
                production_order_id=operation.work_order.production_order_id,
                work_order_id=operation.work_order_id,
                operation_id=record.operation_id,
                payload={
                    "hold_id": hold.id,
                    "disposition_code": disposition_code,
                    "quality_status": record.quality_status,
                },
                tenant_id=tenant_id,
            )
        )
    else:
        db.add(
            ExecutionEvent(
                event_type="qc_hold_released",
                production_order_id=operation.work_order.production_order_id,
                work_order_id=operation.work_order_id,
                operation_id=record.operation_id,
                payload={
                    "hold_id": hold.id,
                    "disposition_code": disposition_code,
                    "quality_status": record.quality_status,
                },
                tenant_id=tenant_id,
            )
        )
    record_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="QUALITY.DISPOSITION_RECORDED",
        resource_type="QUALITY_HOLD",
        resource_id=str(hold.id),
        detail=(
            f"disposition_code={disposition_code}"
            f" quality_status={record.quality_status}"
        ),
        commit=False,
    )
    db.commit()
    db.refresh(decision)

    return QualityDispositionResponse(
        hold_id=hold.id,
        disposition_decision_id=decision.id,
        disposition_code=disposition_code,
        quality_status=record.quality_status,
        review_status=record.review_status,
        hold_status=hold.status,
        accepted_good_release_qty=accepted_good_release_qty,
        held_pending_good_qty=held_pending_good_qty,
        decided_by=decision.decided_by,
        decided_at=decision.created_at,
    )
