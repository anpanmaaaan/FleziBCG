from sqlalchemy.orm import Session
from datetime import datetime

from app.models.security_event import SecurityEventLog
from app.repositories.security_event_repository import (
    append_security_event,
    list_security_events,
)


def record_security_event(
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
    if not event_type.strip():
        raise ValueError("event_type is required")
    return append_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type=event_type.strip().upper(),
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        commit=commit,
    )


def get_security_events(
    db: Session,
    *,
    tenant_id: str,
    limit: int = 100,
    offset: int = 0,
    event_type: str | None = None,
    actor_user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> list[SecurityEventLog]:
    normalized_event_type = event_type.strip().upper() if event_type else None
    return list_security_events(
        db,
        tenant_id=tenant_id,
        limit=limit,
        offset=offset,
        event_type=normalized_event_type,
        actor_user_id=actor_user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        created_from=created_from,
        created_to=created_to,
    )
