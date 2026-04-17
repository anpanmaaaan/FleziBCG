from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class OperationClaim(Base):
    __tablename__ = "operation_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False, index=True
    )
    station_scope_id: Mapped[int] = mapped_column(
        ForeignKey("scopes.id"), nullable=False, index=True
    )
    claimed_by_user_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    claimed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # INTENT: Auto-release mechanism. If an operator abandons a station without
    # explicitly releasing, the claim expires after claim_default_ttl_minutes.
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # WHY: released_at is NULL while the claim is active. A non-NULL value
    # means the operator (or supervisor) explicitly released the station.
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    release_reason: Mapped[str | None] = mapped_column(
        String(256), nullable=True, default=None
    )

    operation = relationship("Operation")


class OperationClaimAuditLog(Base):
    __tablename__ = "operation_claim_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # WHY: Nullable because audit events can be recorded before a claim row
    # exists (e.g., failed claim attempts or queue entries).
    claim_id: Mapped[int | None] = mapped_column(
        ForeignKey("operation_claims.id"), nullable=True, index=True
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    operation_id: Mapped[int] = mapped_column(
        ForeignKey("operations.id"), nullable=False, index=True
    )
    station_scope_id: Mapped[int] = mapped_column(
        ForeignKey("scopes.id"), nullable=False, index=True
    )
    actor_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    acting_role_code: Mapped[str | None] = mapped_column(
        String(32), nullable=True, default=None
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    claim = relationship("OperationClaim")
