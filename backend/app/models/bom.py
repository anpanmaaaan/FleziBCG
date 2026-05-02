from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Bom(Base):
    """Manufacturing BOM definition (read model foundation, MMD-BE-05).

    Boundary lock:
    - Product-scoped definition only.
    - No product_version_id runtime binding in this slice.
    - No execution/inventory/backflush/ERP/traceability behavior fields.
    """

    __tablename__ = "boms"
    __table_args__ = (
        UniqueConstraint("tenant_id", "product_id", "bom_code", name="uq_boms_tenant_product_code"),
    )

    bom_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.product_id"), nullable=False, index=True
    )
    bom_code: Mapped[str] = mapped_column(String(64), nullable=False)
    bom_name: Mapped[str] = mapped_column(String(256), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT")
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    items: Mapped[list[BomItem]] = relationship(
        "BomItem",
        back_populates="bom",
        cascade="all, delete-orphan",
        order_by="BomItem.line_no.asc()",
    )


class BomItem(Base):
    __tablename__ = "bom_items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "bom_id", "line_no", name="uq_bom_items_tenant_bom_line_no"),
    )

    bom_item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    bom_id: Mapped[str] = mapped_column(String(64), ForeignKey("boms.bom_id"), nullable=False, index=True)
    component_product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.product_id"), nullable=False, index=True
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(32), nullable=False)
    scrap_factor: Mapped[float | None] = mapped_column(Float, nullable=True)
    reference_designator: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    bom: Mapped[Bom] = relationship("Bom", back_populates="items")
