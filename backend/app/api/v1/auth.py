from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse
from app.schemas.session import SessionItem, SessionListResponse
from app.security.auth import authenticate_user_db, create_access_token
from app.security.dependencies import RequestIdentity, require_authenticated_identity, require_permission
from app.services.session_service import create_login_session, list_user_sessions, revoke_all_sessions_for_user, revoke_session

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    identity = authenticate_user_db(db, request.username, request.password)
    if not identity:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    session = create_login_session(db, identity.user_id, identity.tenant_id)
    identity.session_id = session.session_id
    access_token = create_access_token(identity)
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=AuthUser(
            user_id=identity.user_id,
            username=identity.username,
            email=identity.email,
            tenant_id=identity.tenant_id,
            role_code=identity.role_code,
            session_id=identity.session_id,
        ),
    )


@router.get("/me", response_model=AuthUser)
def me(identity: RequestIdentity = Depends(require_authenticated_identity)) -> AuthUser:
    return AuthUser(
        user_id=identity.user_id,
        username=identity.username,
        email=identity.email,
        tenant_id=identity.tenant_id,
        role_code=identity.role_code,
        session_id=identity.session_id,
    )


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    if identity.session_id is None:
        raise HTTPException(status_code=401, detail="Session is missing")
    ok = revoke_session(
        db,
        session_id=identity.session_id,
        tenant_id=identity.tenant_id,
        actor_user_id=identity.user_id,
        reason="logout",
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "ok", "revoked_session_id": identity.session_id}


@router.post("/logout-all")
def logout_all(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    revoked_count = revoke_all_sessions_for_user(
        db,
        user_id=identity.user_id,
        tenant_id=identity.tenant_id,
        reason="logout_all",
    )
    return {"status": "ok", "revoked_count": revoked_count}


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> SessionListResponse:
    sessions = [
        SessionItem(
            session_id=item.session_id,
            user_id=item.user_id,
            tenant_id=item.tenant_id,
            issued_at=item.issued_at,
            expires_at=item.expires_at,
            revoked_at=item.revoked_at,
            revoke_reason=item.revoke_reason,
        )
        for item in list_user_sessions(db, user_id=identity.user_id, tenant_id=identity.tenant_id)
    ]
    return SessionListResponse(sessions=sessions)


@router.delete("/sessions/{session_id}")
def admin_revoke_session(
    session_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("ADMIN")),
):
    ok = revoke_session(
        db,
        session_id=session_id,
        tenant_id=identity.tenant_id,
        actor_user_id=identity.user_id,
        reason="admin_revoke",
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "ok", "revoked_session_id": session_id}
