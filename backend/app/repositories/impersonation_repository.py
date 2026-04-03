from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.impersonation import ImpersonationSession


def get_active_impersonation_session(
    db: Session,
    user_id: str,
    tenant_id: str,
) -> ImpersonationSession | None:
    now = datetime.now(timezone.utc)
    statement = (
        select(ImpersonationSession)
        .where(
            and_(
                ImpersonationSession.real_user_id == user_id,
                ImpersonationSession.tenant_id == tenant_id,
                ImpersonationSession.revoked_at.is_(None),
                ImpersonationSession.expires_at > now,
            )
        )
        .order_by(ImpersonationSession.created_at.desc())
        .limit(1)
    )
    return db.scalar(statement)


def get_session_by_id(db: Session, session_id: int) -> ImpersonationSession | None:
    return db.scalar(
        select(ImpersonationSession).where(ImpersonationSession.id == session_id)
    )


def has_active_session(db: Session, user_id: str, tenant_id: str) -> bool:
    return get_active_impersonation_session(db, user_id, tenant_id) is not None
