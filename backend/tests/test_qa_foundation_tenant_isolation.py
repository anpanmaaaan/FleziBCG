from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.products as product_router_module
from app.models.product import Product
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.product_service import create_product


def _build_app(identity: RequestIdentity) -> FastAPI:
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
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


def test_list_products_is_tenant_scoped_and_detail_isolated():
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

    tenant_b_product = create_product(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        payload=ProductCreateRequest(
            product_code="TEN-B-001",
            product_name="Tenant B product",
            product_type="COMPONENT",
        ),
    )

    client = TestClient(app)
    create_a = client.post(
        "/api/v1/products",
        json={
            "product_code": "TEN-A-001",
            "product_name": "Tenant A product",
            "product_type": "FINISHED_GOOD",
        },
    )
    assert create_a.status_code == 200
    tenant_a_product_id = create_a.json()["product_id"]

    listed = client.get("/api/v1/products")
    assert listed.status_code == 200
    listed_ids = {item["product_id"] for item in listed.json()}

    assert tenant_a_product_id in listed_ids
    assert tenant_b_product.product_id not in listed_ids

    hidden_detail = client.get(f"/api/v1/products/{tenant_b_product.product_id}")
    assert hidden_detail.status_code == 404
