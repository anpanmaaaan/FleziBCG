from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.master import Operation
from app.models.quality import (
    QualityGateDefinition,
    QualityGateInstance,
    QualityDispositionDecision,
    QualityHold,
    QualityMeasurementRecord,
    QualityMeasurementValue,
    QualityDeviationRequest,
    QualityNonconformance,
)


def create_measurement_record(
    db: Session,
    *,
    operation_id: int,
    gate_instance_id: int | None,
    submitted_by: str,
    quality_status: str,
    review_status: str,
    tenant_id: str,
) -> QualityMeasurementRecord:
    record = QualityMeasurementRecord(
        operation_id=operation_id,
        gate_instance_id=gate_instance_id,
        submitted_by=submitted_by,
        quality_status=quality_status,
        review_status=review_status,
        tenant_id=tenant_id,
    )
    db.add(record)
    db.flush()
    return record


def create_measurement_values(
    db: Session,
    *,
    measurement_record_id: int,
    values: list[dict],
) -> list[QualityMeasurementValue]:
    rows: list[QualityMeasurementValue] = []
    for value in values:
        row = QualityMeasurementValue(
            measurement_record_id=measurement_record_id,
            item_code=value["item_code"],
            measured_value=value["measured_value"],
            lower_limit=value.get("lower_limit"),
            upper_limit=value.get("upper_limit"),
            is_within_spec=value["is_within_spec"],
        )
        db.add(row)
        rows.append(row)
    db.flush()
    return rows


def create_quality_hold(
    db: Session,
    *,
    operation_id: int,
    measurement_record_id: int,
    status: str,
    review_status: str,
    reason: str,
    created_by: str,
    tenant_id: str,
) -> QualityHold:
    hold = QualityHold(
        operation_id=operation_id,
        measurement_record_id=measurement_record_id,
        status=status,
        review_status=review_status,
        reason=reason,
        created_by=created_by,
        tenant_id=tenant_id,
    )
    db.add(hold)
    db.flush()
    return hold


def list_active_holds(db: Session, *, tenant_id: str) -> list[tuple[QualityHold, Operation]]:
    statement = (
        select(QualityHold, Operation)
        .join(Operation, Operation.id == QualityHold.operation_id)
        .where(QualityHold.tenant_id == tenant_id, QualityHold.status == "ACTIVE")
        .order_by(QualityHold.created_at.desc(), QualityHold.id.desc())
    )
    return list(db.execute(statement).all())


def get_hold_by_id(db: Session, *, hold_id: int, tenant_id: str) -> QualityHold | None:
    statement = select(QualityHold).where(
        QualityHold.id == hold_id,
        QualityHold.tenant_id == tenant_id,
    )
    return db.scalar(statement)


def get_measurement_record_by_id(
    db: Session, *, measurement_record_id: int, tenant_id: str
) -> QualityMeasurementRecord | None:
    statement = select(QualityMeasurementRecord).where(
        QualityMeasurementRecord.id == measurement_record_id,
        QualityMeasurementRecord.tenant_id == tenant_id,
    )
    return db.scalar(statement)


def create_disposition_decision(
    db: Session,
    *,
    hold_id: int,
    disposition_code: str,
    decided_by: str,
    comment: str | None,
    tenant_id: str,
) -> QualityDispositionDecision:
    decision = QualityDispositionDecision(
        hold_id=hold_id,
        disposition_code=disposition_code,
        decided_by=decided_by,
        comment=comment,
        tenant_id=tenant_id,
    )
    db.add(decision)
    db.flush()
    return decision


def has_active_hold_for_operation(
    db: Session,
    *,
    operation_id: int,
    tenant_id: str,
) -> bool:
    statement = (
        select(QualityHold.id)
        .where(
            QualityHold.operation_id == operation_id,
            QualityHold.tenant_id == tenant_id,
            QualityHold.status == "ACTIVE",
        )
        .limit(1)
    )
    return db.scalar(statement) is not None


def create_quality_gate_definition(
    db: Session,
    *,
    code: str,
    name: str,
    status: str,
    gate_type: str,
    rule_set_version: str,
    applicability_scope_type: str | None,
    applicability_scope_value: str | None,
    tenant_id: str,
    created_by: str,
) -> QualityGateDefinition:
    row = QualityGateDefinition(
        code=code,
        name=name,
        status=status,
        gate_type=gate_type,
        rule_set_version=rule_set_version,
        applicability_scope_type=applicability_scope_type,
        applicability_scope_value=applicability_scope_value,
        tenant_id=tenant_id,
        created_by=created_by,
    )
    db.add(row)
    db.flush()
    return row


def list_quality_gate_definitions(
    db: Session,
    *,
    tenant_id: str,
) -> list[QualityGateDefinition]:
    statement = (
        select(QualityGateDefinition)
        .where(QualityGateDefinition.tenant_id == tenant_id)
        .order_by(QualityGateDefinition.id.desc())
    )
    return list(db.scalars(statement))


def get_quality_gate_definition_by_id(
    db: Session,
    *,
    gate_definition_id: int,
    tenant_id: str,
) -> QualityGateDefinition | None:
    statement = select(QualityGateDefinition).where(
        QualityGateDefinition.id == gate_definition_id,
        QualityGateDefinition.tenant_id == tenant_id,
    )
    return db.scalar(statement)


def create_quality_gate_instance(
    db: Session,
    *,
    gate_definition_id: int,
    operation_id: int,
    status: str,
    review_status: str,
    opened_by: str,
    tenant_id: str,
) -> QualityGateInstance:
    row = QualityGateInstance(
        gate_definition_id=gate_definition_id,
        operation_id=operation_id,
        status=status,
        review_status=review_status,
        opened_by=opened_by,
        tenant_id=tenant_id,
    )
    db.add(row)
    db.flush()
    return row


def get_active_quality_gate_instance_for_operation(
    db: Session,
    *,
    operation_id: int,
    tenant_id: str,
) -> QualityGateInstance | None:
    statement = (
        select(QualityGateInstance)
        .where(
            QualityGateInstance.operation_id == operation_id,
            QualityGateInstance.tenant_id == tenant_id,
            QualityGateInstance.status != "CLOSED",
        )
        .order_by(QualityGateInstance.id.desc())
        .limit(1)
    )
    return db.scalar(statement)


def get_quality_gate_instance_by_id(
    db: Session,
    *,
    gate_instance_id: int,
    tenant_id: str,
) -> QualityGateInstance | None:
    statement = select(QualityGateInstance).where(
        QualityGateInstance.id == gate_instance_id,
        QualityGateInstance.tenant_id == tenant_id,
    )
    return db.scalar(statement)


def get_open_deviation_request_for_hold(
    db: Session,
    *,
    hold_id: int,
    tenant_id: str,
) -> QualityDeviationRequest | None:
    statement = (
        select(QualityDeviationRequest)
        .where(
            QualityDeviationRequest.hold_id == hold_id,
            QualityDeviationRequest.tenant_id == tenant_id,
            QualityDeviationRequest.status == "OPEN",
        )
        .order_by(QualityDeviationRequest.id.desc())
        .limit(1)
    )
    return db.scalar(statement)


def get_deviation_request_by_id(
    db: Session,
    *,
    deviation_request_id: int,
    tenant_id: str,
) -> QualityDeviationRequest | None:
    statement = select(QualityDeviationRequest).where(
        QualityDeviationRequest.id == deviation_request_id,
        QualityDeviationRequest.tenant_id == tenant_id,
    )
    return db.scalar(statement)


def create_deviation_request(
    db: Session,
    *,
    hold_id: int,
    gate_instance_id: int | None,
    requested_by: str,
    reason: str,
    tenant_id: str,
) -> QualityDeviationRequest:
    row = QualityDeviationRequest(
        hold_id=hold_id,
        gate_instance_id=gate_instance_id,
        status="OPEN",
        requested_by=requested_by,
        reason=reason,
        tenant_id=tenant_id,
    )
    db.add(row)
    db.flush()
    return row


def list_deviation_requests(
    db: Session,
    *,
    tenant_id: str,
) -> list[QualityDeviationRequest]:
    statement = (
        select(QualityDeviationRequest)
        .where(QualityDeviationRequest.tenant_id == tenant_id)
        .order_by(QualityDeviationRequest.id.desc())
    )
    return list(db.scalars(statement))


def get_nonconformance_by_code(
    db: Session,
    *,
    nc_code: str,
    tenant_id: str,
) -> QualityNonconformance | None:
    statement = select(QualityNonconformance).where(
        QualityNonconformance.nc_code == nc_code,
        QualityNonconformance.tenant_id == tenant_id,
    )
    return db.scalar(statement)


def create_nonconformance(
    db: Session,
    *,
    nc_code: str,
    operation_id: int,
    hold_id: int | None,
    severity: str,
    description: str,
    reported_by: str,
    tenant_id: str,
) -> QualityNonconformance:
    row = QualityNonconformance(
        nc_code=nc_code,
        operation_id=operation_id,
        hold_id=hold_id,
        status="OPEN",
        severity=severity,
        description=description,
        disposition_code=None,
        reported_by=reported_by,
        tenant_id=tenant_id,
    )
    db.add(row)
    db.flush()
    return row


def list_nonconformances(
    db: Session,
    *,
    tenant_id: str,
) -> list[QualityNonconformance]:
    statement = (
        select(QualityNonconformance)
        .where(QualityNonconformance.tenant_id == tenant_id)
        .order_by(QualityNonconformance.id.desc())
    )
    return list(db.scalars(statement))


def list_nonconformances_by_hold(
    db: Session,
    *,
    hold_id: int,
    tenant_id: str,
) -> list[QualityNonconformance]:
    statement = (
        select(QualityNonconformance)
        .where(
            QualityNonconformance.hold_id == hold_id,
            QualityNonconformance.tenant_id == tenant_id,
        )
        .order_by(QualityNonconformance.id.asc())
    )
    return list(db.scalars(statement))
