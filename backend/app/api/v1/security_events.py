from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.security_event import SecurityEventItem
from app.security.dependencies import RequestIdentity, require_action
from app.services.security_event_service import get_security_events

router = APIRouter(prefix="/security-events", tags=["security-events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[SecurityEventItem])
def list_security_events(
    limit: int = 100,
    offset: int = 0,
    event_type: str | None = None,
    actor_user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> list[SecurityEventItem]:
    if created_from and created_to and created_from > created_to:
        raise HTTPException(status_code=422, detail="created_from must be <= created_to")

    rows = get_security_events(
        db,
        tenant_id=identity.tenant_id,
        limit=limit,
        offset=offset,
        event_type=event_type,
        actor_user_id=actor_user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        created_from=created_from,
        created_to=created_to,
    )
    return [SecurityEventItem.model_validate(row) for row in rows]
