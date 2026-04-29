import uuid

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.product import Product
from app.models.routing import Routing, RoutingOperation
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.schemas.resource_requirement import (
    ResourceRequirementCreateRequest,
    ResourceRequirementUpdateRequest,
)
from app.schemas.routing import RoutingCreateRequest, RoutingOperationCreateRequest
from app.services.product_service import create_product
from app.services.resource_requirement_service import (
    create_resource_requirement,
    delete_resource_requirement,
    get_resource_requirement_by_id,
    list_resource_requirements,
    update_resource_requirement,
)
from app.services.routing_service import (
    add_routing_operation,
    create_routing,
    release_routing,
    retire_routing,
)


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Product.__table__.create(bind=engine)
    Routing.__table__.create(bind=engine)
    RoutingOperation.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)

    # Fail-first expectation: this table/model does not exist before implementation.
    from app.models.resource_requirement import ResourceRequirement

    ResourceRequirement.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _mk_product(db, tenant_id: str) -> str:
    row = create_product(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin",
        payload=ProductCreateRequest(
            product_code=f"P-{tenant_id}-{uuid.uuid4().hex[:8]}",
            product_name=f"Product {tenant_id}",
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


def test_create_list_get_update_delete_requirement_happy_path_and_events():
    db = _make_session()
    routing_id, operation_id = _mk_routing_with_operation(db)

    created = create_resource_requirement(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing_id,
        operation_id=operation_id,
        payload=ResourceRequirementCreateRequest(
            required_resource_type="TOOLING",
            required_capability_code="TORQUE_TOOL",
            quantity_required=1,
            notes="Need torque tooling",
            metadata_json='{"critical":true}',
        ),
    )
    assert created.required_resource_type == "TOOLING"

    listed = list_resource_requirements(db, tenant_id="tenant_a", routing_id=routing_id, operation_id=operation_id)
    assert len(listed) == 1

    fetched = get_resource_requirement_by_id(
        db,
        tenant_id="tenant_a",
        routing_id=routing_id,
        operation_id=operation_id,
        requirement_id=created.requirement_id,
    )
    assert fetched is not None

    updated = update_resource_requirement(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing_id,
        operation_id=operation_id,
        requirement_id=created.requirement_id,
        payload=ResourceRequirementUpdateRequest(quantity_required=2, notes="Need two tools"),
    )
    assert updated.quantity_required == 2

    removed = delete_resource_requirement(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing_id,
        operation_id=operation_id,
        requirement_id=created.requirement_id,
    )
    assert removed.requirement_id == created.requirement_id

    events = list(db.scalars(select(SecurityEventLog).order_by(SecurityEventLog.id.asc())))
    event_types = [e.event_type for e in events]
    assert "RESOURCE_REQUIREMENT.CREATED" in event_types
    assert "RESOURCE_REQUIREMENT.UPDATED" in event_types
    assert "RESOURCE_REQUIREMENT.REMOVED" in event_types


def test_cross_tenant_hidden_and_cross_tenant_create_rejected():
    db = _make_session()
    routing_a, operation_a = _mk_routing_with_operation(db, tenant_id="tenant_a")
    routing_b, operation_b = _mk_routing_with_operation(db, tenant_id="tenant_b")

    created = create_resource_requirement(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=routing_a,
        operation_id=operation_a,
        payload=ResourceRequirementCreateRequest(
            required_resource_type="WORK_CENTER",
            required_capability_code="WELDING_CELL",
            quantity_required=1,
        ),
    )

    hidden = get_resource_requirement_by_id(
        db,
        tenant_id="tenant_b",
        routing_id=routing_a,
        operation_id=operation_a,
        requirement_id=created.requirement_id,
    )
    assert hidden is None

    try:
        create_resource_requirement(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            routing_id=routing_b,
            operation_id=operation_b,
            payload=ResourceRequirementCreateRequest(
                required_resource_type="WORK_CENTER",
                required_capability_code="PAINT_BOOTH",
                quantity_required=1,
            ),
        )
        assert False, "Expected cross-tenant routing/operation linkage rejection"
    except LookupError:
        pass


def test_mismatched_routing_operation_duplicate_and_input_validation_rejected():
    db = _make_session()
    routing_id, operation_id = _mk_routing_with_operation(db, tenant_id="tenant_a")
    other_routing_id, _ = _mk_routing_with_operation(db, tenant_id="tenant_a")

    try:
        create_resource_requirement(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin",
            routing_id=other_routing_id,
            operation_id=operation_id,
            payload=ResourceRequirementCreateRequest(
                required_resource_type="TOOLING",
                required_capability_code="TORQUE_TOOL",
                quantity_required=1,
            ),
        )
        assert False, "Expected operation/routing mismatch rejection"
    except LookupError:
        pass

    create_resource_requirement(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing_id,
        operation_id=operation_id,
        payload=ResourceRequirementCreateRequest(
            required_resource_type="TOOLING",
            required_capability_code="TORQUE_TOOL",
            quantity_required=1,
        ),
    )

    try:
        create_resource_requirement(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin",
            routing_id=routing_id,
            operation_id=operation_id,
            payload=ResourceRequirementCreateRequest(
                required_resource_type="TOOLING",
                required_capability_code="TORQUE_TOOL",
                quantity_required=1,
            ),
        )
        assert False, "Expected duplicate requirement rejection"
    except ValueError:
        pass

    try:
        create_resource_requirement(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin",
            routing_id=routing_id,
            operation_id=operation_id,
            payload=ResourceRequirementCreateRequest(
                required_resource_type="INVALID",
                required_capability_code="X",
                quantity_required=1,
            ),
        )
        assert False, "Expected invalid required_resource_type rejection"
    except ValueError:
        pass

    try:
        create_resource_requirement(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin",
            routing_id=routing_id,
            operation_id=operation_id,
            payload=ResourceRequirementCreateRequest(
                required_resource_type="TOOLING",
                required_capability_code="",
                quantity_required=1,
            ),
        )
        assert False, "Expected missing required_capability_code rejection"
    except ValueError:
        pass

    try:
        create_resource_requirement(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin",
            routing_id=routing_id,
            operation_id=operation_id,
            payload=ResourceRequirementCreateRequest(
                required_resource_type="TOOLING",
                required_capability_code="TORQUE_TOOL",
                quantity_required=0,
            ),
        )
        assert False, "Expected quantity_required <= 0 rejection"
    except ValueError:
        pass


def test_released_and_retired_routing_block_mutation():
    db = _make_session()
    routing_id, operation_id = _mk_routing_with_operation(db, tenant_id="tenant_a")

    release_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing_id,
    )

    try:
        create_resource_requirement(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin",
            routing_id=routing_id,
            operation_id=operation_id,
            payload=ResourceRequirementCreateRequest(
                required_resource_type="TOOLING",
                required_capability_code="TORQUE_TOOL",
                quantity_required=1,
            ),
        )
        assert False, "Expected RELEASED create rejection"
    except ValueError:
        pass

    db2 = _make_session()
    routing2, op2 = _mk_routing_with_operation(db2, tenant_id="tenant_a")
    req = create_resource_requirement(
        db2,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing2,
        operation_id=op2,
        payload=ResourceRequirementCreateRequest(
            required_resource_type="TOOLING",
            required_capability_code="TORQUE_TOOL",
            quantity_required=1,
        ),
    )
    retire_routing(
        db2,
        tenant_id="tenant_a",
        actor_user_id="admin",
        routing_id=routing2,
    )

    for action in ("update", "delete", "create"):
        try:
            if action == "update":
                update_resource_requirement(
                    db2,
                    tenant_id="tenant_a",
                    actor_user_id="admin",
                    routing_id=routing2,
                    operation_id=op2,
                    requirement_id=req.requirement_id,
                    payload=ResourceRequirementUpdateRequest(notes="x"),
                )
            elif action == "delete":
                delete_resource_requirement(
                    db2,
                    tenant_id="tenant_a",
                    actor_user_id="admin",
                    routing_id=routing2,
                    operation_id=op2,
                    requirement_id=req.requirement_id,
                )
            else:
                create_resource_requirement(
                    db2,
                    tenant_id="tenant_a",
                    actor_user_id="admin",
                    routing_id=routing2,
                    operation_id=op2,
                    payload=ResourceRequirementCreateRequest(
                        required_resource_type="WORK_CENTER",
                        required_capability_code="FINAL_INSPECTION",
                        quantity_required=1,
                    ),
                )
            assert False, f"Expected RETIRED {action} rejection"
        except ValueError:
            pass
