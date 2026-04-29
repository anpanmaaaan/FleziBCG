from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.user_lifecycle import (
    UserLifecycleActionResponse,
    UserLifecycleItem,
    UserLifecycleListResponse,
)
from app.security.dependencies import RequestIdentity, require_action
from app.services.user_lifecycle_service import (
    activate_user,
    deactivate_user,
    list_tenant_users,
)

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=UserLifecycleListResponse)
def list_users(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> UserLifecycleListResponse:
    users = list_tenant_users(
        db,
        tenant_id=identity.tenant_id,
        include_inactive=include_inactive,
    )
    return UserLifecycleListResponse(
        users=[
            UserLifecycleItem(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                tenant_id=user.tenant_id,
                is_active=user.is_active,
            )
            for user in users
        ]
    )


@router.post("/{user_id}/activate", response_model=UserLifecycleActionResponse)
def activate_tenant_user(
    user_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> UserLifecycleActionResponse:
    user = activate_user(
        db,
        tenant_id=identity.tenant_id,
        user_id=user_id,
        actor_user_id=identity.user_id,
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserLifecycleActionResponse(
        status="ok",
        user_id=user.user_id,
        tenant_id=user.tenant_id,
        is_active=user.is_active,
        action="activate",
    )


@router.post("/{user_id}/deactivate", response_model=UserLifecycleActionResponse)
def deactivate_tenant_user(
    user_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> UserLifecycleActionResponse:
    user = deactivate_user(
        db,
        tenant_id=identity.tenant_id,
        user_id=user_id,
        actor_user_id=identity.user_id,
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserLifecycleActionResponse(
        status="ok",
        user_id=user.user_id,
        tenant_id=user.tenant_id,
        is_active=user.is_active,
        action="deactivate",
    )


# Transitional aliases while dedicated lock state/policy is deferred to ADR.
@router.post("/{user_id}/lock", response_model=UserLifecycleActionResponse)
def lock_tenant_user(
    user_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> UserLifecycleActionResponse:
    user = deactivate_user(
        db,
        tenant_id=identity.tenant_id,
        user_id=user_id,
        actor_user_id=identity.user_id,
        audit_action="lock",
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserLifecycleActionResponse(
        status="ok",
        user_id=user.user_id,
        tenant_id=user.tenant_id,
        is_active=user.is_active,
        action="lock",
    )


@router.post("/{user_id}/unlock", response_model=UserLifecycleActionResponse)
def unlock_tenant_user(
    user_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> UserLifecycleActionResponse:
    user = activate_user(
        db,
        tenant_id=identity.tenant_id,
        user_id=user_id,
        actor_user_id=identity.user_id,
        audit_action="unlock",
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserLifecycleActionResponse(
        status="ok",
        user_id=user.user_id,
        tenant_id=user.tenant_id,
        is_active=user.is_active,
        action="unlock",
    )
