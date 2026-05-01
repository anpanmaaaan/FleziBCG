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
    offset: int = 0,
    event_type: str | None = None,
    actor_user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    created_from=None,
    created_to=None,
) -> list[SecurityEventLog]:
    safe_limit = max(1, min(limit, 500))
    safe_offset = max(0, offset)

    query = select(SecurityEventLog).where(SecurityEventLog.tenant_id == tenant_id)

    if event_type:
        query = query.where(SecurityEventLog.event_type == event_type)
    if actor_user_id:
        query = query.where(SecurityEventLog.actor_user_id == actor_user_id)
    if resource_type:
        query = query.where(SecurityEventLog.resource_type == resource_type)
    if resource_id:
        query = query.where(SecurityEventLog.resource_id == resource_id)
    if created_from is not None:
        query = query.where(SecurityEventLog.created_at >= created_from)
    if created_to is not None:
        query = query.where(SecurityEventLog.created_at <= created_to)

    return list(
        db.scalars(
            query
            .order_by(SecurityEventLog.created_at.desc(), SecurityEventLog.id.desc())
            .limit(safe_limit)
            .offset(safe_offset)
        )
    )
