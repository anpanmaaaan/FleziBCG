from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.downtime_reason import DowntimeReasonItem
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.downtime_reason_service import (
    list_downtime_reasons as list_downtime_reasons_service,
)


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/downtime-reasons", response_model=list[DowntimeReasonItem])
def list_downtime_reasons(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> list[DowntimeReasonItem]:
    """
    Return active downtime reasons available to the requesting tenant,
    ordered by `(sort_order, reason_code)`. This is the canonical source
    for the FE Start-Downtime picker. Clients must submit the chosen
    `reason_code` on `start_downtime`; classification (`reason_group`) is
    display-only and is never client authority.
    """
    return list_downtime_reasons_service(db, tenant_id=identity.tenant_id)
