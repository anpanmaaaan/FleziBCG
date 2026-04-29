from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.rbac import Role, Scope, UserRole, UserRoleAssignment
from app.models.security_event import SecurityEventLog
from app.models.user import User
from app.services.access_service import assign_role, assign_scope
from app.services.user_lifecycle_service import activate_user, deactivate_user


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    User.__table__.create(bind=engine)
    Role.__table__.create(bind=engine)
    Scope.__table__.create(bind=engine)
    UserRole.__table__.create(bind=engine)
    UserRoleAssignment.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _seed_user_and_role(db):
    db.add_all(
        [
            User(
                user_id="u-a",
                username="alice",
                email="alice@example.com",
                password_hash="h",
                tenant_id="tenant_a",
                is_active=True,
            ),
            Role(
                code="SUP",
                tenant_id=None,
                name="Supervisor",
                role_type="system",
                is_active=True,
                is_system=True,
            ),
        ]
    )
    db.commit()


def test_user_lifecycle_records_security_events():
    db = _make_session()
    _seed_user_and_role(db)

    deactivate_user(db, tenant_id="tenant_a", user_id="u-a", actor_user_id="admin-1")
    activate_user(db, tenant_id="tenant_a", user_id="u-a", actor_user_id="admin-1")

    events = list(db.scalars(select(SecurityEventLog).order_by(SecurityEventLog.id.asc())))
    assert [event.event_type for event in events] == ["IAM.USER_DEACTIVATE", "IAM.USER_ACTIVATE"]
    assert all(event.actor_user_id == "admin-1" for event in events)
    assert all(event.tenant_id == "tenant_a" for event in events)


def test_access_assignment_records_security_events():
    db = _make_session()
    _seed_user_and_role(db)

    assign_role(
        db,
        tenant_id="tenant_a",
        user_id="u-a",
        role_code="SUP",
        is_active=True,
        actor_user_id="admin-1",
    )
    assign_scope(
        db,
        tenant_id="tenant_a",
        user_id="u-a",
        role_code="SUP",
        scope_type="plant",
        scope_value="PLANT_1",
        is_primary=True,
        actor_user_id="admin-1",
    )

    events = list(db.scalars(select(SecurityEventLog).order_by(SecurityEventLog.id.asc())))
    assert [event.event_type for event in events] == ["IAM.ROLE_ASSIGNMENT", "IAM.SCOPE_ASSIGNMENT"]
    assert all(event.actor_user_id == "admin-1" for event in events)
