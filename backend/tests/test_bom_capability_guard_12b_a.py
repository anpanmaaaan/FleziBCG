"""BOM Capability Guard tests (MMD-FULLSTACK-12B-A verification patch)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.products as product_router_module
from app.models.bom import Bom, BomItem
from app.models.product import Product
from app.models.product_version import ProductVersion
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.product_service import create_product


def _build_app(identity: RequestIdentity, has_manage: bool = False) -> FastAPI:
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    # Patch has_action to avoid RBAC table queries in isolated SQLite tests.
    product_router_module.has_action = lambda db, ident, action_code, *a, **kw: has_manage
    return app


def _override_action_dependency(app: FastAPI, path: str, method: str, identity: RequestIdentity):
    route = next(
        r
        for r in app.routes
        if getattr(r, "path", "") == path and method in (r.methods or set())
    )
    action_dependency = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[action_dependency] = lambda: identity


def _make_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Product.__table__.create(bind=engine)
    ProductVersion.__table__.create(bind=engine)
    Bom.__table__.create(bind=engine)
    BomItem.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_product_detail_includes_bom_capabilities_field():
    """GET /products/{product_id} includes bom_capabilities field (MMD-FULLSTACK-12B)."""
    identity = RequestIdentity(
        user_id="reader",
        username="reader",
        email=None,
        tenant_id="tenant_bom_caps",
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
        json={"product_code": "BOM-CAP-001", "product_name": "BOM Cap Product", "product_type": "COMPONENT"},
    )
    assert created.status_code == 200
    product_id = created.json()["product_id"]

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert "bom_capabilities" in body, "Missing bom_capabilities field"
    assert "can_create" in body["bom_capabilities"], "Missing can_create in bom_capabilities"


def test_product_detail_bom_can_create_false_for_non_manage_user():
    """GET /products/{product_id} returns bom_capabilities.can_create=false
    when caller lacks admin.master_data.bom.manage permission (MMD-FULLSTACK-12B-A).
    """
    identity = RequestIdentity(
        user_id="operator",
        username="operator",
        email=None,
        tenant_id="tenant_bom_caps2",
        role_code="OPERATOR",
        is_authenticated=True,
        session_id="s-operator",
    )
    # has_manage=False => bom.manage is False
    app = _build_app(identity, has_manage=False)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    client = TestClient(app)

    created = client.post(
        "/api/v1/products",
        json={"product_code": "BOM-CAP-002", "product_name": "BOM Cap 2", "product_type": "COMPONENT"},
    )
    assert created.status_code == 200
    product_id = created.json()["product_id"]

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 200
    assert detail.json()["bom_capabilities"]["can_create"] is False, \
        "User without bom.manage should have can_create=false"


def test_product_detail_bom_can_create_true_for_manage_user():
    """GET /products/{product_id} returns bom_capabilities.can_create=true
    when caller has admin.master_data.bom.manage permission (MMD-FULLSTACK-12B-A).
    """
    identity = RequestIdentity(
        user_id="bom-admin",
        username="bom-admin",
        email=None,
        tenant_id="tenant_bom_caps3",
        role_code="BOM_ADMIN",
        is_authenticated=True,
        session_id="s-bom-admin",
    )
    # has_manage=True => bom.manage is True
    app = _build_app(identity, has_manage=True)
    db = _make_session()
    app.dependency_overrides[product_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/products", "POST", identity)
    client = TestClient(app)

    created = client.post(
        "/api/v1/products",
        json={"product_code": "BOM-CAP-003", "product_name": "BOM Cap 3", "product_type": "COMPONENT"},
    )
    assert created.status_code == 200
    product_id = created.json()["product_id"]

    detail = client.get(f"/api/v1/products/{product_id}")
    assert detail.status_code == 200
    assert detail.json()["bom_capabilities"]["can_create"] is True, \
        "User with bom.manage should have can_create=true"


def test_product_list_includes_bom_capabilities():
    """GET /products includes bom_capabilities in each product item (MMD-FULLSTACK-12B-A)."""
    identity = RequestIdentity(
        user_id="reader",
        username="reader",
        email=None,
        tenant_id="tenant_bom_list_caps",
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
        json={"product_code": "BOM-LIST-001", "product_name": "BOM List Product", "product_type": "COMPONENT"},
    )
    assert created.status_code == 200

    listed = client.get("/api/v1/products")
    assert listed.status_code == 200
    assert len(listed.json()) >= 1
    item = listed.json()[0]
    assert "bom_capabilities" in item, "Missing bom_capabilities in product list item"
    assert "can_create" in item["bom_capabilities"], "Missing can_create in product list item"
    assert item["bom_capabilities"]["can_create"] is False, \
        "Non-manage user should have can_create=false in list"
