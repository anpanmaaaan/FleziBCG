from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.security_event import SecurityEventLog
from app.services.security_event_service import get_security_events, record_security_event


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_record_security_event_normalizes_event_type_and_persists():
    db = _make_session()
    event = record_security_event(
        db,
        tenant_id="tenant_a",
        actor_user_id="u-1",
        event_type=" auth.login ",
        resource_type="session",
        resource_id="s-1",
        detail="login success",
    )

    assert event.id > 0
    assert event.tenant_id == "tenant_a"
    assert event.event_type == "AUTH.LOGIN"


def test_get_security_events_is_tenant_scoped_and_limited():
    db = _make_session()
    for i in range(3):
        record_security_event(
            db,
            tenant_id="tenant_a",
            actor_user_id="u-1",
            event_type=f"event_{i}",
        )
    record_security_event(
        db,
        tenant_id="tenant_b",
        actor_user_id="u-2",
        event_type="event_other",
    )

    tenant_a_events = get_security_events(db, tenant_id="tenant_a", limit=2)
    tenant_b_events = get_security_events(db, tenant_id="tenant_b", limit=10)

    assert len(tenant_a_events) == 2
    assert all(item.tenant_id == "tenant_a" for item in tenant_a_events)
    assert len(tenant_b_events) == 1
    assert tenant_b_events[0].tenant_id == "tenant_b"
