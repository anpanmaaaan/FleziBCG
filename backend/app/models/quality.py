from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class QualityStatusEnum(str, Enum):
    QC_NOT_REQUIRED = "QC_NOT_REQUIRED"
    QC_PENDING = "QC_PENDING"
    QC_PASSED = "QC_PASSED"
    QC_FAILED = "QC_FAILED"
    QC_HOLD = "QC_HOLD"


class QualityReviewStatusEnum(str, Enum):
    NO_REVIEW = "NO_REVIEW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    DECISION_PENDING = "DECISION_PENDING"
    DISPOSITION_DONE = "DISPOSITION_DONE"


class QualityHoldStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


class QualityMeasurementRecord(Base):
    __tablename__ = "quality_measurement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False, index=True
    )
    submitted_by: Mapped[str] = mapped_column(String(128), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    quality_status: Mapped[str] = mapped_column(String(32), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    values: Mapped[list["QualityMeasurementValue"]] = relationship(
        "QualityMeasurementValue",
        back_populates="record",
        cascade="all, delete-orphan",
    )


class QualityMeasurementValue(Base):
    __tablename__ = "quality_measurement_values"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_record_id: Mapped[int] = mapped_column(
        ForeignKey("quality_measurement_records.id"), nullable=False, index=True
    )
    item_code: Mapped[str] = mapped_column(String(64), nullable=False)
    measured_value: Mapped[float] = mapped_column(Float, nullable=False)
    lower_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    upper_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_within_spec: Mapped[bool] = mapped_column(Boolean, nullable=False)

    record: Mapped[QualityMeasurementRecord] = relationship(
        "QualityMeasurementRecord", back_populates="values"
    )


class QualityHold(Base):
    __tablename__ = "quality_holds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False, index=True
    )
    measurement_record_id: Mapped[int] = mapped_column(
        ForeignKey("quality_measurement_records.id"), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class QualityDispositionDecision(Base):
    __tablename__ = "quality_disposition_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hold_id: Mapped[int] = mapped_column(
        ForeignKey("quality_holds.id"), nullable=False, index=True
    )
    disposition_code: Mapped[str] = mapped_column(String(64), nullable=False)
    decided_by: Mapped[str] = mapped_column(String(128), nullable=False)
    comment: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
