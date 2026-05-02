"""Tests for Tenant lifecycle anchor ORM foundation (P0-A-02A).

Covers:
- Tenant ORM model existence and fields
- Tenant lifecycle constants
- Default lifecycle status at Python construction time
- is_lifecycle_active property
- Alembic migration revision 0006 structure
- Migration creates only tenants table / does not modify existing tables
- Unique constraints and indexes
- Downgrade contract
- Alembic head updated to 0006
"""
import ast
import re
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
MIGRATION_FILE = (
    BACKEND_DIR / "alembic" / "versions" / "0006_add_tenant_lifecycle_anchor.py"
)


# ── Model tests ──────────────────────────────────────────────────────────────

def test_tenant_model_exists() -> None:
    """Tenant class must be importable from app.models.tenant."""
    from app.models.tenant import Tenant
    assert Tenant is not None


def test_tenant_fields_exist() -> None:
    """Required fields must exist on the Tenant mapped class."""
    from app.models.tenant import Tenant
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(Tenant)
    column_names = {col.key for col in mapper.mapper.column_attrs}

    required = {
        "tenant_id",
        "tenant_code",
        "tenant_name",
        "lifecycle_status",
        "timezone",
        "locale",
        "country_code",
        "is_active",
        "metadata_json",
        "created_at",
        "updated_at",
    }
    missing = required - column_names
    assert not missing, f"Missing fields on Tenant: {missing}"


def test_tenant_lifecycle_constants_exist() -> None:
    """Lifecycle status constants must be importable with correct values."""
    from app.models.tenant import (
        TENANT_STATUS_ACTIVE,
        TENANT_STATUS_DISABLED,
        TENANT_STATUS_SUSPENDED,
    )
    assert TENANT_STATUS_ACTIVE == "ACTIVE"
    assert TENANT_STATUS_DISABLED == "DISABLED"
    assert TENANT_STATUS_SUSPENDED == "SUSPENDED"


def test_tenant_default_status_is_active() -> None:
    """Tenant() without lifecycle_status must default to ACTIVE at Python init."""
    from app.models.tenant import Tenant, TENANT_STATUS_ACTIVE

    t = Tenant(
        tenant_id="t-test",
        tenant_code="TEST",
        tenant_name="Test Tenant",
    )
    assert t.lifecycle_status == TENANT_STATUS_ACTIVE


def test_tenant_is_active_defaults_true() -> None:
    """Tenant() without is_active must default to True at Python init."""
    from app.models.tenant import Tenant

    t = Tenant(
        tenant_id="t-test2",
        tenant_code="TEST2",
        tenant_name="Test Tenant 2",
    )
    assert t.is_active is True


def test_tenant_is_lifecycle_active_property() -> None:
    """is_lifecycle_active must return True only when both flags indicate active."""
    from app.models.tenant import Tenant, TENANT_STATUS_ACTIVE, TENANT_STATUS_DISABLED

    active_tenant = Tenant(
        tenant_id="t-a",
        tenant_code="A",
        tenant_name="Active",
        is_active=True,
        lifecycle_status=TENANT_STATUS_ACTIVE,
    )
    assert active_tenant.is_lifecycle_active is True

    disabled_tenant = Tenant(
        tenant_id="t-b",
        tenant_code="B",
        tenant_name="Disabled",
        is_active=True,
        lifecycle_status=TENANT_STATUS_DISABLED,
    )
    assert disabled_tenant.is_lifecycle_active is False

    inactive_tenant = Tenant(
        tenant_id="t-c",
        tenant_code="C",
        tenant_name="Inactive",
        is_active=False,
        lifecycle_status=TENANT_STATUS_ACTIVE,
    )
    assert inactive_tenant.is_lifecycle_active is False


# ── SQLite round-trip ─────────────────────────────────────────────────────────

def test_tenant_sqlite_round_trip() -> None:
    """Tenant must persist and retrieve correctly in an in-memory SQLite DB."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base
    from app.models.tenant import Tenant, TENANT_STATUS_ACTIVE

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with Session() as session:
        t = Tenant(
            tenant_id="t-rt",
            tenant_code="ROUNDTRIP",
            tenant_name="Round Trip Corp",
        )
        session.add(t)
        session.commit()

        retrieved = session.get(Tenant, "t-rt")
        assert retrieved is not None
        assert retrieved.tenant_code == "ROUNDTRIP"
        assert retrieved.tenant_name == "Round Trip Corp"
        assert retrieved.lifecycle_status == TENANT_STATUS_ACTIVE
        assert retrieved.is_active is True


# ── Migration tests ───────────────────────────────────────────────────────────

def test_tenant_migration_revision_exists() -> None:
    """Migration file 0006_add_tenant_lifecycle_anchor.py must exist."""
    assert MIGRATION_FILE.exists(), f"Migration file not found: {MIGRATION_FILE}"


def test_tenant_migration_revision_id() -> None:
    """revision must be '0006'."""
    source = MIGRATION_FILE.read_text(encoding="utf-8")
    assert 'revision: str = "0006"' in source, (
        "Expected revision = '0006' in migration file"
    )


def test_tenant_migration_down_revision_matches_current_head() -> None:
    """down_revision must be '0005' — the head before this slice."""
    source = MIGRATION_FILE.read_text(encoding="utf-8")
    assert 'down_revision' in source
    match = re.search(r'down_revision\s*.*=\s*"(\w+)"', source)
    assert match is not None, "Could not find down_revision assignment"
    assert match.group(1) == "0005", (
        f"Expected down_revision '0005', got '{match.group(1)}'"
    )


def test_tenant_migration_creates_tenants_table_only() -> None:
    """upgrade() must create the 'tenants' table and nothing else."""
    tree = ast.parse(MIGRATION_FILE.read_text(encoding="utf-8"))

    upgrade_fn = next(
        (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "upgrade"),
        None,
    )
    assert upgrade_fn is not None, "No upgrade() function found"

    create_calls = []
    for node in ast.walk(upgrade_fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "create_table"
        ):
            if node.args:
                table_name = ast.literal_eval(node.args[0])
                create_calls.append(table_name)

    assert create_calls == ["tenants"], (
        f"Expected upgrade() to create only 'tenants', got: {create_calls}"
    )


def test_tenant_migration_does_not_modify_existing_tables() -> None:
    """upgrade() must not alter, add to, or drop existing tables."""
    tree = ast.parse(MIGRATION_FILE.read_text(encoding="utf-8"))

    upgrade_fn = next(
        (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "upgrade"),
        None,
    )
    assert upgrade_fn is not None

    forbidden_ops = {"alter_table", "add_column", "drop_column", "drop_table"}
    for node in ast.walk(upgrade_fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in forbidden_ops
        ):
            pytest.fail(
                f"upgrade() must not call op.{node.func.attr}() — "
                f"this slice must not modify existing tables."
            )


def test_tenant_unique_constraints_exist() -> None:
    """Migration must declare uq_tenants_tenant_code unique constraint."""
    source = MIGRATION_FILE.read_text(encoding="utf-8")
    assert "uq_tenants_tenant_code" in source, (
        "Expected unique constraint 'uq_tenants_tenant_code' in migration"
    )


def test_tenant_indexes_exist() -> None:
    """Migration must create all three required indexes."""
    source = MIGRATION_FILE.read_text(encoding="utf-8")
    required_indexes = [
        "ix_tenants_tenant_code",
        "ix_tenants_lifecycle_status",
        "ix_tenants_is_active",
    ]
    for idx in required_indexes:
        assert idx in source, f"Expected index '{idx}' in migration file"


def test_tenant_downgrade_drops_tenants_table_only() -> None:
    """downgrade() must drop only the tenants table and its indexes."""
    tree = ast.parse(MIGRATION_FILE.read_text(encoding="utf-8"))

    downgrade_fn = next(
        (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "downgrade"),
        None,
    )
    assert downgrade_fn is not None, "No downgrade() function found"

    # Collect all drop_table calls — must only reference 'tenants'
    for node in ast.walk(downgrade_fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "drop_table"
        ):
            if node.args:
                table_name = ast.literal_eval(node.args[0])
                assert table_name == "tenants", (
                    f"downgrade() must only drop 'tenants', found drop_table('{table_name}')"
                )

    # Collect all create_table calls — there must be none in downgrade
    for node in ast.walk(downgrade_fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "create_table"
        ):
            pytest.fail("downgrade() must not call create_table()")


def test_alembic_head_is_updated_to_new_revision() -> None:
    """Alembic ScriptDirectory must report a single head at '0006'."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    script_dir = ScriptDirectory.from_config(cfg)
    heads = script_dir.get_heads()
    assert len(heads) == 1, f"Expected exactly one Alembic head, got: {heads}"
    assert "0006" in heads, f"Expected '0006' as head, got: {heads}"
