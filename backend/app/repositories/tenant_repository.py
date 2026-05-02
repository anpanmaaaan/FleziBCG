from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant


def get_tenant_by_id(db: Session, tenant_id: str) -> Tenant | None:
    return db.scalar(select(Tenant).where(Tenant.tenant_id == tenant_id))


def is_tenant_lifecycle_active(db: Session, tenant_id: str) -> bool:
    """Return True if the tenant is allowed to operate.

    Policy B (transitional): if no Tenant row exists for this tenant_id, return
    True. This accommodates the existing fleet of tenant_id strings that were
    established before the Tenant table existed (P0-A-02A). A missing row is
    treated as legacy-allowed debt, documented for P0-A-02C enforcement cutover.

    A row that exists MUST be both is_active=True and lifecycle_status=ACTIVE
    to be allowed. DISABLED or SUSPENDED tenants are hard-rejected.
    """
    tenant = get_tenant_by_id(db, tenant_id)
    if tenant is None:
        # Policy B: no row → legacy debt, allow until cutover (P0-A-02C).
        return True
    return tenant.is_lifecycle_active
