from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Routing(Base):
    __tablename__ = "routings"
    __table_args__ = (
        UniqueConstraint("tenant_id", "routing_code", name="uq_routings_tenant_code"),
    )

    routing_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(64), ForeignKey("products.product_id"), nullable=False, index=True)
    routing_code: Mapped[str] = mapped_column(String(64), nullable=False)
    routing_name: Mapped[str] = mapped_column(String(256), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    operations: Mapped[list[RoutingOperation]] = relationship(
        "RoutingOperation",
        back_populates="routing",
        cascade="all, delete-orphan",
        order_by="RoutingOperation.sequence_no.asc()",
    )


class RoutingOperation(Base):
    __tablename__ = "routing_operations"
    __table_args__ = (
        UniqueConstraint("routing_id", "sequence_no", name="uq_routing_ops_sequence"),
    )

    operation_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    routing_id: Mapped[str] = mapped_column(String(64), ForeignKey("routings.routing_id"), nullable=False, index=True)
    operation_code: Mapped[str] = mapped_column(String(64), nullable=False)
    operation_name: Mapped[str] = mapped_column(String(256), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    standard_cycle_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    required_resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # WHY: v1.2 contract boundary patch — RoutingOperation-owned extended fields.
    # All nullable per routing-foundation-contract.md Section 3 (extended structure).
    setup_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    run_time_per_unit: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_center_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    routing: Mapped[Routing] = relationship("Routing", back_populates="operations")
