"""Tests for refresh token rotation invariants (P0-A-03A).

SECURITY INVARIANTS COVERED:
  1. Rotation creates a new token record.
  2. Rotation marks the old token as rotated (and therefore revoked).
  3. Old (rotated) token cannot be reused.
  4. New and old tokens share the same token_family_id.
  5. Rotating an already-rotated token returns None (reuse attack detection).
  6. Rotating a revoked token returns None.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.refresh_token import RefreshToken
from app.services import refresh_token_service as svc


# ---------------------------------------------------------------------------
# Test DB helper
# ---------------------------------------------------------------------------


def _make_db():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    RefreshToken.__table__.create(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_factory()


# ---------------------------------------------------------------------------
# Rotation tests
# ---------------------------------------------------------------------------


def test_rotate_refresh_token_creates_new_record():
    """Rotation must produce a new token record with a different token_hash."""
    db = _make_db()
    raw_old, old_record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a", session_id="sess-123"
    )
    db.commit()

    result = svc.rotate_refresh_token(db, raw_token=raw_old, tenant_id="tenant-a")
    db.commit()

    assert result is not None
    raw_new, new_record = result

    assert raw_new != raw_old, "New raw token must differ from old"
    assert new_record.token_hash != old_record.token_hash, "New hash must differ"
    assert new_record.token_id != old_record.token_id, "New record must have new ID"
    assert new_record.user_id == old_record.user_id
    assert new_record.tenant_id == old_record.tenant_id
    assert new_record.session_id == old_record.session_id


def test_rotate_refresh_token_preserves_family_id():
    """Rotation must preserve token_family_id across the rotation chain."""
    db = _make_db()
    raw_old, old_record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()
    original_family = old_record.token_family_id

    result = svc.rotate_refresh_token(db, raw_token=raw_old, tenant_id="tenant-a")
    db.commit()

    assert result is not None
    _, new_record = result
    assert new_record.token_family_id == original_family, (
        "Rotated token must inherit parent token_family_id"
    )


def test_rotate_refresh_token_marks_old_token_as_rotated():
    """INVARIANT: Old token must have rotated_at set after rotation."""
    db = _make_db()
    raw_old, old_record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    svc.rotate_refresh_token(db, raw_token=raw_old, tenant_id="tenant-a")
    db.commit()
    db.refresh(old_record)

    assert old_record.rotated_at is not None, "Old token must have rotated_at set"
    assert old_record.revoked_at is not None, "Old token must have revoked_at set"


def test_rotated_token_cannot_be_reused():
    """INVARIANT: Using the old token after rotation must return None."""
    db = _make_db()
    raw_old, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    svc.rotate_refresh_token(db, raw_token=raw_old, tenant_id="tenant-a")
    db.commit()

    # Attempt to reuse old token
    result = svc.validate_refresh_token(
        db, raw_token=raw_old, tenant_id="tenant-a"
    )
    assert result is None, "Rotated (consumed) token must not validate"


def test_rotated_token_cannot_be_rotated_again():
    """INVARIANT: Attempting to rotate an already-rotated token must return None.

    This is the primary reuse attack detection signal.
    """
    db = _make_db()
    raw_old, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    # First rotation: valid
    result1 = svc.rotate_refresh_token(db, raw_token=raw_old, tenant_id="tenant-a")
    db.commit()
    assert result1 is not None

    # Second rotation with old token: must fail
    result2 = svc.rotate_refresh_token(db, raw_token=raw_old, tenant_id="tenant-a")
    assert result2 is None, "Re-rotating a rotated token must return None (reuse attack)"


def test_rotate_revoked_token_returns_none():
    """Attempting to rotate an explicitly revoked token must return None."""
    db = _make_db()
    raw_token, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    svc.revoke_refresh_token(db, raw_token=raw_token, tenant_id="tenant-a")
    db.commit()

    result = svc.rotate_refresh_token(db, raw_token=raw_token, tenant_id="tenant-a")
    assert result is None


def test_rotate_cross_tenant_token_returns_none():
    """Attempting to rotate a token with wrong tenant must return None."""
    db = _make_db()
    raw_token, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    result = svc.rotate_refresh_token(
        db, raw_token=raw_token, tenant_id="tenant-b"
    )
    assert result is None


def test_new_token_after_rotation_is_valid():
    """New token returned by rotation must immediately validate."""
    db = _make_db()
    raw_old, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    result = svc.rotate_refresh_token(db, raw_token=raw_old, tenant_id="tenant-a")
    db.commit()
    assert result is not None

    raw_new, _ = result
    validated = svc.validate_refresh_token(
        db, raw_token=raw_new, tenant_id="tenant-a"
    )
    assert validated is not None, "Newly rotated-in token must be valid"
