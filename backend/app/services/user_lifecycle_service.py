from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import list_users_by_tenant, set_user_active
from app.services.security_event_service import record_security_event


def list_tenant_users(
    db: Session,
    *,
    tenant_id: str,
    include_inactive: bool = False,
) -> list[User]:
    return list_users_by_tenant(
        db,
        tenant_id=tenant_id,
        include_inactive=include_inactive,
    )


def activate_user(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    actor_user_id: str | None = None,
    audit_action: str = "activate",
) -> User | None:
    user = set_user_active(
        db,
        user_id=user_id,
        tenant_id=tenant_id,
        is_active=True,
    )
    if user is not None and actor_user_id is not None:
        record_security_event(
            db,
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type=f"IAM.USER_{audit_action}",
            resource_type="user",
            resource_id=user.user_id,
            detail=audit_action,
        )
    return user


def deactivate_user(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    actor_user_id: str | None = None,
    audit_action: str = "deactivate",
) -> User | None:
    user = set_user_active(
        db,
        user_id=user_id,
        tenant_id=tenant_id,
        is_active=False,
    )
    if user is not None and actor_user_id is not None:
        record_security_event(
            db,
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type=f"IAM.USER_{audit_action}",
            resource_type="user",
            resource_id=user.user_id,
            detail=audit_action,
        )
    return user
