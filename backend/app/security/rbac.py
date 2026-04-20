import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.rbac import (
    Permission,
    Role,
    RolePermission,
    RoleScope,
    Scope,
    UserRole,
    UserRoleAssignment,
)

PermissionFamily = Literal["VIEW", "EXECUTE", "APPROVE", "CONFIGURE", "ADMIN"]

# INVARIANT: These mappings are FROZEN per Phase 6 governance. Do NOT modify
# without a Phase 7+ design gate. ADM/OTS intentionally lack EXECUTE —
# they must impersonate an OPR to perform execution actions.
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
    "PLN": {"VIEW"},
    "INV": {"VIEW"},
}

# INTENT: Maps fine-grained action codes to their parent permission family.
# Used for both static impersonation checks and DB-backed permission lookups.
ACTION_CODE_REGISTRY: dict[str, PermissionFamily] = {
    "execution.start": "EXECUTE",
    "execution.complete": "EXECUTE",
    "execution.report_quantity": "EXECUTE",
    "execution.pause": "EXECUTE",
    "execution.resume": "EXECUTE",
    "execution.start_downtime": "EXECUTE",
    "execution.end_downtime": "EXECUTE",
    "approval.create": "APPROVE",
    "approval.decide": "APPROVE",
    "admin.impersonation.create": "ADMIN",
    "admin.impersonation.revoke": "ADMIN",
    "admin.user.manage": "ADMIN",
}

# EDGE: Aliases are resolved at check time in _normalize_role_code, never
# persisted in the DB. This allows seed data to use human-friendly names
# (e.g., "OPERATOR") while the canonical code ("OPR") is the stored value.
ROLE_ALIASES: dict[str, str] = {
    "OPERATOR": "OPR",
    "SUPERVISOR": "SUP",
    "SHIFT_LEADER": "SUP",
    "IE": "IEP",
    "PROCESS": "IEP",
    "QA": "QCI",
    "PLANNER": "PLN",
    "INVENTORY": "INV",
}

SCOPE_TYPE_TENANT = "tenant"
SCOPE_TYPE_PLANT = "plant"
SCOPE_TYPE_AREA = "area"
SCOPE_TYPE_LINE = "line"
SCOPE_TYPE_STATION = "station"
SCOPE_TYPE_EQUIPMENT = "equipment"
SCOPE_WILDCARD = "*"

# INVARIANT: ADM/OTS cannot be impersonation *targets*. An admin impersonating
# another admin would circumvent audit separation. Only non-elevated roles
# (OPR, SUP, etc.) may be used as acting_role_code.
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
        role_code = _normalize_role_code(
            str(item.get("role_code")) if item.get("role_code") is not None else None
        )
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

    role = Role(
        code=code,
        name=code,
        description=f"System role {code}",
        role_type="system",
        is_system=True,
        is_active=True,
    )
    db.add(role)
    db.flush()
    return role


def _get_or_create_permission(db: Session, family: PermissionFamily) -> Permission:
    permission = db.scalar(select(Permission).where(Permission.code == family))
    if permission:
        if permission.family != family or permission.action_code is not None:
            permission.family = family
            permission.action_code = None
            db.flush()
        return permission

    permission = Permission(
        code=family,
        family=family,
        action_code=None,
        description=f"{family} permission family",
    )
    db.add(permission)
    db.flush()
    return permission


def _get_or_create_action_permission(
    db: Session, action_code: str, family: PermissionFamily
) -> Permission:
    permission = db.scalar(select(Permission).where(Permission.code == action_code))
    if permission:
        if permission.action_code != action_code or permission.family != family:
            permission.action_code = action_code
            permission.family = family
            db.flush()
        return permission

    permission = Permission(
        code=action_code,
        family=family,
        action_code=action_code,
        description=f"Action permission: {action_code}",
    )
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

    permission_by_action: dict[str, Permission] = {}
    for action_code, family in ACTION_CODE_REGISTRY.items():
        permission_by_action[action_code] = _get_or_create_action_permission(
            db, action_code, family
        )

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
            if existing_link is None:
                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                        scope_type=SCOPE_TYPE_TENANT,
                        scope_value=SCOPE_WILDCARD,
                        effect="allow",
                    )
                )

        for action_code, family in ACTION_CODE_REGISTRY.items():
            if family not in families:
                continue
            action_permission = permission_by_action[action_code]
            existing_action_link = db.scalar(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == action_permission.id,
                    RolePermission.scope_type == SCOPE_TYPE_TENANT,
                    RolePermission.scope_value == SCOPE_WILDCARD,
                )
            )
            if existing_action_link is None:
                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=action_permission.id,
                        scope_type=SCOPE_TYPE_TENANT,
                        scope_value=SCOPE_WILDCARD,
                        effect="allow",
                    )
                )

    for user in _load_default_users():
        role_code = _normalize_role_code(user.get("role_code"))
        if role_code is None or role_code not in role_by_code:
            continue

        tenant_id = str(user["tenant_id"])

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

    # WHY: When impersonating, permission is resolved from the *acting* role's
    # static family set — the real user's DB-stored permissions are bypassed.
    # This ensures impersonation cannot silently escalate beyond the acting role.
    acting = getattr(identity, "acting_role_code", None)
    if acting:
        acting_families = SYSTEM_ROLE_FAMILIES.get(acting, set())
        return required_family in acting_families

    result = _evaluate_permission_rows(
        db,
        identity=identity,
        required_family=required_family,
        required_action_code=None,
        target_scope_type=target_scope_type,
        target_scope_value=target_scope_value,
    )
    return bool(result)


def has_action(
    db: Session,
    identity: IdentityLike,
    action_code: str,
    target_scope_type: str | None = None,
    target_scope_value: str | None = None,
) -> bool:
    if not identity.is_authenticated:
        return False

    # INTENT: Mirrors has_permission's impersonation path — acting role is
    # checked against static SYSTEM_ROLE_FAMILIES, not DB permissions.
    acting = getattr(identity, "acting_role_code", None)
    if acting:
        acting_families = SYSTEM_ROLE_FAMILIES.get(acting, set())
        required_family = ACTION_CODE_REGISTRY.get(action_code)
        if required_family is None:
            return False
        return required_family in acting_families

    result = _evaluate_permission_rows(
        db,
        identity=identity,
        required_family=None,
        required_action_code=action_code,
        target_scope_type=target_scope_type,
        target_scope_value=target_scope_value,
    )
    return bool(result)


def _evaluate_permission_rows(
    db: Session,
    *,
    identity: IdentityLike,
    required_family: PermissionFamily | None,
    required_action_code: str | None,
    target_scope_type: str | None,
    target_scope_value: str | None,
) -> bool | None:
    now = datetime.now(timezone.utc)

    assignment_rows = list(
        db.execute(
            _build_assignment_query(
                identity, now, required_family, required_action_code
            )
        )
    )

    # WHY: Deny-wins evaluation — a single "deny" row overrides any number of
    # "allow" rows. This prevents permission escalation via additive grants.
    allow_match = False
    deny_match = False
    for assignment, _scope, effect in assignment_rows:
        in_scope = True
        if target_scope_type is not None and target_scope_value is not None:
            in_scope = _scope_contains(
                db,
                tenant_id=identity.tenant_id,
                assignment_scope_id=assignment.scope_id,
                target_scope_type=target_scope_type,
                target_scope_value=target_scope_value,
            )

        if not in_scope:
            continue
        if effect == "deny":
            deny_match = True
        else:
            allow_match = True

    if deny_match:
        return False
    if allow_match:
        return True

    fallback_rows = list(
        db.execute(
            _build_fallback_query(identity, required_family, required_action_code)
        )
    )

    allow_match = False
    deny_match = False
    for _user_role, role_scope, effect in fallback_rows:
        if target_scope_type is None or target_scope_value is None:
            in_scope = True
        elif role_scope is None:
            in_scope = False
        elif role_scope.scope_type == SCOPE_TYPE_TENANT and role_scope.scope_value in (
            identity.tenant_id,
            SCOPE_WILDCARD,
        ):
            in_scope = True
        else:
            in_scope = (
                role_scope.scope_type == target_scope_type
                and role_scope.scope_value == target_scope_value
            )

        if not in_scope:
            continue
        if effect == "deny":
            deny_match = True
        else:
            allow_match = True

    if deny_match:
        return False
    if allow_match:
        return True
    return None


def _build_assignment_query(
    identity: IdentityLike,
    now: datetime,
    required_family: PermissionFamily | None,
    required_action_code: str | None,
):
    statement = (
        select(UserRoleAssignment, Scope, RolePermission.effect)
        .join(RolePermission, RolePermission.role_id == UserRoleAssignment.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .join(Scope, Scope.id == UserRoleAssignment.scope_id)
        .where(
            UserRoleAssignment.user_id == identity.user_id,
            UserRoleAssignment.is_active.is_(True),
            or_(
                UserRoleAssignment.valid_from.is_(None),
                UserRoleAssignment.valid_from <= now,
            ),
            or_(
                UserRoleAssignment.valid_to.is_(None),
                UserRoleAssignment.valid_to >= now,
            ),
            Scope.tenant_id == identity.tenant_id,
            RolePermission.scope_type == SCOPE_TYPE_TENANT,
            or_(
                RolePermission.scope_value == identity.tenant_id,
                RolePermission.scope_value == SCOPE_WILDCARD,
            ),
        )
    )
    if required_family is not None:
        statement = statement.where(Permission.family == required_family)
    if required_action_code is not None:
        statement = statement.where(Permission.action_code == required_action_code)
    return statement


def _build_fallback_query(
    identity: IdentityLike,
    required_family: PermissionFamily | None,
    required_action_code: str | None,
):
    statement = (
        select(UserRole, RoleScope, RolePermission.effect)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .outerjoin(RoleScope, RoleScope.user_role_id == UserRole.id)
        .where(
            UserRole.user_id == identity.user_id,
            UserRole.tenant_id == identity.tenant_id,
            UserRole.is_active.is_(True),
            RolePermission.scope_type == SCOPE_TYPE_TENANT,
            or_(
                RolePermission.scope_value == identity.tenant_id,
                RolePermission.scope_value == SCOPE_WILDCARD,
            ),
        )
    )
    if required_family is not None:
        statement = statement.where(Permission.family == required_family)
    if required_action_code is not None:
        statement = statement.where(Permission.action_code == required_action_code)
    return statement


def _scope_contains(
    db: Session,
    *,
    tenant_id: str,
    assignment_scope_id: int,
    target_scope_type: str,
    target_scope_value: str,
) -> bool:
    assignment_scope = db.get(Scope, assignment_scope_id)
    if assignment_scope is None or assignment_scope.tenant_id != tenant_id:
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

    # WHY: Walk up the scope tree (station→line→plant→tenant) to check if
    # the user's assignment scope contains the target. visited_ids guards
    # against cycles in malformed scope hierarchies.
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
