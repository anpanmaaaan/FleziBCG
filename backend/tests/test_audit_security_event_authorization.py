from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import app.api.v1.security_events as security_events_router_module


def _app_with_router() -> FastAPI:
    app = FastAPI()
    app.include_router(security_events_router_module.router, prefix="/api/v1")
    app.dependency_overrides[security_events_router_module.get_db] = lambda: object()
    return app


def test_security_event_list_requires_authentication(monkeypatch):
    app = _app_with_router()

    client = TestClient(app)
    response = client.get("/api/v1/security-events")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_security_event_list_rejects_user_without_required_action_if_guard_exists(monkeypatch):
    app = _app_with_router()

    route = next(
        r
        for r in app.routes
        if getattr(r, "path", "") == "/api/v1/security-events" and "GET" in (r.methods or set())
    )
    admin_dep = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[admin_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Missing required action: admin.user.manage")
    )

    client = TestClient(app)
    response = client.get("/api/v1/security-events")

    assert response.status_code == 403


def test_security_event_read_does_not_use_frontend_persona_as_auth_truth():
    app = _app_with_router()

    client = TestClient(app)
    response = client.get(
        "/api/v1/security-events",
        headers={
            "X-Persona": "ADMIN",
            "X-Role-Code": "ADMIN",
            "X-Tenant-ID": "default",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_security_event_list_authorized_user_can_read_events(monkeypatch):
    app = _app_with_router()

    route = next(
        r
        for r in app.routes
        if getattr(r, "path", "") == "/api/v1/security-events" and "GET" in (r.methods or set())
    )
    admin_dep = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )

    class _Identity:
        tenant_id = "default"

    app.dependency_overrides[admin_dep] = lambda: _Identity()

    monkeypatch.setattr(
        security_events_router_module,
        "get_security_events",
        lambda db, **kwargs: [
            {
                "tenant_id": "default",
                "actor_user_id": "u-1",
                "event_type": "AUTH.LOGIN",
                "resource_type": "session",
                "resource_id": "s-1",
                "detail": "ok",
                "created_at": "2026-05-01T10:00:00Z",
            }
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/security-events")

    assert response.status_code == 200
    assert len(response.json()) == 1
