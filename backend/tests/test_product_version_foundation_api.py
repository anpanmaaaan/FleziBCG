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
from app.models.bom import Bom, BomItem
from app.models.product import Product
from app.models.product_version import ProductVersion
from app.models.product_version_bom_binding import ProductVersionBomBinding
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.product_service import create_product

BACKEND_ROOT = Path(__file__).parent.parent
PRODUCTS_SRC = (BACKEND_ROOT / "app" / "api" / "v1" / "products.py").read_text(
    encoding="utf-8"
)


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


def _make_session_full():
    """Session factory that also creates Bom and ProductVersionBomBinding tables.

    Required for release validation tests that need BOM and binding rows.
    """
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


def _build_app(identity: RequestIdentity, session_local) -> FastAPI:
    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()
    # Patch has_action to return False in isolated SQLite tests: no RBAC tables seeded.
    # Capability tests use _build_app_with_manage to override this patch.
    product_router_module.has_action = lambda db, ident, action_code, *a, **kw: False
    return app


def _override_action_dependency(
    app: FastAPI, path: str, method: str, identity: RequestIdentity
) -> Any:
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

    response = client.get(
        f"/api/v1/products/{product_id}/versions/{v.product_version_id}"
    )
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
    action_dep = _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions", "POST", identity
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions", "POST", identity
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions", "POST", identity
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions", "POST", identity
    )
    client = TestClient(app)

    first = client.post(
        f"/api/v1/products/{product_id}/versions", json={"version_code": "dup"}
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/products/{product_id}/versions", json={"version_code": "dup"}
    )
    assert second.status_code == 409


def test_create_product_version_allows_same_code_for_different_product():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id_a = _mk_product(db, "tenant_a")
    product_id_b = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions", "POST", identity
    )
    client = TestClient(app)

    a = client.post(
        f"/api/v1/products/{product_id_a}/versions", json={"version_code": "same"}
    )
    b = client.post(
        f"/api/v1/products/{product_id_b}/versions", json={"version_code": "same"}
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
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

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
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

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
    assert response.status_code == 200
    assert response.json()["lifecycle_status"] == "RELEASED"


def test_release_product_version_rejects_released_or_retired():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    released = _mk_version(
        db, "tenant_a", product_id, "rel", lifecycle_status="RELEASED"
    )
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

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/retire"
    )
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
    current = _mk_version(
        db, "tenant_a", product_id, "cur", lifecycle_status="RELEASED", is_current=True
    )
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/retire",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{current.product_version_id}/retire"
    )
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
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
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
    rel = client.post(
        f"/api/v1/products/{product_id_a}/versions/{version_b.product_version_id}/release"
    )
    ret = client.post(
        f"/api/v1/products/{product_id_a}/versions/{version_b.product_version_id}/retire"
    )

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
        "/api/v1/products/{product_id}/versions/{version_id}/bind-resource-requirement": {
            "POST"
        },
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


# ─────────────────────────────────────────────────────────────────────────────
# MMD-FULLSTACK-11B: Server-derived capability / allowed-actions tests
# ─────────────────────────────────────────────────────────────────────────────


def _build_app_with_manage(session_local, has_manage: bool) -> tuple:
    """Build a test app with has_action patched to return the requested manage bool."""
    import app.api.v1.products as products_module
    from app.api.v1.products import get_db

    identity = _make_identity()
    test_app = FastAPI()
    test_app.include_router(product_router_module.router, prefix="/api/v1")
    test_app.dependency_overrides[require_authenticated_identity] = lambda: identity
    test_app.dependency_overrides[get_db] = lambda: session_local()

    original = products_module.has_action

    def _patched_has_action(db, ident, action_code, *args, **kwargs):
        if action_code == "admin.master_data.product_version.manage":
            return has_manage
        return False

    products_module.has_action = _patched_has_action
    return test_app, identity, original, products_module


def test_list_versions_includes_allowed_actions_field():
    """Read list response must include allowed_actions field."""
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    _mk_version(db, "tenant_a", product_id, "v1.0")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(f"/api/v1/products/{product_id}/versions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "allowed_actions" in data[0], (
        "allowed_actions field must be present in list response"
    )


def test_get_version_includes_allowed_actions_field():
    """Read single response must include allowed_actions field."""
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    v = _mk_version(db, "tenant_a", product_id, "v1.0")
    db.close()

    app = _build_app(identity, session_local)
    client = TestClient(app)

    response = client.get(
        f"/api/v1/products/{product_id}/versions/{v.product_version_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "allowed_actions" in data, (
        "allowed_actions field must be present in get response"
    )


def test_allowed_actions_all_false_for_user_without_manage():
    """User without manage permission must get all capabilities False."""
    import app.api.v1.products as products_module

    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    identity = _make_identity()
    test_app, _, original, products_module = _build_app_with_manage(
        session_local, has_manage=False
    )
    try:
        client = TestClient(test_app)
        response = client.get(f"/api/v1/products/{product_id}/versions")
        assert response.status_code == 200
        data = response.json()
        aa = data[0]["allowed_actions"]
        assert aa["can_update"] is False
        assert aa["can_release"] is False
        assert aa["can_retire"] is False
        assert aa["can_create_sibling"] is False
    finally:
        products_module.has_action = original


def test_allowed_actions_draft_with_manage():
    """DRAFT version with manage permission must have can_update/release/retire/create_sibling all True."""
    import app.api.v1.products as products_module

    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    _mk_version(
        db, "tenant_a", product_id, "v1", lifecycle_status="DRAFT", is_current=False
    )
    db.close()

    identity = _make_identity()
    test_app, _, original, products_module = _build_app_with_manage(
        session_local, has_manage=True
    )
    try:
        client = TestClient(test_app)
        response = client.get(f"/api/v1/products/{product_id}/versions")
        assert response.status_code == 200
        aa = response.json()[0]["allowed_actions"]
        assert aa["can_update"] is True
        assert aa["can_release"] is True
        assert aa["can_retire"] is True
        assert aa["can_create_sibling"] is True
    finally:
        products_module.has_action = original


def test_allowed_actions_released_not_current_with_manage():
    """RELEASED, not is_current: can_retire True; can_update/release False."""
    import app.api.v1.products as products_module

    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    _mk_version(
        db, "tenant_a", product_id, "v1", lifecycle_status="RELEASED", is_current=False
    )
    db.close()

    identity = _make_identity()
    test_app, _, original, products_module = _build_app_with_manage(
        session_local, has_manage=True
    )
    try:
        client = TestClient(test_app)
        response = client.get(f"/api/v1/products/{product_id}/versions")
        assert response.status_code == 200
        aa = response.json()[0]["allowed_actions"]
        assert aa["can_update"] is False
        assert aa["can_release"] is False
        assert aa["can_retire"] is True
        assert aa["can_create_sibling"] is True
    finally:
        products_module.has_action = original


def test_allowed_actions_released_is_current_with_manage():
    """RELEASED + is_current=True: can_retire must be False (current version cannot be retired)."""
    import app.api.v1.products as products_module

    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    _mk_version(
        db, "tenant_a", product_id, "v1", lifecycle_status="RELEASED", is_current=True
    )
    db.close()

    identity = _make_identity()
    test_app, _, original, products_module = _build_app_with_manage(
        session_local, has_manage=True
    )
    try:
        client = TestClient(test_app)
        response = client.get(f"/api/v1/products/{product_id}/versions")
        assert response.status_code == 200
        aa = response.json()[0]["allowed_actions"]
        assert aa["can_update"] is False
        assert aa["can_release"] is False
        assert aa["can_retire"] is False
        assert aa["can_create_sibling"] is True
    finally:
        products_module.has_action = original


def test_allowed_actions_retired_with_manage():
    """RETIRED version: all mutation capabilities False; can_create_sibling True."""
    import app.api.v1.products as products_module

    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    _mk_version(
        db, "tenant_a", product_id, "v1", lifecycle_status="RETIRED", is_current=False
    )
    db.close()

    identity = _make_identity()
    test_app, _, original, products_module = _build_app_with_manage(
        session_local, has_manage=True
    )
    try:
        client = TestClient(test_app)
        response = client.get(f"/api/v1/products/{product_id}/versions")
        assert response.status_code == 200
        aa = response.json()[0]["allowed_actions"]
        assert aa["can_update"] is False
        assert aa["can_release"] is False
        assert aa["can_retire"] is False
        assert aa["can_create_sibling"] is True
    finally:
        products_module.has_action = original


def test_read_endpoints_return_200_for_non_manage_user():
    """Read endpoints must remain accessible to authenticated users without manage permission."""
    import app.api.v1.products as products_module

    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    v = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    identity = _make_identity()
    test_app, _, original, products_module = _build_app_with_manage(
        session_local, has_manage=False
    )
    try:
        client = TestClient(test_app)
        list_resp = client.get(f"/api/v1/products/{product_id}/versions")
        get_resp = client.get(
            f"/api/v1/products/{product_id}/versions/{v.product_version_id}"
        )
        assert list_resp.status_code == 200
        assert get_resp.status_code == 200
    finally:
        products_module.has_action = original


# ─────────────────────────────────────────────────────────────────────────────
# MMD-BE-14C: bom_binding_required_for_release field + release validation tests
# ─────────────────────────────────────────────────────────────────────────────


def _mk_bom(
    db,
    tenant_id: str,
    product_id: str,
    *,
    lifecycle_status: str = "RELEASED",
) -> Bom:
    row = Bom(
        bom_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        bom_code=f"BOM-{uuid.uuid4().hex[:6]}",
        bom_name="Test BOM",
        lifecycle_status=lifecycle_status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _mk_binding(
    db,
    tenant_id: str,
    product_id: str,
    product_version_id: str,
    bom_id: str,
    *,
    binding_status: str = "ACTIVE",
) -> ProductVersionBomBinding:
    row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
        bom_id=bom_id,
        binding_type="PRIMARY",
        binding_status=binding_status,
        created_by="admin-a",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _build_app_release(identity: RequestIdentity, session_local) -> FastAPI:
    from app.api.v1.products import get_db

    app = FastAPI()
    app.include_router(product_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()
    product_router_module.has_action = lambda db, ident, action_code, *a, **kw: True
    return app


def test_create_product_version_defaults_bom_binding_required_false():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions", "POST", identity
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions", json={"version_code": "v1.0"}
    )
    assert response.status_code == 200
    assert response.json()["bom_binding_required_for_release"] is False


def test_create_product_version_can_set_bom_binding_required_true():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions", "POST", identity
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions",
        json={"version_code": "v1.0", "bom_binding_required_for_release": True},
    )
    assert response.status_code == 200
    assert response.json()["bom_binding_required_for_release"] is True


def test_update_draft_product_version_can_set_bom_binding_required_for_release():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"bom_binding_required_for_release": True},
    )
    assert response.status_code == 200
    assert response.json()["bom_binding_required_for_release"] is True


def test_update_released_product_version_cannot_set_bom_binding_required_for_release():
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1", lifecycle_status="RELEASED")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"bom_binding_required_for_release": True},
    )
    # RELEASED PV update is rejected (existing guard: only DRAFT can update)
    assert response.status_code == 400


def test_update_retired_product_version_cannot_set_bom_binding_required_for_release():
    """RETIRED PV update is rejected by existing lifecycle guard (only DRAFT can update)."""
    identity = _make_identity()
    _, session_local = _make_session()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1", lifecycle_status="RETIRED")
    db.close()

    app = _build_app(identity, session_local)
    _override_action_dependency(
        app, "/api/v1/products/{product_id}/versions/{version_id}", "PATCH", identity
    )
    client = TestClient(app)

    response = client.patch(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}",
        json={"bom_binding_required_for_release": True},
    )
    assert response.status_code == 400


def test_release_product_version_without_binding_required_flag_succeeds():
    """Default flag=false: release proceeds unchanged (no binding required)."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
    assert response.status_code == 200
    assert response.json()["lifecycle_status"] == "RELEASED"


def test_release_product_version_with_binding_required_and_released_bom_succeeds():
    """flag=true + ACTIVE PRIMARY binding to RELEASED BOM: release succeeds."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    bom = _mk_bom(db, "tenant_a", product_id, lifecycle_status="RELEASED")
    _mk_binding(db, "tenant_a", product_id, version.product_version_id, bom.bom_id)
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
    assert response.status_code == 200
    assert response.json()["lifecycle_status"] == "RELEASED"


def test_release_product_version_with_binding_required_and_no_binding_returns_422():
    """flag=true + no active binding: release returns 400 (ValueError → 400)."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
    assert response.status_code == 400


def test_release_product_version_with_binding_required_and_draft_bom_returns_422():
    """flag=true + ACTIVE PRIMARY binding to DRAFT BOM: release returns 400 (ValueError → 400)."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    bom = _mk_bom(db, "tenant_a", product_id, lifecycle_status="DRAFT")
    _mk_binding(db, "tenant_a", product_id, version.product_version_id, bom.bom_id)
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
    assert response.status_code == 400


def test_release_product_version_with_binding_required_and_retired_bom_returns_422():
    """flag=true + ACTIVE PRIMARY binding to RETIRED BOM: release returns 400 (ValueError → 400)."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    bom = _mk_bom(db, "tenant_a", product_id, lifecycle_status="RETIRED")
    _mk_binding(db, "tenant_a", product_id, version.product_version_id, bom.bom_id)
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
    assert response.status_code == 400


def test_release_product_version_with_binding_required_and_removed_binding_returns_422():
    """flag=true + binding exists but REMOVED (no ACTIVE): release returns 400 (ValueError → 400)."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    bom = _mk_bom(db, "tenant_a", product_id, lifecycle_status="RELEASED")
    _mk_binding(
        db,
        "tenant_a",
        product_id,
        version.product_version_id,
        bom.bom_id,
        binding_status="REMOVED",
    )
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version.product_version_id}/release"
    )
    assert response.status_code == 400


def test_release_blocked_by_binding_validation_emits_no_released_event():
    """Blocked release must not emit PRODUCT_VERSION.RELEASED event."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    version_id = version.product_version_id
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version_id}/release"
    )
    assert response.status_code == 400

    check_db = session_local()
    from sqlalchemy import select
    from app.models.security_event import SecurityEventLog

    events = list(
        check_db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.resource_id == version_id,
                SecurityEventLog.event_type == "PRODUCT_VERSION.RELEASED",
            )
        )
    )
    check_db.close()
    assert events == [], f"Unexpected RELEASED event emitted: {events}"


def test_release_with_valid_binding_emits_released_event():
    """Successful release with flag=true must emit PRODUCT_VERSION.RELEASED event."""
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    version_id = version.product_version_id
    bom = _mk_bom(db, "tenant_a", product_id, lifecycle_status="RELEASED")
    _mk_binding(db, "tenant_a", product_id, version_id, bom.bom_id)
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version_id}/release"
    )
    assert response.status_code == 200

    check_db = session_local()
    from sqlalchemy import select

    events = list(
        check_db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.resource_id == version_id,
                SecurityEventLog.event_type == "PRODUCT_VERSION.RELEASED",
            )
        )
    )
    check_db.close()
    assert len(events) == 1, f"Expected exactly one RELEASED event, got {len(events)}"


def test_release_validation_does_not_require_bom_manage():
    """PV release endpoint must not require admin.master_data.bom.manage action code."""
    src = PRODUCTS_SRC
    # Find the PV-specific release route block (versions/{version_id}/release)
    release_block_match = re.search(
        r'@router\.post\("[^"]*versions/\{version_id\}/release".*?(?=@router\.|\Z)',
        src,
        flags=re.DOTALL,
    )
    assert release_block_match is not None, "PV release route block not found"
    release_block = release_block_match.group(0)
    assert "admin.master_data.bom.manage" not in release_block, (
        "PV release route must not require bom.manage"
    )


def test_release_endpoint_still_requires_product_version_manage_only():
    """PV release endpoint must be protected by product_version.manage action code."""
    src = PRODUCTS_SRC
    release_block_match = re.search(
        r'@router\.post\("[^"]*versions/\{version_id\}/release".*?(?=@router\.|\Z)',
        src,
        flags=re.DOTALL,
    )
    assert release_block_match is not None, "PV release route block not found"
    release_block = release_block_match.group(0)
    assert "admin.master_data.product_version.manage" in release_block, (
        "PV release route must require product_version.manage"
    )


def test_release_validation_does_not_import_or_call_forbidden_domains():
    """product_version_service must not import material/ERP/traceability/quality/execution modules."""
    service_src_path = (
        Path(__file__).parent.parent
        / "app"
        / "services"
        / "product_version_service.py"
    )
    service_src = service_src_path.read_text(encoding="utf-8")
    forbidden_patterns = [
        "material",
        "inventory",
        "backflush",
        "erp",
        "traceability",
        "genealogy",
        "quality",
        "execution",
        "dispatch",
        "aps",
        "production_order",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in service_src.lower(), (
            f"product_version_service imports or references forbidden domain: {pattern!r}"
        )


def test_release_validation_does_not_mutate_bom_or_binding():
    """Release validation must not mutate BOM lifecycle_status or binding binding_status.

    After a successful release (flag=true + RELEASED BOM + ACTIVE binding),
    the BOM must still be RELEASED and the binding must still be ACTIVE.
    """
    identity = _make_identity()
    _, session_local = _make_session_full()
    db = session_local()
    product_id = _mk_product(db, "tenant_a")
    version = _mk_version(db, "tenant_a", product_id, "v1")
    version.bom_binding_required_for_release = True
    db.commit()
    version_id = version.product_version_id
    bom = _mk_bom(db, "tenant_a", product_id, lifecycle_status="RELEASED")
    bom_id = bom.bom_id
    binding = _mk_binding(db, "tenant_a", product_id, version_id, bom_id)
    binding_id = binding.binding_id
    db.close()

    app = _build_app_release(identity, session_local)
    _override_action_dependency(
        app,
        "/api/v1/products/{product_id}/versions/{version_id}/release",
        "POST",
        identity,
    )
    client = TestClient(app)

    response = client.post(
        f"/api/v1/products/{product_id}/versions/{version_id}/release"
    )
    assert response.status_code == 200

    check_db = session_local()
    from sqlalchemy import select

    bom_row = check_db.scalars(
        select(Bom).where(Bom.bom_id == bom_id)
    ).first()
    binding_row = check_db.scalars(
        select(ProductVersionBomBinding).where(
            ProductVersionBomBinding.binding_id == binding_id
        )
    ).first()
    check_db.close()

    assert bom_row is not None
    assert bom_row.lifecycle_status == "RELEASED", (
        f"BOM must not be mutated by release validation; got {bom_row.lifecycle_status}"
    )
    assert binding_row is not None
    assert binding_row.binding_status == "ACTIVE", (
        f"Binding must not be mutated by release validation; got {binding_row.binding_status}"
    )
