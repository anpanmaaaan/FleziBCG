from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Role, RoleScope, Scope, UserRole, UserRoleAssignment
from app.security.dependencies import RequestIdentity


def _in_valid_window(valid_from: datetime | None, valid_to: datetime | None, now: datetime) -> bool:
    if valid_from is not None and valid_from > now:
        return False
    if valid_to is not None and valid_to < now:
        return False
    return True


def get_role_assignments_for_identity(db: Session, identity: RequestIdentity) -> list[dict]:
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
        scope_value = role_scope.scope_value if role_scope is not None else identity.tenant_id
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
