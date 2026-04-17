from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.impersonation import ImpersonationCreateRequest, ImpersonationResponse
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.impersonation_service import (
    create_impersonation_session,
    get_current_session_for_user,
    revoke_impersonation_session,
)

router = APIRouter(prefix="/impersonations", tags=["impersonation"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# INTENT: _to_response maps ORM model to Pydantic schema field-by-field to
# avoid leaking internal model attributes (e.g., SQLAlchemy state) into
# the API contract.
def _to_response(session) -> ImpersonationResponse:
    return ImpersonationResponse(
        id=session.id,
        real_user_id=session.real_user_id,
        real_role_code=session.real_role_code,
        acting_role_code=session.acting_role_code,
        tenant_id=session.tenant_id,
        reason=session.reason,
        expires_at=session.expires_at,
        revoked_at=session.revoked_at,
        created_at=session.created_at,
        is_active=session.is_active,
    )


# WHY: require_authenticated_identity (not require_permission) — impersonation
# authorization (ADM/OTS only, no admin-to-admin) is enforced in the service
# layer, not via route-level RBAC.
@router.post("", response_model=ImpersonationResponse, status_code=201)
def create_session(
    request_data: ImpersonationCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    """
    Create a temporary impersonation session.

    Allowed callers: ADM, OTS.
    acting_role_code must not be ADM or OTS.
    Only one active session per user per tenant is permitted.
    """
    try:
        session = create_impersonation_session(
            db=db,
            real_user_id=identity.user_id,
            real_role_code=identity.role_code,
            tenant_id=identity.tenant_id,
            request_data=request_data,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _to_response(session)


# EDGE: Returns None (not 404) when no active impersonation session exists —
# absence is a normal state, not an error.
@router.get("/current", response_model=ImpersonationResponse | None)
def get_current(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    """
    Return the caller's active impersonation session, if any.
    Returns null when no active session exists.
    """
    session = get_current_session_for_user(db, identity.user_id, identity.tenant_id)
    if session is None:
        return None
    return _to_response(session)


@router.post("/{session_id}/revoke", response_model=ImpersonationResponse)
def revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    """
    Revoke an impersonation session.

    Users may only revoke their own sessions.
    Revocation is immediate and irreversible.
    """
    try:
        session = revoke_impersonation_session(
            db=db,
            session_id=session_id,
            requesting_user_id=identity.user_id,
            tenant_id=identity.tenant_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _to_response(session)
