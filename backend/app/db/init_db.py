from pathlib import Path

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.db.session import SessionLocal

# INVARIANT: Every model file must be imported here so that SQLAlchemy
# registers the table with Base.metadata before optional local bootstrap
# create_all() runs. Forgetting an import causes a silent missing-table bug.
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
from app.models.station_claim import OperationClaim, OperationClaimAuditLog  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.security_event import SecurityEventLog  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.routing import Routing, RoutingOperation  # noqa: F401
from app.models.resource_requirement import ResourceRequirement  # noqa: F401
from app.security.rbac import seed_rbac_core
from app.services.approval_service import seed_approval_rules
from app.services.user_service import seed_demo_users


def _apply_sql_migrations() -> None:
    migrations_dir = Path(__file__).resolve().parents[2] / "scripts" / "migrations"
    if not migrations_dir.exists():
        return

    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        return

    with engine.begin() as conn:
        for migration_file in migration_files:
            sql_text = migration_file.read_text(encoding="utf-8")
            statements = [
                statement.strip()
                for statement in sql_text.split(";")
                if statement.strip()
            ]
            for statement in statements:
                conn.execute(text(statement))


def init_db(*, bootstrap_schema: bool = False) -> None:
    # SAFETY: Production startup must not call create_all() implicitly.
    # bootstrap_schema=True is for explicit local bootstrap workflows only.
    if bootstrap_schema:
        Base.metadata.create_all(bind=engine)

    _apply_sql_migrations()
    # INTENT: Seed order matters — RBAC roles/permissions first, then approval
    # rules (which reference role codes), then demo users (which reference roles).
    with SessionLocal() as db:
        seed_rbac_core(db)
        seed_approval_rules(db)
        seed_demo_users(db)


if __name__ == "__main__":
    # CLI/local bootstrap path: explicit schema bootstrap + seed.
    init_db(bootstrap_schema=True)
