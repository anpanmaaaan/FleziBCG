from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.routings as routing_router_module
from app.models.product import Product
from app.models.routing import Routing, RoutingOperation
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.product_service import create_product, retire_product


def _build_app(identity: RequestIdentity) -> FastAPI:
    app = FastAPI()
    app.include_router(routing_router_module.router, prefix="/api/v1")
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
    Routing.__table__.create(bind=engine)
    RoutingOperation.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _mk_product(db, tenant_id: str) -> str:
    row = create_product(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        payload=ProductCreateRequest(
            product_code=f"P-{tenant_id}",
            product_name=f"Product {tenant_id}",
            product_type="FINISHED_GOOD",
        ),
    )
    return row.product_id


def test_routing_routes_happy_path_and_lifecycle():
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
    app.dependency_overrides[routing_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/routings", "POST", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}", "PATCH", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/operations", "POST", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/operations/{operation_id}", "PATCH", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/operations/{operation_id}", "DELETE", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/release", "POST", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/retire", "POST", identity)

    product_id = _mk_product(db, tenant_id="tenant_a")

    client = TestClient(app)

    created = client.post(
        "/api/v1/routings",
        json={
            "product_id": product_id,
            "routing_code": "API-R-001",
            "routing_name": "API Routing",
        },
    )
    assert created.status_code == 200
    routing_id = created.json()["routing_id"]

    listed = client.get("/api/v1/routings")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    add_op = client.post(
        f"/api/v1/routings/{routing_id}/operations",
        json={
            "operation_code": "OP10",
            "operation_name": "Cut",
            "sequence_no": 10,
        },
    )
    assert add_op.status_code == 200
    operation_id = add_op.json()["operations"][0]["operation_id"]

    update_op = client.patch(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}",
        json={"operation_name": "Cut updated"},
    )
    assert update_op.status_code == 200

    release = client.post(f"/api/v1/routings/{routing_id}/release")
    assert release.status_code == 200
    assert release.json()["lifecycle_status"] == "RELEASED"

    structural_reject = client.patch(
        f"/api/v1/routings/{routing_id}",
        json={"routing_code": "API-R-002"},
    )
    assert structural_reject.status_code == 400

    op_reject = client.post(
        f"/api/v1/routings/{routing_id}/operations",
        json={
            "operation_code": "OP20",
            "operation_name": "Weld",
            "sequence_no": 20,
        },
    )
    assert op_reject.status_code == 400

    retire = client.post(f"/api/v1/routings/{routing_id}/retire")
    assert retire.status_code == 200
    assert retire.json()["lifecycle_status"] == "RETIRED"

    retired_reject = client.patch(
        f"/api/v1/routings/{routing_id}",
        json={"routing_name": "Nope"},
    )
    assert retired_reject.status_code == 400


def test_cross_tenant_detail_404_duplicate_409_and_retired_product_link_reject():
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
    app.dependency_overrides[routing_router_module.get_db] = lambda: db

    _override_action_dependency(app, "/api/v1/routings", "POST", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}", "PATCH", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/operations", "POST", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/operations/{operation_id}", "PATCH", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/operations/{operation_id}", "DELETE", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/release", "POST", identity)
    _override_action_dependency(app, "/api/v1/routings/{routing_id}/retire", "POST", identity)

    product_a = _mk_product(db, tenant_id="tenant_a")
    product_b = _mk_product(db, tenant_id="tenant_b")

    created_other_tenant = TestClient(app).post(
        "/api/v1/routings",
        json={
            "product_id": product_a,
            "routing_code": "X-TEN-A",
            "routing_name": "A",
        },
    )
    assert created_other_tenant.status_code == 200

    other_tenant_routing = create_product(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        payload=ProductCreateRequest(
            product_code="P2-tenant_b",
            product_name="Product tenant_b 2",
            product_type="FINISHED_GOOD",
        ),
    )
    created_b = TestClient(app).post(
        "/api/v1/routings",
        json={
            "product_id": other_tenant_routing.product_id,
            "routing_code": "X-TEN-B",
            "routing_name": "B",
        },
    )
    assert created_b.status_code == 400

    client = TestClient(app)

    first = client.post(
        "/api/v1/routings",
        json={
            "product_id": product_a,
            "routing_code": "DUP-R-001",
            "routing_name": "First",
        },
    )
    assert first.status_code == 200
    routing_id = first.json()["routing_id"]

    duplicate = client.post(
        "/api/v1/routings",
        json={
            "product_id": product_a,
            "routing_code": "DUP-R-001",
            "routing_name": "Duplicate",
        },
    )
    assert duplicate.status_code == 409

    hidden = client.get(f"/api/v1/routings/{routing_id}")
    assert hidden.status_code == 200

    foreign_identity = RequestIdentity(
        user_id="admin-b",
        username="admin-b",
        email=None,
        tenant_id="tenant_b",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-admin-b",
    )
    app.dependency_overrides[require_authenticated_identity] = lambda: foreign_identity
    hidden_cross_tenant = client.get(f"/api/v1/routings/{routing_id}")
    assert hidden_cross_tenant.status_code == 404

    app.dependency_overrides[require_authenticated_identity] = lambda: identity

    retire_product(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        product_id=product_b,
    )

    retired_link = client.post(
        "/api/v1/routings",
        json={
            "product_id": product_b,
            "routing_code": "RET-LINK-1",
            "routing_name": "Should fail",
        },
    )
    assert retired_link.status_code == 400


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
    app.dependency_overrides[routing_router_module.get_db] = lambda: db

    product_id = _mk_product(db, tenant_id="tenant_a")

    action_dependency = _override_action_dependency(app, "/api/v1/routings", "POST", identity)
    app.dependency_overrides[action_dependency] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    denied = client.post(
        "/api/v1/routings",
        json={
            "product_id": product_id,
            "routing_code": "DENY-R-001",
            "routing_name": "Denied",
        },
    )
    assert denied.status_code == 403
