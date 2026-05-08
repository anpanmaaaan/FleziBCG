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
from app.models.product_version_bom_binding import ProductVersionBomBinding  # noqa: F401
from app.models.routing import Routing, RoutingOperation  # noqa: F401
from app.models.resource_requirement import ResourceRequirement  # noqa: F401
from app.models.quality import (  # noqa: F401
    QualityMeasurementRecord,  # noqa: F401
    QualityMeasurementValue,  # noqa: F401
    QualityHold,  # noqa: F401
    QualityDispositionDecision,  # noqa: F401
)
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

import logging as _logging

_log = _logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Alembic live migration driver
# ---------------------------------------------------------------------------

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_ALEMBIC_INI = _BACKEND_DIR / "alembic.ini"

_ALEMBIC_UPGRADE_RAN = False
_ALEMBIC_UPGRADE_LOCK = Lock()


def _repair_schema_drift() -> None:
    """Apply missing DDL that Alembic skipped due to a create_all stamping bug.

    BACKGROUND: An earlier startup path called ``create_all(checkfirst=True)``
    and then immediately stamped at Alembic ``head``.  ``create_all`` skips
    tables that already exist — it does NOT add new columns to existing tables.
    This leaves the DB missing columns that were added in ALTER-based Alembic
    revisions (0004, 0011, 0012) whose parent tables were created by the legacy
    SQL scripts before Alembic took over.

    This function detects and applies only those known missing columns.  Every
    operation is idempotent (checks column presence before acting).  It is
    safe to call on any DB state and is a no-op once the columns are present.

    Migrations repaired here (in chronological order):
      0004 — users.lifecycle_status (VARCHAR 32, NOT NULL after backfill)
      0011 — approval_requests governed_resource_* columns (nullable)
      0012 — approval_rules scope applicability columns (nullable)
    """
    from sqlalchemy import inspect as sa_inspect, text as sa_text

    with engine.begin() as conn:
        insp = sa_inspect(conn)

        # ---- 0004: users.lifecycle_status --------------------------------
        user_cols = {c["name"] for c in insp.get_columns("users")}
        if "lifecycle_status" not in user_cols:
            _log.warning("schema-repair: adding users.lifecycle_status (0004 drift)")
            conn.execute(sa_text(
                "ALTER TABLE users ADD COLUMN lifecycle_status VARCHAR(32)"
            ))
            conn.execute(sa_text(
                "UPDATE users SET lifecycle_status = 'ACTIVE' WHERE is_active = true"
            ))
            conn.execute(sa_text(
                "UPDATE users SET lifecycle_status = 'DISABLED' WHERE is_active = false"
            ))
            conn.execute(sa_text(
                "UPDATE users SET lifecycle_status = 'ACTIVE' WHERE lifecycle_status IS NULL"
            ))
            conn.execute(sa_text(
                "ALTER TABLE users ALTER COLUMN lifecycle_status SET NOT NULL"
            ))
            conn.execute(sa_text(
                "CREATE INDEX IF NOT EXISTS ix_users_lifecycle_status"
                " ON users (lifecycle_status)"
            ))

        # ---- 0011: approval_requests governed_resource_* columns ----------
        ar_cols = {c["name"] for c in insp.get_columns("approval_requests")}
        _GOVERNED_REQUEST_COLS: list[tuple[str, str]] = [
            ("governed_resource_type", "VARCHAR(64)"),
            ("governed_resource_id", "VARCHAR(128)"),
            ("governed_resource_display_ref", "VARCHAR(256)"),
            ("governed_resource_tenant_id", "VARCHAR(64)"),
            ("governed_resource_scope_ref", "VARCHAR(256)"),
            ("governed_action_type", "VARCHAR(64)"),
        ]
        for col, dtype in _GOVERNED_REQUEST_COLS:
            if col not in ar_cols:
                _log.warning(
                    "schema-repair: adding approval_requests.%s (0011 drift)", col
                )
                conn.execute(sa_text(
                    f"ALTER TABLE approval_requests ADD COLUMN {col} {dtype}"
                ))

        # ---- 0012: approval_rules scope applicability columns -------------
        aru_cols = {c["name"] for c in insp.get_columns("approval_rules")}
        _SCOPE_RULE_COLS: list[tuple[str, str]] = [
            ("governed_action_type", "VARCHAR(64)"),
            ("governed_resource_type", "VARCHAR(64)"),
            ("scope_ref", "VARCHAR(256)"),
            ("scope_type", "VARCHAR(32)"),
            ("priority", "INTEGER"),
            ("effective_from", "TIMESTAMPTZ"),
            ("effective_to", "TIMESTAMPTZ"),
        ]
        for col, dtype in _SCOPE_RULE_COLS:
            if col not in aru_cols:
                _log.warning(
                    "schema-repair: adding approval_rules.%s (0012 drift)", col
                )
                conn.execute(sa_text(
                    f"ALTER TABLE approval_rules ADD COLUMN {col} {dtype}"
                ))


def _bootstrap_state() -> str:
    """Classify the DB state to choose the correct startup migration path.

    Returns one of three values:

    ``"alembic"``
        ``alembic_version`` table exists and has at least one row.  The DB has
        been managed by Alembic before.  Normal ``upgrade head`` is sufficient.

    ``"legacy"``
        No ``alembic_version`` row/table, but other application tables already
        exist.  This happens when:
          - the DB was provisioned by the legacy SQL scripts
            (``scripts/migrations/``) without ever stamping Alembic, OR
          - a previous startup ran ``Base.metadata.create_all()`` on an *older*
            schema version (missing later ALTER-added columns) and the volume
            was reused without wiping it.

        In this case the correct path is to stamp at ``0001`` (the no-op
        baseline that corresponds to the legacy SQL schema) and then run
        ``upgrade head`` so each ALTER-based revision adds the missing columns
        to the already-existing tables.

    ``"fresh"``
        No ``alembic_version`` AND no application tables at all.  Truly clean
        Docker volume.  Use ``Base.metadata.create_all()`` + ``stamp head`` so
        that the full current schema is created in one pass and Alembic sees no
        pending migrations.

    WHY this matters:
        The 0001 Alembic baseline is an *intentional no-op* — it was designed
        to be stamped against a DB that already had its schema.  Running the
        chain from scratch on a clean DB fails on ALTER-based revisions (e.g.
        0003 adds columns to ``routing_operations``, which was never created by
        Alembic itself).  Detecting the state correctly routes to the one safe
        path for each scenario.
    """
    from sqlalchemy import inspect as sa_inspect, text as sa_text

    with engine.connect() as conn:
        insp = sa_inspect(conn)
        tables = set(insp.get_table_names())

        if "alembic_version" in tables:
            result = conn.execute(sa_text("SELECT COUNT(*) FROM alembic_version"))
            if result.scalar() > 0:
                return "alembic"

        # No valid alembic stamp — check whether any application tables exist.
        # Use approval_rules as the sentinel: it is created by the legacy SQL
        # scripts but never by an Alembic CREATE TABLE migration, so its
        # presence reliably indicates a pre-Alembic or mismatched-schema state.
        if "approval_rules" in tables:
            return "legacy"

        return "fresh"


def run_alembic_upgrade() -> None:
    """Run ``alembic upgrade head`` programmatically.

    INVARIANT: This is the canonical production startup migration path.
    It is idempotent — running it against an already-current schema is a no-op.
    It respects the migration history recorded in ``alembic_version``.

    Bootstrap paths (see ``_bootstrap_state`` for full rationale):

    - ``"fresh"``: ``create_all()`` builds the complete current schema, then
      ``stamp head`` registers it.  ``upgrade head`` is then a no-op.
    - ``"legacy"``: stamp at ``0001`` (the no-op baseline) so Alembic knows the
      legacy SQL schema is already in place, then ``upgrade head`` applies every
      ALTER/CREATE migration from 0002 onwards.
    - ``"alembic"``: ``upgrade head`` only (normal path).

    SAFETY: Guarded by a module-level lock and a flag so that multiple
    threads/workers on the same process only run it once per process lifetime.
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
        state = _bootstrap_state()

        if state == "fresh":
            # Truly clean volume: build the full schema from ORM models in one
            # pass, then stamp at head so upgrade below is a no-op.
            Base.metadata.create_all(bind=engine)
            command.stamp(cfg, "head")
        elif state == "legacy":
            # Legacy SQL tables already exist without an Alembic stamp.
            # Stamp at 0001 (the no-op baseline) so Alembic knows the base
            # schema is present, then let upgrade head add the missing columns.
            command.stamp(cfg, "0001")

        command.upgrade(cfg, "head")

        # SCHEMA DRIFT REPAIR: idempotent guard for columns that were missed
        # by an erroneous create_all+stamp path on a partially-provisioned DB.
        # No-op once the columns are present.
        _repair_schema_drift()

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
        seed_tenant_row(
            db, tenant_id="default", tenant_code="DEFAULT", tenant_name="Default Tenant"
        )
        seed_rbac_core(db)
        seed_approval_rules(db)
        seed_demo_users(db)


if __name__ == "__main__":
    # CLI/local bootstrap path: explicit schema bootstrap + seed.
    init_db(bootstrap_schema=True)
