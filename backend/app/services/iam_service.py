from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import (
    Permission,
    Role,
    RolePermission,
    RoleScope,
    Scope,
    UserRole,
    UserRoleAssignment,
)
from app.security.dependencies import RequestIdentity
from app.security.rbac import SYSTEM_ROLE_FAMILIES


def _in_valid_window(
    valid_from: datetime | None, valid_to: datetime | None, now: datetime
) -> bool:
    if valid_from is not None and valid_from > now:
        return False
    if valid_to is not None and valid_to < now:
        return False
    return True


def get_role_assignments_for_identity(
    db: Session, identity: RequestIdentity
) -> list[dict]:
    now = datetime.now(timezone.utc)

    rows = list(
        db.execute(
            select(UserRoleAssignment, Role, Scope)
            .join(Role, Role.id == UserRoleAssignment.role_id)
            .join(Scope, Scope.id == UserRoleAssignment.scope_id)
            .where(
                UserRoleAssignment.user_id == identity.user_id,
                UserRoleAssignment.is_active.is_(True),
                Scope.tenant_id == identity.tenant_id,
            )
            .order_by(UserRoleAssignment.is_primary.desc(), UserRoleAssignment.id.asc())
        )
    )

    assignments: list[dict] = []
    for assignment, role, scope in rows:
        if not _in_valid_window(assignment.valid_from, assignment.valid_to, now):
            continue
        assignments.append(
            {
                "assignment_id": assignment.id,
                "role_code": role.code,
                "is_primary": assignment.is_primary,
                "is_active": assignment.is_active,
                "valid_from": assignment.valid_from,
                "valid_to": assignment.valid_to,
                "scope": {
                    "id": scope.id,
                    "tenant_id": scope.tenant_id,
                    "scope_type": scope.scope_type,
                    "scope_value": scope.scope_value,
                    "parent_scope_id": scope.parent_scope_id,
                },
            }
        )

    if assignments:
        return assignments

    # Backward-compatible fallback to legacy user_roles + role_scopes.
    legacy_rows = list(
        db.execute(
            select(UserRole, Role, RoleScope)
            .join(Role, Role.id == UserRole.role_id)
            .outerjoin(RoleScope, RoleScope.user_role_id == UserRole.id)
            .where(
                UserRole.user_id == identity.user_id,
                UserRole.tenant_id == identity.tenant_id,
                UserRole.is_active.is_(True),
            )
            .order_by(UserRole.id.asc())
        )
    )

    fallback_assignments: list[dict] = []
    synthetic_assignment_id = 1
    for user_role, role, role_scope in legacy_rows:
        scope_type = role_scope.scope_type if role_scope is not None else "tenant"
        scope_value = (
            role_scope.scope_value if role_scope is not None else identity.tenant_id
        )
        fallback_assignments.append(
            {
                "assignment_id": None,
                "role_code": role.code,
                "is_primary": synthetic_assignment_id == 1,
                "is_active": user_role.is_active,
                "valid_from": None,
                "valid_to": None,
                "scope": {
                    "id": -synthetic_assignment_id,
                    "tenant_id": identity.tenant_id,
                    "scope_type": scope_type,
                    "scope_value": scope_value,
                    "parent_scope_id": None,
                },
            }
        )
        synthetic_assignment_id += 1

    return fallback_assignments


def create_custom_role(
    db: Session,
    *,
    tenant_id: str,
    code: str,
    name: str,
    description: str | None,
    base_role_code: str,
    owner_user_id: str,
    allow_action_codes: list[str] | None = None,
) -> Role:
    base_role = db.scalar(select(Role).where(Role.code == base_role_code))
    if base_role is None or base_role.role_type != "system":
        raise ValueError("Custom role must derive from an existing system role")

    normalized_code = code.strip().upper()
    if not normalized_code:
        raise ValueError("Role code is required")

    existing = db.scalar(select(Role).where(Role.code == normalized_code))
    if existing is not None:
        raise ValueError("Role code already exists")

    base_families = SYSTEM_ROLE_FAMILIES.get(base_role.code, set())
    if "ADMIN" in base_families and base_role.code not in {"ADM", "OTS"}:
        raise ValueError("Invalid base system role for ADMIN policy")

    if base_role.code not in {"ADM", "OTS"} and allow_action_codes:
        for action in allow_action_codes:
            if action.startswith("admin."):
                raise ValueError(
                    "Custom roles must not grant ADMIN actions beyond baseline"
                )

    custom_role = Role(
        code=normalized_code,
        tenant_id=tenant_id,
        name=name.strip(),
        description=description,
        role_type="custom",
        base_role_id=base_role.id,
        owner_user_id=owner_user_id,
        is_active=True,
        is_system=False,
    )
    db.add(custom_role)
    db.flush()

    base_permissions = list(
        db.scalars(select(RolePermission).where(RolePermission.role_id == base_role.id))
    )
    cloned_keys: set[tuple[int, str, str]] = set()
    for link in base_permissions:
        key = (link.permission_id, link.scope_type, link.scope_value)
        if key in cloned_keys:
            continue
        cloned_keys.add(key)
        db.add(
            RolePermission(
                role_id=custom_role.id,
                permission_id=link.permission_id,
                scope_type=link.scope_type,
                scope_value=link.scope_value,
                effect=link.effect,
            )
        )

    allow_action_codes = allow_action_codes or []
    for action in allow_action_codes:
        permission = db.scalar(
            select(Permission).where(Permission.action_code == action)
        )
        if permission is None:
            continue
        key = (permission.id, "tenant", "*")
        if key not in cloned_keys:
            cloned_keys.add(key)
            db.add(
                RolePermission(
                    role_id=custom_role.id,
                    permission_id=permission.id,
                    scope_type="tenant",
                    scope_value="*",
                    effect="allow",
                )
            )

    db.commit()
    db.refresh(custom_role)
    return custom_role
