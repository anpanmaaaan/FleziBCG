from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import app.api.v1.products as product_router_module
from app.models.product import Product
from app.models.security_event import SecurityEventLog
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.product_service import create_product
from app.schemas.product import ProductCreateRequest


def _build_app(identity: RequestIdentity, has_manage: bool = False) -> FastAPI:
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    # Patch has_action to avoid RBAC table queries in isolated SQLite tests.
    product_router_module.has_action = lambda db, ident, action_code, *a, **kw: has_manage
    return app


def _override_action_dependency(app: FastAPI, path: str, method: str, identity: RequestIdentity) -> Any:
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == path and method in (r.methods or set())
        ),
    )
    action_dependency = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[action_dependency] = lambda: identity
    return action_dependency


def _make_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Product.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_product_routes_happy_path_and_state_transitions():
    identity = RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id="tenant_a",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-admin-a",
    )
    app = _build_app(identity)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}", "PATCH", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}/release", "POST", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}/retire", "POST", identity)

    client = TestClient(app)

    created = client.post(
        "/api/v1/products",
        json={
            "product_code": "API-001",
            "product_name": "API Product",
            "product_type": "FINISHED_GOOD",
            "description": "api created",
            "display_metadata": {"label": "new"},
        },
    )
    assert created.status_code == 200
    product_id = created.json()["product_id"]

    listed = client.get("/api/v1/products")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["product_id"] == product_id

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 200
    assert detail.json()["product_code"] == "API-001"

    patch_draft = client.patch(
        f"/api/v1/products/{product_id}",
        json={
            "product_code": "API-002",
            "product_name": "API Product draft updated",
            "product_type": "COMPONENT",
        },
    )
    assert patch_draft.status_code == 200
    assert patch_draft.json()["product_code"] == "API-002"

    release = client.post(f"/api/v1/products/{product_id}/release")
    assert release.status_code == 200
    assert release.json()["lifecycle_status"] == "RELEASED"

    released_non_structural = client.patch(
        f"/api/v1/products/{product_id}",
        json={"product_name": "Released rename", "description": "Released description"},
    )
    assert released_non_structural.status_code == 200

    released_structural_reject = client.patch(
        f"/api/v1/products/{product_id}",
        json={"product_code": "API-003"},
    )
    assert released_structural_reject.status_code == 400

    retire = client.post(f"/api/v1/products/{product_id}/retire")
    assert retire.status_code == 200
    assert retire.json()["lifecycle_status"] == "RETIRED"

    retired_update_reject = client.patch(
        f"/api/v1/products/{product_id}",
        json={"product_name": "Nope"},
    )
    assert retired_update_reject.status_code == 400

    retired_release_reject = client.post(f"/api/v1/products/{product_id}/release")
    assert retired_release_reject.status_code == 400


def test_cross_tenant_get_returns_404_and_duplicate_code_returns_409():
    tenant_a_identity = RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id="tenant_a",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-admin-a",
    )
    app = _build_app(tenant_a_identity)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", tenant_a_identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}", "PATCH", tenant_a_identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}/release", "POST", tenant_a_identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}/retire", "POST", tenant_a_identity)

    created_other_tenant = create_product(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        payload=ProductCreateRequest(
            product_code="X-TEN-001",
            product_name="Other tenant",
            product_type="SEMI_FINISHED",
        ),
    )

    client = TestClient(app)

    hidden = client.get(f"/api/v1/products/{created_other_tenant.product_id}")
    assert hidden.status_code == 404

    first = client.post(
        "/api/v1/products",
        json={
            "product_code": "DUP-001",
            "product_name": "First",
            "product_type": "COMPONENT",
        },
    )
    assert first.status_code == 200

    duplicate = client.post(
        "/api/v1/products",
        json={
            "product_code": "DUP-001",
            "product_name": "Duplicate",
            "product_type": "COMPONENT",
        },
    )
    assert duplicate.status_code == 409


def test_write_routes_reject_without_required_action_override():
    identity = RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id="tenant_a",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-admin-a",
    )
    app = _build_app(identity)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    action_dependency = _override_action_dependency(app, "/api/v1/products", "POST", identity)
    app.dependency_overrides[action_dependency] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    denied = client.post(
        "/api/v1/products",
        json={
            "product_code": "DENY-001",
            "product_name": "Denied",
            "product_type": "COMPONENT",
        },
    )
    assert denied.status_code == 403


def test_product_detail_includes_product_version_capabilities_field():
    identity = RequestIdentity(
        user_id="reader",
        username="reader",
        email=None,
        tenant_id="tenant_caps",
        role_code="OPERATOR",
        is_authenticated=True,
        session_id="s-reader",
    )
    app = _build_app(identity, has_manage=False)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    client = TestClient(app)

    created = client.post(
        "/api/v1/products",
        json={"product_code": "CAP-001", "product_name": "Cap Product", "product_type": "COMPONENT"},
    )
    assert created.status_code == 200
    product_id = created.json()["product_id"]

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert "product_version_capabilities" in body
    assert "can_create" in body["product_version_capabilities"]


def test_product_detail_can_create_false_for_non_manage_user():
    identity = RequestIdentity(
        user_id="reader",
        username="reader",
        email=None,
        tenant_id="tenant_caps2",
        role_code="OPERATOR",
        is_authenticated=True,
        session_id="s-reader2",
    )
    app = _build_app(identity, has_manage=False)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    client = TestClient(app)

    created = client.post(
        "/api/v1/products",
        json={"product_code": "CAP-002", "product_name": "Cap Product 2", "product_type": "COMPONENT"},
    )
    assert created.status_code == 200
    product_id = created.json()["product_id"]

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 200
    assert detail.json()["product_version_capabilities"]["can_create"] is False


def test_product_detail_can_create_true_for_manage_user():
    identity = RequestIdentity(
        user_id="planner",
        username="planner",
        email=None,
        tenant_id="tenant_caps3",
        role_code="PLANNER",
        is_authenticated=True,
        session_id="s-planner",
    )
    app = _build_app(identity, has_manage=True)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    client = TestClient(app)

    created = client.post(
        "/api/v1/products",
        json={"product_code": "CAP-003", "product_name": "Cap Product 3", "product_type": "COMPONENT"},
    )
    assert created.status_code == 200
    product_id = created.json()["product_id"]

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 200
    assert detail.json()["product_version_capabilities"]["can_create"] is True


def test_product_list_includes_product_version_capabilities():
    identity = RequestIdentity(
        user_id="reader",
        username="reader",
        email=None,
        tenant_id="tenant_caps4",
        role_code="OPERATOR",
        is_authenticated=True,
        session_id="s-reader4",
    )
    app = _build_app(identity, has_manage=False)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    client = TestClient(app)

    client.post(
        "/api/v1/products",
        json={"product_code": "CAP-004", "product_name": "Cap Product 4", "product_type": "COMPONENT"},
    )

    listed = client.get("/api/v1/products")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    item = listed.json()[0]
    assert "product_version_capabilities" in item
    assert item["product_version_capabilities"]["can_create"] is False


def test_product_write_response_can_create_false_when_no_pv_manage():
    """Product create/update/release/retire responses return can_create=false
    when the caller lacks admin.master_data.product_version.manage.
    Proves that product.manage alone does NOT imply product_version create capability.
    """
    identity = RequestIdentity(
        user_id="product-admin",
        username="product-admin",
        email=None,
        tenant_id="tenant_write_caps1",
        role_code="PRODUCT_ADMIN",
        is_authenticated=True,
        session_id="s-product-admin",
    )
    # has_manage=False => product_version.manage is False; product.manage is mocked via _override_action_dependency
    app = _build_app(identity, has_manage=False)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}", "PATCH", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}/release", "POST", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}/retire", "POST", identity)
    client = TestClient(app)

    create_resp = client.post(
        "/api/v1/products",
        json={"product_code": "WC-001", "product_name": "Write Cap Product", "product_type": "COMPONENT"},
    )
    assert create_resp.status_code == 200
    assert create_resp.json()["product_version_capabilities"]["can_create"] is False
    product_id = create_resp.json()["product_id"]

    update_resp = client.patch(
        f"/api/v1/products/{product_id}",
        json={"product_name": "Write Cap Product Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["product_version_capabilities"]["can_create"] is False

    release_resp = client.post(f"/api/v1/products/{product_id}/release")
    assert release_resp.status_code == 200
    assert release_resp.json()["product_version_capabilities"]["can_create"] is False

    retire_resp = client.post(f"/api/v1/products/{product_id}/retire")
    assert retire_resp.status_code == 200
    assert retire_resp.json()["product_version_capabilities"]["can_create"] is False


def test_product_write_response_can_create_true_when_has_pv_manage():
    """Product create/update/release/retire responses return can_create=true
    when the caller has admin.master_data.product_version.manage.
    """
    identity = RequestIdentity(
        user_id="super-admin",
        username="super-admin",
        email=None,
        tenant_id="tenant_write_caps2",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-super-admin",
    )
    # has_manage=True => product_version.manage is True
    app = _build_app(identity, has_manage=True)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}", "PATCH", identity)
    _override_action_dependency(app, "/api/v1/products/{product_id}/release", "POST", identity)
    client = TestClient(app)

    create_resp = client.post(
        "/api/v1/products",
        json={"product_code": "WC-002", "product_name": "Super Product", "product_type": "FINISHED_GOOD"},
    )
    assert create_resp.status_code == 200
    assert create_resp.json()["product_version_capabilities"]["can_create"] is True
    product_id = create_resp.json()["product_id"]

    update_resp = client.patch(
        f"/api/v1/products/{product_id}",
        json={"product_name": "Super Product Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["product_version_capabilities"]["can_create"] is True

    release_resp = client.post(f"/api/v1/products/{product_id}/release")
    assert release_resp.status_code == 200
    assert release_resp.json()["product_version_capabilities"]["can_create"] is True
