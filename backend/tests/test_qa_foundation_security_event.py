from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.security_event import SecurityEventLog
from app.services.security_event_service import get_security_events, record_security_event


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_record_security_event_persists_actor_and_resource_fields():
    db = _make_session()
    event = record_security_event(
        db,
        tenant_id="tenant_a",
        actor_user_id="u-qa-1",
        event_type=" product.created ",
        resource_type="product",
        resource_id="prod-001",
        detail="created from qa foundation",
    )

    assert event.id > 0
    assert event.tenant_id == "tenant_a"
    assert event.actor_user_id == "u-qa-1"
    assert event.event_type == "PRODUCT.CREATED"
    assert event.resource_type == "product"
    assert event.resource_id == "prod-001"
    assert event.detail == "created from qa foundation"
    assert event.created_at is not None


def test_get_security_events_filters_by_tenant_and_limit():
    db = _make_session()

    for idx in range(3):
        record_security_event(
            db,
            tenant_id="tenant_a",
            actor_user_id="u-qa-a",
            event_type=f"TENANT_A_EVENT_{idx}",
            resource_type="product",
            resource_id=f"a-{idx}",
        )

    record_security_event(
        db,
        tenant_id="tenant_b",
        actor_user_id="u-qa-b",
        event_type="TENANT_B_EVENT",
        resource_type="product",
        resource_id="b-1",
    )

    tenant_a_events = get_security_events(db, tenant_id="tenant_a", limit=2)
    tenant_b_events = get_security_events(db, tenant_id="tenant_b", limit=10)

    assert len(tenant_a_events) == 2
    assert all(item.tenant_id == "tenant_a" for item in tenant_a_events)
    assert len(tenant_b_events) == 1
    assert tenant_b_events[0].event_type == "TENANT_B_EVENT"
