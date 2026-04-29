from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.rbac import Role, Scope, UserRole, UserRoleAssignment
from app.models.user import User
from app.services.access_service import assign_role, assign_scope


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    User.__table__.create(bind=engine)
    Role.__table__.create(bind=engine)
    Scope.__table__.create(bind=engine)
    UserRole.__table__.create(bind=engine)
    UserRoleAssignment.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_assign_role_enforces_tenant_boundary():
    db = _make_session()
    db.add_all(
        [
            User(
                user_id="u-a",
                username="alice",
                email=None,
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

    assigned = assign_role(
        db,
        tenant_id="tenant_a",
        user_id="u-a",
        role_code="SUP",
        is_active=True,
    )
    assert assigned.tenant_id == "tenant_a"

    try:
        assign_role(
            db,
            tenant_id="tenant_b",
            user_id="u-a",
            role_code="SUP",
            is_active=True,
        )
        assert False, "Expected ValueError for cross-tenant user"
    except ValueError:
        pass


def test_assign_scope_creates_tenant_scope_and_assignment():
    db = _make_session()
    db.add_all(
        [
            User(
                user_id="u-a",
                username="alice",
                email=None,
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

    assignment, role, scope = assign_scope(
        db,
        tenant_id="tenant_a",
        user_id="u-a",
        role_code="SUP",
        scope_type="plant",
        scope_value="PLANT_1",
        is_primary=True,
    )

    assert assignment.user_id == "u-a"
    assert role.code == "SUP"
    assert scope.tenant_id == "tenant_a"
    assert scope.scope_type == "plant"
    assert scope.parent_scope_id is not None


def test_assign_scope_rejects_unsupported_scope_type():
    db = _make_session()
    db.add_all(
        [
            User(
                user_id="u-a",
                username="alice",
                email=None,
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

    try:
        assign_scope(
            db,
            tenant_id="tenant_a",
            user_id="u-a",
            role_code="SUP",
            scope_type="workcenter",
            scope_value="WC_1",
            is_primary=False,
        )
        assert False, "Expected ValueError for unsupported scope_type"
    except ValueError:
        pass
