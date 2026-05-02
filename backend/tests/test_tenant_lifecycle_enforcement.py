"""Tests for P0-A-02B: Tenant Lifecycle Enforcement in Auth / Request Context.

INVARIANTS COVERED:
  1. Active tenant row (ACTIVE + is_active=True) → request allowed.
  2. Tenant row with lifecycle_status=DISABLED → 403 "Tenant is not active".
  3. Tenant row with lifecycle_status=SUSPENDED → 403 "Tenant is not active".
  4. Tenant row with is_active=False (any status) → 403 "Tenant is not active".
  5. Missing tenant row → Policy B → request allowed (transitional debt).
  6. Existing invariant: tenant header mismatch → 403 "Tenant header mismatch"
     (check happens BEFORE lifecycle; unchanged behavior).
  7. Unauthenticated request → 401 "Authentication required" (unchanged).

POLICY: Policy B (transitional). Missing tenant row → allowed. Enforcement
cutover (strict Policy A) is deferred to P0-A-02C after seed/fixture backfill.
"""

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.tenant import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_DISABLED,
    TENANT_STATUS_SUSPENDED,
    Tenant,
)
from app.security.auth import AuthIdentity
from app.security.dependencies import (
    RequestIdentity,
    _get_security_db,
    require_authenticated_identity,
)


# ---------------------------------------------------------------------------
# Test DB helpers
# ---------------------------------------------------------------------------


def _make_factory():
    """SQLite in-memory DB with only the tenants table — isolation boundary."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Tenant.__table__.create(bind=engine, checkfirst=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _seed_tenant(factory, *, lifecycle_status=TENANT_STATUS_ACTIVE, is_active=True):
    db = factory()
    db.add(
        Tenant(
            tenant_id="t-test",
            tenant_code="TEST",
            tenant_name="Test Tenant",
            lifecycle_status=lifecycle_status,
            is_active=is_active,
        )
    )
    db.commit()
    db.close()


def _build_app(factory, *, token_tenant_id="t-test"):
    """FastAPI test app wired with the in-memory DB and a fixed auth identity."""
    app = FastAPI()

    @app.middleware("http")
    async def attach_identity(request, call_next):
        request.state.auth_identity = AuthIdentity(
            user_id="u-1",
            username="demo",
            email="demo@mes.local",
            tenant_id=token_tenant_id,
            role_code="SUP",
            session_id="s-1",
        )
        return await call_next(request)

    @app.get("/secure")
    def secure(identity: RequestIdentity = Depends(require_authenticated_identity)):
        return {"tenant_id": identity.tenant_id}

    def _override_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[_get_security_db] = _override_db
    return app


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_active_tenant_request_context_allowed(monkeypatch) -> None:
    """Tenant row exists, lifecycle_status=ACTIVE, is_active=True → allowed."""
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    factory = _make_factory()
    _seed_tenant(factory, lifecycle_status=TENANT_STATUS_ACTIVE, is_active=True)

    client = TestClient(_build_app(factory))
    response = client.get("/secure")

    assert response.status_code == 200
    assert response.json()["tenant_id"] == "t-test"


def test_disabled_tenant_request_context_rejected(monkeypatch) -> None:
    """Tenant row exists, lifecycle_status=DISABLED → 403 Tenant is not active."""
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    factory = _make_factory()
    _seed_tenant(factory, lifecycle_status=TENANT_STATUS_DISABLED)

    client = TestClient(_build_app(factory))
    response = client.get("/secure")

    assert response.status_code == 403
    assert response.json()["detail"] == "Tenant is not active"


def test_suspended_tenant_request_context_rejected(monkeypatch) -> None:
    """Tenant row exists, lifecycle_status=SUSPENDED → 403 Tenant is not active."""
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    factory = _make_factory()
    _seed_tenant(factory, lifecycle_status=TENANT_STATUS_SUSPENDED)

    client = TestClient(_build_app(factory))
    response = client.get("/secure")

    assert response.status_code == 403
    assert response.json()["detail"] == "Tenant is not active"


def test_is_active_false_request_context_rejected(monkeypatch) -> None:
    """Tenant row exists, is_active=False (status=ACTIVE) → 403 Tenant is not active."""
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    factory = _make_factory()
    _seed_tenant(factory, lifecycle_status=TENANT_STATUS_ACTIVE, is_active=False)

    client = TestClient(_build_app(factory))
    response = client.get("/secure")

    assert response.status_code == 403
    assert response.json()["detail"] == "Tenant is not active"


def test_missing_tenant_row_policy_b_allows(monkeypatch) -> None:
    """No Tenant row for the given tenant_id → Policy B → request allowed.

    This is the transitional behavior. Cutover to strict enforcement (Policy A)
    is P0-A-02C, after seed/fixture backfill creates rows for all active tenants.
    """
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    factory = _make_factory()
    # No tenant row seeded — Policy B: absent row → allowed

    client = TestClient(_build_app(factory))
    response = client.get("/secure")

    assert response.status_code == 200
    assert response.json()["tenant_id"] == "t-test"


def test_tenant_header_mismatch_still_rejected(monkeypatch) -> None:
    """Header mismatch check runs BEFORE lifecycle check; existing invariant preserved."""
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    factory = _make_factory()
    # Seed an active tenant for token_tenant_id; the request header is different
    _seed_tenant(factory, lifecycle_status=TENANT_STATUS_ACTIVE, is_active=True)

    client = TestClient(_build_app(factory, token_tenant_id="t-test"))
    response = client.get("/secure", headers={"X-Tenant-ID": "t-other"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Tenant header mismatch"


def test_unauthenticated_request_still_rejected(monkeypatch) -> None:
    """No auth_identity on request state → 401 Authentication required (unchanged)."""
    factory = _make_factory()

    # Build app WITHOUT the identity-attaching middleware
    app = FastAPI()

    @app.get("/secure")
    def secure(identity: RequestIdentity = Depends(require_authenticated_identity)):
        return {"tenant_id": identity.tenant_id}

    def _override_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[_get_security_db] = _override_db

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/secure")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"
