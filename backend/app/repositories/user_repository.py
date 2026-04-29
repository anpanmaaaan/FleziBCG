from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def list_users_by_tenant(
    db: Session,
    *,
    tenant_id: str,
    include_inactive: bool = False,
) -> list[User]:
    query = select(User).where(User.tenant_id == tenant_id)
    if not include_inactive:
        query = query.where(User.is_active.is_(True))
    query = query.order_by(User.username.asc())
    return list(db.scalars(query))


def get_user_by_user_id(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
) -> User | None:
    return db.scalar(
        select(User).where(
            User.user_id == user_id,
            User.tenant_id == tenant_id,
        )
    )


def set_user_active(
    db: Session,
    *,
    user_id: str,
    tenant_id: str,
    is_active: bool,
) -> User | None:
    user = get_user_by_user_id(db, user_id=user_id, tenant_id=tenant_id)
    if user is None:
        return None
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user
