from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reason_code import ReasonCode


def list_reason_codes_by_tenant(
    db: Session,
    *,
    tenant_id: str,
    reason_domain: str | None = None,
    reason_category: str | None = None,
    lifecycle_status: str | None = None,
    include_inactive: bool = False,
) -> list[ReasonCode]:
    """
    List reason codes for a tenant with optional filtering.
    
    Default behavior: returns RELEASED codes that are active.
    """
    query = select(ReasonCode).where(ReasonCode.tenant_id == tenant_id)

    if lifecycle_status is None:
        # Default: only RELEASED codes
        query = query.where(ReasonCode.lifecycle_status == "RELEASED")
    else:
        # Filter by specified status
        query = query.where(ReasonCode.lifecycle_status == lifecycle_status)

    if not include_inactive:
        # Default: only active codes
        query = query.where(ReasonCode.is_active == True)

    if reason_domain is not None:
        query = query.where(ReasonCode.reason_domain == reason_domain)

    if reason_category is not None:
        query = query.where(ReasonCode.reason_category == reason_category)

    # Order by domain, category, sort_order, reason_code
    query = query.order_by(
        ReasonCode.reason_domain.asc(),
        ReasonCode.reason_category.asc(),
        ReasonCode.sort_order.asc(),
        ReasonCode.reason_code.asc(),
    )

    return list(db.scalars(query))


def get_reason_code_by_id(
    db: Session,
    *,
    tenant_id: str,
    reason_code_id: str,
) -> ReasonCode | None:
    """
    Get a single reason code by ID.
    Tenant-scoped: returns None if code belongs to different tenant.
    """
    return db.scalar(
        select(ReasonCode).where(
            ReasonCode.tenant_id == tenant_id,
            ReasonCode.reason_code_id == reason_code_id,
        )
    )
