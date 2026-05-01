from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import app.api.v1.security_events as security_events_router_module
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _build_app() -> tuple[FastAPI, RequestIdentity]:
    app = FastAPI()
    app.include_router(security_events_router_module.router, prefix="/api/v1")
    identity = RequestIdentity(
        user_id="admin-user",
        username="admin-user",
        email=None,
        tenant_id="default",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="session-admin",
    )
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app, identity


def _override_admin_dependency(app: FastAPI, identity: RequestIdentity) -> Any:
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == "/api/v1/security-events" and "GET" in (r.methods or set())
        ),
    )
    admin_dependency = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[admin_dependency] = lambda: identity
    return admin_dependency


def test_security_events_endpoint_delegates_with_tenant_and_limit(monkeypatch):
    app, identity = _build_app()
    _override_admin_dependency(app, identity)

    fake_db = object()
    app.dependency_overrides[security_events_router_module.get_db] = lambda: fake_db

    captured = {}

    monkeypatch.setattr(
        security_events_router_module,
        "get_security_events",
        lambda db, tenant_id, limit, offset, event_type, actor_user_id, resource_type, resource_id, created_from, created_to: [
            {
                "tenant_id": tenant_id,
                "actor_user_id": "admin-user",
                "event_type": "AUTH.LOGIN",
                "resource_type": "session",
                "resource_id": "s-1",
                "detail": "login",
                "created_at": "2026-04-29T00:00:00Z",
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/security-events?limit=25")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["tenant_id"] == "default"
    assert body[0]["event_type"] == "AUTH.LOGIN"


def test_security_events_endpoint_rejects_without_admin_permission():
    app, identity = _build_app()
    admin_dependency = _override_admin_dependency(app, identity)
    app.dependency_overrides[admin_dependency] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.get("/api/v1/security-events")

    assert response.status_code == 403


def test_security_events_endpoint_rejects_invalid_time_range():
    app, identity = _build_app()
    _override_admin_dependency(app, identity)
    app.dependency_overrides[security_events_router_module.get_db] = lambda: object()

    client = TestClient(app)
    response = client.get(
        "/api/v1/security-events?created_from=2026-05-01T12:00:00Z&created_to=2026-05-01T10:00:00Z"
    )

    assert response.status_code == 422
