"""Tests for Alembic baseline configuration (P0-A-02).

These tests verify the Alembic project structure is correctly wired without
requiring a live database connection.  The DB-level upgrade test uses a
pytest fixture that skips when psycopg cannot connect.
"""
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


def _get_script_dir() -> ScriptDirectory:
    cfg = Config(str(ALEMBIC_INI))
    return ScriptDirectory.from_config(cfg)


@pytest.fixture
def db_engine():
    """Provide the app engine, or skip the test if the DB is not reachable.

    Uses a 2-second psycopg connect_timeout so CI/local runs without Docker
    fail fast instead of hanging on the default TCP timeout.
    """
    import psycopg
    from app.config.settings import settings

    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
    except Exception:
        pytest.skip("DB not reachable - skipping live DB test")

    from app.db.session import engine
    return engine


def test_alembic_ini_exists():
    """alembic.ini must be present in backend/."""
    assert ALEMBIC_INI.exists(), "backend/alembic.ini not found"


def test_alembic_ini_is_ascii():
    """alembic.ini must be pure ASCII to avoid locale-encoding failures on
    Windows (cp932 / cp1252 environments)."""
    content_bytes = ALEMBIC_INI.read_bytes()
    non_ascii = [
        (i, b) for i, b in enumerate(content_bytes) if b > 127
    ]
    assert non_ascii == [], (
        f"Non-ASCII bytes found in alembic.ini: {non_ascii[:5]}"
    )


def test_alembic_script_location_resolves():
    """alembic/ directory must exist and contain env.py."""
    alembic_dir = BACKEND_DIR / "alembic"
    assert alembic_dir.is_dir(), "backend/alembic/ directory not found"
    assert (alembic_dir / "env.py").exists(), "backend/alembic/env.py not found"
    assert (alembic_dir / "script.py.mako").exists(), (
        "backend/alembic/script.py.mako not found"
    )


def test_alembic_baseline_revision_exists():
    """Baseline revision 0001 must be discoverable by ScriptDirectory."""
    script_dir = _get_script_dir()
    revisions = list(script_dir.walk_revisions())
    rev_ids = [r.revision for r in revisions]
    assert "0001" in rev_ids, (
        f"Baseline revision '0001' not found. Available: {rev_ids}"
    )


def test_alembic_baseline_is_root_revision():
    """Baseline revision must have no parent (it is the first migration)."""
    script_dir = _get_script_dir()
    baseline = script_dir.get_revision("0001")
    assert baseline is not None
    assert baseline.down_revision is None, (
        f"Expected no parent for 0001, got: {baseline.down_revision}"
    )


def test_alembic_head_is_baseline():
    """HEAD must resolve to the latest revision in the chain.

    Updated: 0010 (reason_codes) is now head;
    chain is 0001 -> 0002 (add_refresh_tokens) -> 0003 (routing_operation_extended_fields)
    -> 0004 (add_user_lifecycle_status) -> 0005 (add_plant_hierarchy)
    -> 0006 (add_tenant_lifecycle_anchor) -> 0007 (product_versions)
    -> 0008 (boms) -> 0009 (drop_station_claims) -> 0010 (reason_codes).
    This test validates the migration chain is linear and has a single head.
    """
    script_dir = _get_script_dir()
    heads = script_dir.get_heads()
    assert len(heads) == 1, f"Expected exactly one head, got: {heads}"
    assert "0010" in heads, f"Expected 0010 as head, got: {heads}"


def test_alembic_upgrade_head_live(db_engine):
    """When DB is reachable, upgrade head must succeed and stamp alembic_version."""
    from alembic import command
    from sqlalchemy import text

    cfg = Config(str(ALEMBIC_INI))
    command.upgrade(cfg, "head")

    with db_engine.connect() as conn:
        result = conn.execute(
            text("SELECT version_num FROM alembic_version")
        )
        rows = [r[0] for r in result]
    assert "0010" in rows, f"Expected 0010 in alembic_version, got: {rows}"

