"""Tests for routing operation extended fields (MMD-BE-01).

Per routing-foundation-contract.md v1.2, RoutingOperation has 3 nullable
extended fields:
  - setup_time
  - run_time_per_unit
  - work_center_code

This slice (MMD-BE-01) is read-only:
  - Schema migration adds the 3 columns (Alembic 0002).
  - Model gains 3 attributes.
  - RoutingOperationItem response schema exposes the 3 fields.
  - Service _to_operation_item projection includes the 3 fields.

Out of scope (verified by negative tests below):
  - Create/Update request schemas do NOT accept the 3 fields. Mutation must
    happen via direct SQL or future MMD-BE-01b slice.
  - required_skill / required_skill_level / qc_checkpoint_count are NOT on
    RoutingOperation (deferred / rejected per contract Section 10).
"""
from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.routings as routing_router_module
from app.models.product import Product
from app.models.routing import Routing, RoutingOperation
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.schemas.routing import (
    RoutingCreateRequest,
    RoutingOperationCreateRequest,
    RoutingOperationItem,
    RoutingOperationUpdateRequest,
)
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.product_service import create_product
from app.services.routing_service import (
    add_routing_operation,
    create_routing,
)


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


def _mk_product(db, tenant_id: str = "tenant_a") -> str:
    row = create_product(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        payload=ProductCreateRequest(
            product_code="FG-EXT",
            product_name="Extended fields product",
            product_type="FINISHED_GOOD",
        ),
    )
    return row.product_id


def _mk_routing_with_operation(db, tenant_id: str = "tenant_a") -> tuple[str, str]:
    product_id = _mk_product(db, tenant_id=tenant_id)
    routing = create_routing(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        payload=RoutingCreateRequest(
            product_id=product_id,
            routing_code="R-EXT",
            routing_name="Routing with extended ops",
        ),
    )
    add_routing_operation(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        routing_id=routing.routing_id,
        payload=RoutingOperationCreateRequest(
            operation_code="OP-10",
            operation_name="Op 10",
            sequence_no=10,
            standard_cycle_time=120.0,
            required_resource_type="WORK_CENTER",
        ),
    )
    operation_id = db.scalar(
        select(RoutingOperation.operation_id).where(
            RoutingOperation.routing_id == routing.routing_id
        )
    )
    return routing.routing_id, operation_id


# ---------- Model tests (T5-T7 from evidence pack) ----------


def test_model_persists_with_extended_fields_populated():
    """T5: RoutingOperation persists when extended fields populated."""
    db = _make_session()
    routing_id, operation_id = _mk_routing_with_operation(db)

    op_row = db.scalar(
        select(RoutingOperation).where(RoutingOperation.operation_id == operation_id)
    )
    op_row.setup_time = 30.5
    op_row.run_time_per_unit = 12.0
    op_row.work_center_code = "WC-LATHE-01"
    db.commit()
    db.refresh(op_row)

    assert op_row.setup_time == 30.5
    assert op_row.run_time_per_unit == 12.0
    assert op_row.work_center_code == "WC-LATHE-01"


def test_model_persists_with_extended_fields_null():
    """T6: RoutingOperation persists when extended fields NULL (backward compat)."""
    db = _make_session()
    _, operation_id = _mk_routing_with_operation(db)

    op_row = db.scalar(
        select(RoutingOperation).where(RoutingOperation.operation_id == operation_id)
    )

    # Operation was created via add_routing_operation without populating extended
    # fields; they should default to NULL per schema.
    assert op_row.setup_time is None
    assert op_row.run_time_per_unit is None
    assert op_row.work_center_code is None


# ---------- Schema projection tests ----------


def test_routing_operation_item_includes_extended_fields_when_populated():
    """RoutingOperationItem serializes extended fields when DB row has them."""
    db = _make_session()
    _, operation_id = _mk_routing_with_operation(db)

    op_row = db.scalar(
        select(RoutingOperation).where(RoutingOperation.operation_id == operation_id)
    )
    op_row.setup_time = 45.0
    op_row.run_time_per_unit = 8.5
    op_row.work_center_code = "WC-CNC-02"
    db.commit()
    db.refresh(op_row)

    from app.services.routing_service import _to_operation_item

    item = _to_operation_item(op_row)
    assert item.setup_time == 45.0
    assert item.run_time_per_unit == 8.5
    assert item.work_center_code == "WC-CNC-02"


def test_routing_operation_item_includes_extended_fields_as_null_when_empty():
    """RoutingOperationItem serializes NULL extended fields as None."""
    db = _make_session()
    _, operation_id = _mk_routing_with_operation(db)

    op_row = db.scalar(
        select(RoutingOperation).where(RoutingOperation.operation_id == operation_id)
    )

    from app.services.routing_service import _to_operation_item

    item = _to_operation_item(op_row)
    assert item.setup_time is None
    assert item.run_time_per_unit is None
    assert item.work_center_code is None


# ---------- API response tests (T8-T10 from evidence pack) ----------


def test_get_routing_response_includes_extended_fields():
    """T8/T9: GET /v1/routings/{id} response includes 3 extended fields."""
    db = _make_session()
    routing_id, operation_id = _mk_routing_with_operation(db)

    # Populate extended fields directly via DB
    op_row = db.scalar(
        select(RoutingOperation).where(RoutingOperation.operation_id == operation_id)
    )
    op_row.setup_time = 60.0
    op_row.run_time_per_unit = 15.0
    op_row.work_center_code = "WC-PRESS-A"
    db.commit()

    identity = RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id="tenant_a",
        role_code="ADM",
        is_authenticated=True,
        session_id="s-a",
    )
    app = FastAPI()
    app.include_router(routing_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[routing_router_module.get_db] = lambda: db

    client = TestClient(app)
    response = client.get(f"/api/v1/routings/{routing_id}")
    assert response.status_code == 200
    body = response.json()
    operations = body["operations"]
    assert len(operations) == 1
    op = operations[0]
    assert op["setup_time"] == 60.0
    assert op["run_time_per_unit"] == 15.0
    assert op["work_center_code"] == "WC-PRESS-A"


def test_get_routing_response_serializes_null_extended_fields():
    """T9: GET response includes 3 fields as null when DB row has NULL."""
    db = _make_session()
    routing_id, _ = _mk_routing_with_operation(db)

    identity = RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id="tenant_a",
        role_code="ADM",
        is_authenticated=True,
        session_id="s-a",
    )
    app = FastAPI()
    app.include_router(routing_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[routing_router_module.get_db] = lambda: db

    client = TestClient(app)
    response = client.get(f"/api/v1/routings/{routing_id}")
    assert response.status_code == 200
    op = response.json()["operations"][0]
    assert op["setup_time"] is None
    assert op["run_time_per_unit"] is None
    assert op["work_center_code"] is None


# ---------- Negative tests (T17 from evidence pack) ----------


def test_create_request_schema_does_not_accept_extended_fields():
    """T17 part 1: RoutingOperationCreateRequest does not include 3 extended
    fields — they remain out of scope for MMD-BE-01 write path.
    """
    fields = RoutingOperationCreateRequest.model_fields.keys()
    assert "setup_time" not in fields
    assert "run_time_per_unit" not in fields
    assert "work_center_code" not in fields
    # Sanity: original fields still present
    assert "operation_code" in fields
    assert "sequence_no" in fields


def test_update_request_schema_does_not_accept_extended_fields():
    """T17 part 2: RoutingOperationUpdateRequest does not include 3 extended
    fields — same out-of-scope guarantee.
    """
    fields = RoutingOperationUpdateRequest.model_fields.keys()
    assert "setup_time" not in fields
    assert "run_time_per_unit" not in fields
    assert "work_center_code" not in fields


def test_request_schema_rejects_deferred_and_rejected_fields():
    """Sanity: Pydantic does not silently accept the deferred/rejected fields
    (required_skill, required_skill_level, qc_checkpoint_count). They are not
    declared on any routing schema.
    """
    item_fields = RoutingOperationItem.model_fields.keys()
    create_fields = RoutingOperationCreateRequest.model_fields.keys()
    update_fields = RoutingOperationUpdateRequest.model_fields.keys()

    for forbidden in ("required_skill", "required_skill_level", "qc_checkpoint_count"):
        assert forbidden not in item_fields, f"Item should not have {forbidden}"
        assert forbidden not in create_fields, f"Create should not have {forbidden}"
        assert forbidden not in update_fields, f"Update should not have {forbidden}"


# ---------- Backward compatibility regression (T13/T14) ----------


def test_existing_create_payload_still_works_without_extended_fields():
    """T13: POST equivalent flow — create operation with old-style payload
    (no extended fields) succeeds and produces NULL extended fields.
    """
    db = _make_session()
    product_id = _mk_product(db)
    routing = create_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin",
        payload=RoutingCreateRequest(
            product_id=product_id,
            routing_code="R-LEGACY",
            routing_name="Legacy payload routing",
        ),
    )

    # Old-style payload — only original fields
    add_routing_operation(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing.routing_id,
        payload=RoutingOperationCreateRequest(
            operation_code="OP-OLD",
            operation_name="Old style op",
            sequence_no=10,
            standard_cycle_time=90.0,
            required_resource_type="WORK_CENTER",
        ),
    )

    op_row = db.scalar(
        select(RoutingOperation).where(RoutingOperation.routing_id == routing.routing_id)
    )
    assert op_row.operation_code == "OP-OLD"
    assert op_row.standard_cycle_time == 90.0
    # Extended fields default to NULL when not specified
    assert op_row.setup_time is None
    assert op_row.run_time_per_unit is None
    assert op_row.work_center_code is None
