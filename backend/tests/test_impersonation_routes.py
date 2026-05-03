"""P0-A-07D: Impersonation Route Guard Tests

Verifies that:
- POST /impersonations uses admin.impersonation.create action guard
- POST /impersonations/{id}/revoke uses admin.impersonation.revoke action guard
- GET /impersonations/current uses require_authenticated_identity (identity-only)
- Service errors map to correct HTTP status codes
- Route dependency is auto-discovered (survives action code changes)
"""
from datetime import datetime, timezone
from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import app.api.v1.impersonations as impersonations_router_module
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _make_identity(role_code: str = "ADM") -> RequestIdentity:
    return RequestIdentity(
        user_id="admin-user",
        username="admin-user",
        email=None,
        tenant_id="default",
        role_code=role_code,
        is_authenticated=True,
        session_id="session-admin",
    )


def _build_app() -> tuple[FastAPI, RequestIdentity]:
    app = FastAPI()
    app.include_router(impersonations_router_module.router, prefix="/api/v1")
    identity = _make_identity()
    return app, identity


def _find_route_dependency(app: FastAPI, path: str, method: str) -> Any:
    """Auto-discover the non-get_db dependency for the given route."""
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == path and method in (r.methods or set())
        ),
    )
    return next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )


def _override_action_dependency(app: FastAPI, path: str, method: str, identity: RequestIdentity) -> Any:
    dep = _find_route_dependency(app, path, method)
    app.dependency_overrides[dep] = lambda: identity
    return dep


# ---------------------------------------------------------------------------
# POST /impersonations (create) — uses admin.impersonation.create
# ---------------------------------------------------------------------------


def test_create_impersonation_delegates_with_correct_params(monkeypatch):
    app, identity = _build_app()
    _override_action_dependency(app, "/api/v1/impersonations", "POST", identity)
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    fake_session = type("S", (), {
        "id": 1,
        "real_user_id": "admin-user",
        "real_role_code": "ADM",
        "acting_role_code": "OPR",
        "tenant_id": "default",
        "reason": "testing",
        "expires_at": datetime(2099, 1, 1, tzinfo=timezone.utc),
        "revoked_at": None,
        "created_at": datetime(2026, 5, 3, tzinfo=timezone.utc),
        "is_active": True,
    })()

    captured = {}

    def fake_create(db, real_user_id, real_role_code, tenant_id, request_data):
        captured["real_user_id"] = real_user_id
        captured["tenant_id"] = tenant_id
        return fake_session

    monkeypatch.setattr(impersonations_router_module, "create_impersonation_session", fake_create)

    client = TestClient(app)
    response = client.post(
        "/api/v1/impersonations",
        json={"acting_role_code": "OPR", "reason": "testing", "duration_minutes": 60},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["real_user_id"] == "admin-user"
    assert body["acting_role_code"] == "OPR"
    assert captured["tenant_id"] == "default"


def test_create_impersonation_rejects_without_action():
    app, identity = _build_app()
    dep = _find_route_dependency(app, "/api/v1/impersonations", "POST")
    app.dependency_overrides[dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/impersonations",
        json={"acting_role_code": "OPR", "reason": "testing", "duration_minutes": 60},
    )

    assert response.status_code == 403


def test_create_impersonation_service_permission_error_returns_403(monkeypatch):
    app, identity = _build_app()
    _override_action_dependency(app, "/api/v1/impersonations", "POST", identity)
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    monkeypatch.setattr(
        impersonations_router_module,
        "create_impersonation_session",
        lambda *a, **kw: (_ for _ in ()).throw(PermissionError("Not allowed")),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/impersonations",
        json={"acting_role_code": "OPR", "reason": "testing", "duration_minutes": 60},
    )

    assert response.status_code == 403


def test_create_impersonation_service_value_error_returns_400(monkeypatch):
    app, identity = _build_app()
    _override_action_dependency(app, "/api/v1/impersonations", "POST", identity)
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    monkeypatch.setattr(
        impersonations_router_module,
        "create_impersonation_session",
        lambda *a, **kw: (_ for _ in ()).throw(ValueError("Bad value")),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/impersonations",
        json={"acting_role_code": "OPR", "reason": "testing", "duration_minutes": 60},
    )

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# POST /impersonations/{id}/revoke — uses admin.impersonation.revoke
# ---------------------------------------------------------------------------


def test_revoke_impersonation_delegates_with_correct_params(monkeypatch):
    app, identity = _build_app()
    _override_action_dependency(app, "/api/v1/impersonations/{session_id}/revoke", "POST", identity)
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    fake_session = type("S", (), {
        "id": 42,
        "real_user_id": "admin-user",
        "real_role_code": "ADM",
        "acting_role_code": "OPR",
        "tenant_id": "default",
        "reason": "testing",
        "expires_at": datetime(2099, 1, 1, tzinfo=timezone.utc),
        "revoked_at": datetime(2026, 5, 3, tzinfo=timezone.utc),
        "created_at": datetime(2026, 5, 3, tzinfo=timezone.utc),
        "is_active": False,
    })()

    captured = {}

    def fake_revoke(db, session_id, requesting_user_id, tenant_id):
        captured["session_id"] = session_id
        captured["requesting_user_id"] = requesting_user_id
        return fake_session

    monkeypatch.setattr(impersonations_router_module, "revoke_impersonation_session", fake_revoke)

    client = TestClient(app)
    response = client.post("/api/v1/impersonations/42/revoke")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 42
    assert captured["session_id"] == 42
    assert captured["requesting_user_id"] == "admin-user"


def test_revoke_impersonation_rejects_without_action():
    app, identity = _build_app()
    dep = _find_route_dependency(app, "/api/v1/impersonations/{session_id}/revoke", "POST")
    app.dependency_overrides[dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.post("/api/v1/impersonations/1/revoke")

    assert response.status_code == 403


def test_revoke_impersonation_not_found_returns_404(monkeypatch):
    app, identity = _build_app()
    _override_action_dependency(app, "/api/v1/impersonations/{session_id}/revoke", "POST", identity)
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    monkeypatch.setattr(
        impersonations_router_module,
        "revoke_impersonation_session",
        lambda *a, **kw: (_ for _ in ()).throw(LookupError("Not found")),
    )

    client = TestClient(app)
    response = client.post("/api/v1/impersonations/999/revoke")

    assert response.status_code == 404


def test_revoke_impersonation_permission_error_returns_403(monkeypatch):
    app, identity = _build_app()
    _override_action_dependency(app, "/api/v1/impersonations/{session_id}/revoke", "POST", identity)
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    monkeypatch.setattr(
        impersonations_router_module,
        "revoke_impersonation_session",
        lambda *a, **kw: (_ for _ in ()).throw(PermissionError("Not owner")),
    )

    client = TestClient(app)
    response = client.post("/api/v1/impersonations/1/revoke")

    assert response.status_code == 403


# ---------------------------------------------------------------------------
# GET /impersonations/current — uses require_authenticated_identity
# ---------------------------------------------------------------------------


def test_current_impersonation_returns_active_session(monkeypatch):
    app, identity = _build_app()
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    fake_session = type("S", (), {
        "id": 7,
        "real_user_id": "admin-user",
        "real_role_code": "ADM",
        "acting_role_code": "OPR",
        "tenant_id": "default",
        "reason": "testing",
        "expires_at": datetime(2099, 1, 1, tzinfo=timezone.utc),
        "revoked_at": None,
        "created_at": datetime(2026, 5, 3, tzinfo=timezone.utc),
        "is_active": True,
    })()

    monkeypatch.setattr(
        impersonations_router_module,
        "get_current_session_for_user",
        lambda db, user_id, tenant_id: fake_session,
    )

    client = TestClient(app)
    response = client.get("/api/v1/impersonations/current")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 7
    assert body["acting_role_code"] == "OPR"


def test_current_impersonation_returns_null_when_no_session(monkeypatch):
    app, identity = _build_app()
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[impersonations_router_module.get_db] = lambda: object()

    monkeypatch.setattr(
        impersonations_router_module,
        "get_current_session_for_user",
        lambda db, user_id, tenant_id: None,
    )

    client = TestClient(app)
    response = client.get("/api/v1/impersonations/current")

    assert response.status_code == 200
    assert response.json() is None
