from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security_event import SecurityEventLog


def append_security_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str | None,
    event_type: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    detail: str | None = None,
    commit: bool = True,
) -> SecurityEventLog:
    event = SecurityEventLog(
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    return event


def list_security_events(
    db: Session,
    *,
    tenant_id: str,
    limit: int = 100,
) -> list[SecurityEventLog]:
    safe_limit = max(1, min(limit, 500))
    return list(
        db.scalars(
            select(SecurityEventLog)
            .where(SecurityEventLog.tenant_id == tenant_id)
            .order_by(SecurityEventLog.created_at.desc(), SecurityEventLog.id.desc())
            .limit(safe_limit)
        )
    )
