from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant


def get_tenant_by_id(db: Session, tenant_id: str) -> Tenant | None:
    return db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))


def is_tenant_lifecycle_active(db: Session, tenant_id: str) -> bool:
    """Return True only if the tenant row exists and is operationally active.

    Policy A (strict, P0-A-02C): a missing Tenant row is treated as inactive
    and causes the request to be rejected. This supersedes the transitional
    Policy B (P0-A-02B) which allowed missing rows for legacy string tenants.

    INVARIANTS:
    - Row missing → False (reject).
    - Row exists, is_active=False → False (reject).
    - Row exists, lifecycle_status != ACTIVE → False (reject).
    - Row exists, is_active=True, lifecycle_status=ACTIVE → True (allow).
    """
    tenant = get_tenant_by_id(db, tenant_id)
    if tenant is None:
        # Policy A: no row → tenant does not exist → reject.
        return False
    return tenant.is_lifecycle_active
