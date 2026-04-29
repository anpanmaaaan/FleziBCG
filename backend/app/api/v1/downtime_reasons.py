from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.downtime_reason import (
    DowntimeReasonAdminItem,
    DowntimeReasonItem,
    DowntimeReasonUpsertRequest,
)
from app.security.dependencies import (
    RequestIdentity,
    require_action,
    require_authenticated_identity,
)
from app.services.downtime_reason_service import (
    deactivate_downtime_reason as deactivate_downtime_reason_service,
    list_downtime_reasons as list_downtime_reasons_service,
    upsert_downtime_reason as upsert_downtime_reason_service,
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


@router.post("/downtime-reasons", response_model=DowntimeReasonAdminItem)
def upsert_downtime_reason(
    payload: DowntimeReasonUpsertRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> DowntimeReasonAdminItem:
    return upsert_downtime_reason_service(
        db,
        tenant_id=identity.tenant_id,
        actor_user_id=identity.user_id,
        payload=payload,
    )


@router.post(
    "/downtime-reasons/{reason_code}/deactivate",
    response_model=DowntimeReasonAdminItem,
)
def deactivate_downtime_reason(
    reason_code: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> DowntimeReasonAdminItem:
    row = deactivate_downtime_reason_service(
        db,
        tenant_id=identity.tenant_id,
        actor_user_id=identity.user_id,
        reason_code=reason_code,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Downtime reason not found")
    return row
