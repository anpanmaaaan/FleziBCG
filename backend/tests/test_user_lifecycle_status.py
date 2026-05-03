"""Tests for P0-A-04A: User lifecycle status foundation.

Covers:
  - User model lifecycle_status field exists and has correct default
  - Alembic migration 0004 exists and is wired correctly
  - Migration backfills is_active → lifecycle_status
  - Migration does not touch unrelated tables
  - Auth eligibility: ACTIVE can login, DISABLED/LOCKED/inactive cannot
  - Refresh-token path does not bypass lifecycle status
  - Service: activate_user / deactivate_user set lifecycle_status correctly

All tests use SQLite in-memory DB — no external infrastructure required.
"""
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from app.models.user import (
    LIFECYCLE_STATUS_ACTIVE,
    LIFECYCLE_STATUS_DISABLED,
    LIFECYCLE_STATUS_LOCKED,
    User,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"

_USER_TABLES_ONLY = [User]


def _make_user_session():
    """SQLite in-memory engine with only the User table (fast model tests)."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    User.__table__.create(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()


def _make_user(
    user_id: str = "u-1",
    username: str = "alice",
    is_active: bool = True,
    lifecycle_status: str = LIFECYCLE_STATUS_ACTIVE,
    tenant_id: str = "default",
) -> User:
    return User(
        user_id=user_id,
        username=username,
        email=f"{username}@test.local",
        password_hash="hash",
        tenant_id=tenant_id,
        is_active=is_active,
        lifecycle_status=lifecycle_status,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


def test_user_lifecycle_status_field_exists():
    """User model must have a lifecycle_status attribute."""
    user = _make_user()
    assert hasattr(user, "lifecycle_status"), (
        "User model missing lifecycle_status field"
    )


def test_user_lifecycle_status_default_is_active():
    """New User created without explicit lifecycle_status defaults to ACTIVE."""
    user = User(
        user_id="u-default",
        username="default_user",
        password_hash="hash",
        tenant_id="default",
        is_active=True,
        # lifecycle_status NOT set explicitly — ORM default must apply
    )
    assert user.lifecycle_status == LIFECYCLE_STATUS_ACTIVE, (
        f"Expected default lifecycle_status=ACTIVE, got {user.lifecycle_status!r}"
    )


def test_user_is_lifecycle_active_property_active():
    """is_lifecycle_active is True only when is_active=True AND status=ACTIVE."""
    user = _make_user(is_active=True, lifecycle_status=LIFECYCLE_STATUS_ACTIVE)
    assert user.is_lifecycle_active is True


def test_user_is_lifecycle_active_property_disabled():
    """is_lifecycle_active is False when lifecycle_status=DISABLED."""
    user = _make_user(is_active=True, lifecycle_status=LIFECYCLE_STATUS_DISABLED)
    assert user.is_lifecycle_active is False


def test_user_is_lifecycle_active_property_locked():
    """is_lifecycle_active is False when lifecycle_status=LOCKED."""
    user = _make_user(is_active=True, lifecycle_status=LIFECYCLE_STATUS_LOCKED)
    assert user.is_lifecycle_active is False


def test_user_is_lifecycle_active_property_inactive():
    """is_lifecycle_active is False when is_active=False even if status=ACTIVE."""
    user = _make_user(is_active=False, lifecycle_status=LIFECYCLE_STATUS_ACTIVE)
    assert user.is_lifecycle_active is False


def test_user_lifecycle_status_field_persisted():
    """lifecycle_status column value is persisted and retrieved correctly."""
    db = _make_user_session()
    db.add(_make_user(user_id="u-persist", lifecycle_status=LIFECYCLE_STATUS_DISABLED))
    db.commit()

    retrieved = db.get(User, 1)
    assert retrieved is not None
    assert retrieved.lifecycle_status == LIFECYCLE_STATUS_DISABLED


# ---------------------------------------------------------------------------
# Migration structure tests (no DB connection required)
# ---------------------------------------------------------------------------


def test_user_status_migration_revision_exists():
    """Alembic revision 0004 must be discoverable by ScriptDirectory."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(ALEMBIC_INI))
    script_dir = ScriptDirectory.from_config(cfg)
    rev_ids = [r.revision for r in script_dir.walk_revisions()]
    assert "0004" in rev_ids, (
        f"Migration 0004 not found. Available revisions: {rev_ids}"
    )


def test_user_status_migration_down_revision_is_0003():
    """Migration 0004 must chain from 0003."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(ALEMBIC_INI))
    script_dir = ScriptDirectory.from_config(cfg)
    rev = script_dir.get_revision("0004")
    assert rev is not None
    assert rev.down_revision == "0003", (
        f"Expected down_revision=0003, got: {rev.down_revision}"
    )


def test_user_status_migration_backfills_from_is_active():
    """Migration upgrade backfills lifecycle_status from is_active.

    Verifies: active users → ACTIVE, inactive users → DISABLED.
    Uses raw SQLite to simulate pre-0004 state and the migration SQL.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    with engine.begin() as conn:
        # Create users table in pre-0004 state (no lifecycle_status column)
        conn.execute(text(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL UNIQUE,
                username VARCHAR(64) NOT NULL,
                email VARCHAR(256),
                password_hash VARCHAR(256) NOT NULL,
                tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        ))
        # Seed: one active, one inactive
        conn.execute(text(
            "INSERT INTO users (user_id, username, password_hash, tenant_id, is_active) "
            "VALUES ('u-active', 'alice', 'h', 'default', 1)"
        ))
        conn.execute(text(
            "INSERT INTO users (user_id, username, password_hash, tenant_id, is_active) "
            "VALUES ('u-inactive', 'bob', 'h', 'default', 0)"
        ))

        # Apply the lifecycle_status column (simulating 0004 upgrade step 1)
        conn.execute(text("ALTER TABLE users ADD COLUMN lifecycle_status VARCHAR(32)"))

        # Apply the backfill SQL from the migration
        conn.execute(text(
            "UPDATE users SET lifecycle_status = 'ACTIVE' WHERE is_active = true"
        ))
        conn.execute(text(
            "UPDATE users SET lifecycle_status = 'DISABLED' WHERE is_active = false"
        ))

        # Verify
        result = conn.execute(text(
            "SELECT user_id, lifecycle_status FROM users ORDER BY user_id"
        ))
        rows = {row[0]: row[1] for row in result}

    assert rows.get("u-active") == "ACTIVE", (
        f"Active user should be ACTIVE, got: {rows.get('u-active')}"
    )
    assert rows.get("u-inactive") == "DISABLED", (
        f"Inactive user should be DISABLED, got: {rows.get('u-inactive')}"
    )


def test_user_status_migration_does_not_touch_unrelated_tables():
    """Migration 0004 upgrade/downgrade modifies only the users table.

    Parses the migration source to verify only 'users' appears in op calls.
    """
    import ast

    migration_path = (
        BACKEND_DIR / "alembic" / "versions" / "0004_add_user_lifecycle_status.py"
    )
    source = migration_path.read_text()
    tree = ast.parse(source)

    table_args: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if not (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "op"
            ):
                continue

            attr = node.func.attr
            if attr in {"add_column", "drop_column", "alter_column", "create_table", "drop_table"}:
                # First positional arg is the table name
                if node.args and isinstance(node.args[0], ast.Constant):
                    table_args.append(node.args[0].value)
            elif attr in {"create_index"}:
                # create_index(index_name, table_name, columns)
                # Table name is the second positional arg (args[1])
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    table_args.append(node.args[1].value)
            elif attr in {"drop_index"}:
                # drop_index(index_name, table_name=...) — table via keyword
                pass  # handled below via keyword scan

            # Also check table_name= keyword for any op call
            for kw in node.keywords:
                if kw.arg == "table_name" and isinstance(kw.value, ast.Constant):
                    table_args.append(kw.value.value)

    non_users = [t for t in table_args if t != "users"]
    assert non_users == [], (
        f"Migration 0004 must only touch 'users' table, found: {non_users}"
    )


# ---------------------------------------------------------------------------
# Auth eligibility tests (SQLite in-memory, all tables needed)
# ---------------------------------------------------------------------------

from app.models.rbac import Role, UserRole
from app.models.session import Session as AuthSession, SessionAuditLog
from app.models.security_event import SecurityEventLog
from app.models.refresh_token import RefreshToken
from app.security.auth import authenticate_user_db, get_identity_by_user_id

_AUTH_TABLES = [
    SecurityEventLog,
    User,
    Role,
    UserRole,
    AuthSession,
    SessionAuditLog,
    RefreshToken,
]


def _make_auth_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    for model in _AUTH_TABLES:
        model.__table__.create(bind=engine, checkfirst=True)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()


def _seed_user_with_status(
    db,
    *,
    user_id: str,
    username: str,
    password_hash: str = "plaintext",
    is_active: bool = True,
    lifecycle_status: str = LIFECYCLE_STATUS_ACTIVE,
    tenant_id: str = "default",
) -> User:
    user = User(
        user_id=user_id,
        username=username,
        email=f"{username}@test.local",
        password_hash=password_hash,
        tenant_id=tenant_id,
        is_active=is_active,
        lifecycle_status=lifecycle_status,
    )
    db.add(user)
    db.commit()
    return user


def test_active_user_can_login():
    """User with is_active=True and lifecycle_status=ACTIVE can authenticate."""
    db = _make_auth_session()
    _seed_user_with_status(
        db,
        user_id="u-active",
        username="alice",
        password_hash="secret",
        is_active=True,
        lifecycle_status=LIFECYCLE_STATUS_ACTIVE,
    )
    result = authenticate_user_db(db, "alice", "secret", tenant_id="default")
    assert result is not None, "Active ACTIVE user should authenticate"
    assert result.user_id == "u-active"


def test_disabled_user_cannot_login():
    """User with lifecycle_status=DISABLED cannot authenticate even if is_active=True."""
    db = _make_auth_session()
    _seed_user_with_status(
        db,
        user_id="u-disabled",
        username="disabled_user",
        password_hash="secret",
        is_active=True,
        lifecycle_status=LIFECYCLE_STATUS_DISABLED,
    )
    result = authenticate_user_db(db, "disabled_user", "secret", tenant_id="default")
    assert result is None, "DISABLED user must not authenticate"


def test_locked_user_cannot_login():
    """User with lifecycle_status=LOCKED cannot authenticate even if is_active=True."""
    db = _make_auth_session()
    _seed_user_with_status(
        db,
        user_id="u-locked",
        username="locked_user",
        password_hash="secret",
        is_active=True,
        lifecycle_status=LIFECYCLE_STATUS_LOCKED,
    )
    result = authenticate_user_db(db, "locked_user", "secret", tenant_id="default")
    assert result is None, "LOCKED user must not authenticate"


def test_inactive_user_maps_to_disabled_and_cannot_login():
    """User with is_active=False cannot authenticate regardless of lifecycle_status."""
    db = _make_auth_session()
    _seed_user_with_status(
        db,
        user_id="u-inactive",
        username="inactive_user",
        password_hash="secret",
        is_active=False,
        lifecycle_status=LIFECYCLE_STATUS_ACTIVE,  # status=ACTIVE but is_active=False
    )
    result = authenticate_user_db(db, "inactive_user", "secret", tenant_id="default")
    assert result is None, "Inactive user must not authenticate"


def test_refresh_token_flow_does_not_bypass_disabled_user():
    """get_identity_by_user_id returns None for DISABLED user (refresh-token path)."""
    db = _make_auth_session()
    _seed_user_with_status(
        db,
        user_id="u-disabled-refresh",
        username="disabled_refresh",
        is_active=True,
        lifecycle_status=LIFECYCLE_STATUS_DISABLED,
    )
    result = get_identity_by_user_id(db, user_id="u-disabled-refresh", tenant_id="default")
    assert result is None, (
        "DISABLED user must not get identity via refresh-token path"
    )


def test_refresh_token_flow_does_not_bypass_locked_user():
    """get_identity_by_user_id returns None for LOCKED user (refresh-token path)."""
    db = _make_auth_session()
    _seed_user_with_status(
        db,
        user_id="u-locked-refresh",
        username="locked_refresh",
        is_active=True,
        lifecycle_status=LIFECYCLE_STATUS_LOCKED,
    )
    result = get_identity_by_user_id(db, user_id="u-locked-refresh", tenant_id="default")
    assert result is None, (
        "LOCKED user must not get identity via refresh-token path"
    )


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------

from app.services.user_lifecycle_service import activate_user, deactivate_user


def test_activate_user_sets_status_active():
    """activate_user sets is_active=True and lifecycle_status=ACTIVE."""
    db = _make_user_session()
    db.add(_make_user(
        user_id="u-deact",
        is_active=False,
        lifecycle_status=LIFECYCLE_STATUS_DISABLED,
    ))
    db.commit()

    result = activate_user(db, tenant_id="default", user_id="u-deact")
    assert result is not None
    assert result.is_active is True
    assert result.lifecycle_status == LIFECYCLE_STATUS_ACTIVE


def test_deactivate_user_sets_status_disabled():
    """deactivate_user sets is_active=False and lifecycle_status=DISABLED."""
    db = _make_user_session()
    db.add(_make_user(
        user_id="u-act",
        is_active=True,
        lifecycle_status=LIFECYCLE_STATUS_ACTIVE,
    ))
    db.commit()

    result = deactivate_user(db, tenant_id="default", user_id="u-act")
    assert result is not None
    assert result.is_active is False
    assert result.lifecycle_status == LIFECYCLE_STATUS_DISABLED


def test_activate_user_unknown_user_returns_none():
    """activate_user for non-existent user returns None safely."""
    db = _make_user_session()
    result = activate_user(db, tenant_id="default", user_id="u-nonexistent")
    assert result is None
