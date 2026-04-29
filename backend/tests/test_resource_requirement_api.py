import uuid
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
from app.services.product_service import create_product
from app.services.routing_service import add_routing_operation, create_routing, release_routing, retire_routing
from app.schemas.routing import RoutingCreateRequest, RoutingOperationCreateRequest


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

    # Fail-first expectation: this table/model does not exist before implementation.
    from app.models.resource_requirement import ResourceRequirement

    ResourceRequirement.__table__.create(bind=engine)

    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _mk_routing_with_operation(db, tenant_id: str = "tenant_a") -> tuple[str, str]:
    product = create_product(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        payload=ProductCreateRequest(
            product_code=f"P-{tenant_id}-{uuid.uuid4().hex[:8]}",
            product_name=f"Product {tenant_id}",
            product_type="FINISHED_GOOD",
        ),
    )
    routing = create_routing(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        payload=RoutingCreateRequest(
            product_id=product.product_id,
            routing_code=f"R-{tenant_id}-{uuid.uuid4().hex[:8]}",
            routing_name=f"Routing {tenant_id}",
        ),
    )
    routing = add_routing_operation(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        routing_id=routing.routing_id,
        payload=RoutingOperationCreateRequest(
            operation_code="OP10",
            operation_name="Cut",
            sequence_no=10,
        ),
    )
    return routing.routing_id, routing.operations[0].operation_id


def test_resource_requirement_routes_happy_path_and_lifecycle_guards():
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

    _override_action_dependency(
        app,
        "/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements",
        "POST",
        identity,
    )
    _override_action_dependency(
        app,
        "/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}",
        "PATCH",
        identity,
    )
    _override_action_dependency(
        app,
        "/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}",
        "DELETE",
        identity,
    )

    routing_id, operation_id = _mk_routing_with_operation(db, tenant_id="tenant_a")
    client = TestClient(app)

    created = client.post(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "TORQUE_TOOL",
            "quantity_required": 1,
            "notes": "need tooling",
        },
    )
    assert created.status_code == 200
    req_id = created.json()["requirement_id"]

    listed = client.get(f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    detail = client.get(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req_id}"
    )
    assert detail.status_code == 200

    updated = client.patch(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req_id}",
        json={"quantity_required": 2},
    )
    assert updated.status_code == 200

    removed = client.delete(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req_id}"
    )
    assert removed.status_code == 200

    req2 = client.post(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "TORQUE_TOOL",
            "quantity_required": 1,
        },
    )
    assert req2.status_code == 200
    req2_id = req2.json()["requirement_id"]

    release_routing(db, tenant_id="tenant_a", actor_user_id="admin-a", routing_id=routing_id)

    reject_create_released = client.post(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements",
        json={
            "required_resource_type": "WORK_CENTER",
            "required_capability_code": "WELDING_CELL",
            "quantity_required": 1,
        },
    )
    assert reject_create_released.status_code == 400

    reject_update_released = client.patch(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req2_id}",
        json={"notes": "x"},
    )
    assert reject_update_released.status_code == 400

    reject_delete_released = client.delete(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req2_id}"
    )
    assert reject_delete_released.status_code == 400


def test_cross_tenant_404_input_rejections_and_auth_rejection():
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

    write_path = "/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements"
    write_detail = "/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}"
    action_dep = _override_action_dependency(app, write_path, "POST", identity)
    _override_action_dependency(app, write_detail, "PATCH", identity)
    _override_action_dependency(app, write_detail, "DELETE", identity)

    routing_a, op_a = _mk_routing_with_operation(db, tenant_id="tenant_a")
    routing_b, op_b = _mk_routing_with_operation(db, tenant_id="tenant_b")

    client = TestClient(app)

    created = client.post(
        f"/api/v1/routings/{routing_a}/operations/{op_a}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "TORQUE_TOOL",
            "quantity_required": 1,
        },
    )
    assert created.status_code == 200
    req_id = created.json()["requirement_id"]

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
    hidden = client.get(
        f"/api/v1/routings/{routing_a}/operations/{op_a}/resource-requirements/{req_id}"
    )
    assert hidden.status_code == 404

    app.dependency_overrides[require_authenticated_identity] = lambda: identity

    mismatch = client.post(
        f"/api/v1/routings/{routing_b}/operations/{op_a}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "TORQUE_TOOL",
            "quantity_required": 1,
        },
    )
    assert mismatch.status_code == 404

    duplicate = client.post(
        f"/api/v1/routings/{routing_a}/operations/{op_a}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "TORQUE_TOOL",
            "quantity_required": 1,
        },
    )
    assert duplicate.status_code == 409

    invalid_resource_type = client.post(
        f"/api/v1/routings/{routing_a}/operations/{op_a}/resource-requirements",
        json={
            "required_resource_type": "INVALID",
            "required_capability_code": "X",
            "quantity_required": 1,
        },
    )
    assert invalid_resource_type.status_code == 400

    missing_capability = client.post(
        f"/api/v1/routings/{routing_a}/operations/{op_a}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "",
            "quantity_required": 1,
        },
    )
    assert missing_capability.status_code == 400

    invalid_quantity = client.post(
        f"/api/v1/routings/{routing_a}/operations/{op_a}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "X2",
            "quantity_required": 0,
        },
    )
    assert invalid_quantity.status_code == 400

    app.dependency_overrides[action_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )
    denied = client.post(
        f"/api/v1/routings/{routing_a}/operations/{op_a}/resource-requirements",
        json={
            "required_resource_type": "WORK_CENTER",
            "required_capability_code": "WELDING_CELL",
            "quantity_required": 1,
        },
    )
    assert denied.status_code == 403


def test_retired_routing_rejects_create_update_delete():
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

    write_path = "/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements"
    write_detail = "/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}"
    _override_action_dependency(app, write_path, "POST", identity)
    _override_action_dependency(app, write_detail, "PATCH", identity)
    _override_action_dependency(app, write_detail, "DELETE", identity)

    routing_id, operation_id = _mk_routing_with_operation(db, tenant_id="tenant_a")
    client = TestClient(app)

    created = client.post(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements",
        json={
            "required_resource_type": "TOOLING",
            "required_capability_code": "TORQUE_TOOL",
            "quantity_required": 1,
        },
    )
    assert created.status_code == 200
    req_id = created.json()["requirement_id"]

    retire_routing(db, tenant_id="tenant_a", actor_user_id="admin-a", routing_id=routing_id)

    reject_create = client.post(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements",
        json={
            "required_resource_type": "WORK_CENTER",
            "required_capability_code": "WELDING_CELL",
            "quantity_required": 1,
        },
    )
    assert reject_create.status_code == 400

    reject_update = client.patch(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req_id}",
        json={"notes": "x"},
    )
    assert reject_update.status_code == 400

    reject_delete = client.delete(
        f"/api/v1/routings/{routing_id}/operations/{operation_id}/resource-requirements/{req_id}"
    )
    assert reject_delete.status_code == 400
