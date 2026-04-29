from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.product import Product
from app.models.routing import Routing, RoutingOperation
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest
from app.schemas.routing import (
    RoutingCreateRequest,
    RoutingOperationCreateRequest,
    RoutingOperationUpdateRequest,
    RoutingUpdateRequest,
)
from app.services.product_service import create_product, retire_product
from app.services.routing_service import (
    add_routing_operation,
    create_routing,
    get_routing_by_id,
    list_routings,
    release_routing,
    remove_routing_operation,
    retire_routing,
    update_routing,
    update_routing_operation,
)


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Product.__table__.create(bind=engine)
    Routing.__table__.create(bind=engine)
    RoutingOperation.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _mk_product(db, tenant_id: str = "tenant_a") -> str:
    created = create_product(
        db,
        tenant_id=tenant_id,
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code="FG-100",
            product_name="Routing product",
            product_type="FINISHED_GOOD",
        ),
    )
    return created.product_id


def test_create_routing_happy_path_and_event():
    db = _make_session()
    product_id = _mk_product(db)

    created = create_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=RoutingCreateRequest(
            product_id=product_id,
            routing_code="R-001",
            routing_name="Primary routing",
        ),
    )

    assert created.tenant_id == "tenant_a"
    assert created.routing_code == "R-001"
    assert created.lifecycle_status == "DRAFT"

    events = list(db.scalars(select(SecurityEventLog).order_by(SecurityEventLog.id.asc())))
    assert events[-1].event_type == "ROUTING.CREATED"


def test_routing_code_unique_per_tenant_but_allowed_cross_tenant():
    db = _make_session()
    product_a = _mk_product(db, tenant_id="tenant_a")
    product_b = _mk_product(db, tenant_id="tenant_b")

    create_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=RoutingCreateRequest(
            product_id=product_a,
            routing_code="R-DUP",
            routing_name="A routing",
        ),
    )

    try:
        create_routing(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            payload=RoutingCreateRequest(
                product_id=product_a,
                routing_code="R-DUP",
                routing_name="A routing duplicate",
            ),
        )
        assert False, "Expected duplicate routing_code rejection in same tenant"
    except ValueError:
        pass

    created_other_tenant = create_routing(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        payload=RoutingCreateRequest(
            product_id=product_b,
            routing_code="R-DUP",
            routing_name="B routing",
        ),
    )
    assert created_other_tenant.tenant_id == "tenant_b"


def test_tenant_scoped_list_and_get_and_cross_tenant_hidden():
    db = _make_session()
    product_a = _mk_product(db, tenant_id="tenant_a")
    product_b = _mk_product(db, tenant_id="tenant_b")

    routing_a = create_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=RoutingCreateRequest(
            product_id=product_a,
            routing_code="A-R-1",
            routing_name="Tenant A routing",
        ),
    )
    create_routing(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        payload=RoutingCreateRequest(
            product_id=product_b,
            routing_code="B-R-1",
            routing_name="Tenant B routing",
        ),
    )

    listed_a = list_routings(db, tenant_id="tenant_a")
    assert len(listed_a) == 1
    assert listed_a[0].routing_id == routing_a.routing_id

    found = get_routing_by_id(db, tenant_id="tenant_a", routing_id=routing_a.routing_id)
    assert found is not None

    hidden = get_routing_by_id(db, tenant_id="tenant_b", routing_id=routing_a.routing_id)
    assert hidden is None


def test_retired_product_cannot_be_newly_linked_for_routing_create():
    db = _make_session()
    product_id = _mk_product(db)

    retire_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=product_id,
    )

    try:
        create_routing(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            payload=RoutingCreateRequest(
                product_id=product_id,
                routing_code="R-REJECT",
                routing_name="Should fail",
            ),
        )
        assert False, "Expected retired product linkage rejection"
    except ValueError:
        pass


def test_draft_operations_and_release_retired_guards():
    db = _make_session()
    product_id = _mk_product(db)

    created = create_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=RoutingCreateRequest(
            product_id=product_id,
            routing_code="R-OPS-1",
            routing_name="Ops routing",
        ),
    )

    add_routing_operation(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=created.routing_id,
        payload=RoutingOperationCreateRequest(
            operation_code="OP10",
            operation_name="Cut",
            sequence_no=10,
            standard_cycle_time=12.5,
            required_resource_type="MACHINE",
        ),
    )

    try:
        add_routing_operation(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            routing_id=created.routing_id,
            payload=RoutingOperationCreateRequest(
                operation_code="OP20",
                operation_name="Weld",
                sequence_no=10,
            ),
        )
        assert False, "Expected duplicate sequence_no rejection"
    except ValueError:
        pass

    current = get_routing_by_id(db, tenant_id="tenant_a", routing_id=created.routing_id)
    operation_id = current.operations[0].operation_id

    updated = update_routing_operation(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=created.routing_id,
        operation_id=operation_id,
        payload=RoutingOperationUpdateRequest(operation_name="Cut revised"),
    )
    assert updated.operations[0].operation_name == "Cut revised"

    removed = remove_routing_operation(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=created.routing_id,
        operation_id=operation_id,
    )
    assert len(removed.operations) == 0

    add_routing_operation(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=created.routing_id,
        payload=RoutingOperationCreateRequest(
            operation_code="OP30",
            operation_name="Assemble",
            sequence_no=30,
        ),
    )

    released = release_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=created.routing_id,
    )
    assert released.lifecycle_status == "RELEASED"

    renamed = update_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=created.routing_id,
        payload=RoutingUpdateRequest(routing_name="Released rename"),
    )
    assert renamed.routing_name == "Released rename"

    try:
        update_routing(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            routing_id=created.routing_id,
            payload=RoutingUpdateRequest(routing_code="R-OPS-2"),
        )
        assert False, "Expected structural update rejection for RELEASED routing"
    except ValueError:
        pass

    try:
        add_routing_operation(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            routing_id=created.routing_id,
            payload=RoutingOperationCreateRequest(
                operation_code="OP40",
                operation_name="Paint",
                sequence_no=40,
            ),
        )
        assert False, "Expected RELEASED operation mutation rejection"
    except ValueError:
        pass

    retired = retire_routing(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        routing_id=created.routing_id,
    )
    assert retired.lifecycle_status == "RETIRED"

    try:
        update_routing(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            routing_id=created.routing_id,
            payload=RoutingUpdateRequest(routing_name="Nope"),
        )
        assert False, "Expected RETIRED update rejection"
    except ValueError:
        pass

    try:
        release_routing(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            routing_id=created.routing_id,
        )
        assert False, "Expected RETIRED release rejection"
    except ValueError:
        pass
