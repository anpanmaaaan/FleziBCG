from fastapi import APIRouter, Depends
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
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> list[SecurityEventItem]:
    rows = get_security_events(db, tenant_id=identity.tenant_id, limit=limit)
    return [SecurityEventItem.model_validate(row) for row in rows]
