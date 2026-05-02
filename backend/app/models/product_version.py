from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ProductVersion(Base):
    """Versioned manufacturing definition context for a Product.

    WHY: Product Version is required by P0-B MMD baseline (MMD-BE-03).
    It represents a versioned snapshot of the manufacturing definition context
    for a product. It does not replace ERP/PLM revision truth. BOM, Routing,
    and Resource Requirement bindings to Product Version are deferred.

    INVARIANTS:
    - tenant_id is always set and is part of all read queries.
    - product_id FK references products.product_id (tenant boundary relies on
      the parent product's tenant_id — callers must also filter tenant_id).
    - version_code is unique within (tenant_id, product_id).
    - is_current is advisory; partial-unique enforcement is deferred.
    - No write-path endpoints exist in this slice.
    """

    __tablename__ = "product_versions"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "product_id", "version_code",
            name="uq_product_versions_tenant_product_code",
        ),
    )

    product_version_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.product_id"), nullable=False, index=True
    )
    version_code: Mapped[str] = mapped_column(String(64), nullable=False)
    version_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    lifecycle_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="DRAFT"
    )
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
