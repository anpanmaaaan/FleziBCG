"""Tests for BOM foundation API layer (MMD-BE-05)."""

from __future__ import annotations

import uuid
from typing import Any, cast

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
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
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


def _mk_bom(
    db,
    *,
    tenant_id: str,
    product_id: str,
    bom_code: str,
    bom_name: str = "Main BOM",
    lifecycle_status: str = "DRAFT",
) -> Bom:
    row = Bom(
        bom_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        bom_code=bom_code,
        bom_name=bom_name,
        lifecycle_status=lifecycle_status,
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


def test_bom_write_routes_exist_for_mmd_be_12():
    """MMD-BE-12: BOM write routes must now be present."""
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")

    bom_paths_and_methods = [
        (getattr(r, "path", ""), frozenset(getattr(r, "methods", set())))
        for r in app.routes
        if "/boms" in getattr(r, "path", "")
    ]
    all_methods = set()
    for _, methods in bom_paths_and_methods:
        all_methods |= methods

    assert "GET" in all_methods
    assert "POST" in all_methods
    assert "PATCH" in all_methods
    assert "DELETE" in all_methods


def test_no_bom_hard_delete_reactivate_clone_bind_product_version_routes_exist():
    """Boundary guard: forbidden BOM endpoints must not be added until governed."""
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")

    route_signatures = [
        (getattr(r, "path", ""), frozenset(getattr(r, "methods", set())))
        for r in app.routes
    ]
    forbidden = [
        ("/api/v1/products/{product_id}/boms/{bom_id}", {"DELETE"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/reactivate", {"POST"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/clone", {"POST"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/bind-product-version", {"POST"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/bulk-import", {"POST"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/replace-items", {"POST"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/material-reserve", {"POST"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/backflush", {"POST"}),
        ("/api/v1/products/{product_id}/boms/{bom_id}/erp-post", {"POST"}),
    ]
    for path, methods in forbidden:
        matched = [
            r_methods
            for r_path, r_methods in route_signatures
            if r_path == path and r_methods & methods
        ]
        assert not matched, f"Forbidden route found: {methods} {path}"


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


# ─── MMD-BE-12 BOM write API tests ───────────────────────────────────────────

def _override_bom_manage(app: FastAPI, path: str, method: str, identity: RequestIdentity) -> Any:
    """Override the require_action dependency for a specific BOM write route."""
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == path and method in (r.methods or set())
        ),
    )
    action_dep = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[action_dep] = lambda: identity
    return action_dep


def _make_managed_app(identity: RequestIdentity, session_local) -> FastAPI:
    """Build app with manage identity injected for all BOM write routes."""
    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    write_routes = [
        ("/api/v1/products/{product_id}/boms", "POST"),
        ("/api/v1/products/{product_id}/boms/{bom_id}", "PATCH"),
        ("/api/v1/products/{product_id}/boms/{bom_id}/release", "POST"),
        ("/api/v1/products/{product_id}/boms/{bom_id}/retire", "POST"),
        ("/api/v1/products/{product_id}/boms/{bom_id}/items", "POST"),
        ("/api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}", "PATCH"),
        ("/api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}", "DELETE"),
    ]
    for path, method in write_routes:
        _override_bom_manage(app, path, method, identity)

    return app


# ── Create BOM ────────────────────────────────────────────────────────────────

def test_create_bom_creates_draft():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms",
        json={"bom_code": "BOM-A", "bom_name": "BOM Alpha"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bom_code"] == "BOM-A"
    assert data["lifecycle_status"] == "DRAFT"
    assert data["product_id"] == product_id


def test_create_bom_rejects_duplicate_code_for_same_product():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)
    client.post(f"/api/v1/products/{product_id}/boms", json={"bom_code": "BOM-DUP", "bom_name": "BOM"})
    second = client.post(f"/api/v1/products/{product_id}/boms", json={"bom_code": "BOM-DUP", "bom_name": "BOM"})
    assert second.status_code == 409


def test_create_bom_rejects_lifecycle_status_payload():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms",
        json={"bom_code": "BOM-A", "bom_name": "BOM Alpha", "lifecycle_status": "RELEASED"},
    )
    assert response.status_code == 422


def test_create_bom_rejects_product_version_id_payload():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms",
        json={"bom_code": "BOM-A", "bom_name": "BOM Alpha", "product_version_id": "pv-001"},
    )
    assert response.status_code == 422


def test_create_bom_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    # Build app WITHOUT manage override  (uses require_authenticated_identity for reads only)
    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    # Override the action dependency to deny
    deny_dep = _override_bom_manage(app, "/api/v1/products/{product_id}/boms", "POST", identity)
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/products/{product_id}/boms",
        json={"bom_code": "BOM-A", "bom_name": "BOM Alpha"},
    )
    assert response.status_code == 403


# ── Update BOM ────────────────────────────────────────────────────────────────

def test_update_bom_allows_draft_metadata_update():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="U-001")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}",
        json={"bom_name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["bom_name"] == "Updated Name"


def test_update_bom_rejects_released():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="U-002", lifecycle_status="RELEASED")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}",
        json={"bom_name": "Changed"},
    )
    assert response.status_code == 400


def test_update_bom_rejects_retired():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="U-003", lifecycle_status="RETIRED")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}",
        json={"bom_name": "Changed"},
    )
    assert response.status_code == 400


def test_update_bom_rejects_lifecycle_status_patch():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="U-004")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}",
        json={"lifecycle_status": "RELEASED"},
    )
    assert response.status_code == 422


def test_update_bom_rejects_product_version_id_patch():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="U-005")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}",
        json={"product_version_id": "pv-x"},
    )
    assert response.status_code == 422


def test_update_bom_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="U-006")
    db.close()

    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    deny_dep = _override_bom_manage(
        app, "/api/v1/products/{product_id}/boms/{bom_id}", "PATCH", identity
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}",
        json={"bom_name": "Changed"},
    )
    assert response.status_code == 403


# ── Release BOM ───────────────────────────────────────────────────────────────

def test_release_bom_changes_draft_to_released():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="R-001")
    _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=comp_id, line_no=10)
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(f"/api/v1/products/{product_id}/boms/{bom.bom_id}/release")
    assert response.status_code == 200
    assert response.json()["lifecycle_status"] == "RELEASED"


def test_release_bom_rejects_released_or_retired():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom_released = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="R-002", lifecycle_status="RELEASED"
    )
    bom_retired = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="R-003", lifecycle_status="RETIRED"
    )
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    assert client.post(f"/api/v1/products/{product_id}/boms/{bom_released.bom_id}/release").status_code == 400
    assert client.post(f"/api/v1/products/{product_id}/boms/{bom_retired.bom_id}/release").status_code == 400


def test_release_bom_requires_items():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="R-004")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(f"/api/v1/products/{product_id}/boms/{bom.bom_id}/release")
    assert response.status_code == 400


def test_release_bom_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="R-005")
    db.close()

    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    deny_dep = _override_bom_manage(
        app, "/api/v1/products/{product_id}/boms/{bom_id}/release", "POST", identity
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    assert client.post(f"/api/v1/products/{product_id}/boms/{bom.bom_id}/release").status_code == 403


# ── Retire BOM ────────────────────────────────────────────────────────────────

def test_retire_bom_changes_draft_or_released_to_retired():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom_draft = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RT-001")
    bom_released = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="RT-002", lifecycle_status="RELEASED"
    )
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    r1 = client.post(f"/api/v1/products/{product_id}/boms/{bom_draft.bom_id}/retire")
    assert r1.status_code == 200
    assert r1.json()["lifecycle_status"] == "RETIRED"

    r2 = client.post(f"/api/v1/products/{product_id}/boms/{bom_released.bom_id}/retire")
    assert r2.status_code == 200
    assert r2.json()["lifecycle_status"] == "RETIRED"


def test_retire_bom_rejects_retired():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="RT-003", lifecycle_status="RETIRED"
    )
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(f"/api/v1/products/{product_id}/boms/{bom.bom_id}/retire")
    assert response.status_code == 400


def test_retire_bom_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RT-004")
    db.close()

    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    deny_dep = _override_bom_manage(
        app, "/api/v1/products/{product_id}/boms/{bom_id}/retire", "POST", identity
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    assert client.post(f"/api/v1/products/{product_id}/boms/{bom.bom_id}/retire").status_code == 403


# ── Add BOM Item ──────────────────────────────────────────────────────────────

def test_add_bom_item_allows_draft_parent():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-001")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items",
        json={"component_product_id": comp_id, "line_no": 10, "quantity": 2.0, "unit_of_measure": "PCS"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["component_product_id"] == comp_id
    assert data["line_no"] == 10


def test_add_bom_item_rejects_released_or_retired_parent():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom_released = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-002", lifecycle_status="RELEASED"
    )
    bom_retired = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-003", lifecycle_status="RETIRED"
    )
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    item_payload = {"component_product_id": comp_id, "line_no": 10, "quantity": 1.0, "unit_of_measure": "PCS"}
    assert client.post(
        f"/api/v1/products/{product_id}/boms/{bom_released.bom_id}/items", json=item_payload
    ).status_code == 400
    assert client.post(
        f"/api/v1/products/{product_id}/boms/{bom_retired.bom_id}/items", json=item_payload
    ).status_code == 400


def test_add_bom_item_rejects_parent_as_component():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-004")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items",
        json={"component_product_id": product_id, "line_no": 10, "quantity": 1.0, "unit_of_measure": "PCS"},
    )
    assert response.status_code == 400


def test_add_bom_item_rejects_duplicate_line_no():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-005")
    _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=comp_id, line_no=10)
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items",
        json={"component_product_id": comp_id, "line_no": 10, "quantity": 1.0, "unit_of_measure": "PCS"},
    )
    assert response.status_code == 409


def test_add_bom_item_rejects_non_positive_quantity():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-006")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items",
        json={"component_product_id": comp_id, "line_no": 10, "quantity": 0.0, "unit_of_measure": "PCS"},
    )
    assert response.status_code == 400


def test_add_bom_item_rejects_negative_scrap_factor():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-007")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items",
        json={
            "component_product_id": comp_id,
            "line_no": 10,
            "quantity": 1.0,
            "unit_of_measure": "PCS",
            "scrap_factor": -0.1,
        },
    )
    assert response.status_code == 400


def test_add_bom_item_validates_component_exists():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-008")
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items",
        json={"component_product_id": "nonexistent-id", "line_no": 10, "quantity": 1.0, "unit_of_measure": "PCS"},
    )
    assert response.status_code == 404


def test_add_bom_item_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AI-009")
    db.close()

    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    deny_dep = _override_bom_manage(
        app, "/api/v1/products/{product_id}/boms/{bom_id}/items", "POST", identity
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.post(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items",
        json={"component_product_id": comp_id, "line_no": 10, "quantity": 1.0, "unit_of_measure": "PCS"},
    )
    assert response.status_code == 403


# ── Update BOM Item ───────────────────────────────────────────────────────────

def test_update_bom_item_allows_draft_parent():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="UI-001")
    item = _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=comp_id, line_no=10)
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items/{item.bom_item_id}",
        json={"quantity": 5.0},
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 5.0


def test_update_bom_item_rejects_released_or_retired_parent():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom_released = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="UI-002", lifecycle_status="RELEASED"
    )
    item = _mk_bom_item(
        db, tenant_id="tenant_a", bom_id=bom_released.bom_id, component_product_id=comp_id, line_no=10
    )
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom_released.bom_id}/items/{item.bom_item_id}",
        json={"quantity": 5.0},
    )
    assert response.status_code == 400


def test_update_bom_item_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="UI-003")
    item = _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=comp_id, line_no=10)
    db.close()

    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    deny_dep = _override_bom_manage(
        app,
        "/api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}",
        "PATCH",
        identity,
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.patch(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items/{item.bom_item_id}",
        json={"quantity": 5.0},
    )
    assert response.status_code == 403


# ── Remove BOM Item ───────────────────────────────────────────────────────────

def test_remove_bom_item_allows_draft_parent():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RI-001")
    item = _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=comp_id, line_no=10)
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.delete(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items/{item.bom_item_id}"
    )
    assert response.status_code == 204


def test_remove_bom_item_rejects_released_or_retired_parent():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom_released = _mk_bom(
        db, tenant_id="tenant_a", product_id=product_id, bom_code="RI-002", lifecycle_status="RELEASED"
    )
    item = _mk_bom_item(
        db, tenant_id="tenant_a", bom_id=bom_released.bom_id, component_product_id=comp_id, line_no=10
    )
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.delete(
        f"/api/v1/products/{product_id}/boms/{bom_released.bom_id}/items/{item.bom_item_id}"
    )
    assert response.status_code == 400


def test_remove_bom_item_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    comp_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RI-003")
    item = _mk_bom_item(db, tenant_id="tenant_a", bom_id=bom.bom_id, component_product_id=comp_id, line_no=10)
    db.close()

    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()

    deny_dep = _override_bom_manage(
        app,
        "/api/v1/products/{product_id}/boms/{bom_id}/items/{bom_item_id}",
        "DELETE",
        identity,
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.delete(
        f"/api/v1/products/{product_id}/boms/{bom.bom_id}/items/{item.bom_item_id}"
    )
    assert response.status_code == 403


def test_bom_read_endpoints_do_not_require_manage_action():
    """Read endpoints must remain authenticated-read — no require_action gate."""
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RD-001")
    db.close()

    # Build app with authenticated identity but NO manage override
    app = _build_app(identity, session_local)
    client = TestClient(app)

    r1 = client.get(f"/api/v1/products/{product_id}/boms")
    assert r1.status_code == 200

    r2 = client.get(f"/api/v1/products/{product_id}/boms/{bom.bom_id}")
    assert r2.status_code == 200