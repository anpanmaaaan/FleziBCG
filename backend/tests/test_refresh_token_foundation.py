"""Tests for RefreshToken model, repository, and service foundation (P0-A-03A).

SECURITY INVARIANTS COVERED:
  1. Raw tokens are never stored — only hashes.
  2. Revoked tokens cannot validate.
  3. Expired tokens cannot validate.
  4. Cross-tenant tokens cannot validate.
  5. Session/user revocation invalidates refresh tokens.
  6. Migration adds only the refresh_tokens table.
  7. Migration 0002 has correct chain (down_revision = 0001).
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.refresh_token import RefreshToken
from app.services import refresh_token_service as svc

BACKEND_DIR = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Test DB helper
# ---------------------------------------------------------------------------


def _make_db():
    """SQLite in-memory session with the RefreshToken table created."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    RefreshToken.__table__.create(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_factory()


# ---------------------------------------------------------------------------
# Model structure
# ---------------------------------------------------------------------------


def test_refresh_token_model_fields_exist():
    """RefreshToken ORM model must expose all required attributes."""
    required_fields = [
        "id",
        "token_id",
        "tenant_id",
        "user_id",
        "session_id",
        "token_hash",
        "token_family_id",
        "issued_at",
        "expires_at",
        "rotated_at",
        "revoked_at",
        "revoke_reason",
        "created_at",
    ]
    for field in required_fields:
        assert hasattr(RefreshToken, field), (
            f"RefreshToken is missing required field: {field}"
        )


def test_refresh_token_table_name():
    assert RefreshToken.__tablename__ == "refresh_tokens"


# ---------------------------------------------------------------------------
# Migration structure (no DB needed)
# ---------------------------------------------------------------------------


def test_refresh_token_migration_revision_exists():
    """Revision 0002 must be discoverable by Alembic ScriptDirectory."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())
    rev_ids = [r.revision for r in revisions]
    assert "0002" in rev_ids, f"Revision 0002 not found. Available: {rev_ids}"


def test_refresh_token_migration_chain():
    """Revision 0002 must chain from 0001 (down_revision = 0001)."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    script_dir = ScriptDirectory.from_config(cfg)
    rev = script_dir.get_revision("0002")
    assert rev is not None
    assert rev.down_revision == "0001", (
        f"Expected down_revision='0001', got: {rev.down_revision}"
    )


def test_refresh_token_migration_head_is_0002():
    """Revision 0002 exists in the migration chain and has the correct down_revision.

    NOTE: 0002 may no longer be the Alembic head if subsequent revisions were added
    by other workstreams. The structural invariant is that 0002 exists with
    down_revision='0001', not that it is the current head.
    """
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    script_dir = ScriptDirectory.from_config(cfg)
    rev = script_dir.get_revision("0002")
    assert rev is not None, "Revision 0002 must exist in the migration chain"
    assert rev.down_revision == "0001", (
        f"Expected 0002 down_revision='0001', got: {rev.down_revision}"
    )


def test_refresh_token_migration_upgrade_creates_only_refresh_tokens():
    """The upgrade() function in 0002 must reference only the refresh_tokens table.

    This ensures the migration does not accidentally touch existing tables.
    """
    migration_file = BACKEND_DIR / "alembic" / "versions" / "0002_add_refresh_tokens.py"
    assert migration_file.exists(), "Migration file 0002_add_refresh_tokens.py not found"

    source = migration_file.read_text(encoding="utf-8")

    # Verify the migration creates refresh_tokens
    assert '"refresh_tokens"' in source or "'refresh_tokens'" in source, (
        "Migration must create the refresh_tokens table"
    )

    # Verify downgrade drops refresh_tokens
    assert "drop_table" in source, "Migration downgrade must drop the table"

    # Verify the migration does NOT touch known existing tables
    forbidden_tables = [
        "users",
        "sessions",
        "session_audit_logs",
        "security_event_logs",
        "roles",
        "permissions",
        "user_roles",
    ]
    for table in forbidden_tables:
        assert f'"{table}"' not in source and f"'{table}'" not in source, (
            f"Migration 0002 must not touch existing table: {table}"
        )


# ---------------------------------------------------------------------------
# Security / storage invariants
# ---------------------------------------------------------------------------


def test_issue_refresh_token_stores_hash_not_plaintext():
    """INVARIANT: raw token must not appear in the persisted record."""
    db = _make_db()
    raw_token, record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    assert record.token_hash != raw_token, (
        "token_hash must not equal raw_token — raw token must not be stored"
    )
    assert len(record.token_hash) == 64, (
        "SHA-256 hex digest must be 64 characters"
    )
    # Verify the hash is hex
    int(record.token_hash, 16)


def test_issue_refresh_token_hash_is_sha256_of_raw():
    """token_hash must be the SHA-256 hex digest of the raw token."""
    import hashlib

    db = _make_db()
    raw_token, record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    expected_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    assert record.token_hash == expected_hash


def test_token_hash_is_unique_per_token():
    """Two different issued tokens must produce different hashes."""
    db = _make_db()
    raw1, rec1 = svc.issue_refresh_token(db, user_id="u-001", tenant_id="tenant-a")
    raw2, rec2 = svc.issue_refresh_token(db, user_id="u-001", tenant_id="tenant-a")
    db.commit()

    assert raw1 != raw2
    assert rec1.token_hash != rec2.token_hash


def test_raw_token_not_in_record_repr():
    """Raw token must not appear in the model's __repr__ or __str__."""
    db = _make_db()
    raw_token, record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    record_repr = repr(record)
    assert raw_token not in record_repr, (
        "Raw token must not appear in RefreshToken repr"
    )


# ---------------------------------------------------------------------------
# Service behavior
# ---------------------------------------------------------------------------


def test_issue_refresh_token_record():
    """Issued record must have correct tenant/user/family fields."""
    db = _make_db()
    raw_token, record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a", session_id="sess-123"
    )
    db.commit()

    assert record.user_id == "u-001"
    assert record.tenant_id == "tenant-a"
    assert record.session_id == "sess-123"
    assert record.token_id is not None
    assert record.token_family_id is not None
    assert record.issued_at is not None
    assert record.expires_at > record.issued_at
    assert record.revoked_at is None
    assert record.rotated_at is None


def test_validate_refresh_token_success():
    """Valid token must return the record."""
    db = _make_db()
    raw_token, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    result = svc.validate_refresh_token(db, raw_token=raw_token, tenant_id="tenant-a")
    assert result is not None
    assert result.user_id == "u-001"


def test_validate_rejects_unknown_token():
    """Unknown token hash must return None."""
    db = _make_db()
    result = svc.validate_refresh_token(
        db, raw_token="unknown-token-abc123", tenant_id="tenant-a"
    )
    assert result is None


def test_validate_rejects_revoked_token():
    """INVARIANT: Revoked token must not validate."""
    db = _make_db()
    raw_token, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    revoked = svc.revoke_refresh_token(
        db, raw_token=raw_token, tenant_id="tenant-a", reason="test_revoke"
    )
    db.commit()
    assert revoked is True

    result = svc.validate_refresh_token(
        db, raw_token=raw_token, tenant_id="tenant-a"
    )
    assert result is None, "Revoked token must not validate"


def test_validate_rejects_expired_token():
    """INVARIANT: Expired token must not validate."""
    db = _make_db()
    raw_token, record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    # Backdate expires_at to the past
    record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()

    result = svc.validate_refresh_token(
        db, raw_token=raw_token, tenant_id="tenant-a"
    )
    assert result is None, "Expired token must not validate"


def test_validate_rejects_cross_tenant_token():
    """INVARIANT: Token issued to tenant-a must not validate for tenant-b."""
    db = _make_db()
    raw_token, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    result = svc.validate_refresh_token(
        db, raw_token=raw_token, tenant_id="tenant-b"
    )
    assert result is None, "Cross-tenant validation must return None"


def test_revoke_refresh_token():
    """Revoke sets revoked_at; subsequent validate returns None."""
    db = _make_db()
    raw_token, record = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    db.commit()

    ok = svc.revoke_refresh_token(
        db, raw_token=raw_token, tenant_id="tenant-a", reason="logout"
    )
    db.commit()

    assert ok is True
    db.refresh(record)
    assert record.revoked_at is not None
    assert record.revoke_reason == "logout"


def test_revoke_unknown_token_returns_false():
    """Revoking a token that does not exist must return False."""
    db = _make_db()
    ok = svc.revoke_refresh_token(
        db, raw_token="no-such-token", tenant_id="tenant-a"
    )
    assert ok is False


def test_revoke_tokens_for_session():
    """INVARIANT: All tokens linked to a session must be revoked on session revocation."""
    db = _make_db()
    raw1, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a", session_id="sess-abc"
    )
    raw2, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a", session_id="sess-abc"
    )
    raw3, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a", session_id="sess-other"
    )
    db.commit()

    count = svc.revoke_tokens_for_session(
        db, session_id="sess-abc", tenant_id="tenant-a", reason="session_ended"
    )
    db.commit()

    assert count == 2, f"Expected 2 tokens revoked, got {count}"
    # Tokens for the other session are unaffected
    r3 = svc.validate_refresh_token(db, raw_token=raw3, tenant_id="tenant-a")
    assert r3 is not None, "Token for a different session must remain valid"
    # Revoked tokens must not validate
    assert svc.validate_refresh_token(db, raw_token=raw1, tenant_id="tenant-a") is None
    assert svc.validate_refresh_token(db, raw_token=raw2, tenant_id="tenant-a") is None


def test_revoke_tokens_for_user():
    """INVARIANT: All tokens for a user must be revoked on logout-all."""
    db = _make_db()
    raw1, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    raw2, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    raw3, _ = svc.issue_refresh_token(
        db, user_id="u-002", tenant_id="tenant-a"
    )
    db.commit()

    count = svc.revoke_tokens_for_user(
        db, user_id="u-001", tenant_id="tenant-a", reason="logout_all"
    )
    db.commit()

    assert count == 2
    assert svc.validate_refresh_token(db, raw_token=raw1, tenant_id="tenant-a") is None
    assert svc.validate_refresh_token(db, raw_token=raw2, tenant_id="tenant-a") is None
    # Other user's token must be unaffected
    assert svc.validate_refresh_token(db, raw_token=raw3, tenant_id="tenant-a") is not None


def test_revoke_tokens_for_user_is_tenant_scoped():
    """Revoke-all for tenant-a must not affect tokens in tenant-b."""
    db = _make_db()
    raw_a, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-a"
    )
    raw_b, _ = svc.issue_refresh_token(
        db, user_id="u-001", tenant_id="tenant-b"
    )
    db.commit()

    count = svc.revoke_tokens_for_user(
        db, user_id="u-001", tenant_id="tenant-a", reason="logout_all"
    )
    db.commit()

    assert count == 1
    # tenant-b token must not be affected
    assert svc.validate_refresh_token(db, raw_token=raw_b, tenant_id="tenant-b") is not None
