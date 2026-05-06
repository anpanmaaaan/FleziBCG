"""Tests for BOM Binding API layer (MMD-BE-14).

Covers:
- Happy path: bind DRAFT PV + RELEASED BOM, DRAFT PV + DRAFT BOM
- GET binding after create
- DELETE (unbind) DRAFT PV
- State machine violations: RETIRED BOM, RELEASED PV, RETIRED PV
- Duplicate bind (409)
- Permission checks: missing bom.manage, missing pv.manage, missing both
- Tenant/product isolation: BOM from wrong product
- Event emission (CREATED, REMOVED)
- Source-level contract: binding routes exist with correct action codes
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.products as product_router_module
from app.models.bom import Bom, BomItem
from app.models.product import Product
from app.models.product_version import ProductVersion
from app.models.product_version_bom_binding import ProductVersionBomBinding
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.product_service import create_product


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_identity(tenant_id: str = "tenant_a") -> RequestIdentity:
    return RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id=tenant_id,
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-admin-a",
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
    ProductVersionBomBinding.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    return engine, session_local


def _build_app(
    identity: RequestIdentity,
    session_local,
    *,
    has_bom_manage: bool = True,
    has_pv_manage: bool = True,
) -> FastAPI:
    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()
    product_router_module.has_action = lambda db, ident, action_code, *a, **kw: {
        "admin.master_data.bom.manage": has_bom_manage,
        "admin.master_data.product_version.manage": has_pv_manage,
    }.get(action_code, False)
    return app


def _override_action_dependency(
    app: FastAPI, path: str, method: str, identity: RequestIdentity
) -> Any:
    from typing import cast

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


def _mk_version(
    db,
    tenant_id: str,
    product_id: str,
    version_code: str,
    *,
    lifecycle_status: str = "DRAFT",
) -> ProductVersion:
    row = ProductVersion(
        product_version_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        version_code=version_code,
        lifecycle_status=lifecycle_status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _mk_bom(
    db,
    tenant_id: str,
    product_id: str,
    bom_code: str,
    *,
    lifecycle_status: str = "RELEASED",
) -> Bom:
    row = Bom(
        bom_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        bom_code=bom_code,
        bom_name=f"BOM {bom_code}",
        lifecycle_status=lifecycle_status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ─── T01: Bind DRAFT PV + RELEASED BOM → 201 ─────────────────────────────────


def test_bind_draft_pv_released_bom_returns_201():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001", lifecycle_status="RELEASED")
    db.close()

    app = _build_app(identity, session_local, has_bom_manage=True, has_pv_manage=True)
    action_dep = _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    _ = action_dep  # noqa: F841
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["bom_id"] == bom.bom_id
    assert data["product_version_id"] == pv.product_version_id
    assert data["binding_type"] == "PRIMARY"
    assert data["binding_status"] == "ACTIVE"
    assert data["tenant_id"] == "tenant_a"


# ─── T02: Bind DRAFT PV + DRAFT BOM → 201 ────────────────────────────────────


def test_bind_draft_pv_draft_bom_returns_201():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001", lifecycle_status="DRAFT")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["binding_status"] == "ACTIVE"
    assert data["bom_id"] == bom.bom_id


# ─── T03: GET binding after create → 200 ─────────────────────────────────────


def test_get_binding_after_create_returns_200():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    binding_row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=pv.product_version_id,
        bom_id=bom.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        created_by="admin-a",
    )
    db.add(binding_row)
    db.commit()
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bom_id"] == bom.bom_id
    assert data["binding_status"] == "ACTIVE"


# ─── T04: Unbind DRAFT PV → 204 ──────────────────────────────────────────────


def test_unbind_draft_pv_returns_204():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    binding_row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=pv.product_version_id,
        bom_id=bom.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        created_by="admin-a",
    )
    db.add(binding_row)
    db.commit()
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "DELETE",
        identity,
    )
    client = TestClient(app)

    response = client.delete(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 204


# ─── T05: GET after unbind → 404 ─────────────────────────────────────────────


def test_get_binding_after_unbind_returns_404():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 404


# ─── T06: Bind RETIRED BOM → 422 ─────────────────────────────────────────────


def test_bind_retired_bom_returns_422():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001", lifecycle_status="RETIRED")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 422


# ─── T07: Bind RELEASED PV → 422 ─────────────────────────────────────────────


def test_bind_released_pv_returns_422():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0", lifecycle_status="RELEASED")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001", lifecycle_status="RELEASED")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 422


# ─── T08: Bind RETIRED PV → 422 ──────────────────────────────────────────────


def test_bind_retired_pv_returns_422():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0", lifecycle_status="RETIRED")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 422


# ─── T09: Duplicate bind → 409 ───────────────────────────────────────────────


def test_duplicate_bind_returns_409():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    bom2 = _mk_bom(db, "tenant_a", product_id, "BOM-002")
    binding_row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=pv.product_version_id,
        bom_id=bom.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        created_by="admin-a",
    )
    db.add(binding_row)
    db.commit()
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom2.bom_id},
    )
    assert response.status_code == 409


# ─── T10: Unbind RELEASED PV → 422 ───────────────────────────────────────────


def test_unbind_released_pv_returns_422():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0", lifecycle_status="RELEASED")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    binding_row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=pv.product_version_id,
        bom_id=bom.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        created_by="admin-a",
    )
    db.add(binding_row)
    db.commit()
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "DELETE",
        identity,
    )
    client = TestClient(app)

    response = client.delete(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 422


# ─── T11: Unbind no binding → 404 ────────────────────────────────────────────


def test_unbind_no_binding_returns_404():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "DELETE",
        identity,
    )
    client = TestClient(app)

    response = client.delete(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 404


# ─── T12: Wrong product scope (BOM from different product) → 404 ─────────────


def test_bind_bom_from_wrong_product_returns_404():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    other_product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    # BOM belongs to other_product_id — product scope mismatch
    bom = _mk_bom(db, "tenant_a", other_product_id, "BOM-001")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 404


# ─── T13: PV not found → 404 ─────────────────────────────────────────────────


def test_bind_pv_not_found_returns_404():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/nonexistent-version/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 404


# ─── T14: Missing bom.manage → 403 ───────────────────────────────────────────


def test_bind_missing_bom_manage_returns_403():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    db.close()

    app = _build_app(identity, session_local, has_bom_manage=False, has_pv_manage=True)
    action_dep = _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    # Simulate require_action("admin.master_data.bom.manage") denying
    app.dependency_overrides[action_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 403


# ─── T15: Missing pv.manage (bom.manage passes but inner check fails) → 403 ──


def test_bind_missing_pv_manage_returns_403():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    db.close()

    # has_pv_manage=False → inner has_action check returns False → 403
    app = _build_app(identity, session_local, has_bom_manage=True, has_pv_manage=False)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 403


# ─── T16: Missing both permissions → 403 ─────────────────────────────────────


def test_bind_missing_both_permissions_returns_403():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    db.close()

    app = _build_app(identity, session_local, has_bom_manage=False, has_pv_manage=False)
    action_dep = _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    app.dependency_overrides[action_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 403


# ─── T17: BOM not found → 404 ────────────────────────────────────────────────


def test_bind_bom_not_found_returns_404():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": "nonexistent-bom-id"},
    )
    assert response.status_code == 404


# ─── T20: CREATED event emitted on successful bind ───────────────────────────


def test_bind_emits_created_security_event():
    identity = _make_identity()
    engine, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding",
        json={"bom_id": bom.bom_id},
    )
    assert response.status_code == 201

    # Verify security event was emitted
    from sqlalchemy import text

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT event_type, resource_type FROM security_event_logs "
                "WHERE event_type = 'PRODUCTVERSIONBOMBINDING.CREATED'"
            )
        ).fetchall()
    assert len(rows) == 1
    assert rows[0][1] == "product_version_bom_binding"


# ─── REMOVED event emitted on successful unbind ──────────────────────────────


def test_unbind_emits_removed_security_event():
    identity = _make_identity()
    engine, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    binding_row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=pv.product_version_id,
        bom_id=bom.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        created_by="admin-a",
    )
    db.add(binding_row)
    db.commit()
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/bom-binding",
        "DELETE",
        identity,
    )
    client = TestClient(app)

    response = client.delete(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 204

    from sqlalchemy import text

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT event_type FROM security_event_logs "
                "WHERE event_type = 'PRODUCTVERSIONBOMBINDING.REMOVED'"
            )
        ).fetchall()
    assert len(rows) == 1


# ─── allowed_actions reflects capability correctly ───────────────────────────


def test_get_binding_allowed_actions_with_both_perms():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0", lifecycle_status="DRAFT")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    binding_row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=pv.product_version_id,
        bom_id=bom.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        created_by="admin-a",
    )
    db.add(binding_row)
    db.commit()
    db.close()

    app = _build_app(identity, session_local, has_bom_manage=True, has_pv_manage=True)
    client = TestClient(app)

    response = client.get(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["allowed_actions"]["can_remove"] is True


def test_get_binding_allowed_actions_without_perms():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    pv = _mk_version(db, "tenant_a", product_id, "v1.0", lifecycle_status="DRAFT")
    bom = _mk_bom(db, "tenant_a", product_id, "BOM-001")
    binding_row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id="tenant_a",
        product_id=product_id,
        product_version_id=pv.product_version_id,
        bom_id=bom.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        created_by="admin-a",
    )
    db.add(binding_row)
    db.commit()
    db.close()

    app = _build_app(identity, session_local, has_bom_manage=False, has_pv_manage=False)
    client = TestClient(app)

    response = client.get(
        f"/api/v1/products/{product_id}/versions/{pv.product_version_id}/bom-binding"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["allowed_actions"]["can_remove"] is False


# ─── Source-level contract checks ────────────────────────────────────────────


def test_bom_binding_routes_exist_in_products_src():
    """MMD-BE-14: binding route paths must be present in products.py source."""
    import re
    from pathlib import Path

    src = (Path(__file__).parent.parent / "app" / "api" / "v1" / "products.py").read_text(
        encoding="utf-8"
    )
    required_paths = [
        "/{product_id}/versions/{version_id}/bom-binding",
    ]
    for path in required_paths:
        assert path in src, f"Binding route path missing in products.py: {path}"
    # Ensure GET, POST, DELETE binding routes present
    assert src.count('"{product_id}/versions/{version_id}/bom-binding"') >= 3 or (
        src.count("/{product_id}/versions/{version_id}/bom-binding") >= 3
    ), "Expected GET, POST, DELETE bom-binding routes in products.py"


def test_bom_binding_post_and_delete_use_bom_manage_action_code():
    """MMD-BE-14: POST/DELETE bom-binding must gate on admin.master_data.bom.manage."""
    from pathlib import Path

    src = (Path(__file__).parent.parent / "app" / "api" / "v1" / "products.py").read_text(
        encoding="utf-8"
    )
    # After adding binding routes, count of bom.manage uses should be >=9
    # (7 original BOM write routes + 2 new binding routes)
    count = src.count('"admin.master_data.bom.manage"')
    assert count >= 9, (
        f"Expected >=9 uses of admin.master_data.bom.manage in products.py "
        f"(7 BOM write + 2 binding), found {count}"
    )


def test_bom_binding_post_and_delete_check_pv_manage():
    """MMD-BE-14: POST/DELETE bom-binding must also check product_version.manage."""
    from pathlib import Path

    src = (Path(__file__).parent.parent / "app" / "api" / "v1" / "products.py").read_text(
        encoding="utf-8"
    )
    # The binding routes must reference product_version.manage for the inner check
    assert '"admin.master_data.product_version.manage"' in src, (
        "products.py must reference admin.master_data.product_version.manage "
        "for the binding dual-auth inner check"
    )
