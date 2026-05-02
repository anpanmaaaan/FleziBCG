from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import app.api.v1.auth as auth_router_module
from app.security.auth import AuthIdentity
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def test_require_authenticated_identity_rejects_tenant_header_mismatch(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    monkeypatch.setattr(
        "app.repositories.tenant_repository.is_tenant_lifecycle_active",
        lambda db, tenant_id: True,
    )

    app = FastAPI()

    @app.middleware("http")
    async def attach_identity(request, call_next):
        request.state.auth_identity = AuthIdentity(
            user_id="u-1",
            username="demo",
            email="demo@mes.local",
            tenant_id="tenant_a",
            role_code="SUP",
            session_id="s-1",
        )
        return await call_next(request)

    @app.get("/secure")
    def secure(identity: RequestIdentity = Depends(require_authenticated_identity)):
        return {"tenant_id": identity.tenant_id}

    client = TestClient(app)
    response = client.get("/secure", headers={"X-Tenant-ID": "tenant_b"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Tenant header mismatch"


def test_require_authenticated_identity_allows_missing_tenant_header(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "app.services.session_service.is_session_active",
        lambda db, session_id, tenant_id: True,
    )
    monkeypatch.setattr(
        "app.repositories.tenant_repository.is_tenant_lifecycle_active",
        lambda db, tenant_id: True,
    )

    app = FastAPI()

    @app.middleware("http")
    async def attach_identity(request, call_next):
        request.state.auth_identity = AuthIdentity(
            user_id="u-1",
            username="demo",
            email="demo@mes.local",
            tenant_id="tenant_a",
            role_code="SUP",
            session_id="s-1",
        )
        return await call_next(request)

    @app.get("/secure")
    def secure(identity: RequestIdentity = Depends(require_authenticated_identity)):
        return {"tenant_id": identity.tenant_id}

    client = TestClient(app)
    response = client.get("/secure")

    assert response.status_code == 200
    assert response.json()["tenant_id"] == "tenant_a"


def test_login_uses_x_tenant_id_for_auth_and_session(monkeypatch) -> None:
    captured = {"auth_tenant": None, "session_tenant": None}

    def _auth(db, username, password, tenant_id="default"):
        captured["auth_tenant"] = tenant_id
        return AuthIdentity(
            user_id="u-1",
            username=username,
            email="demo@mes.local",
            tenant_id=tenant_id,
            role_code="SUP",
            session_id=None,
        )

    class _SessionObj:
        session_id = "session-xyz"

    def _create_session(db, user_id, tenant_id):
        captured["session_tenant"] = tenant_id
        return _SessionObj()

    monkeypatch.setattr(auth_router_module, "authenticate_user_db", _auth)
    monkeypatch.setattr(auth_router_module, "create_login_session", _create_session)

    app = FastAPI()
    app.include_router(auth_router_module.router)
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        json={"username": "demo", "password": "secret"},
        headers={"X-Tenant-ID": "tenant_b"},
    )

    assert response.status_code == 200
    assert captured["auth_tenant"] == "tenant_b"
    assert captured["session_tenant"] == "tenant_b"
    assert response.json()["user"]["tenant_id"] == "tenant_b"
