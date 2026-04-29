from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ResourceRequirement(Base):
    __tablename__ = "resource_requirements"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "operation_id",
            "required_resource_type",
            "required_capability_code",
            name="uq_rr_tenant_operation_type_capability",
        ),
    )

    requirement_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    routing_id: Mapped[str] = mapped_column(String(64), ForeignKey("routings.routing_id"), nullable=False, index=True)
    operation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("routing_operations.operation_id"),
        nullable=False,
        index=True,
    )
    required_resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    required_capability_code: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity_required: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
