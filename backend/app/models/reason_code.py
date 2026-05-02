from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Text, UniqueConstraint, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ReasonCodeLifecycleStatus(str, Enum):
    DRAFT = "DRAFT"
    RELEASED = "RELEASED"
    RETIRED = "RETIRED"


class ReasonCodeDomain(str, Enum):
    EXECUTION_PAUSE = "EXECUTION_PAUSE"
    DOWNTIME = "DOWNTIME"
    SCRAP = "SCRAP"
    QUALITY_HOLD = "QUALITY_HOLD"
    MAINTENANCE = "MAINTENANCE"
    MATERIAL = "MATERIAL"
    REWORK = "REWORK"
    EXCEPTION = "EXCEPTION"
    GENERAL = "GENERAL"


class ReasonCode(Base):
    __tablename__ = "reason_codes"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "reason_domain", "reason_code",
            name="uq_reason_codes_tenant_domain_code"
        ),
    )

    reason_code_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    reason_domain: Mapped[str] = mapped_column(String(32), nullable=False)
    reason_category: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT")
    requires_comment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
