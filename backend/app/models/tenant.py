"""Tenant lifecycle anchor ORM model (P0-A-02A).

WHY: All existing models carry tenant_id as an unconstrained string. This
module adds the canonical Tenant table so that future Admin, scope assignment,
tenant lifecycle governance, and stronger tenant isolation can anchor to a
real row rather than a floating string.

INVARIANTS (P0-A-02A):
- Existing tenant_id string columns in other models are NOT modified in this
  slice. No FK retrofit is performed here.
- Tenant lifecycle status is stored but NOT enforced in auth/session/API yet.
  Enforcement is deferred to a future slice.
- No API endpoints are added in this slice.
- No Admin UI is added in this slice.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base

# Lifecycle status constants — plain strings (not a DB-native enum) so that
# values survive DB introspection without enum type registration. Follows the
# same pattern as user.LIFECYCLE_STATUS_* constants.
TENANT_STATUS_ACTIVE = "ACTIVE"
TENANT_STATUS_DISABLED = "DISABLED"
TENANT_STATUS_SUSPENDED = "SUSPENDED"


class Tenant(Base):
    """Canonical tenant anchor.

    One row per tenant. Lifecycle status tracks operational state.
    Enforcement of lifecycle in auth/session is deferred to a future slice.
    """

    __tablename__ = "tenants"
    __table_args__ = (
        UniqueConstraint("tenant_code", name="uq_tenants_tenant_code"),
        Index("ix_tenants_tenant_code", "tenant_code"),
        Index("ix_tenants_lifecycle_status", "lifecycle_status"),
        Index("ix_tenants_is_active", "is_active"),
    )

    tenant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_code: Mapped[str] = mapped_column(String(64), nullable=False)
    tenant_name: Mapped[str] = mapped_column(String(256), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=TENANT_STATUS_ACTIVE,
        server_default=TENANT_STATUS_ACTIVE,
    )
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    locale: Mapped[str | None] = mapped_column(String(32), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    @property
    def is_lifecycle_active(self) -> bool:
        """True only when both is_active and lifecycle_status indicate an active tenant.

        Future enforcement in auth/session MUST use this property so the
        invariant is checked in one place.
        """
        return self.is_active and self.lifecycle_status == TENANT_STATUS_ACTIVE

    def __init__(self, **kwargs: object) -> None:
        # Ensure lifecycle_status and is_active default at Python construction
        # time. SQLAlchemy mapped_column(default=...) only applies at INSERT;
        # this override guarantees attributes are never None before flush.
        kwargs.setdefault("lifecycle_status", TENANT_STATUS_ACTIVE)
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)
