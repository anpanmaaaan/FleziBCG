from pathlib import Path

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.db.session import SessionLocal

# ✅ Import ALL models here
from app.models.master import ProductionOrder, WorkOrder, Operation
from app.models.execution import ExecutionEvent
from app.models.rbac import Role, Permission, RolePermission, UserRole, RoleScope, Scope, UserRoleAssignment
from app.models.impersonation import ImpersonationSession, ImpersonationAuditLog
from app.models.approval import ApprovalRule, ApprovalRequest, ApprovalDecision, ApprovalAuditLog
from app.models.session import Session, SessionAuditLog
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.models.user import User
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
            statements = [statement.strip() for statement in sql_text.split(";") if statement.strip()]
            for statement in statements:
                conn.execute(text(statement))

def init_db():
    _apply_sql_migrations()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_rbac_core(db)
        seed_approval_rules(db)
        seed_demo_users(db)


if __name__ == "__main__":
    init_db()