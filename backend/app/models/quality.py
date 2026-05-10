from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
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


class QualityGateDefinitionStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class QualityGateTypeEnum(str, Enum):
    PRE_ACCEPTANCE = "PRE_ACCEPTANCE"


class QualityGateInstanceStatusEnum(str, Enum):
    PENDING_MEASUREMENT = "PENDING_MEASUREMENT"
    PENDING_EVALUATION = "PENDING_EVALUATION"
    PASSED = "PASSED"
    HOLD_ACTIVE = "HOLD_ACTIVE"
    DEVIATION_PENDING = "DEVIATION_PENDING"
    RECHECK_REQUIRED = "RECHECK_REQUIRED"
    RELEASED = "RELEASED"
    CLOSED = "CLOSED"


class QualityDeviationRequestStatusEnum(str, Enum):
    OPEN = "OPEN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class QualityNonconformanceStatusEnum(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    DISPOSITIONED = "DISPOSITIONED"
    CLOSED = "CLOSED"


class QualityMeasurementRecord(Base):
    __tablename__ = "quality_measurement_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False, index=True
    )
    gate_instance_id: Mapped[int | None] = mapped_column(
        ForeignKey("quality_gate_instances.id"), nullable=True, index=True
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


class QualityGateDefinition(Base):
    __tablename__ = "quality_gate_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    gate_type: Mapped[str] = mapped_column(String(32), nullable=False)
    rule_set_version: Mapped[str] = mapped_column(String(64), nullable=False)
    applicability_scope_type: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    applicability_scope_value: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    instances: Mapped[list["QualityGateInstance"]] = relationship(
        "QualityGateInstance",
        back_populates="definition",
    )


class QualityGateInstance(Base):
    __tablename__ = "quality_gate_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gate_definition_id: Mapped[int] = mapped_column(
        ForeignKey("quality_gate_definitions.id"), nullable=False, index=True
    )
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    opened_by: Mapped[str] = mapped_column(String(128), nullable=False)
    closed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    definition: Mapped[QualityGateDefinition] = relationship(
        "QualityGateDefinition",
        back_populates="instances",
    )


class QualityApplicabilityPolicy(Base):
    __tablename__ = "quality_applicability_policies"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "policy_code",
            name="uq_quality_applicability_policies_tenant_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_code: Mapped[str] = mapped_column(String(64), nullable=False)
    policy_name: Mapped[str] = mapped_column(String(128), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(32), nullable=False)
    scope_value: Mapped[str] = mapped_column(String(128), nullable=False)
    qc_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    gate_definition_id: Mapped[int | None] = mapped_column(
        ForeignKey("quality_gate_definitions.id"),
        nullable=True,
    )
    lifecycle_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="DRAFT"
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class QualityRuleSet(Base):
    __tablename__ = "quality_rule_sets"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "rule_set_code",
            "rule_set_version",
            name="uq_quality_rule_sets_tenant_code_version",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_set_code: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_set_name: Mapped[str] = mapped_column(String(128), nullable=False)
    rule_set_version: Mapped[str] = mapped_column(String(64), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="DRAFT"
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    rules: Mapped[list["QualityRuleDefinition"]] = relationship(
        "QualityRuleDefinition",
        back_populates="rule_set",
        cascade="all, delete-orphan",
    )


class QualityRuleDefinition(Base):
    __tablename__ = "quality_rule_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_set_id: Mapped[int] = mapped_column(
        ForeignKey("quality_rule_sets.id"), nullable=False, index=True
    )
    item_code: Mapped[str] = mapped_column(String(64), nullable=False)
    evaluation_operator: Mapped[str] = mapped_column(String(32), nullable=False)
    lower_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    upper_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_boolean: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    rule_set: Mapped[QualityRuleSet] = relationship(
        "QualityRuleSet",
        back_populates="rules",
    )


class QualityDispositionCatalog(Base):
    __tablename__ = "quality_disposition_catalog"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "disposition_code",
            name="uq_quality_disposition_catalog_tenant_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    disposition_code: Mapped[str] = mapped_column(String(64), nullable=False)
    disposition_name: Mapped[str] = mapped_column(String(128), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="DRAFT"
    )
    requires_comment: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    requires_quality_approval: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    releases_hold: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quality_status_target: Mapped[str] = mapped_column(String(32), nullable=False)
    review_status_target: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class QualityDeviationRequest(Base):
    __tablename__ = "quality_deviation_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hold_id: Mapped[int] = mapped_column(
        ForeignKey("quality_holds.id"), nullable=False, index=True
    )
    gate_instance_id: Mapped[int | None] = mapped_column(
        ForeignKey("quality_gate_instances.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    requested_by: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)


class QualityNonconformance(Base):
    __tablename__ = "quality_nonconformances"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "nc_code",
            name="uq_quality_nonconformances_tenant_nc_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nc_code: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False, index=True
    )
    hold_id: Mapped[int | None] = mapped_column(
        ForeignKey("quality_holds.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    disposition_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reported_by: Mapped[str] = mapped_column(String(128), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
