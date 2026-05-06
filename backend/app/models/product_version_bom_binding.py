from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ProductVersionBomBinding(Base):
    """Association entity linking a ProductVersion to a BOM.

    Boundary lock (MMD-BE-14):
    - Definition applicability metadata only.
    - No execution/material/inventory/ERP/traceability/quality behavior.
    - binding_type PRIMARY only in this slice.
    - effective_from/effective_to deferred to a later effective-dating slice.
    - One ACTIVE PRIMARY binding per Product Version enforced at service layer.
    - Historical REMOVED rows remain readable.
    """

    __tablename__ = "product_version_bom_bindings"

    binding_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.product_id"), nullable=False, index=True
    )
    product_version_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("product_versions.product_version_id"),
        nullable=False,
        index=True,
    )
    bom_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("boms.bom_id"), nullable=False, index=True
    )
    binding_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="PRIMARY"
    )
    binding_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="ACTIVE"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
