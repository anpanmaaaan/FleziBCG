"""Tests for product version foundation API layer (MMD-BE-03).

Covers:
- GET /products/{product_id}/versions — list versions (200, 404 for missing product)
- GET /products/{product_id}/versions/{version_id} — get one (200, 404 for missing)
- Requires only require_authenticated_identity (no action guard)
- No write endpoints present (scope guard regression)
"""
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.products as product_router_module
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
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine, session_local


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


def _mk_version(db, tenant_id: str, product_id: str, version_code: str) -> ProductVersion:
    row = ProductVersion(
        product_version_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        product_id=product_id,
        version_code=version_code,
        version_name=f"Version {version_code}",
        lifecycle_status="DRAFT",
        is_current=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_list_product_versions_returns_200_with_versions():
    identity = _make_identity()
    engine, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    v = _mk_version(db, "tenant_a", product_id, "v1.0")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/versions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["product_version_id"] == v.product_version_id
    assert data[0]["version_code"] == "v1.0"
    assert data[0]["tenant_id"] == "tenant_a"


def test_list_product_versions_returns_empty_list_for_product_without_versions():
    identity = _make_identity()
    engine, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/versions")
    assert response.status_code == 200
    assert response.json() == []


def test_list_product_versions_returns_404_for_missing_product():
    identity = _make_identity()
    engine, session_local = _make_session()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get("/api/v1/products/nonexistent-product-id/versions")
    assert response.status_code == 404


def test_get_product_version_returns_200_with_correct_data():
    identity = _make_identity()
    engine, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    v = _mk_version(db, "tenant_a", product_id, "v2.0")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/versions/{v.product_version_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["product_version_id"] == v.product_version_id
    assert data["version_code"] == "v2.0"
    assert data["product_id"] == product_id
    assert data["lifecycle_status"] == "DRAFT"
    assert data["is_current"] is False


def test_get_product_version_returns_404_for_missing_version():
    identity = _make_identity()
    engine, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/versions/nonexistent-version-id")
    assert response.status_code == 404


def test_get_product_version_returns_404_for_wrong_product():
    identity = _make_identity()
    engine, session_local = _make_session()
    db = session_local()
    product_id_a = _mk_product(db, "tenant_a")
    product_id_b = _mk_product(db, "tenant_a")
    v = _mk_version(db, "tenant_a", product_id_b, "v1.0")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    # Ask for version v (which belongs to product_id_b) via product_id_a
    response = client.get(f"/api/v1/products/{product_id_a}/versions/{v.product_version_id}")
    assert response.status_code == 404


def test_no_write_endpoints_for_product_versions_registered():
    """Scope guard: assert that no POST/PATCH/PUT/DELETE for product versions exists.

    This regression test locks MMD-BE-03 out-of-scope write endpoints.
    """
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")

    write_version_routes = [
        r for r in app.routes
        if hasattr(r, "path") and "/versions" in getattr(r, "path", "")
        and bool(getattr(r, "methods", set()) & {"POST", "PATCH", "PUT", "DELETE"})
    ]
    assert write_version_routes == [], (
        f"Unexpected write endpoints for product versions: {write_version_routes}"
    )
