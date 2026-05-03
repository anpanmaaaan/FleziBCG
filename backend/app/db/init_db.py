from pathlib import Path
from threading import Lock

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.db.session import SessionLocal

# INVARIANT: Every model file must be imported here so that SQLAlchemy
# registers the table with Base.metadata before optional local bootstrap
# create_all() runs. Forgetting an import causes a silent missing-table bug.
#
# WHY: alembic env.py also imports this module (import app.db.init_db as
# _models) so that all ORM classes are registered with Base.metadata before
# autogenerate/upgrade runs. This import must remain side-effect-only — no
# DB mutation at import time.
from app.models.master import ProductionOrder, WorkOrder, Operation  # noqa: F401
from app.models.execution import ExecutionEvent  # noqa: F401
from app.models.downtime_reason import DowntimeReason  # noqa: F401
from app.models.rbac import (  # noqa: F401
    Role,  # noqa: F401
    Permission,  # noqa: F401
    RolePermission,  # noqa: F401
    UserRole,  # noqa: F401
    RoleScope,  # noqa: F401
    Scope,  # noqa: F401
    UserRoleAssignment,  # noqa: F401
)
from app.models.impersonation import ImpersonationSession, ImpersonationAuditLog  # noqa: F401
from app.models.approval import (  # noqa: F401
    ApprovalRule,  # noqa: F401
    ApprovalRequest,  # noqa: F401
    ApprovalDecision,  # noqa: F401
    ApprovalAuditLog,  # noqa: F401
)
from app.models.session import Session, SessionAuditLog  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.security_event import SecurityEventLog  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.product_version import ProductVersion  # noqa: F401
from app.models.reason_code import ReasonCode  # noqa: F401
from app.models.bom import Bom, BomItem  # noqa: F401
from app.models.routing import Routing, RoutingOperation  # noqa: F401
from app.models.resource_requirement import ResourceRequirement  # noqa: F401
from app.models.station_session import StationSession  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.plant_hierarchy import (  # noqa: F401
    Plant,  # noqa: F401
    Area,  # noqa: F401
    Line,  # noqa: F401
    Station,  # noqa: F401
    Equipment,  # noqa: F401
)
from app.models.tenant import Tenant  # noqa: F401
from app.security.rbac import seed_rbac_core
from app.services.approval_service import seed_approval_rules
from app.services.user_service import seed_demo_users
from scripts.seed_default_tenant import seed_tenant_row

# ---------------------------------------------------------------------------
# Alembic live migration driver
# ---------------------------------------------------------------------------

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ALEMBIC_INI = _BACKEND_DIR / "alembic.ini"

_ALEMBIC_UPGRADE_RAN = False
_ALEMBIC_UPGRADE_LOCK = Lock()


def run_alembic_upgrade() -> None:
    """Run ``alembic upgrade head`` programmatically.

    INVARIANT: This is the canonical production startup migration path.
    It is idempotent — running it against an already-current schema is a no-op.
    It respects the migration history recorded in ``alembic_version``.

    SAFETY: Guarded by a module-level lock and a flag so that multiple
    threads/workers on the same process only run it once per process lifetime.
    Cross-process serialization is handled by Alembic's own locking if
    the DB supports advisory locks (PostgreSQL).
    """
    global _ALEMBIC_UPGRADE_RAN

    if _ALEMBIC_UPGRADE_RAN:
        return

    with _ALEMBIC_UPGRADE_LOCK:
        if _ALEMBIC_UPGRADE_RAN:
            return

        from alembic import command
        from alembic.config import Config

        cfg = Config(str(_ALEMBIC_INI))
        command.upgrade(cfg, "head")
        _ALEMBIC_UPGRADE_RAN = True


# ---------------------------------------------------------------------------
# Legacy / dev-bootstrap SQL runner  (NOT called on production startup)
# ---------------------------------------------------------------------------

_MIGRATIONS_APPLIED = False
_MIGRATION_APPLY_LOCK = Lock()
_MIGRATION_ADVISORY_LOCK_KEY = 84082026


def _apply_sql_migrations() -> None:
    """Apply raw SQL migration files from ``backend/scripts/migrations/``.

    DEPRECATED PRODUCTION PATH — do not call from production startup.
    This function is retained as a dev/test/CLI bootstrap utility only.
    The canonical migration path is ``run_alembic_upgrade()``.

    Calling this from production code is a governance violation.
    """
    global _MIGRATIONS_APPLIED

    if _MIGRATIONS_APPLIED:
        return

    with _MIGRATION_APPLY_LOCK:
        if _MIGRATIONS_APPLIED:
            return

        migrations_dir = Path(__file__).resolve().parents[2] / "scripts" / "migrations"
        if not migrations_dir.exists():
            _MIGRATIONS_APPLIED = True
            return

        migration_files = sorted(migrations_dir.glob("*.sql"))
        if not migration_files:
            _MIGRATIONS_APPLIED = True
            return

        with engine.begin() as conn:
            locked = False
            if engine.dialect.name == "postgresql":
                # Serialize migration DDL across processes in shared test DB usage.
                conn.execute(
                    text("SELECT pg_advisory_lock(:lock_key)"),
                    {"lock_key": _MIGRATION_ADVISORY_LOCK_KEY},
                )
                locked = True
            try:
                for migration_file in migration_files:
                    sql_text = migration_file.read_text(encoding="utf-8")
                    statements = [
                        statement.strip()
                        for statement in sql_text.split(";")
                        if statement.strip()
                    ]
                    for statement in statements:
                        conn.execute(text(statement))
            finally:
                if locked:
                    conn.execute(
                        text("SELECT pg_advisory_unlock(:lock_key)"),
                        {"lock_key": _MIGRATION_ADVISORY_LOCK_KEY},
                    )

        _MIGRATIONS_APPLIED = True


def init_db(*, bootstrap_schema: bool = False, _use_sql_runner: bool = False) -> None:
    """Initialize the database for production or dev/test startup.

    Production path (default):
        1. ``run_alembic_upgrade()`` — brings schema to Alembic head (idempotent).
        2. Seed RBAC, approval rules, demo users.
        ``create_all()`` and the legacy SQL runner are NOT invoked.

    Dev/local bootstrap path (explicit only):
        Pass ``bootstrap_schema=True`` to call ``Base.metadata.create_all()``
        before running seeds.  Intended for local dev when no Alembic-managed
        DB exists yet.

        Pass ``_use_sql_runner=True`` (dev/test CLI only) to additionally run
        the legacy SQL migration files.  This flag must never be enabled in
        production or CI test runs.

    INVARIANT: The default call ``init_db()`` must never call ``create_all()``
    or ``_apply_sql_migrations()``.
    """
    # SAFETY: create_all() is for explicit local bootstrap only.
    if bootstrap_schema:
        Base.metadata.create_all(bind=engine)

    # INVARIANT: Legacy SQL runner is dev/test only — never called in default
    # production startup.
    if _use_sql_runner:
        _apply_sql_migrations()
    else:
        # CANONICAL PRODUCTION PATH: Alembic manages all schema changes.
        run_alembic_upgrade()

    # INTENT: Seed order matters — RBAC roles/permissions first, then approval
    # rules (which reference role codes), then demo users (which reference roles).
    # Tenant row is seeded first so all subsequent auth checks can pass.
    with SessionLocal() as db:
        seed_tenant_row(db, tenant_id="default", tenant_code="DEFAULT", tenant_name="Default Tenant")
        seed_rbac_core(db)
        seed_approval_rules(db)
        seed_demo_users(db)


if __name__ == "__main__":
    # CLI/local bootstrap path: explicit schema bootstrap + seed.
    init_db(bootstrap_schema=True)
