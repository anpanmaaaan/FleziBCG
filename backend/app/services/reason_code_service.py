from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.reason_code import ReasonCode
from app.repositories.reason_code_repository import (
    get_reason_code_by_id as get_reason_code_row,
    list_reason_codes_by_tenant,
)
from app.schemas.reason_code import ReasonCodeItem


def _to_item(row: ReasonCode) -> ReasonCodeItem:
    """Convert ORM model to read schema."""
    return ReasonCodeItem(
        reason_code_id=row.reason_code_id,
        tenant_id=row.tenant_id,
        reason_domain=row.reason_domain,
        reason_category=row.reason_category,
        reason_code=row.reason_code,
        reason_name=row.reason_name,
        description=row.description,
        lifecycle_status=row.lifecycle_status,
        requires_comment=row.requires_comment,
        is_active=row.is_active,
        sort_order=row.sort_order,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def list_reason_codes(
    db: Session,
    *,
    tenant_id: str,
    reason_domain: str | None = None,
    reason_category: str | None = None,
    lifecycle_status: str | None = None,
    include_inactive: bool = False,
) -> list[ReasonCodeItem]:
    """
    List reason codes for a tenant.
    
    Default: returns RELEASED + active codes.
    """
    rows = list_reason_codes_by_tenant(
        db,
        tenant_id=tenant_id,
        reason_domain=reason_domain,
        reason_category=reason_category,
        lifecycle_status=lifecycle_status,
        include_inactive=include_inactive,
    )
    return [_to_item(row) for row in rows]


def get_reason_code(
    db: Session,
    *,
    tenant_id: str,
    reason_code_id: str,
) -> ReasonCodeItem | None:
    """
    Get a single reason code by ID.
    Tenant-scoped: returns None if code belongs to different tenant.
    """
    row = get_reason_code_row(
        db,
        tenant_id=tenant_id,
        reason_code_id=reason_code_id,
    )
    if row is None:
        return None
    return _to_item(row)
