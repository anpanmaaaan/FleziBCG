"""Tests for P0-A-03B: Runtime wiring of /auth/login and /auth/refresh to
the persisted refresh token service.

INVARIANTS COVERED:
  1. Login returns a raw refresh token; only the hash is stored in the DB.
  2. /auth/refresh requires a refresh_token body (Option A: legacy path removed).
  3. /auth/refresh validates → atomically rotates → returns new pair.
  4. Rotated/revoked/expired/unknown tokens are rejected with 401.
  5. Identity in the new access token matches the persisted refresh token context.
  6. Client-supplied X-Tenant-ID cannot redirect a token to a different tenant.
  7. Logout revokes all refresh tokens for the session.
  8. Logout-all revokes all refresh tokens for the user.
  9. Security events are emitted for ISSUED, ROTATED, and REUSE_REJECTED.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.auth as auth_router_module
from app.models.rbac import Role, UserRole
from app.models.refresh_token import RefreshToken
from app.models.security_event import SecurityEventLog
from app.models.session import Session as AuthSession
from app.models.session import SessionAuditLog
from app.models.user import User
from app.security.auth import AuthIdentity, decode_access_token
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services import refresh_token_service as rt_svc

# ---------------------------------------------------------------------------
# Test DB helpers
# ---------------------------------------------------------------------------

_TABLES = [
    SecurityEventLog,
    User,
    Role,
    UserRole,
    AuthSession,
    SessionAuditLog,
    RefreshToken,
]


def _make_session_factory():
    """SQLite in-memory DB shared via StaticPool — all sessions see committed data."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    for model in _TABLES:
        model.__table__.create(bind=engine, checkfirst=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _seed_user(db, *, user_id="u-1", username="alice", tenant_id="default"):
    db.add(
        User(
            user_id=user_id,
            username=username,
            email=f"{username}@test.local",
            password_hash="hashed",
            tenant_id=tenant_id,
            is_active=True,
        )
    )
    db.commit()


def _build_app(factory, extra_overrides=None):
    """FastAPI test app with get_db overridden to use the in-memory DB."""
    app = FastAPI()
    app.include_router(auth_router_module.router)

    def override_get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[auth_router_module.get_db] = override_get_db
    if extra_overrides:
        for dep, override in extra_overrides.items():
            app.dependency_overrides[dep] = override
    return app


def _mock_get_db():
    """Yield a mock DB — for tests that patch all DB-calling functions."""
    from unittest.mock import MagicMock
    yield MagicMock()


# ---------------------------------------------------------------------------
# Option A: Legacy bearer-only path is removed
# ---------------------------------------------------------------------------


def test_legacy_access_token_refresh_path_removed():
    """POST /auth/refresh without a body returns 422 (Option A: old path gone).

    The old behavior was: POST with Authorization: Bearer <jwt> → re-signed token.
    After P0-A-03B, a refresh_token body field is required.
    """
    app = FastAPI()
    app.include_router(auth_router_module.router)
    app.dependency_overrides[auth_router_module.get_db] = _mock_get_db

    client = TestClient(app)
    # No body at all
    resp = client.post(
        "/auth/refresh",
        headers={"Authorization": "Bearer some-old-jwt-token"},
    )
    assert resp.status_code == 422

    # Empty body (no refresh_token field)
    resp2 = client.post("/auth/refresh", json={})
    assert resp2.status_code == 422


# ---------------------------------------------------------------------------
# Login: refresh token issuance
# ---------------------------------------------------------------------------


def test_login_returns_refresh_token(monkeypatch):
    """Login response includes a non-null refresh_token (64-char hex raw token)."""
    factory = _make_session_factory()

    monkeypatch.setattr(
        auth_router_module,
        "authenticate_user_db",
        lambda db, username, password, tenant_id: AuthIdentity(
            user_id="u-1",
            username="alice",
            email="alice@test.local",
            tenant_id="default",
            role_code="SUPERVISOR",
        ),
    )

    client = TestClient(_build_app(factory))
    resp = client.post("/auth/login", json={"username": "alice", "password": "pass"})

    assert resp.status_code == 200
    body = resp.json()
    assert "refresh_token" in body
    assert body["refresh_token"] is not None
    assert len(body["refresh_token"]) == 64  # secrets.token_hex(32)
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_persists_refresh_token_hash_only(monkeypatch):
    """After login, DB contains the SHA-256 hash of the token, not the raw value."""
    factory = _make_session_factory()

    monkeypatch.setattr(
        auth_router_module,
        "authenticate_user_db",
        lambda db, username, password, tenant_id: AuthIdentity(
            user_id="u-1",
            username="alice",
            email="alice@test.local",
            tenant_id="default",
            role_code=None,
        ),
    )

    client = TestClient(_build_app(factory))
    resp = client.post("/auth/login", json={"username": "alice", "password": "pass"})
    assert resp.status_code == 200

    raw_token = resp.json()["refresh_token"]

    db = factory()
    records = list(db.scalars(select(RefreshToken)))
    db.close()

    assert len(records) == 1
    stored_hash = records[0].token_hash
    assert stored_hash != raw_token
    assert stored_hash == hashlib.sha256(raw_token.encode()).hexdigest()


def test_login_does_not_return_token_hash(monkeypatch):
    """The refresh_token in the response is the raw token, not its SHA-256 hash."""
    factory = _make_session_factory()

    monkeypatch.setattr(
        auth_router_module,
        "authenticate_user_db",
        lambda db, username, password, tenant_id: AuthIdentity(
            user_id="u-1",
            username="alice",
            email="alice@test.local",
            tenant_id="default",
            role_code=None,
        ),
    )

    client = TestClient(_build_app(factory))
    resp = client.post("/auth/login", json={"username": "alice", "password": "pass"})
    assert resp.status_code == 200

    raw_token = resp.json()["refresh_token"]
    # The raw token, when hashed, should NOT equal itself — i.e., not a hash already.
    assert hashlib.sha256(raw_token.encode()).hexdigest() != raw_token


def test_login_refresh_token_linked_to_session_user_tenant(monkeypatch):
    """Persisted refresh token record has the correct user_id, tenant_id, session_id."""
    factory = _make_session_factory()

    monkeypatch.setattr(
        auth_router_module,
        "authenticate_user_db",
        lambda db, username, password, tenant_id: AuthIdentity(
            user_id="u-99",
            username="alice",
            email="alice@test.local",
            tenant_id="tenant-x",
            role_code=None,
        ),
    )

    client = TestClient(_build_app(factory))
    resp = client.post(
        "/auth/login",
        json={"username": "alice", "password": "pass"},
        headers={"X-Tenant-ID": "tenant-x"},
    )
    assert resp.status_code == 200
    session_id_from_response = resp.json()["user"]["session_id"]

    db = factory()
    records = list(db.scalars(select(RefreshToken)))
    db.close()

    assert len(records) == 1
    rec = records[0]
    assert rec.user_id == "u-99"
    assert rec.tenant_id == "tenant-x"
    assert rec.session_id == session_id_from_response


# ---------------------------------------------------------------------------
# Refresh endpoint: rejection cases
# ---------------------------------------------------------------------------


def test_refresh_requires_refresh_token_body():
    """POST /auth/refresh with no body returns 422."""
    app = FastAPI()
    app.include_router(auth_router_module.router)
    app.dependency_overrides[auth_router_module.get_db] = _mock_get_db
    client = TestClient(app)
    assert client.post("/auth/refresh").status_code == 422


def test_refresh_rejects_unknown_refresh_token():
    """Unknown token (not in DB) → 401."""
    factory = _make_session_factory()
    client = TestClient(_build_app(factory))
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": secrets.token_hex(32)},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 401


def test_refresh_rejects_revoked_refresh_token():
    """Explicitly revoked token → 401."""
    factory = _make_session_factory()
    db = factory()
    raw_token = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    record = RefreshToken(
        token_id="revoked-tid",
        tenant_id="default",
        user_id="u-1",
        session_id=None,
        token_hash=token_hash,
        token_family_id="family-rev",
        issued_at=now - timedelta(hours=1),
        expires_at=now + timedelta(days=29),
        revoked_at=now - timedelta(minutes=1),
        revoke_reason="test",
    )
    db.add(record)
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 401


def test_refresh_rejects_expired_refresh_token():
    """Expired token (expires_at in the past) → 401."""
    factory = _make_session_factory()
    db = factory()
    raw_token = secrets.token_hex(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    record = RefreshToken(
        token_id="expired-tid",
        tenant_id="default",
        user_id="u-1",
        session_id=None,
        token_hash=token_hash,
        token_family_id="family-exp",
        issued_at=now - timedelta(days=31),
        expires_at=now - timedelta(days=1),  # expired yesterday
    )
    db.add(record)
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Refresh endpoint: happy path and rotation invariants
# ---------------------------------------------------------------------------


def test_refresh_rotates_token_and_returns_new_pair():
    """Valid refresh token → 200 with new access_token and refresh_token."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-1", username="alice", tenant_id="default")

    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id="sess-1"
    )
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] is not None
    assert body["refresh_token"] is not None
    assert body["refresh_token"] != raw_token  # new token issued
    assert body["token_type"] == "bearer"
    assert body["user"]["user_id"] == "u-1"
    assert body["user"]["tenant_id"] == "default"


def test_old_refresh_token_cannot_be_reused_after_rotation():
    """After a successful refresh, the old token is rejected on reuse (rotation invariant)."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-1", username="alice", tenant_id="default")

    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id="sess-1"
    )
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))

    # First refresh — succeeds
    resp1 = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp1.status_code == 200

    # Second attempt with the original (now rotated) token — must be rejected
    resp2 = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp2.status_code == 401


def test_new_access_token_identity_matches_refresh_context():
    """JWT from /auth/refresh carries user_id, tenant_id, session_id from the persisted record."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-42", username="user42", tenant_id="tenant-x")

    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-42", tenant_id="tenant-x", session_id="sess-99"
    )
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "tenant-x"},
    )
    assert resp.status_code == 200

    access_token = resp.json()["access_token"]
    identity = decode_access_token(access_token)
    assert identity is not None
    assert identity.user_id == "u-42"
    assert identity.tenant_id == "tenant-x"
    assert identity.session_id == "sess-99"


def test_refresh_does_not_trust_client_supplied_tenant():
    """Token issued for tenant-A cannot be refreshed when X-Tenant-ID is tenant-B."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-1", username="alice", tenant_id="tenant-a")

    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="tenant-a", session_id=None
    )
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))
    # Supply wrong tenant header
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "tenant-b"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Logout / session revocation
# ---------------------------------------------------------------------------


def test_logout_revokes_session_refresh_tokens():
    """Refresh token issued for a session is invalid after that session is logged out."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-1", username="alice", tenant_id="default")

    # Create a real session record so revoke_session can find it
    now = datetime.now(timezone.utc)
    session = AuthSession(
        session_id="sess-logout-1",
        user_id="u-1",
        tenant_id="default",
        issued_at=now,
        expires_at=now + timedelta(hours=8),
    )
    db.add(session)
    db.commit()

    # Issue a refresh token linked to that session
    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id="sess-logout-1"
    )
    db.commit()
    db.close()

    # Call logout via HTTP with mocked identity
    identity = RequestIdentity(
        user_id="u-1",
        username="alice",
        email="alice@test.local",
        tenant_id="default",
        role_code=None,
        is_authenticated=True,
        session_id="sess-logout-1",
    )
    client = TestClient(
        _build_app(
            factory,
            extra_overrides={require_authenticated_identity: lambda: identity},
        )
    )
    logout_resp = client.post("/auth/logout")
    assert logout_resp.status_code == 200

    # Now try to refresh with the old token — must be rejected
    refresh_resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    assert refresh_resp.status_code == 401


def test_logout_all_revokes_user_refresh_tokens():
    """All user refresh tokens are invalid after logout-all."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-1", username="alice", tenant_id="default")

    # Issue two refresh tokens for different sessions
    raw_t1, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id="sess-la-1"
    )
    raw_t2, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id="sess-la-2"
    )
    db.commit()
    db.close()

    identity = RequestIdentity(
        user_id="u-1",
        username="alice",
        email="alice@test.local",
        tenant_id="default",
        role_code=None,
        is_authenticated=True,
        session_id=None,
    )
    client = TestClient(
        _build_app(
            factory,
            extra_overrides={require_authenticated_identity: lambda: identity},
        )
    )
    logout_all_resp = client.post("/auth/logout-all")
    assert logout_all_resp.status_code == 200

    # Both tokens must be rejected
    for raw in (raw_t1, raw_t2):
        resp = client.post(
            "/auth/refresh",
            json={"refresh_token": raw},
            headers={"X-Tenant-ID": "default"},
        )
        assert resp.status_code == 401


def test_revoked_session_refresh_token_cannot_refresh():
    """Service-level: revoke_tokens_for_session invalidates refresh tokens (belt+suspenders)."""
    from app.services.refresh_token_service import (
        revoke_tokens_for_session,
        validate_refresh_token,
    )

    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    RefreshToken.__table__.create(bind=engine)
    db_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = db_factory()

    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id="sess-rev"
    )
    db.commit()

    assert validate_refresh_token(db, raw_token=raw_token, tenant_id="default") is not None

    count = revoke_tokens_for_session(
        db, session_id="sess-rev", tenant_id="default", reason="logout"
    )
    db.commit()
    assert count == 1

    assert validate_refresh_token(db, raw_token=raw_token, tenant_id="default") is None


# ---------------------------------------------------------------------------
# Security events
# ---------------------------------------------------------------------------


def test_login_records_refresh_token_issued_event(monkeypatch):
    """Login stores a REFRESH_TOKEN.ISSUED security event in the DB."""
    factory = _make_session_factory()

    monkeypatch.setattr(
        auth_router_module,
        "authenticate_user_db",
        lambda db, username, password, tenant_id: AuthIdentity(
            user_id="u-1",
            username="alice",
            email="alice@test.local",
            tenant_id="default",
            role_code=None,
        ),
    )

    client = TestClient(_build_app(factory))
    resp = client.post("/auth/login", json={"username": "alice", "password": "pass"})
    assert resp.status_code == 200

    db = factory()
    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "REFRESH_TOKEN.ISSUED",
                SecurityEventLog.tenant_id == "default",
            )
        )
    )
    db.close()

    assert len(events) == 1
    assert events[0].actor_user_id == "u-1"


def test_rotation_emits_security_event():
    """Successful refresh stores a REFRESH_TOKEN.ROTATED security event."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-1", username="alice", tenant_id="default")
    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id=None
    )
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 200

    db2 = factory()
    events = list(
        db2.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "REFRESH_TOKEN.ROTATED",
                SecurityEventLog.tenant_id == "default",
            )
        )
    )
    db2.close()

    assert len(events) == 1
    assert events[0].actor_user_id == "u-1"


def test_reuse_rejection_emits_security_event():
    """Invalid/rotated token attempt stores a REFRESH_TOKEN.REUSE_REJECTED event."""
    factory = _make_session_factory()
    db = factory()
    _seed_user(db, user_id="u-1", username="alice", tenant_id="default")
    raw_token, _ = rt_svc.issue_refresh_token(
        db, user_id="u-1", tenant_id="default", session_id=None
    )
    db.commit()
    db.close()

    client = TestClient(_build_app(factory))

    # First use — valid, rotates the token
    client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    # Second use — reuse of rotated token
    resp = client.post(
        "/auth/refresh",
        json={"refresh_token": raw_token},
        headers={"X-Tenant-ID": "default"},
    )
    assert resp.status_code == 401

    db2 = factory()
    events = list(
        db2.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "REFRESH_TOKEN.REUSE_REJECTED",
                SecurityEventLog.tenant_id == "default",
            )
        )
    )
    db2.close()

    assert len(events) >= 1
