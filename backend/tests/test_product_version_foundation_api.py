"""Tests for product version API layer.

Covers read foundations and MMD-BE-11 write API foundation for create/update/release/retire.
"""

import re
import uuid
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI, HTTPException
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

BACKEND_ROOT = Path(__file__).parent.parent
PRODUCTS_SRC = (BACKEND_ROOT / "app" / "api" / "v1" / "products.py").read_text(encoding="utf-8")


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


def _override_action_dependency(app: FastAPI, path: str, method: str, identity: RequestIdentity) -> Any:
    route = cast(
        Any,
        next(
            r for r in app.routes if getattr(r, "path", "") == path and method in (r.methods or set())
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
    is_current: bool = False,
) -> ProductVersion:
    row = ProductVersion(
        product_version_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        version_code=version_code,
        version_name=f"Version {version_code}",
        lifecycle_status=lifecycle_status,
        is_current=is_current,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def test_list_product_versions_returns_200_with_versions():
    identity = _make_identity()
    _, session_local = _make_session()
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


def test_get_product_version_returns_200_with_correct_data():
    identity = _make_identity()
    _, session_local = _make_session()
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
    assert data["lifecycle_status"] == "DRAFT"


def test_create_product_version_requires_manage_action():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    action_dep = _override_action_dependency(app, "/api/v1/products/{product_id}/versions", "POST", identity)
    app.dependency_overrides[action_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions",
        json={"version_code": "v1.0"},
    )
    assert response.status_code == 403


def test_create_product_version_creates_draft():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions", "POST", identity)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions",
        json={
            "version_code": "v1.0",
            "version_name": "Initial",
            "description": "First version",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lifecycle_status"] == "DRAFT"
    assert data["is_current"] is False


def test_create_product_version_rejects_is_current_payload():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions", "POST", identity)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions",
        json={"version_code": "v1.0", "is_current": True},
    )
    assert response.status_code == 422


def test_create_product_version_rejects_duplicate_code_for_same_product():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions", "POST", identity)
    client = TestClient(app)

    first = client.post(f"/api/v1/products/{product_id}/versions", json={"version_code": "dup"})
    assert first.status_code == 200

    second = client.post(f"/api/v1/products/{product_id}/versions", json={"version_code": "dup"})
    assert second.status_code == 409


def test_create_product_version_allows_same_code_for_different_product():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id_a = _mk_product(db, "tenant_a")
    product_id_b = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions", "POST", identity)
    client = TestClient(app)

    a = client.post(f"/api/v1/products/{product_id_a}/versions", json={"version_code": "same"})
    b = client.post(f"/api/v1/products/{product_id_b}/versions", json={"version_code": "same"})
    assert a.status_code == 200
    assert b.status_code == 200


def test_update_product_version_requires_manage_action():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    action_dep = _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}",
        "PATCH",
        identity,
    )
    app.dependency_overrides[action_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"description": "x"},
    )
    assert response.status_code == 403


def test_update_product_version_allows_draft_metadata_update():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"version_name": "Renamed", "description": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["version_name"] == "Renamed"


def test_update_product_version_rejects_released():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1", lifecycle_status="RELEASED")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"description": "nope"},
    )
    assert response.status_code == 400


def test_update_product_version_rejects_retired():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1", lifecycle_status="RETIRED")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"description": "nope"},
    )
    assert response.status_code == 400


def test_update_product_version_rejects_lifecycle_status_patch():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"lifecycle_status": "RELEASED"},
    )
    assert response.status_code == 422


def test_update_product_version_rejects_is_current_patch():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity)
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"is_current": True},
    )
    assert response.status_code == 422


def test_release_product_version_requires_manage_action():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    action_dep = _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    app.dependency_overrides[action_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )
    client = TestClient(app)

    response = client.post(f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release")
    assert response.status_code == 403


def test_release_product_version_changes_draft_to_released():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release")
    assert response.status_code == 200
    assert response.json()["lifecycle_status"] == "RELEASED"


def test_release_product_version_rejects_released_or_retired():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    released = _mk_version(db, "tenant_a", product_id, "rel", lifecycle_status="RELEASED")
    retired = _mk_version(db, "tenant_a", product_id, "ret", lifecycle_status="RETIRED")
    released_id = released.product_version_id
    retired_id = retired.product_version_id
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    r1 = client.post(f"/api/v1/products/{product_id}/versions/{released_id}/release")
    r2 = client.post(f"/api/v1/products/{product_id}/versions/{retired_id}/release")
    assert r1.status_code == 400
    assert r2.status_code == 400


def test_retire_product_version_requires_manage_action():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    action_dep = _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/retire",
        "POST",
        identity,
    )
    app.dependency_overrides[action_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )
    client = TestClient(app)

    response = client.post(f"/api/v1/products/{product_id}/versions/{version.product_version_id}/retire")
    assert response.status_code == 403


def test_retire_product_version_changes_draft_or_released_to_retired():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    draft = _mk_version(db, "tenant_a", product_id, "d", lifecycle_status="DRAFT")
    released = _mk_version(db, "tenant_a", product_id, "r", lifecycle_status="RELEASED")
    draft_id = draft.product_version_id
    released_id = released.product_version_id
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/retire",
        "POST",
        identity,
    )
    client = TestClient(app)

    d = client.post(f"/api/v1/products/{product_id}/versions/{draft_id}/retire")
    r = client.post(f"/api/v1/products/{product_id}/versions/{released_id}/retire")
    assert d.status_code == 200
    assert r.status_code == 200
    assert d.json()["lifecycle_status"] == "RETIRED"
    assert r.json()["lifecycle_status"] == "RETIRED"


def test_retire_product_version_rejects_current_version_if_policy_applies():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    current = _mk_version(db, "tenant_a", product_id, "cur", lifecycle_status="RELEASED", is_current=True)
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/retire",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(f"/api/v1/products/{product_id}/versions/{current.product_version_id}/retire")
    assert response.status_code == 400


def test_write_routes_return_404_for_wrong_product():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id_a = _mk_product(db, "tenant_a")
    product_id_b = _mk_product(db, "tenant_a")
    version_b = _mk_version(db, "tenant_a", product_id_b, "v1")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/retire",
        "POST",
        identity,
    )
    client = TestClient(app)

    patch = client.patch(
        f"/api/v1/products/{product_id_a}/versions/{version_b.product_version_id}",
        json={"description": "x"},
    )
    rel = client.post(f"/api/v1/products/{product_id_a}/versions/{version_b.product_version_id}/release")
    ret = client.post(f"/api/v1/products/{product_id_a}/versions/{version_b.product_version_id}/retire")

    assert patch.status_code == 404
    assert rel.status_code == 404
    assert ret.status_code == 404


def test_no_delete_reactivate_set_current_clone_binding_routes_exist():
    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")

    forbidden_paths = {
        "/api/v1/products/{product_id}/versions/{version_id}": {"DELETE"},
        "/api/v1/products/{product_id}/versions/{version_id}/reactivate": {"POST"},
        "/api/v1/products/{product_id}/versions/{version_id}/set-current": {"POST"},
        "/api/v1/products/{product_id}/versions/{version_id}/clone": {"POST"},
        "/api/v1/products/{product_id}/versions/{version_id}/bind-bom": {"POST"},
        "/api/v1/products/{product_id}/versions/{version_id}/bind-routing": {"POST"},
        "/api/v1/products/{product_id}/versions/{version_id}/bind-resource-requirement": {"POST"},
    }

    existing = {
        (getattr(r, "path", ""), frozenset(getattr(r, "methods", set())))
        for r in app.routes
        if hasattr(r, "path")
    }

    for path, methods in forbidden_paths.items():
        for method in methods:
            assert (path, frozenset({method})) not in existing
            assert not any(p == path and method in m for p, m in existing)


def test_read_endpoints_do_not_require_manage_action():
    version_get_blocks = re.findall(
        r'@router\.get\("/\{product_id\}/versions(?:/\{version_id\})?".*?\)[^@]+?(?=@router\.|$)',
        PRODUCTS_SRC,
        flags=re.DOTALL,
    )
    assert len(version_get_blocks) == 2
    for block in version_get_blocks:
        assert 'require_action("admin.master_data.product_version.manage")' not in block
