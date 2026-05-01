from datetime import datetime

from sqlalchemy import DateTime, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class RefreshToken(Base):
    """Persisted refresh token record.

    INVARIANT: Raw token values are NEVER stored here.
    Only the SHA-256 hash of the raw token is persisted in ``token_hash``.

    WHY: Refresh tokens are long-lived credentials. Storing hashes only means
    a DB compromise does not directly expose usable tokens.

    token_family_id groups tokens in a rotation chain. On each rotation:
      - the old record gains ``rotated_at`` (treated as revoked);
      - a new record is created with the same ``token_family_id``.
    Detecting use of a rotated token signals a reuse attack.

    session_id is a soft reference (no DB FK) — consistent with the existing
    codebase convention where ``sessions.user_id`` is also a soft reference to
    ``users.user_id``.
    """

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_token_hash"),
        Index("ix_refresh_tokens_tenant_user", "tenant_id", "user_id"),
        Index("ix_refresh_tokens_session_id", "session_id"),
        Index("ix_refresh_tokens_family", "token_family_id"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # WHY: token_id is a separate string identifier for cross-service references.
    token_id: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    # SOFT REFERENCE: session_id links to sessions.session_id without a DB FK.
    session_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, default=None
    )
    # SECURITY: SHA-256 hex digest of the raw token. Never the raw token itself.
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    # ROTATION: All tokens in a rotation chain share the same token_family_id.
    token_family_id: Mapped[str] = mapped_column(String(64), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # LIFECYCLE: rotated_at is set when this token is exchanged for a newer one.
    # A non-None rotated_at means the token cannot validate.
    rotated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    # LIFECYCLE: revoked_at is set on explicit revocation (logout, admin).
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    revoke_reason: Mapped[str | None] = mapped_column(
        String(256), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
