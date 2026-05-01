"""Service for refresh token lifecycle management.

SECURITY INVARIANTS:
  1. Raw token values are NEVER persisted — only SHA-256 hashes.
  2. Revoked tokens cannot validate.
  3. Rotated tokens cannot be reused (rotated_at implies revoked_at).
  4. Expired tokens cannot validate.
  5. Tenant mismatch cannot validate.
  6. Token lookup always uses hash comparison.

SCOPE: P0-A-03A — model/service foundation only.
The /auth/refresh endpoint wiring is deferred to P0-A-03B.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.refresh_token import RefreshToken
from app.repositories import refresh_token_repository as repo


def _generate_raw_token() -> str:
    """Generate a cryptographically random raw token (64-char hex string).

    INVARIANT: This value must never be persisted. Only its hash is stored.
    """
    return secrets.token_hex(32)


def _hash_token(raw_token: str) -> str:
    """Return the SHA-256 hex digest of a raw token.

    WHY: SHA-256 is a one-way function. Given the hash in the DB, an attacker
    cannot recover the raw token (assuming sufficient entropy in token_hex(32)).
    """
    return hashlib.sha256(raw_token.encode()).hexdigest()


def issue_refresh_token(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
    session_id: str | None = None,
    token_family_id: str | None = None,
) -> tuple[str, RefreshToken]:
    """Issue a new refresh token record.

    Returns (raw_token, record). The caller must deliver raw_token to the
    client; it is not available later from the DB.

    INVARIANT: raw_token is never stored. Only its hash appears in the DB.
    """
    raw_token = _generate_raw_token()
    token_hash = _hash_token(raw_token)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.jwt_refresh_token_expire_days)

    record = RefreshToken(
        token_id=str(uuid4()),
        tenant_id=tenant_id,
        user_id=user_id,
        session_id=session_id,
        token_hash=token_hash,
        token_family_id=token_family_id or str(uuid4()),
        issued_at=now,
        expires_at=expires_at,
    )
    repo.create_refresh_token(db, record)
    return raw_token, record


def validate_refresh_token(
    db: Session,
    *,
    raw_token: str,
    tenant_id: str,
) -> RefreshToken | None:
    """Validate a raw refresh token.

    Returns the RefreshToken record if valid, or None for ANY invalid case:
    - unknown token
    - cross-tenant token
    - revoked token
    - rotated (consumed) token
    - expired token

    INVARIANT: Returning None for all failure cases prevents timing analysis
    from distinguishing between "not found" and "revoked".
    """
    token_hash = _hash_token(raw_token)
    record = repo.get_by_token_hash(db, tenant_id=tenant_id, token_hash=token_hash)

    if record is None:
        return None

    # INVARIANT: Tenant check is enforced at the repository layer (tenant_id
    # is part of the query). Double-check here as a defence-in-depth measure.
    if record.tenant_id != tenant_id:
        return None

    # INVARIANT: revoked_at covers both explicit revocations and rotated tokens
    # (mark_rotated sets both rotated_at and revoked_at).
    if record.revoked_at is not None:
        return None

    # INVARIANT: Expired tokens cannot validate regardless of revocation status.
    # WHY: SQLite returns timezone-naive datetimes; normalize before comparison
    # to support both SQLite (tests) and PostgreSQL (production).
    now_utc = datetime.now(timezone.utc)
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now_utc:
        return None

    return record


def rotate_refresh_token(
    db: Session,
    *,
    raw_token: str,
    tenant_id: str,
) -> tuple[str, RefreshToken] | None:
    """Rotate a refresh token.

    Validates the old token, marks it as rotated/consumed, and issues a new
    token with the same token_family_id.

    Returns (new_raw_token, new_record) or None if the old token is invalid.

    INVARIANT: The old token is immediately invalidated before the new one
    is issued, preventing replay.

    ROTATION DETECTION: If the old token is already rotated (rotated_at set),
    validate_refresh_token returns None, so rotation is rejected. This detects
    refresh token reuse attacks.
    """
    old_record = validate_refresh_token(db, raw_token=raw_token, tenant_id=tenant_id)
    if old_record is None:
        return None

    # Capture family/context before marking old record (immutable after flush).
    family_id = old_record.token_family_id
    user_id = old_record.user_id
    session_id = old_record.session_id

    # INVARIANT: Invalidate old token atomically before issuing new one.
    repo.mark_rotated(db, old_record)

    new_raw_token, new_record = issue_refresh_token(
        db,
        user_id=user_id,
        tenant_id=tenant_id,
        session_id=session_id,
        token_family_id=family_id,
    )
    return new_raw_token, new_record


def revoke_refresh_token(
    db: Session,
    *,
    raw_token: str,
    tenant_id: str,
    reason: str = "revoked",
) -> bool:
    """Explicitly revoke a single refresh token by raw value.

    Returns True if the token was found (and revoked or was already revoked),
    False if no matching token exists for this tenant.
    """
    token_hash = _hash_token(raw_token)
    return repo.revoke_by_token_hash(
        db, tenant_id=tenant_id, token_hash=token_hash, reason=reason
    )


def revoke_tokens_for_session(
    db: Session,
    *,
    session_id: str,
    tenant_id: str,
    reason: str = "session_revoked",
) -> int:
    """Revoke all active refresh tokens associated with a session.

    Called when a session is explicitly revoked (e.g., logout).
    Returns the count of tokens revoked.
    """
    return repo.revoke_by_session_id(
        db, tenant_id=tenant_id, session_id=session_id, reason=reason
    )


def revoke_tokens_for_user(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
    reason: str = "user_logout_all",
) -> int:
    """Revoke all active refresh tokens for a user.

    Called on logout-all or account deactivation.
    Returns the count of tokens revoked.
    """
    return repo.revoke_by_user_id(
        db, tenant_id=tenant_id, user_id=user_id, reason=reason
    )
