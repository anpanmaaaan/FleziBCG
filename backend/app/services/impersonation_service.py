import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.impersonation import ImpersonationAuditLog, ImpersonationSession
from app.repositories.impersonation_repository import (
    get_active_impersonation_session,
    get_session_by_id,
    has_active_session,
)
from app.schemas.impersonation import ImpersonationCreateRequest
from app.security.rbac import FORBIDDEN_ACTING_ROLES, SYSTEM_ROLE_FAMILIES

logger = logging.getLogger(__name__)

# INVARIANT: Only ADM and OTS may create impersonation sessions.
# This is the entry guard; FORBIDDEN_ACTING_ROLES in rbac.py is the
# complementary guard preventing ADM/OTS from being *targets*.
ALLOWED_IMPERSONATORS = frozenset({"ADM", "OTS"})
MAX_DURATION_MINUTES = settings.impersonation_max_duration_minutes


def _normalize(code: str | None) -> str | None:
    if not code:
        return None
    return code.strip().upper()


def _log_event(
    db: Session,
    session: ImpersonationSession,
    event_type: str,
    permission_family: str | None = None,
    endpoint: str | None = None,
) -> None:
    audit_entry = ImpersonationAuditLog(
        session_id=session.id,
        real_user_id=session.real_user_id,
        acting_role_code=session.acting_role_code,
        tenant_id=session.tenant_id,
        event_type=event_type,
        permission_family=permission_family,
        endpoint=endpoint[:256] if endpoint else None,
    )
    db.add(audit_entry)


def create_impersonation_session(
    db: Session,
    real_user_id: str,
    real_role_code: str | None,
    tenant_id: str,
    request_data: ImpersonationCreateRequest,
) -> ImpersonationSession:
    real_role = _normalize(real_role_code)
    if real_role not in ALLOWED_IMPERSONATORS:
        raise PermissionError(
            f"Role {real_role!r} is not permitted to create impersonation sessions. "
            f"Required: {sorted(ALLOWED_IMPERSONATORS)}"
        )

    acting_role = _normalize(request_data.acting_role_code)
    if acting_role is None:
        raise ValueError("acting_role_code is required")

    if acting_role in FORBIDDEN_ACTING_ROLES:
        raise ValueError(
            f"acting_role_code {acting_role!r} is forbidden. "
            f"Elevated roles cannot be impersonated: {sorted(FORBIDDEN_ACTING_ROLES)}"
        )

    if acting_role not in SYSTEM_ROLE_FAMILIES:
        raise ValueError(
            f"acting_role_code {acting_role!r} is not a recognised system role"
        )

    duration = request_data.duration_minutes
    if duration > MAX_DURATION_MINUTES:
        raise ValueError(
            f"duration_minutes {duration} exceeds maximum {MAX_DURATION_MINUTES}"
        )

    # INVARIANT: One active session per user per tenant. This prevents
    # stacking sessions to combine permission families.
    if has_active_session(db, real_user_id, tenant_id):
        raise ValueError(
            "An active impersonation session already exists. Revoke it first."
        )

    session = ImpersonationSession(
        real_user_id=real_user_id,
        real_role_code=real_role,
        acting_role_code=acting_role,
        tenant_id=tenant_id,
        reason=request_data.reason.strip(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=duration),
    )
    db.add(session)
    db.flush()

    _log_event(db, session, "SESSION_CREATED")

    db.commit()
    db.refresh(session)

    logger.info(
        "Impersonation session created: real_user=%s real_role=%s acting_role=%s "
        "tenant=%s session_id=%d reason=%r expires_at=%s",
        real_user_id,
        real_role,
        acting_role,
        tenant_id,
        session.id,
        request_data.reason,
        session.expires_at.isoformat(),
    )
    return session


def revoke_impersonation_session(
    db: Session,
    session_id: int,
    requesting_user_id: str,
    tenant_id: str,
) -> ImpersonationSession:
    session = get_session_by_id(db, session_id)
    if session is None or session.tenant_id != tenant_id:
        raise LookupError("Impersonation session not found")

    if session.real_user_id != requesting_user_id:
        raise PermissionError("Not authorized to revoke this session")

    if session.revoked_at is not None:
        raise ValueError("Session has already been revoked")

    session.revoked_at = datetime.now(timezone.utc)
    _log_event(db, session, "SESSION_REVOKED")
    db.commit()
    db.refresh(session)

    logger.info(
        "Impersonation session revoked: session_id=%d real_user=%s acting_role=%s tenant=%s",
        session.id,
        session.real_user_id,
        session.acting_role_code,
        session.tenant_id,
    )
    return session


def get_current_session_for_user(
    db: Session,
    user_id: str,
    tenant_id: str,
) -> ImpersonationSession | None:
    return get_active_impersonation_session(db, user_id, tenant_id)


def log_impersonation_permission_use(
    db: Session,
    session: ImpersonationSession,
    permission_family: str,
    endpoint: str = "",
) -> None:
    try:
        _log_event(
            db,
            session,
            "PERMISSION_USED",
            permission_family=permission_family,
            endpoint=endpoint,
        )
        db.commit()
    except Exception:
        logger.exception(
            "Failed to write impersonation audit log for session_id=%d permission=%s",
            session.id,
            permission_family,
        )
