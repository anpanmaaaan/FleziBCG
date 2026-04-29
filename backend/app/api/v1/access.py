from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.rbac import Role
from app.schemas.access import (
    RoleAssignmentRequest,
    RoleAssignmentResponse,
    ScopeAssignmentRequest,
    ScopeAssignmentResponse,
)
from app.security.dependencies import RequestIdentity, require_action
from app.services.access_service import assign_role, assign_scope

router = APIRouter(prefix="/access", tags=["access"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/role-assignments", response_model=RoleAssignmentResponse)
def create_role_assignment(
    payload: RoleAssignmentRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> RoleAssignmentResponse:
    try:
        user_role = assign_role(
            db,
            tenant_id=identity.tenant_id,
            user_id=payload.user_id,
            role_code=payload.role_code,
            is_active=payload.is_active,
            actor_user_id=identity.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    role = db.scalar(select(Role).where(Role.id == user_role.role_id))
    role_code = role.code if role is not None else payload.role_code
    return RoleAssignmentResponse(
        id=user_role.id,
        user_id=user_role.user_id,
        role_code=role_code,
        tenant_id=user_role.tenant_id,
        is_active=user_role.is_active,
    )


@router.post("/scope-assignments", response_model=ScopeAssignmentResponse)
def create_scope_assignment(
    payload: ScopeAssignmentRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("admin.user.manage")),
) -> ScopeAssignmentResponse:
    try:
        assignment, role, scope = assign_scope(
            db,
            tenant_id=identity.tenant_id,
            user_id=payload.user_id,
            role_code=payload.role_code,
            scope_type=payload.scope_type,
            scope_value=payload.scope_value,
            is_primary=payload.is_primary,
            actor_user_id=identity.user_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return ScopeAssignmentResponse(
        assignment_id=assignment.id,
        user_id=assignment.user_id,
        role_code=role.code,
        scope_id=scope.id,
        tenant_id=scope.tenant_id,
        scope_type=scope.scope_type,
        scope_value=scope.scope_value,
        is_primary=assignment.is_primary,
    )
