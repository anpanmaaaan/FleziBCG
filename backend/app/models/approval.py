from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class ApprovalRule(Base):
    __tablename__ = "approval_rules"
    # INVARIANT: (action_type, approver_role_code, tenant_id) must be unique
    # to prevent duplicate rule grants that would break approval logic.
    __table_args__ = (
        UniqueConstraint(
            "action_type", "approver_role_code", "tenant_id", name="uq_approval_rule"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    approver_role_code: Mapped[str] = mapped_column(String(32), nullable=False)
    # WHY: Wildcard "*" makes the rule apply to all tenants. Tenant-specific
    # rules override the wildcard when both exist (see approval_repository ordering).
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default="*")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    requester_id: Mapped[str] = mapped_column(String(64), nullable=False)
    requester_role_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    subject_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subject_ref: Mapped[str | None] = mapped_column(String(256), nullable=True)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    decisions: Mapped[list["ApprovalDecision"]] = relationship(
        "ApprovalDecision", back_populates="request", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["ApprovalAuditLog"]] = relationship(
        "ApprovalAuditLog", back_populates="request", cascade="all, delete-orphan"
    )


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("approval_requests.id"), nullable=False, index=True
    )
    decider_id: Mapped[str] = mapped_column(String(64), nullable=False)
    decider_role_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    comment: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # INVARIANT: Links the decision to an impersonation session (if any) so the
    # audit trail always records who really approved, even under impersonation.
    impersonation_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("impersonation_sessions.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    request: Mapped["ApprovalRequest"] = relationship(
        "ApprovalRequest", back_populates="decisions"
    )


class ApprovalAuditLog(Base):
    __tablename__ = "approval_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("approval_requests.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    role_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    detail: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    request: Mapped["ApprovalRequest"] = relationship(
        "ApprovalRequest", back_populates="audit_logs"
    )
