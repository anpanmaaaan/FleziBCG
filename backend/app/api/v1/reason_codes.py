from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.reason_code import ReasonCodeItem
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.reason_code_service import (
    get_reason_code as get_reason_code_service,
    list_reason_codes as list_reason_codes_service,
)

router = APIRouter(prefix="/reason-codes", tags=["reason-codes"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[ReasonCodeItem])
def list_reason_codes(
    domain: str | None = None,
    category: str | None = None,
    lifecycle_status: str | None = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[ReasonCodeItem]:
    """
    List reason codes for the requesting tenant.
    
    Query parameters:
    - domain: filter by reason_domain (e.g., 'DOWNTIME', 'SCRAP')
    - category: filter by reason_category (e.g., 'Planned Maintenance')
    - lifecycle_status: filter by status ('DRAFT', 'RELEASED', 'RETIRED')
      Default: returns RELEASED codes only
    - include_inactive: if true, includes is_active=false codes
      Default: false (only active codes)
    
    Codes are ordered by domain, category, sort_order, and reason_code.
    """
    return list_reason_codes_service(
        db,
        tenant_id=identity.tenant_id,
        reason_domain=domain,
        reason_category=category,
        lifecycle_status=lifecycle_status,
        include_inactive=include_inactive,
    )


@router.get("/{reason_code_id}", response_model=ReasonCodeItem)
def get_reason_code(
    reason_code_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> ReasonCodeItem:
    """
    Get a single reason code by ID.
    
    Returns 404 if code not found or belongs to a different tenant.
    """
    code = get_reason_code_service(
        db,
        tenant_id=identity.tenant_id,
        reason_code_id=reason_code_id,
    )
    if code is None:
        raise HTTPException(status_code=404, detail="Reason code not found")
    return code
