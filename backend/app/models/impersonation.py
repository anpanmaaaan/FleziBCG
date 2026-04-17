from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ImpersonationSession(Base):
    __tablename__ = "impersonation_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    real_user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    real_role_code: Mapped[str] = mapped_column(String(32), nullable=False)
    acting_role_code: Mapped[str] = mapped_column(String(32), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    audit_logs: Mapped[list["ImpersonationAuditLog"]] = relationship(
        "ImpersonationAuditLog",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    @property
    def is_active(self) -> bool:
        if self.revoked_at is not None:
            return False
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now < expires


class ImpersonationAuditLog(Base):
    __tablename__ = "impersonation_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("impersonation_sessions.id"), nullable=False, index=True
    )
    real_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    acting_role_code: Mapped[str] = mapped_column(String(32), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    permission_family: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default=None
    )
    endpoint: Mapped[str | None] = mapped_column(
        String(256), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    session: Mapped[ImpersonationSession] = relationship(
        "ImpersonationSession", back_populates="audit_logs"
    )
