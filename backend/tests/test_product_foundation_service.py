from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.product import Product
from app.models.security_event import SecurityEventLog
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest
from app.services.product_service import (
    create_product,
    get_product_by_id,
    list_products,
    release_product,
    retire_product,
    update_product,
)


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Product.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_create_product_happy_path_records_event():
    db = _make_session()

    created = create_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code="FG-001",
            product_name="Widget A",
            product_type="FINISHED_GOOD",
            description="Initial product",
            display_metadata={"color": "red"},
        ),
    )

    assert created.tenant_id == "tenant_a"
    assert created.product_code == "FG-001"
    assert created.lifecycle_status == "DRAFT"

    events = list(db.scalars(select(SecurityEventLog).order_by(SecurityEventLog.id.asc())))
    assert len(events) == 1
    assert events[0].event_type == "PRODUCT.CREATED"
    assert events[0].tenant_id == "tenant_a"
    assert events[0].actor_user_id == "admin-a"
    assert events[0].resource_id == created.product_id


def test_product_code_unique_per_tenant_but_allowed_cross_tenant():
    db = _make_session()

    create_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code="FG-001",
            product_name="Widget A",
            product_type="FINISHED_GOOD",
        ),
    )

    try:
        create_product(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            payload=ProductCreateRequest(
                product_code="FG-001",
                product_name="Widget A duplicate",
                product_type="SEMI_FINISHED",
            ),
        )
        assert False, "Expected duplicate product_code rejection in same tenant"
    except ValueError:
        pass

    created_other_tenant = create_product(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        payload=ProductCreateRequest(
            product_code="FG-001",
            product_name="Widget B",
            product_type="COMPONENT",
        ),
    )
    assert created_other_tenant.tenant_id == "tenant_b"


def test_list_and_get_are_tenant_scoped():
    db = _make_session()

    a = create_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code="A-001",
            product_name="Tenant A product",
            product_type="COMPONENT",
        ),
    )
    create_product(
        db,
        tenant_id="tenant_b",
        actor_user_id="admin-b",
        payload=ProductCreateRequest(
            product_code="B-001",
            product_name="Tenant B product",
            product_type="COMPONENT",
        ),
    )

    listed_a = list_products(db, tenant_id="tenant_a")
    assert len(listed_a) == 1
    assert listed_a[0].product_id == a.product_id

    found_in_tenant = get_product_by_id(db, tenant_id="tenant_a", product_id=a.product_id)
    assert found_in_tenant is not None

    hidden_cross_tenant = get_product_by_id(db, tenant_id="tenant_b", product_id=a.product_id)
    assert hidden_cross_tenant is None


def test_release_and_retire_transitions_and_events():
    db = _make_session()

    created = create_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code="FG-200",
            product_name="Release candidate",
            product_type="FINISHED_GOOD",
        ),
    )

    released = release_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=created.product_id,
    )
    assert released.lifecycle_status == "RELEASED"

    retired = retire_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=created.product_id,
    )
    assert retired.lifecycle_status == "RETIRED"

    try:
        release_product(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=created.product_id,
        )
        assert False, "Expected release rejection for RETIRED product"
    except ValueError:
        pass

    events = list(db.scalars(select(SecurityEventLog).order_by(SecurityEventLog.id.asc())))
    assert [event.event_type for event in events] == [
        "PRODUCT.CREATED",
        "PRODUCT.RELEASED",
        "PRODUCT.RETIRED",
    ]


def test_update_rules_for_draft_released_and_retired():
    db = _make_session()

    created = create_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        payload=ProductCreateRequest(
            product_code="UPD-001",
            product_name="Editable",
            product_type="SEMI_FINISHED",
        ),
    )

    draft_updated = update_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=created.product_id,
        payload=ProductUpdateRequest(
            product_code="UPD-002",
            product_name="Editable updated",
            product_type="COMPONENT",
            description="draft update",
            display_metadata={"priority": "high"},
        ),
    )
    assert draft_updated.product_code == "UPD-002"
    assert draft_updated.product_type == "COMPONENT"

    release_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=created.product_id,
    )

    released_updated = update_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=created.product_id,
        payload=ProductUpdateRequest(
            product_name="Released rename",
            description="released description",
            display_metadata={"ui": "badge"},
        ),
    )
    assert released_updated.product_name == "Released rename"

    try:
        update_product(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=created.product_id,
            payload=ProductUpdateRequest(product_code="ILLEGAL-CODE"),
        )
        assert False, "Expected structural update rejection for RELEASED product"
    except ValueError:
        pass

    retire_product(
        db,
        tenant_id="tenant_a",
        actor_user_id="admin-a",
        product_id=created.product_id,
    )

    try:
        update_product(
            db,
            tenant_id="tenant_a",
            actor_user_id="admin-a",
            product_id=created.product_id,
            payload=ProductUpdateRequest(product_name="Nope"),
        )
        assert False, "Expected update rejection for RETIRED product"
    except ValueError:
        pass

    events = list(db.scalars(select(SecurityEventLog).order_by(SecurityEventLog.id.asc())))
    assert [event.event_type for event in events] == [
        "PRODUCT.CREATED",
        "PRODUCT.UPDATED",
        "PRODUCT.RELEASED",
        "PRODUCT.UPDATED",
        "PRODUCT.RETIRED",
    ]
