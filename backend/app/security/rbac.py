import json
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.rbac import Permission, Role, RolePermission, RoleScope, UserRole

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

        user_role = db.scalar(
            select(UserRole).where(
                UserRole.user_id == str(user["user_id"]),
                UserRole.role_id == role_by_code[role_code].id,
                UserRole.tenant_id == str(user["tenant_id"]),
            )
        )
        if user_role is None:
            user_role = UserRole(
                user_id=str(user["user_id"]),
                role_id=role_by_code[role_code].id,
                tenant_id=str(user["tenant_id"]),
                is_active=True,
            )
            db.add(user_role)
            db.flush()
        elif not user_role.is_active:
            user_role.is_active = True
            db.flush()

        tenant_scope = db.scalar(
            select(RoleScope).where(
                RoleScope.user_role_id == user_role.id,
                RoleScope.scope_type == SCOPE_TYPE_TENANT,
                RoleScope.scope_value == str(user["tenant_id"]),
            )
        )
        if tenant_scope is None:
            db.add(
                RoleScope(
                    user_role_id=user_role.id,
                    scope_type=SCOPE_TYPE_TENANT,
                    scope_value=str(user["tenant_id"]),
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
) -> bool:
    if not identity.is_authenticated:
        return False

    # Impersonation path: resolve permissions from acting role's family set directly.
    # This fully replaces the DB lookup — the DB is not consulted for acting role grants.
    acting = getattr(identity, "acting_role_code", None)
    if acting:
        acting_families = SYSTEM_ROLE_FAMILIES.get(acting, set())
        return required_family in acting_families

    tenant_scope_exists = exists(
        select(RoleScope.id).where(
            RoleScope.user_role_id == UserRole.id,
            RoleScope.scope_type == SCOPE_TYPE_TENANT,
            or_(
                RoleScope.scope_value == identity.tenant_id,
                RoleScope.scope_value == SCOPE_WILDCARD,
            ),
        )
    )

    statement = (
        select(UserRole.id)
        .join(RolePermission, RolePermission.role_id == UserRole.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
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
            tenant_scope_exists,
        )
        .limit(1)
    )

    return db.scalar(statement) is not None
