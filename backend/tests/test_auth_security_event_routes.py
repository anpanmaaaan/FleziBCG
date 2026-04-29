from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.v1.auth as auth_router_module
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _test_app(identity: RequestIdentity) -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router_module.router)
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app


def test_refresh_records_security_event(monkeypatch):
    identity = RequestIdentity(
        user_id="u-demo",
        username="demo",
        email="demo@mes.local",
        tenant_id="default",
        role_code="SUP",
        is_authenticated=True,
        session_id="session-123",
    )
    captured = {}

    monkeypatch.setattr(auth_router_module, "create_access_token", lambda identity: "token")
    monkeypatch.setattr(
        auth_router_module,
        "record_security_event",
        lambda db, **kwargs: captured.update(kwargs),
    )

    client = TestClient(_test_app(identity))
    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert captured["tenant_id"] == "default"
    assert captured["actor_user_id"] == "u-demo"
    assert captured["event_type"] == "AUTH.REFRESH"
    assert captured["resource_type"] == "session"
    assert captured["resource_id"] == "session-123"
