"""Regression tests for init_db bootstrap guard (P0-A-03)."""

import app.db.init_db as init_db_module


class _DummySessionContext:
    def __enter__(self):
        return object()

    def __exit__(self, exc_type, exc, tb):
        return False


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
    monkeypatch.setattr(init_db_module, "_apply_sql_migrations", lambda: None)
    monkeypatch.setattr(init_db_module, "seed_rbac_core", lambda db: None)
    monkeypatch.setattr(init_db_module, "seed_approval_rules", lambda db: None)
    monkeypatch.setattr(init_db_module, "seed_demo_users", lambda db: None)
    monkeypatch.setattr(init_db_module, "SessionLocal", lambda: _DummySessionContext())

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
    monkeypatch.setattr(init_db_module, "_apply_sql_migrations", lambda: None)
    monkeypatch.setattr(init_db_module, "seed_rbac_core", lambda db: None)
    monkeypatch.setattr(init_db_module, "seed_approval_rules", lambda db: None)
    monkeypatch.setattr(init_db_module, "seed_demo_users", lambda db: None)
    monkeypatch.setattr(init_db_module, "SessionLocal", lambda: _DummySessionContext())

    init_db_module.init_db(bootstrap_schema=True)

    assert called["count"] == 1
