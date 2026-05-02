"""Tests for BOM foundation API layer (MMD-BE-05)."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException
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


def _make_identity(tenant_id: str = "tenant_a") -> RequestIdentity:
    return RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id=tenant_id,
        role_code="ADMIN",
        is_authenticated=True,
    )


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
    return session_local


def _build_app(identity: RequestIdentity, session_local) -> FastAPI:
    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()
    return app


def _mk_product(db, tenant_id: str = "tenant_a") -> str:
    created = create_product(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code=f"FG-{uuid.uuid4().hex[:8]}",
            product_name="Test Product",
            product_type="FINISHED_GOOD",
        ),
    )
    return created.product_id


def _mk_bom(db, *, tenant_id: str, product_id: str, bom_code: str, bom_name: str = "Main BOM") -> Bom:
    row = Bom(
        bom_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        bom_code=bom_code,
        bom_name=bom_name,
        lifecycle_status="DRAFT",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _mk_bom_item(db, *, tenant_id: str, bom_id: str, component_product_id: str, line_no: int) -> BomItem:
    row = BomItem(
        bom_item_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        bom_id=bom_id,
        component_product_id=component_product_id,
        line_no=line_no,
        quantity=1.0,
        unit_of_measure="PCS",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_list_boms_returns_boms_for_product():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="BOM-1")
    _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="BOM-2")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_boms_returns_empty_for_product_with_no_boms():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms")
    assert response.status_code == 200
    assert response.json() == []


def test_list_boms_returns_404_for_missing_product():
    identity = _make_identity()
    session_local = _make_session()
    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get("/api/v1/products/not-found-product/boms")
    assert response.status_code == 404


def test_get_bom_returns_detail_with_items():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    parent_product = _mk_product(db, "tenant_a")
    component_1 = _mk_product(db, "tenant_a")
    component_2 = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=parent_product, bom_code="BOM-DET")
    bom_id = bom.bom_id
    _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=component_1, line_no=20)
    _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=component_2, line_no=10)
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{parent_product}/boms/{bom_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["bom_id"] == bom_id
    assert [item["line_no"] for item in payload["items"]] == [10, 20]


def test_get_bom_returns_404_for_wrong_product():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_a = _mk_product(db, "tenant_a")
    product_b = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_a, bom_code="BOM-A")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_b}/boms/{bom.bom_id}")
    assert response.status_code == 404


def test_get_bom_returns_404_for_missing_bom():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms/not-found-bom")
    assert response.status_code == 404


def test_bom_read_requires_auth_if_product_reads_require_auth():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    app.dependency_overrides[require_authenticated_identity] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=401, detail="Unauthorized")
    )
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms")
    assert response.status_code == 401


def test_bom_routes_do_not_expose_write_methods():
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")

    write_bom_routes = [
        route
        for route in app.routes
        if hasattr(route, "path")
        and "/boms" in getattr(route, "path", "")
        and bool(getattr(route, "methods", set()) & {"POST", "PATCH", "PUT", "DELETE"})
    ]
    assert write_bom_routes == []


def test_bom_api_has_no_post_patch_delete_routes():
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")

    methods = set()
    for route in app.routes:
        if hasattr(route, "path") and "/boms" in getattr(route, "path", ""):
            methods |= set(getattr(route, "methods", set()))

    assert "GET" in methods
    assert not ({"POST", "PATCH", "PUT", "DELETE"} & methods)


def test_bom_model_has_no_backflush_or_erp_fields():
    columns = set(Bom.__table__.columns.keys())
    forbidden = {
        "backflush",
        "backflush_policy",
        "erp_posting",
        "erp_document",
        "inventory_movement",
        "material_consumption",
    }
    assert columns.isdisjoint(forbidden)


def test_bom_model_has_no_inventory_movement_fields():
    columns = set(Bom.__table__.columns.keys())
    forbidden = {
        "inventory_movement",
        "inventory_issue",
        "reservation_id",
        "warehouse_location",
    }
    assert columns.isdisjoint(forbidden)
