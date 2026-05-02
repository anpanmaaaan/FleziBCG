from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base

# Minimal lifecycle status constants — not a DB-native enum so the column
# value survives DB introspection without enum type registration.
LIFECYCLE_STATUS_ACTIVE = "ACTIVE"
LIFECYCLE_STATUS_DISABLED = "DISABLED"
LIFECYCLE_STATUS_LOCKED = "LOCKED"


class User(Base):
    __tablename__ = "users"
    # INVARIANT: Same username may exist in different tenants (multi-tenant
    # isolation). The unique constraint is on the (username, tenant_id) pair,
    # NOT on username alone.
    __table_args__ = (
        UniqueConstraint("username", "tenant_id", name="uq_username_tenant"),
        Index("ix_users_lifecycle_status", "lifecycle_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # WHY: user_id is a separate string identifier (not the auto-int PK) because
    # it is carried in JWT claims and used across service boundaries.
    user_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    tenant_id: Mapped[str] = mapped_column(
        String(64), nullable=False, default="default"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # WHY: lifecycle_status provides fine-grained account state beyond the boolean
    # is_active flag. Allowed values: ACTIVE, DISABLED, LOCKED.
    # is_active is retained for backward compatibility — auth checks require BOTH.
    # server_default ensures existing rows are backfilled by the migration and new
    # rows created outside the ORM get a safe default.
    lifecycle_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=LIFECYCLE_STATUS_ACTIVE,
        server_default=LIFECYCLE_STATUS_ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    @property
    def is_lifecycle_active(self) -> bool:
        """True only when both is_active and lifecycle_status indicate an active account.

        Auth eligibility MUST use this property rather than checking the two
        fields separately, so the invariant is enforced in one place.
        """
        return self.is_active and self.lifecycle_status == LIFECYCLE_STATUS_ACTIVE

    def __init__(self, **kwargs: object) -> None:
        # Ensure lifecycle_status defaults to ACTIVE at Python construction time.
        # SQLAlchemy mapped_column(default=...) only applies at INSERT time;
        # this override guarantees the attribute is never None before flush.
        kwargs.setdefault("lifecycle_status", LIFECYCLE_STATUS_ACTIVE)
        super().__init__(**kwargs)
