from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.security_event import SecurityEventLog
from app.models.session import Session, SessionAuditLog
from app.services.session_service import (
    create_login_session,
    revoke_all_sessions_for_user,
    revoke_session,
)


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Session.__table__.create(bind=engine)
    SessionAuditLog.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_create_login_session_records_security_event():
    db = _make_session()

    session = create_login_session(db, user_id="u-1", tenant_id="tenant_a")

    events = list(db.scalars(select(SecurityEventLog)))
    assert len(events) == 1
    assert events[0].tenant_id == "tenant_a"
    assert events[0].actor_user_id == "u-1"
    assert events[0].event_type == "AUTH.LOGIN"
    assert events[0].resource_type == "session"
    assert events[0].resource_id == session.session_id


def test_revoke_session_records_logout_security_event():
    db = _make_session()
    session = create_login_session(db, user_id="u-1", tenant_id="tenant_a")

    revoke_session(
        db,
        session_id=session.session_id,
        tenant_id="tenant_a",
        actor_user_id="u-1",
        reason="logout",
    )

    events = list(
        db.scalars(
            select(SecurityEventLog).order_by(SecurityEventLog.id.asc())
        )
    )
    assert [event.event_type for event in events] == ["AUTH.LOGIN", "AUTH.LOGOUT"]
    assert events[-1].resource_id == session.session_id


def test_revoke_all_sessions_records_security_event_per_revoked_session():
    db = _make_session()
    first = create_login_session(db, user_id="u-1", tenant_id="tenant_a")
    second = create_login_session(db, user_id="u-1", tenant_id="tenant_a")

    revoked = revoke_all_sessions_for_user(
        db,
        user_id="u-1",
        tenant_id="tenant_a",
        reason="logout_all",
    )

    events = list(
        db.scalars(
            select(SecurityEventLog)
            .where(SecurityEventLog.event_type == "AUTH.LOGOUT_ALL")
            .order_by(SecurityEventLog.id.asc())
        )
    )
    assert revoked == 2
    assert len(events) == 2
    assert {event.resource_id for event in events} == {first.session_id, second.session_id}


def test_admin_revoke_records_admin_session_revoke_event():
    db = _make_session()
    session = create_login_session(db, user_id="u-2", tenant_id="tenant_a")

    revoke_session(
        db,
        session_id=session.session_id,
        tenant_id="tenant_a",
        actor_user_id="admin-1",
        reason="admin_revoke",
    )

    events = list(
        db.scalars(
            select(SecurityEventLog)
            .where(SecurityEventLog.event_type == "AUTH.SESSION_REVOKE")
        )
    )
    assert len(events) == 1
    assert events[0].actor_user_id == "admin-1"
    assert events[0].resource_id == session.session_id
