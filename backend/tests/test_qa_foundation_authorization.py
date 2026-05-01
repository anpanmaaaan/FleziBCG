from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.security.auth import AuthIdentity
from app.security.dependencies import (
    _get_security_db,
    RequestIdentity,
    require_action,
    require_authenticated_identity,
)


class _DummyDb:
    def close(self) -> None:
        return None


def _with_identity(identity: AuthIdentity | None):
    app = FastAPI()

    @app.middleware("http")
    async def attach_identity(request, call_next):
        request.state.auth_identity = identity
        return await call_next(request)

    return app


def test_protected_route_requires_authentication(monkeypatch):
    app = _with_identity(None)
    app.dependency_overrides[_get_security_db] = lambda: _DummyDb()

    @app.get("/protected")
    def protected(identity: RequestIdentity = Depends(require_authenticated_identity)):
        return {"tenant_id": identity.tenant_id}

    client = TestClient(app)
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_missing_required_action_returns_403(monkeypatch):
    identity = AuthIdentity(
        user_id="u-1",
        username="demo",
        email="demo@mes.local",
        tenant_id="default",
        role_code="SUP",
        session_id="s-1",
    )
    app = _with_identity(identity)
    app.dependency_overrides[_get_security_db] = lambda: _DummyDb()

    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    monkeypatch.setattr("app.security.dependencies.has_action", lambda db, identity, code: False)
    monkeypatch.setattr(
        "app.repositories.impersonation_repository.get_active_impersonation_session",
        lambda db, user_id, tenant_id: None,
    )

    @app.get("/guarded")
    def guarded(_: RequestIdentity = Depends(require_action("admin.user.manage"))):
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/guarded")

    assert response.status_code == 403
    assert response.json()["detail"] == "Missing required action: admin.user.manage"


def test_action_guard_allows_request_when_action_present(monkeypatch):
    identity = AuthIdentity(
        user_id="u-2",
        username="planner",
        email="planner@mes.local",
        tenant_id="default",
        role_code="SUP",
        session_id="s-2",
    )
    app = _with_identity(identity)
    app.dependency_overrides[_get_security_db] = lambda: _DummyDb()

    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    monkeypatch.setattr("app.security.dependencies.has_action", lambda db, identity, code: True)
    monkeypatch.setattr(
        "app.repositories.impersonation_repository.get_active_impersonation_session",
        lambda db, user_id, tenant_id: None,
    )

    @app.get("/guarded")
    def guarded(_: RequestIdentity = Depends(require_action("admin.user.manage"))):
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/guarded")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
