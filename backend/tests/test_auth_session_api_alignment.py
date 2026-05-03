from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.v1.auth as auth_router_module
from app.models.refresh_token import RefreshToken
from app.security.auth import AuthIdentity
from datetime import datetime, timezone


def _mock_get_db():
    """Yield a MagicMock DB session — used when all DB-calling functions are mocked."""
    yield MagicMock()


def test_refresh_endpoint_returns_new_bearer_token(monkeypatch):
    """POST /auth/refresh with a valid refresh_token body returns new token pair.

    P0-A-03B: Refresh now requires a refresh_token body field (Option A).
    Identity is derived from the persisted record, not from a Bearer JWT.
    """
    fake_record = RefreshToken(
        token_id="new-tid",
        user_id="u-demo",
        tenant_id="default",
        session_id="session-123",
        token_hash="fakehash",
        token_family_id="family-1",
        issued_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
    )

    monkeypatch.setattr(
        auth_router_module,
        "rotate_refresh_token",
        lambda db, **kwargs: ("new-refresh-abc", fake_record),
    )
    monkeypatch.setattr(
        auth_router_module,
        "get_identity_by_user_id",
        lambda db, user_id, tenant_id: AuthIdentity(
            user_id="u-demo",
            username="demo",
            email="demo@mes.local",
            tenant_id="default",
            role_code="SUPERVISOR",
            session_id=None,
        ),
    )
    monkeypatch.setattr(
        auth_router_module,
        "create_access_token",
        lambda identity: "new-token-abc",
    )
    monkeypatch.setattr(
        auth_router_module,
        "record_security_event",
        lambda db, **kwargs: None,
    )

    app = FastAPI()
    app.include_router(auth_router_module.router)
    app.dependency_overrides[auth_router_module.get_db] = _mock_get_db

    client = TestClient(app)
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "some-raw-token"},
        headers={"X-Tenant-ID": "default"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "new-token-abc"
    assert body["refresh_token"] == "new-refresh-abc"
    assert body["token_type"] == "bearer"
    assert body["user"]["user_id"] == "u-demo"
    assert body["user"]["tenant_id"] == "default"


def test_session_revoke_routes_include_canonical_and_legacy():
    app = FastAPI()
    app.include_router(auth_router_module.router)

    route_signatures = {
        (route.path, tuple(sorted(route.methods or [])))
        for route in app.routes
        if hasattr(route, "methods")
    }

    assert ("/auth/sessions/{session_id}/revoke", ("POST",)) in route_signatures
    assert ("/auth/sessions/{session_id}", ("DELETE",)) in route_signatures
