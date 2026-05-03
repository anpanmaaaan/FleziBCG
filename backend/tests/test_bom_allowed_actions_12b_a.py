"""BOM Allowed Actions tests (MMD-FULLSTACK-12B-A verification patch)."""

from __future__ import annotations

import uuid
from typing import cast

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


def _build_app(identity: RequestIdentity, session_local, has_manage: bool = False) -> FastAPI:
    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()
    # Patch has_action for permission checks
    product_router_module.has_action = lambda db, ident, action_code, *a, **kw: has_manage
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


def test_get_boms_includes_allowed_actions():
    """GET /products/{product_id}/boms includes allowed_actions in each BOM (MMD-FULLSTACK-12B-A)."""
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="AA-001")
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms")
    assert response.status_code == 200
    boms = response.json()
    assert len(boms) == 1
    assert "allowed_actions" in boms[0], "Missing allowed_actions in BOM list"
    assert "can_update" in boms[0]["allowed_actions"]
    assert "can_release" in boms[0]["allowed_actions"]
    assert "can_retire" in boms[0]["allowed_actions"]


def test_get_bom_detail_includes_allowed_actions():
    """GET /products/{product_id}/boms/{bom_id} includes allowed_actions (MMD-FULLSTACK-12B-A)."""
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="BD-001")
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms/{bom.bom_id}")
    assert response.status_code == 200
    bom_detail = response.json()
    assert "allowed_actions" in bom_detail, "Missing allowed_actions in BOM detail"
    assert "can_update" in bom_detail["allowed_actions"]
    assert "can_add_item" in bom_detail["allowed_actions"]


def test_draft_bom_allowed_actions_all_true_with_manage():
    """DRAFT BOM with admin.master_data.bom.manage: all mutations allowed (MMD-FULLSTACK-12B-A)."""
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="DRAFT-001", lifecycle_status="DRAFT")
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms/{bom.bom_id}")
    assert response.status_code == 200
    actions = response.json()["allowed_actions"]
    assert actions["can_update"] is True, "DRAFT BOM should allow update"
    assert actions["can_release"] is True, "DRAFT BOM should allow release"
    assert actions["can_retire"] is True, "DRAFT BOM should allow retire"
    assert actions["can_add_item"] is True, "DRAFT BOM should allow add_item"
    assert actions["can_update_item"] is True, "DRAFT BOM should allow update_item"
    assert actions["can_remove_item"] is True, "DRAFT BOM should allow remove_item"
    assert actions["can_create_sibling"] is True, "DRAFT BOM should allow create_sibling"


def test_released_bom_allowed_actions_retire_only_with_manage():
    """RELEASED BOM with admin.master_data.bom.manage: only retire and create_sibling allowed (MMD-FULLSTACK-12B-A)."""
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="REL-001", lifecycle_status="RELEASED")
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms/{bom.bom_id}")
    assert response.status_code == 200
    actions = response.json()["allowed_actions"]
    assert actions["can_update"] is False, "RELEASED BOM should not allow update"
    assert actions["can_release"] is False, "RELEASED BOM should not allow release"
    assert actions["can_retire"] is True, "RELEASED BOM should allow retire"
    assert actions["can_add_item"] is False, "RELEASED BOM should not allow add_item"
    assert actions["can_update_item"] is False, "RELEASED BOM should not allow update_item"
    assert actions["can_remove_item"] is False, "RELEASED BOM should not allow remove_item"
    assert actions["can_create_sibling"] is True, "RELEASED BOM should allow create_sibling"


def test_retired_bom_allowed_actions_sibling_only_with_manage():
    """RETIRED BOM with admin.master_data.bom.manage: only create_sibling allowed (MMD-FULLSTACK-12B-A)."""
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code="RET-001", lifecycle_status="RETIRED")
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/boms/{bom.bom_id}")
    assert response.status_code == 200
    actions = response.json()["allowed_actions"]
    assert actions["can_update"] is False, "RETIRED BOM should not allow update"
    assert actions["can_release"] is False, "RETIRED BOM should not allow release"
    assert actions["can_retire"] is False, "RETIRED BOM should not allow retire"
    assert actions["can_add_item"] is False, "RETIRED BOM should not allow add_item"
    assert actions["can_update_item"] is False, "RETIRED BOM should not allow update_item"
    assert actions["can_remove_item"] is False, "RETIRED BOM should not allow remove_item"
    assert actions["can_create_sibling"] is True, "RETIRED BOM should allow create_sibling"


def test_bom_allowed_actions_all_false_without_manage():
    """BOM with NO admin.master_data.bom.manage: all actions false regardless of lifecycle_status (MMD-FULLSTACK-12B-A)."""
    identity = _make_identity()
    session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db)
    # Test with DRAFT, RELEASED, RETIRED
    for lifecycle in ["DRAFT", "RELEASED", "RETIRED"]:
        bom = _mk_bom(db, tenant_id="tenant_a", product_id=product_id, bom_code=f"NOAUTH-{lifecycle}", lifecycle_status=lifecycle)
        db.close()

        app = _build_app(identity, session_local, has_manage=False)  # NO manage permission
        client = TestClient(app)

        response = client.get(f"/api/v1/products/{product_id}/boms/{bom.bom_id}")
        assert response.status_code == 200
        actions = response.json()["allowed_actions"]
        assert actions["can_update"] is False, f"{lifecycle} BOM without manage: can_update should be False"
        assert actions["can_release"] is False, f"{lifecycle} BOM without manage: can_release should be False"
        assert actions["can_retire"] is False, f"{lifecycle} BOM without manage: can_retire should be False"
        assert actions["can_add_item"] is False, f"{lifecycle} BOM without manage: can_add_item should be False"
        assert actions["can_update_item"] is False, f"{lifecycle} BOM without manage: can_update_item should be False"
        assert actions["can_remove_item"] is False, f"{lifecycle} BOM without manage: can_remove_item should be False"
        assert actions["can_create_sibling"] is False, f"{lifecycle} BOM without manage: can_create_sibling should be False"

        db = session_local()
