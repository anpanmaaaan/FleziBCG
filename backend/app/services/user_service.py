import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Role
from app.models.user import User
from app.security.auth import pwd_context

logger = logging.getLogger(__name__)


def hash_password(plain_password: str) -> str:
    """Hash a plain password using bcrypt."""
    return pwd_context.hash(plain_password)


def get_or_create_user(
    db: Session,
    user_id: str,
    username: str,
    password: str,
    email: str | None = None,
    tenant_id: str = "default",
    is_active: bool = True,
) -> User:
    """Get existing user or create new one with hashed password."""
    existing = db.scalar(
        select(User).where(
            User.user_id == user_id,
            User.tenant_id == tenant_id,
        )
    )
    if existing:
        return existing

    password_hash = hash_password(password)
    user = User(
        user_id=user_id,
        username=username,
        email=email,
        password_hash=password_hash,
        tenant_id=tenant_id,
        is_active=is_active,
    )
    db.add(user)
    db.flush()
    logger.info("User created: user_id=%s username=%s tenant=%s", user_id, username, tenant_id)
    return user


def seed_demo_users(db: Session) -> None:
    """Seed demo users and assign them to roles via user_roles."""
    from app.models.rbac import UserRole, RoleScope

    # Get all system roles (they should be created by seed_rbac_core).
    roles_by_code = {}
    for role_code in ["ADM", "PMG", "SUP", "OPR", "QAL"]:
        role = db.scalar(select(Role).where(Role.code == role_code))
        if role is None:
            logger.warning("Role %s not found; skipping seed user assignment", role_code)
            continue
        roles_by_code[role_code] = role

    # Demo users: (user_id, username, password, email, role_code)
    demo_users = [
        ("adm-001", "admin", "password123", "admin@example.com", "ADM"),
        ("pmg-001", "manager", "password123", "manager@example.com", "PMG"),
        ("sup-001", "supervisor", "password123", "supervisor@example.com", "SUP"),
        ("opr-001", "operator", "password123", "operator@example.com", "OPR"),
        ("qal-001", "qa", "password123", "qa@example.com", "QAL"),
    ]

    tenant_id = "default"

    for user_id, username, password, email, role_code in demo_users:
        user = get_or_create_user(
            db,
            user_id=user_id,
            username=username,
            password=password,
            email=email,
            tenant_id=tenant_id,
        )

        if role_code not in roles_by_code:
            logger.warning("Role %s not found for user %s; skipping", role_code, username)
            continue

        # Check if user_role already exists.
        existing_ur = db.scalar(
            select(UserRole).where(
                UserRole.user_id == user.user_id,
                UserRole.role_id == roles_by_code[role_code].id,
                UserRole.tenant_id == tenant_id,
            )
        )
        if existing_ur:
            continue

        # Create user_role.
        user_role = UserRole(
            user_id=user.user_id,
            role_id=roles_by_code[role_code].id,
            tenant_id=tenant_id,
            is_active=True,
        )
        db.add(user_role)
        db.flush()

        # Create role_scope.
        db.add(
            RoleScope(
                user_role_id=user_role.id,
                scope_type="tenant",
                scope_value=tenant_id,
            )
        )

    db.commit()
    logger.info("Demo users seeded.")
