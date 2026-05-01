"""Repository for RefreshToken records.

INVARIANT: All queries are tenant-scoped. No query may return tokens
belonging to a different tenant, even if token_hash matches.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def create_refresh_token(db: Session, record: RefreshToken) -> RefreshToken:
    db.add(record)
    db.flush()
    return record


def get_by_token_hash(
    db: Session,
    *,
    tenant_id: str,
    token_hash: str,
) -> RefreshToken | None:
    # INVARIANT: tenant_id filter ensures cross-tenant hash collision cannot
    # return a token from a different tenant.
    return db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.tenant_id == tenant_id,
        )
    )


def revoke_by_token_hash(
    db: Session,
    *,
    tenant_id: str,
    token_hash: str,
    reason: str,
) -> bool:
    record = get_by_token_hash(db, tenant_id=tenant_id, token_hash=token_hash)
    if record is None:
        return False
    if record.revoked_at is not None:
        return True
    now = datetime.now(timezone.utc)
    record.revoked_at = now
    record.revoke_reason = reason[:256]
    db.flush()
    return True


def mark_rotated(db: Session, record: RefreshToken, *, reason: str = "rotated") -> RefreshToken:
    """Mark a token as rotated (consumed in exchange for a new token).

    INVARIANT: A rotated token sets both rotated_at and revoked_at so that
    a single validation path can check revoked_at only.
    """
    now = datetime.now(timezone.utc)
    record.rotated_at = now
    record.revoked_at = now
    record.revoke_reason = reason[:256]
    db.flush()
    return record


def revoke_by_session_id(
    db: Session,
    *,
    tenant_id: str,
    session_id: str,
    reason: str,
) -> int:
    """Revoke all active tokens for the given session."""
    now = datetime.now(timezone.utc)
    active_records = list(
        db.scalars(
            select(RefreshToken).where(
                RefreshToken.tenant_id == tenant_id,
                RefreshToken.session_id == session_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
    )
    for record in active_records:
        record.revoked_at = now
        record.revoke_reason = reason[:256]
    db.flush()
    return len(active_records)


def revoke_by_user_id(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    reason: str,
) -> int:
    """Revoke all active tokens for the given user (logout-all)."""
    now = datetime.now(timezone.utc)
    active_records = list(
        db.scalars(
            select(RefreshToken).where(
                RefreshToken.tenant_id == tenant_id,
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
    )
    for record in active_records:
        record.revoked_at = now
        record.revoke_reason = reason[:256]
    db.flush()
    return len(active_records)
