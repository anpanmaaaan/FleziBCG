"""Tests for P0-A-02D: Tenant Seed / Bootstrap for Dev + CI.

INVARIANTS COVERED:
  1. Seed creates an ACTIVE Tenant row (is_active=True, lifecycle_status=ACTIVE).
  2. Seed is idempotent — running twice produces exactly one row, unchanged.
  3. Seed respects custom env vars for tenant_id/code/name.
  4. Seed does NOT create users, sessions, or roles.
  5. Production guard raises when app_env=production and override is not set.
  6. Production guard allows when FLEZIBCG_ALLOW_PRODUCTION_SEED=true.
  7. Strict tenant enforcement still rejects a missing tenant row (regression).
  8. Strict tenant enforcement allows a seeded ACTIVE tenant (integration check).
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.tenant import TENANT_STATUS_ACTIVE, Tenant
from scripts.seed_default_tenant import (
    check_production_guard,
    seed_tenant_row,
    _resolve_tenant_values,
)


# ---------------------------------------------------------------------------
# Test DB helpers
# ---------------------------------------------------------------------------


def _make_db():
    """SQLite in-memory DB with only the tenants table."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Tenant.__table__.create(bind=engine, checkfirst=True)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return factory


# ---------------------------------------------------------------------------
# Seed correctness tests
# ---------------------------------------------------------------------------


def test_seed_default_tenant_creates_active_tenant():
    """Seed creates a row with ACTIVE status and is_active=True."""
    factory = _make_db()
    db = factory()
    try:
        tenant = seed_tenant_row(
            db,
            tenant_id="default",
            tenant_code="DEFAULT",
            tenant_name="Default Tenant",
        )
        assert tenant.tenant_id == "default"
        assert tenant.tenant_code == "DEFAULT"
        assert tenant.tenant_name == "Default Tenant"
        assert tenant.lifecycle_status == TENANT_STATUS_ACTIVE
        assert tenant.is_active is True
        assert tenant.is_lifecycle_active is True
    finally:
        db.close()


def test_seed_default_tenant_is_idempotent():
    """Running seed twice produces exactly one row with the same values."""
    factory = _make_db()
    db = factory()
    try:
        seed_tenant_row(
            db,
            tenant_id="default",
            tenant_code="DEFAULT",
            tenant_name="Default Tenant",
        )
        seed_tenant_row(
            db,
            tenant_id="default",
            tenant_code="DEFAULT",
            tenant_name="Default Tenant",
        )
        from sqlalchemy import select, func

        count = db.scalar(
            select(func.count()).select_from(Tenant).where(Tenant.tenant_id == "default")
        )
        assert count == 1
    finally:
        db.close()


def test_seed_default_tenant_updates_existing_row():
    """Seed updates fields on an existing row (upsert, not skip)."""
    factory = _make_db()
    db = factory()
    try:
        # First seed with different name
        seed_tenant_row(
            db,
            tenant_id="default",
            tenant_code="OLD",
            tenant_name="Old Name",
        )
        # Second seed with updated values
        tenant = seed_tenant_row(
            db,
            tenant_id="default",
            tenant_code="DEFAULT",
            tenant_name="Default Tenant",
        )
        assert tenant.tenant_code == "DEFAULT"
        assert tenant.tenant_name == "Default Tenant"
        assert tenant.lifecycle_status == TENANT_STATUS_ACTIVE
        assert tenant.is_active is True
    finally:
        db.close()


def test_seed_default_tenant_uses_custom_env_values_if_supported(monkeypatch):
    """_resolve_tenant_values reads env vars when set."""
    monkeypatch.setenv("FLEZIBCG_SEED_TENANT_ID", "my-tenant")
    monkeypatch.setenv("FLEZIBCG_SEED_TENANT_CODE", "MY")
    monkeypatch.setenv("FLEZIBCG_SEED_TENANT_NAME", "My Tenant")
    tenant_id, tenant_code, tenant_name = _resolve_tenant_values()
    assert tenant_id == "my-tenant"
    assert tenant_code == "MY"
    assert tenant_name == "My Tenant"


def test_seed_default_tenant_uses_defaults_when_env_not_set(monkeypatch):
    """_resolve_tenant_values falls back to documented defaults."""
    monkeypatch.delenv("FLEZIBCG_SEED_TENANT_ID", raising=False)
    monkeypatch.delenv("FLEZIBCG_SEED_TENANT_CODE", raising=False)
    monkeypatch.delenv("FLEZIBCG_SEED_TENANT_NAME", raising=False)
    tenant_id, tenant_code, tenant_name = _resolve_tenant_values()
    assert tenant_id == "default"
    assert tenant_code == "DEFAULT"
    assert tenant_name == "Default Tenant"


def test_seed_default_tenant_does_not_create_users_sessions_or_roles():
    """Seed only creates the Tenant row — no other tables are touched."""
    factory = _make_db()
    db = factory()
    try:
        seed_tenant_row(
            db,
            tenant_id="default",
            tenant_code="DEFAULT",
            tenant_name="Default Tenant",
        )
        # Only the tenants table was created in this in-memory DB.
        # Verify no attempt was made to write to users/sessions/roles tables
        # (they don't exist — if seed tried to use them, it would have raised).
        insp = inspect(db.get_bind())
        table_names = insp.get_table_names()
        assert "tenants" in table_names
        # users/sessions/roles are not present in this isolated DB
        assert "users" not in table_names
        assert "sessions" not in table_names
        assert "roles" not in table_names
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Production guard tests
# ---------------------------------------------------------------------------


def test_seed_default_tenant_refuses_production_without_explicit_override():
    """Production guard raises when app_env=production and override is unset."""
    with pytest.raises(RuntimeError, match="refuses to run in production"):
        check_production_guard("production", "")


def test_seed_default_tenant_refuses_production_with_wrong_override():
    """Production guard raises when override is not exactly 'true'."""
    with pytest.raises(RuntimeError, match="refuses to run in production"):
        check_production_guard("production", "yes")


def test_seed_default_tenant_allows_production_with_explicit_override():
    """Production guard passes when FLEZIBCG_ALLOW_PRODUCTION_SEED=true."""
    # Should not raise
    check_production_guard("production", "true")


def test_seed_default_tenant_allows_dev_environment():
    """Production guard is not triggered for dev/test environments."""
    check_production_guard("dev", "")
    check_production_guard("test", "")
    check_production_guard("staging", "")


# ---------------------------------------------------------------------------
# Enforcement compatibility regression tests
# ---------------------------------------------------------------------------


def test_strict_tenant_enforcement_still_rejects_missing_tenant():
    """is_tenant_lifecycle_active returns False when no row exists (Policy A)."""
    from app.repositories.tenant_repository import is_tenant_lifecycle_active

    factory = _make_db()
    db = factory()
    try:
        result = is_tenant_lifecycle_active(db, "default")
        assert result is False
    finally:
        db.close()


def test_strict_tenant_enforcement_allows_seeded_active_tenant():
    """is_tenant_lifecycle_active returns True after seed creates the row."""
    from app.repositories.tenant_repository import is_tenant_lifecycle_active

    factory = _make_db()
    db = factory()
    try:
        seed_tenant_row(
            db,
            tenant_id="default",
            tenant_code="DEFAULT",
            tenant_name="Default Tenant",
        )
        result = is_tenant_lifecycle_active(db, "default")
        assert result is True
    finally:
        db.close()
