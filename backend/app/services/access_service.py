from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Role, Scope, UserRole, UserRoleAssignment
from app.models.user import User
from app.services.security_event_service import record_security_event

_SCOPE_ORDER = {
    "tenant": 0,
    "plant": 1,
    "area": 2,
    "line": 3,
    "station": 4,
    "equipment": 5,
}


def _normalize_scope_type(scope_type: str) -> str:
    normalized = scope_type.strip().lower()
    if normalized not in _SCOPE_ORDER:
        raise ValueError("Unsupported scope_type")
    return normalized


def _get_tenant_root_scope(db: Session, tenant_id: str) -> Scope:
    root = db.scalar(
        select(Scope).where(
            Scope.tenant_id == tenant_id,
            Scope.scope_type == "tenant",
            Scope.scope_value == tenant_id,
        )
    )
    if root is not None:
        return root

    root = Scope(
        tenant_id=tenant_id,
        scope_type="tenant",
        scope_value=tenant_id,
        parent_scope_id=None,
    )
    db.add(root)
    db.flush()
    return root


def _resolve_role(db: Session, tenant_id: str, role_code: str) -> Role:
    role = db.scalar(
        select(Role).where(
            Role.code == role_code,
            Role.is_active.is_(True),
        )
    )
    if role is None:
        raise ValueError("Role not found")
    if role.tenant_id not in (None, tenant_id):
        raise ValueError("Role is outside tenant boundary")
    return role


def _ensure_user_in_tenant(db: Session, tenant_id: str, user_id: str) -> None:
    user = db.scalar(
        select(User).where(
            User.user_id == user_id,
            User.tenant_id == tenant_id,
        )
    )
    if user is None:
        raise ValueError("User not found")


def assign_role(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    role_code: str,
    is_active: bool,
    actor_user_id: str | None = None,
) -> UserRole:
    _ensure_user_in_tenant(db, tenant_id, user_id)
    role = _resolve_role(db, tenant_id, role_code)

    existing = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role.id,
            UserRole.tenant_id == tenant_id,
        )
    )
    if existing is not None:
        existing.is_active = is_active
        db.commit()
        db.refresh(existing)
        if actor_user_id is not None:
            record_security_event(
                db,
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                event_type="IAM.ROLE_ASSIGNMENT",
                resource_type="user_role",
                resource_id=str(existing.id),
                detail=f"{user_id}:{role.code}",
            )
        return existing

    user_role = UserRole(
        user_id=user_id,
        role_id=role.id,
        tenant_id=tenant_id,
        is_active=is_active,
    )
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    if actor_user_id is not None:
        record_security_event(
            db,
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type="IAM.ROLE_ASSIGNMENT",
            resource_type="user_role",
            resource_id=str(user_role.id),
            detail=f"{user_id}:{role.code}",
        )
    return user_role


def assign_scope(
    db: Session,
    *,
    tenant_id: str,
    user_id: str,
    role_code: str,
    scope_type: str,
    scope_value: str,
    is_primary: bool,
    actor_user_id: str | None = None,
) -> tuple[UserRoleAssignment, Role, Scope]:
    _ensure_user_in_tenant(db, tenant_id, user_id)
    role = _resolve_role(db, tenant_id, role_code)
    normalized_scope_type = _normalize_scope_type(scope_type)
    normalized_scope_value = scope_value.strip()
    if not normalized_scope_value:
        raise ValueError("scope_value is required")

    tenant_scope = _get_tenant_root_scope(db, tenant_id)

    scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == tenant_id,
            Scope.scope_type == normalized_scope_type,
            Scope.scope_value == normalized_scope_value,
        )
    )
    if scope is None:
        parent_scope_id = None
        if normalized_scope_type != "tenant":
            parent_scope_id = tenant_scope.id
        scope = Scope(
            tenant_id=tenant_id,
            scope_type=normalized_scope_type,
            scope_value=normalized_scope_value,
            parent_scope_id=parent_scope_id,
        )
        db.add(scope)
        db.flush()

    existing_assignment = db.scalar(
        select(UserRoleAssignment).where(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.role_id == role.id,
            UserRoleAssignment.scope_id == scope.id,
        )
    )
    if existing_assignment is not None:
        existing_assignment.is_active = True
        existing_assignment.is_primary = is_primary
        db.commit()
        db.refresh(existing_assignment)
        if actor_user_id is not None:
            record_security_event(
                db,
                tenant_id=tenant_id,
                actor_user_id=actor_user_id,
                event_type="IAM.SCOPE_ASSIGNMENT",
                resource_type="user_role_assignment",
                resource_id=str(existing_assignment.id),
                detail=f"{user_id}:{role.code}:{scope.scope_type}:{scope.scope_value}",
            )
        return existing_assignment, role, scope

    assignment = UserRoleAssignment(
        user_id=user_id,
        role_id=role.id,
        scope_id=scope.id,
        is_primary=is_primary,
        is_active=True,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    if actor_user_id is not None:
        record_security_event(
            db,
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type="IAM.SCOPE_ASSIGNMENT",
            resource_type="user_role_assignment",
            resource_id=str(assignment.id),
            detail=f"{user_id}:{role.code}:{scope.scope_type}:{scope.scope_value}",
        )
    return assignment, role, scope
