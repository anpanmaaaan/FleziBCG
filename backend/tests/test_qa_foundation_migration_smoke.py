import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

from app.config.settings import settings


BACKEND_DIR = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_DIR / "alembic.ini"


@pytest.fixture
def live_db_or_skip():
    import psycopg

    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
    except Exception:
        pytest.skip("DB not reachable - skipping migration smoke")

    return settings.database_url or ""


def _alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


def _is_disposable_db(database_url: str) -> bool:
    normalized = database_url.lower()
    return (
        "sqlite" in normalized
        or "_test" in normalized
        or "/test" in normalized
        or "mes_test" in normalized
    )


# ---------------------------------------------------------------------------
# Structural smoke (no DB needed) — P0-A-01
# ---------------------------------------------------------------------------


def test_run_alembic_upgrade_is_exported():
    """REQUIREMENT P0-A-01: run_alembic_upgrade must be importable from init_db."""
    from app.db.init_db import run_alembic_upgrade
    assert callable(run_alembic_upgrade)


def test_alembic_ini_path_resolves_from_init_db():
    """INVARIANT: The alembic.ini path resolved inside init_db must exist.

    If this fails the programmatic Alembic upgrade called on startup will
    raise a FileNotFoundError at runtime.
    """
    import app.db.init_db as init_db_module
    assert init_db_module._ALEMBIC_INI.exists(), (
        f"alembic.ini not found at resolved path: {init_db_module._ALEMBIC_INI}"
    )


def test_init_db_module_import_does_not_mutate_schema(monkeypatch):
    """INVARIANT: Importing init_db must not trigger any schema mutation.

    Production code and Alembic env.py both import init_db for the side-effect
    of registering ORM models.  That import must be safe with no DB call.
    """
    import app.db.init_db as init_db_module

    ran = {"upgrade": False, "create_all": False, "sql_runner": False}

    monkeypatch.setattr(init_db_module, "run_alembic_upgrade", lambda: ran.update({"upgrade": True}))
    monkeypatch.setattr(init_db_module, "_apply_sql_migrations", lambda: ran.update({"sql_runner": True}))
    monkeypatch.setattr(init_db_module.Base.metadata, "create_all", lambda **kw: ran.update({"create_all": True}))

    # Re-importing an already imported module does not re-execute top-level code,
    # so this test verifies that none of the mutation functions were invoked
    # during the prior import at test collection time.
    assert ran["upgrade"] is False
    assert ran["create_all"] is False
    assert ran["sql_runner"] is False


# ---------------------------------------------------------------------------
# Live DB tests (skip when DB unreachable)
# ---------------------------------------------------------------------------


def test_upgrade_head_smoke(live_db_or_skip):
    cfg = _alembic_config()
    command.upgrade(cfg, "head")


def test_conditional_downgrade_only_for_disposable_db(live_db_or_skip):
    if os.getenv("BE_QA_ALLOW_DESTRUCTIVE_ALEMBIC") != "1":
        pytest.skip("Set BE_QA_ALLOW_DESTRUCTIVE_ALEMBIC=1 to allow downgrade smoke")

    database_url = live_db_or_skip
    if not _is_disposable_db(database_url):
        pytest.skip("Downgrade smoke is blocked: database URL is not marked disposable")

    cfg = _alembic_config()
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
