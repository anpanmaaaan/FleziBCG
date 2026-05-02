#!/usr/bin/env python3
"""Seed / upsert the default Tenant row for dev and CI environments.

PURPOSE: After P0-A-02C strict tenant existence enforcement, any authenticated
request requires a Tenant row for the tenant_id used in the JWT. This script
creates or updates that row so dev/CI environments can authenticate.

INVARIANTS:
- Idempotent: safe to run multiple times; existing rows are updated in-place.
- Does NOT create users, sessions, roles, plants, or any other entities.
- Does NOT run automatically on production startup.
- Production guard: refuses unless FLEZIBCG_ALLOW_PRODUCTION_SEED=true when
  settings.app_env == "production".

USAGE (dev):
    cd backend
    python scripts/seed_default_tenant.py

USAGE (CI — after alembic upgrade head):
    cd backend
    python scripts/seed_default_tenant.py

ENV VARS (optional overrides):
    FLEZIBCG_SEED_TENANT_ID   — default: "default"
    FLEZIBCG_SEED_TENANT_CODE — default: "DEFAULT"
    FLEZIBCG_SEED_TENANT_NAME — default: "Default Tenant"
    FLEZIBCG_ALLOW_PRODUCTION_SEED — set to "true" to allow production seeding
"""
from __future__ import annotations

import os
import sys

from sqlalchemy.orm import Session

from app.models.tenant import TENANT_STATUS_ACTIVE, Tenant


# ---------------------------------------------------------------------------
# Core seed function — pure, no session management, no production guard.
# Suitable for direct use in tests with an injected test DB session.
# ---------------------------------------------------------------------------


def seed_tenant_row(
    db: Session,
    *,
    tenant_id: str,
    tenant_code: str,
    tenant_name: str,
) -> Tenant:
    """Upsert the given Tenant row. Returns the Tenant instance.

    INVARIANT: idempotent — if the row already exists, fields are updated to
    the supplied values and the existing row is returned after commit.
    """
    from sqlalchemy import select

    tenant = db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))
    if tenant is None:
        tenant = Tenant(
            tenant_id=tenant_id,
            tenant_code=tenant_code,
            tenant_name=tenant_name,
            lifecycle_status=TENANT_STATUS_ACTIVE,
            is_active=True,
        )
        db.add(tenant)
    else:
        tenant.tenant_code = tenant_code
        tenant.tenant_name = tenant_name
        tenant.lifecycle_status = TENANT_STATUS_ACTIVE
        tenant.is_active = True
    db.commit()
    db.refresh(tenant)
    return tenant


# ---------------------------------------------------------------------------
# Default-value resolver — reads from env vars with documented defaults.
# ---------------------------------------------------------------------------


def _resolve_tenant_values() -> tuple[str, str, str]:
    """Return (tenant_id, tenant_code, tenant_name) from env vars or defaults."""
    tenant_id = os.environ.get("FLEZIBCG_SEED_TENANT_ID", "default")
    tenant_code = os.environ.get("FLEZIBCG_SEED_TENANT_CODE", "DEFAULT")
    tenant_name = os.environ.get("FLEZIBCG_SEED_TENANT_NAME", "Default Tenant")
    return tenant_id, tenant_code, tenant_name


# ---------------------------------------------------------------------------
# Production guard — call before opening a real DB session.
# ---------------------------------------------------------------------------


def check_production_guard(app_env: str, allow_production_seed: str) -> None:
    """Raise RuntimeError if app_env is production and override is not set.

    INVARIANT: Production seed requires explicit opt-in via
    FLEZIBCG_ALLOW_PRODUCTION_SEED=true to prevent accidental execution.
    """
    if app_env.lower() == "production" and allow_production_seed.lower() != "true":
        raise RuntimeError(
            "seed_default_tenant refuses to run in production. "
            "Set FLEZIBCG_ALLOW_PRODUCTION_SEED=true to override."
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # Import here so the module remains importable in test environments that
    # may not have a live DATABASE_URL configured.
    from app.config.settings import settings
    from app.db.session import SessionLocal

    allow_prod = os.environ.get("FLEZIBCG_ALLOW_PRODUCTION_SEED", "")
    try:
        check_production_guard(settings.app_env, allow_prod)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    tenant_id, tenant_code, tenant_name = _resolve_tenant_values()

    db = SessionLocal()
    try:
        tenant = seed_tenant_row(
            db,
            tenant_id=tenant_id,
            tenant_code=tenant_code,
            tenant_name=tenant_name,
        )
        print(
            f"OK  tenant_id={tenant.tenant_id!r}  "
            f"tenant_code={tenant.tenant_code!r}  "
            f"lifecycle_status={tenant.lifecycle_status}  "
            f"is_active={tenant.is_active}"
        )
    finally:
        db.close()
