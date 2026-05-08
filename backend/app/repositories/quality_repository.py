from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.master import Operation
from app.models.quality import (
    QualityDispositionDecision,
    QualityHold,
    QualityMeasurementRecord,
    QualityMeasurementValue,
)


def create_measurement_record(
    db: Session,
    *,
    operation_id: int,
    submitted_by: str,
    quality_status: str,
    review_status: str,
    tenant_id: str,
) -> QualityMeasurementRecord:
    record = QualityMeasurementRecord(
        operation_id=operation_id,
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
