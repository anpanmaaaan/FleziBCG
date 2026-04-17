from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.session import Session as AuthSession
from app.models.session import SessionAuditLog


def create_login_session(db: Session, user_id: str, tenant_id: str) -> AuthSession:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    session = AuthSession(
        session_id=str(uuid4()),
        user_id=user_id,
        tenant_id=tenant_id,
        issued_at=now,
        expires_at=expires_at,
    )
    db.add(session)
    db.flush()
    db.add(
        SessionAuditLog(
            session_id=session.session_id,
            tenant_id=tenant_id,
            actor_user_id=user_id,
            event_type="SESSION_CREATED",
            detail="login",
        )
    )
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: str) -> AuthSession | None:
    return db.scalar(select(AuthSession).where(AuthSession.session_id == session_id))


def is_session_active(db: Session, session_id: str, tenant_id: str) -> bool:
    session = db.scalar(
        select(AuthSession).where(
            AuthSession.session_id == session_id,
            AuthSession.tenant_id == tenant_id,
        )
    )
    if session is None:
        return False
    if session.revoked_at is not None:
        return False
    return session.expires_at > datetime.now(timezone.utc)


def revoke_session(
    db: Session,
    *,
    session_id: str,
    tenant_id: str,
    actor_user_id: str,
    reason: str,
) -> bool:
    session = get_session(db, session_id)
    if session is None or session.tenant_id != tenant_id:
        return False
    if session.revoked_at is not None:
        return True

    session.revoked_at = datetime.now(timezone.utc)
    session.revoke_reason = reason[:256]
    db.add(
        SessionAuditLog(
            session_id=session.session_id,
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type="SESSION_REVOKED",
            detail=reason[:512],
        )
    )
    db.commit()
    return True


def revoke_all_sessions_for_user(db: Session, *, user_id: str, tenant_id: str, reason: str) -> int:
    now = datetime.now(timezone.utc)
    active_sessions = list(
        db.scalars(
            select(AuthSession).where(
                AuthSession.user_id == user_id,
                AuthSession.tenant_id == tenant_id,
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > now,
            )
        )
    )
    for session in active_sessions:
        session.revoked_at = now
        session.revoke_reason = reason[:256]
        db.add(
            SessionAuditLog(
                session_id=session.session_id,
                tenant_id=tenant_id,
                actor_user_id=user_id,
                event_type="SESSION_REVOKED",
                detail=reason[:512],
            )
        )
    db.commit()
    return len(active_sessions)


def list_user_sessions(db: Session, *, user_id: str, tenant_id: str) -> list[AuthSession]:
    return list(
        db.scalars(
            select(AuthSession)
            .where(
                AuthSession.user_id == user_id,
                AuthSession.tenant_id == tenant_id,
            )
            .order_by(AuthSession.issued_at.desc())
        )
    )
