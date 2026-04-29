from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.services.user_lifecycle_service import (
    activate_user,
    deactivate_user,
    list_tenant_users,
)


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    User.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_list_tenant_users_filters_by_tenant_and_active_flag():
    db = _make_session()
    db.add_all(
        [
            User(
                user_id="u-a-1",
                username="alice",
                email="alice@example.com",
                password_hash="h",
                tenant_id="tenant_a",
                is_active=True,
            ),
            User(
                user_id="u-a-2",
                username="amy",
                email="amy@example.com",
                password_hash="h",
                tenant_id="tenant_a",
                is_active=False,
            ),
            User(
                user_id="u-b-1",
                username="bob",
                email="bob@example.com",
                password_hash="h",
                tenant_id="tenant_b",
                is_active=True,
            ),
        ]
    )
    db.commit()

    active_only = list_tenant_users(db, tenant_id="tenant_a")
    all_users = list_tenant_users(db, tenant_id="tenant_a", include_inactive=True)

    assert [u.user_id for u in active_only] == ["u-a-1"]
    assert [u.user_id for u in all_users] == ["u-a-1", "u-a-2"]


def test_activate_and_deactivate_user_are_tenant_scoped():
    db = _make_session()
    db.add_all(
        [
            User(
                user_id="u-a-1",
                username="alice",
                email="alice@example.com",
                password_hash="h",
                tenant_id="tenant_a",
                is_active=True,
            ),
            User(
                user_id="u-b-1",
                username="bob",
                email="bob@example.com",
                password_hash="h",
                tenant_id="tenant_b",
                is_active=True,
            ),
        ]
    )
    db.commit()

    updated = deactivate_user(db, tenant_id="tenant_a", user_id="u-a-1")
    assert updated is not None
    assert updated.is_active is False

    cross_tenant = activate_user(db, tenant_id="tenant_a", user_id="u-b-1")
    assert cross_tenant is None
