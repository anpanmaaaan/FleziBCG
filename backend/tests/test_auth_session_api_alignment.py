from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.v1.auth as auth_router_module
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _test_app(identity: RequestIdentity) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router_module.router)

    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app


def test_refresh_endpoint_returns_new_bearer_token(monkeypatch):
    identity = RequestIdentity(
        user_id="u-demo",
        username="demo",
        email="demo@mes.local",
        tenant_id="default",
        role_code="SUPERVISOR",
        is_authenticated=True,
        session_id="session-123",
    )

    monkeypatch.setattr(
        auth_router_module,
        "create_access_token",
        lambda auth_identity: "new-token-abc",
    )
    # /auth/refresh emits a security event via record_security_event(db, ...).
    # Patch it here so the test does not require a real DB connection.
    monkeypatch.setattr(
        auth_router_module,
        "record_security_event",
        lambda db, **kwargs: None,
    )

    client = TestClient(_test_app(identity))
    response = client.post("/auth/refresh")

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "new-token-abc"
    assert body["token_type"] == "bearer"
    assert body["user"]["session_id"] == "session-123"
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
