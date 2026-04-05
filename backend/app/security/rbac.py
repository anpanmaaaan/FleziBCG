import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.rbac import Permission, Role, RolePermission, RoleScope, Scope, UserRole, UserRoleAssignment

PermissionFamily = Literal["VIEW", "EXECUTE", "APPROVE", "CONFIGURE", "ADMIN"]

SYSTEM_ROLE_FAMILIES: dict[str, set[PermissionFamily]] = {
    "OPR": {"EXECUTE"},
    "SUP": {"VIEW", "EXECUTE"},
    "IEP": {"VIEW", "CONFIGURE"},
    "QCI": {"VIEW"},
    "QAL": {"VIEW", "APPROVE"},
    "PMG": {"VIEW", "APPROVE"},
    "EXE": {"VIEW"},
    "ADM": {"VIEW", "ADMIN"},
    "OTS": {"VIEW", "ADMIN"},
}

ROLE_ALIASES: dict[str, str] = {
    "OPERATOR": "OPR",
    "SUPERVISOR": "SUP",
    "SHIFT_LEADER": "SUP",
    "IE": "IEP",
    "PROCESS": "IEP",
    "QA": "QCI",
}

SCOPE_TYPE_TENANT = "tenant"
SCOPE_TYPE_PLANT = "plant"
SCOPE_TYPE_AREA = "area"
SCOPE_TYPE_LINE = "line"
SCOPE_TYPE_STATION = "station"
SCOPE_TYPE_EQUIPMENT = "equipment"
SCOPE_WILDCARD = "*"

# Roles that cannot be the target of impersonation.
FORBIDDEN_ACTING_ROLES: frozenset[str] = frozenset({"ADM", "OTS"})


@dataclass
class IdentityLike:
    user_id: str
    tenant_id: str
    is_authenticated: bool
    acting_role_code: str | None = None  # Set when an impersonation session is active


def _normalize_role_code(raw_role_code: str | None) -> str | None:
    if raw_role_code is None:
        return None
    normalized = raw_role_code.strip().upper()
    if not normalized:
        return None
    return ROLE_ALIASES.get(normalized, normalized)


def _load_default_users() -> list[dict[str, str | None]]:
    settings = Settings()
    try:
        raw = json.loads(settings.auth_default_users_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid auth_default_users_json configuration") from exc

    if not isinstance(raw, list):
        raise ValueError("auth_default_users_json must be a JSON list")

    users: list[dict[str, str | None]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        username = str(item.get("username", "")).strip()
        user_id = str(item.get("user_id", username)).strip()
        tenant_id = str(item.get("tenant_id", "default")).strip() or "default"
        role_code = _normalize_role_code(str(item.get("role_code")) if item.get("role_code") is not None else None)
        if not username or not user_id:
            continue
        users.append(
            {
                "username": username,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role_code": role_code,
            }
        )
    return users


def _get_or_create_role(db: Session, code: str) -> Role:
    role = db.scalar(select(Role).where(Role.code == code))
    if role:
        return role

    role = Role(code=code, name=code, description=f"System role {code}", is_system=True)
    db.add(role)
    db.flush()
    return role


def _get_or_create_permission(db: Session, family: PermissionFamily) -> Permission:
    permission = db.scalar(select(Permission).where(Permission.family == family))
    if permission:
        return permission

    permission = Permission(code=family, family=family, description=f"{family} permission family")
    db.add(permission)
    db.flush()
    return permission


def _get_or_create_scope(
    db: Session,
    *,
    tenant_id: str,
    scope_type: str,
    scope_value: str,
    parent_scope_id: int | None,
) -> Scope:
    scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == tenant_id,
            Scope.scope_type == scope_type,
            Scope.scope_value == scope_value,
        )
    )
    if scope is not None:
        if scope.parent_scope_id != parent_scope_id:
            scope.parent_scope_id = parent_scope_id
            db.flush()
        return scope

    scope = Scope(
        tenant_id=tenant_id,
        scope_type=scope_type,
        scope_value=scope_value,
        parent_scope_id=parent_scope_id,
    )
    db.add(scope)
    db.flush()
    return scope


def seed_rbac_core(db: Session) -> None:
    role_by_code: dict[str, Role] = {}
    for role_code in SYSTEM_ROLE_FAMILIES:
        role_by_code[role_code] = _get_or_create_role(db, role_code)

    permission_by_family: dict[PermissionFamily, Permission] = {}
    for family in ("VIEW", "EXECUTE", "APPROVE", "CONFIGURE", "ADMIN"):
        permission_by_family[family] = _get_or_create_permission(db, family)

    for role_code, families in SYSTEM_ROLE_FAMILIES.items():
        role = role_by_code[role_code]
        for family in families:
            permission = permission_by_family[family]
            existing_link = db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                    RolePermission.scope_type == SCOPE_TYPE_TENANT,
                    RolePermission.scope_value == SCOPE_WILDCARD,
                )
            )
            if existing_link:
                continue
            db.add(
                RolePermission(
                    role_id=role.id,
                    permission_id=permission.id,
                    scope_type=SCOPE_TYPE_TENANT,
                    scope_value=SCOPE_WILDCARD,
                )
            )

    for user in _load_default_users():
        role_code = _normalize_role_code(user.get("role_code"))
        if role_code is None or role_code not in role_by_code:
            continue

        tenant_id = str(user["tenant_id"])

        # Deterministic scope chain used by Tier 1 evaluation and tests.
        tenant_scope = _get_or_create_scope(
            db,
            tenant_id=tenant_id,
            scope_type=SCOPE_TYPE_TENANT,
            scope_value=tenant_id,
            parent_scope_id=None,
        )
        plant_scope = _get_or_create_scope(
            db,
            tenant_id=tenant_id,
            scope_type=SCOPE_TYPE_PLANT,
            scope_value="PLANT_01",
            parent_scope_id=tenant_scope.id,
        )
        line_scope = _get_or_create_scope(
            db,
            tenant_id=tenant_id,
            scope_type=SCOPE_TYPE_LINE,
            scope_value="LINE_A",
            parent_scope_id=plant_scope.id,
        )
        station_scope = _get_or_create_scope(
            db,
            tenant_id=tenant_id,
            scope_type=SCOPE_TYPE_STATION,
            scope_value="STATION_01",
            parent_scope_id=line_scope.id,
        )

        user_role = db.scalar(
            select(UserRole).where(
                UserRole.user_id == str(user["user_id"]),
                UserRole.role_id == role_by_code[role_code].id,
                UserRole.tenant_id == tenant_id,
            )
        )
        if user_role is None:
            user_role = UserRole(
                user_id=str(user["user_id"]),
                role_id=role_by_code[role_code].id,
                tenant_id=tenant_id,
                is_active=True,
            )
            db.add(user_role)
            db.flush()
        elif not user_role.is_active:
            user_role.is_active = True
            db.flush()

        legacy_tenant_scope = db.scalar(
            select(RoleScope).where(
                RoleScope.user_role_id == user_role.id,
                RoleScope.scope_type == SCOPE_TYPE_TENANT,
                RoleScope.scope_value == tenant_id,
            )
        )
        if legacy_tenant_scope is None:
            db.add(
                RoleScope(
                    user_role_id=user_role.id,
                    scope_type=SCOPE_TYPE_TENANT,
                    scope_value=tenant_id,
                )
            )

        assignment = db.scalar(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == str(user["user_id"]),
                UserRoleAssignment.role_id == role_by_code[role_code].id,
                UserRoleAssignment.scope_id == station_scope.id,
            )
        )
        if assignment is None:
            db.add(
                UserRoleAssignment(
                    user_id=str(user["user_id"]),
                    role_id=role_by_code[role_code].id,
                    scope_id=station_scope.id,
                    is_primary=True,
                    is_active=True,
                )
            )

    db.commit()


def normalize_role_code(raw_role_code: str | None) -> str | None:
    """Public alias for role code normalization with alias resolution."""
    return _normalize_role_code(raw_role_code)


def has_permission(
    db: Session,
    identity: IdentityLike,
    required_family: PermissionFamily,
    target_scope_type: str | None = None,
    target_scope_value: str | None = None,
) -> bool:
    if not identity.is_authenticated:
        return False

    # Impersonation path: resolve permissions from acting role's family set directly.
    # This fully replaces the DB lookup; DB grants are not consulted for acting role grants.
    acting = getattr(identity, "acting_role_code", None)
    if acting:
        acting_families = SYSTEM_ROLE_FAMILIES.get(acting, set())
        return required_family in acting_families

    now = datetime.now(timezone.utc)

    # Preferred path: new multi-scope assignment table.
    assignment_rows = list(
        db.execute(
            select(UserRoleAssignment, Scope)
            .join(RolePermission, RolePermission.role_id == UserRoleAssignment.role_id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .join(Scope, Scope.id == UserRoleAssignment.scope_id)
            .where(
                UserRoleAssignment.user_id == identity.user_id,
                UserRoleAssignment.is_active.is_(True),
                or_(UserRoleAssignment.valid_from.is_(None), UserRoleAssignment.valid_from <= now),
                or_(UserRoleAssignment.valid_to.is_(None), UserRoleAssignment.valid_to >= now),
                Scope.tenant_id == identity.tenant_id,
                Permission.family == required_family,
                RolePermission.scope_type == SCOPE_TYPE_TENANT,
                or_(
                    RolePermission.scope_value == identity.tenant_id,
                    RolePermission.scope_value == SCOPE_WILDCARD,
                ),
            )
        )
    )

    if assignment_rows:
        # If no target scope is requested, permission union across roles is enough.
        if target_scope_type is None or target_scope_value is None:
            return True

        for assignment, scope in assignment_rows:
            if _scope_contains(
                db,
                tenant_id=identity.tenant_id,
                assignment_scope_id=assignment.scope_id,
                target_scope_type=target_scope_type,
                target_scope_value=target_scope_value,
            ):
                return True

    # Backward-compatible fallback: legacy user_roles + role_scopes.
    fallback_rows = list(
        db.execute(
            select(UserRole, RoleScope)
            .join(RolePermission, RolePermission.role_id == UserRole.role_id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .outerjoin(RoleScope, RoleScope.user_role_id == UserRole.id)
            .where(
                UserRole.user_id == identity.user_id,
                UserRole.tenant_id == identity.tenant_id,
                UserRole.is_active.is_(True),
                Permission.family == required_family,
                RolePermission.scope_type == SCOPE_TYPE_TENANT,
                or_(
                    RolePermission.scope_value == identity.tenant_id,
                    RolePermission.scope_value == SCOPE_WILDCARD,
                ),
            )
        )
    )

    if not fallback_rows:
        return False

    if target_scope_type is None or target_scope_value is None:
        return True

    for _user_role, role_scope in fallback_rows:
        if role_scope is None:
            continue
        if role_scope.scope_type == SCOPE_TYPE_TENANT and role_scope.scope_value in (identity.tenant_id, SCOPE_WILDCARD):
            return True
        if role_scope.scope_type == target_scope_type and role_scope.scope_value == target_scope_value:
            return True

    return False


def _scope_contains(
    db: Session,
    *,
    tenant_id: str,
    assignment_scope_id: int,
    target_scope_type: str,
    target_scope_value: str,
) -> bool:
    assignment_scope = db.get(Scope, assignment_scope_id)
    if assignment_scope is None:
        return False

    if assignment_scope.tenant_id != tenant_id:
        return False

    if assignment_scope.scope_type == SCOPE_TYPE_TENANT:
        return assignment_scope.scope_value in (tenant_id, SCOPE_WILDCARD)

    target_scope = db.scalar(
        select(Scope).where(
            Scope.tenant_id == tenant_id,
            Scope.scope_type == target_scope_type,
            Scope.scope_value == target_scope_value,
        )
    )

    if target_scope is None:
        # Missing hierarchy data: fallback to exact scope match behavior.
        return (
            assignment_scope.scope_type == target_scope_type
            and assignment_scope.scope_value == target_scope_value
        )

    cursor = target_scope
    visited_ids: set[int] = set()
    while cursor is not None and cursor.id not in visited_ids:
        visited_ids.add(cursor.id)
        if cursor.id == assignment_scope.id:
            return True
        if cursor.parent_scope_id is None:
            break
        cursor = db.get(Scope, cursor.parent_scope_id)

    return False
