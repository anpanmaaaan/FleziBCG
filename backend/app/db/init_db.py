from app.db.base import Base
from app.db.session import engine
from app.db.session import SessionLocal

# ✅ Import ALL models here
from app.models.master import ProductionOrder, WorkOrder, Operation
from app.models.execution import ExecutionEvent
from app.models.rbac import Role, Permission, RolePermission, UserRole, RoleScope
from app.models.impersonation import ImpersonationSession, ImpersonationAuditLog
from app.models.approval import ApprovalRule, ApprovalRequest, ApprovalDecision, ApprovalAuditLog
from app.models.user import User
from app.security.rbac import seed_rbac_core
from app.services.approval_service import seed_approval_rules
from app.services.user_service import seed_demo_users

def init_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_rbac_core(db)
        seed_approval_rules(db)
        seed_demo_users(db)


if __name__ == "__main__":
    init_db()