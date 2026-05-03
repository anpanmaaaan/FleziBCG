"""Regression tests for init_db bootstrap guard (P0-A-01 / P0-A-03).

Verifies:
- Default ``init_db()`` does NOT call ``create_all()`` (P0-A-03 invariant).
- Default ``init_db()`` does NOT call the legacy SQL runner (P0-A-01 invariant).
- Default ``init_db()`` DOES call ``run_alembic_upgrade()`` (P0-A-01 requirement).
- ``bootstrap_schema=True`` calls ``create_all()`` exactly once (explicit path).
- ``_use_sql_runner=True`` calls legacy SQL runner and skips Alembic (explicit path).
"""

import pytest

import app.db.init_db as init_db_module


class _DummySessionContext:
    def __enter__(self):
        return object()

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def _reset_upgrade_flag(monkeypatch):
    """Reset the process-lifetime idempotency flag before each test."""
    monkeypatch.setattr(init_db_module, "_ALEMBIC_UPGRADE_RAN", False)


def _common_patches(monkeypatch, *, alembic_stub=None, sql_stub=None):
    """Apply common no-op patches to isolate init_db from external I/O."""
    monkeypatch.setattr(
        init_db_module, "run_alembic_upgrade", alembic_stub or (lambda: None)
    )
    monkeypatch.setattr(
        init_db_module, "_apply_sql_migrations", sql_stub or (lambda: None)
    )
    monkeypatch.setattr(init_db_module, "seed_rbac_core", lambda db: None)
    monkeypatch.setattr(init_db_module, "seed_approval_rules", lambda db: None)
    monkeypatch.setattr(init_db_module, "seed_demo_users", lambda db: None)
    monkeypatch.setattr(init_db_module, "seed_tenant_row", lambda db, **kw: None)
    monkeypatch.setattr(init_db_module, "SessionLocal", lambda: _DummySessionContext())


# ---------------------------------------------------------------------------
# create_all() guard (P0-A-03 invariant)
# ---------------------------------------------------------------------------


def test_init_db_default_does_not_call_create_all(monkeypatch):
    """Production/default init path must not invoke Base.metadata.create_all."""
    called = {"create_all": False}

    def _fail_create_all(*args, **kwargs):
        called["create_all"] = True
        raise AssertionError("create_all must not be called by default init_db")

    monkeypatch.setattr(
        init_db_module.Base.metadata,
        "create_all",
        _fail_create_all,
    )
    _common_patches(monkeypatch)

    init_db_module.init_db()

    assert called["create_all"] is False


def test_init_db_bootstrap_true_calls_create_all(monkeypatch):
    """Explicit local bootstrap path must invoke create_all exactly once."""
    called = {"count": 0}

    def _mark_create_all(*args, **kwargs):
        called["count"] += 1

    monkeypatch.setattr(
        init_db_module.Base.metadata,
        "create_all",
        _mark_create_all,
    )
    _common_patches(monkeypatch)

    init_db_module.init_db(bootstrap_schema=True)

    assert called["count"] == 1


# ---------------------------------------------------------------------------
# SQL runner retirement (P0-A-01 invariant)
# ---------------------------------------------------------------------------


def test_init_db_default_does_not_call_sql_runner(monkeypatch):
    """INVARIANT P0-A-01: Default init_db() must not call the legacy SQL runner.

    The custom _apply_sql_migrations() must be retired from the production
    startup path.  Calling it on every startup is the P0-BLOCKER identified
    in GAP-01.
    """
    called = {"sql_runner": False}

    def _fail_sql_runner():
        called["sql_runner"] = True
        raise AssertionError(
            "_apply_sql_migrations must not be called by default init_db"
        )

    _common_patches(monkeypatch, sql_stub=_fail_sql_runner)

    init_db_module.init_db()

    assert called["sql_runner"] is False


def test_init_db_default_calls_alembic_upgrade(monkeypatch):
    """REQUIREMENT P0-A-01: Default init_db() must call run_alembic_upgrade().

    Alembic is the canonical migration driver.  The production startup path
    must invoke it so the schema is always at the Alembic head.
    """
    called = {"alembic": False}

    def _record_alembic():
        called["alembic"] = True

    _common_patches(monkeypatch, alembic_stub=_record_alembic)

    init_db_module.init_db()

    assert called["alembic"] is True


def test_init_db_sql_runner_flag_calls_sql_runner(monkeypatch):
    """Dev/test bootstrap flag must enable the legacy SQL runner and skip Alembic."""
    called = {"sql_runner": False, "alembic": False}

    def _record_sql():
        called["sql_runner"] = True

    def _fail_alembic():
        called["alembic"] = True
        raise AssertionError(
            "run_alembic_upgrade must not be called when _use_sql_runner=True"
        )

    _common_patches(monkeypatch, alembic_stub=_fail_alembic, sql_stub=_record_sql)

    init_db_module.init_db(_use_sql_runner=True)

    assert called["sql_runner"] is True
    assert called["alembic"] is False
