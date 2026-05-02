from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse, RefreshRequest
from app.schemas.session import SessionItem, SessionListResponse
from app.security.auth import (
    authenticate_user_db,
    create_access_token,
    get_identity_by_user_id,
)
from app.security.dependencies import (
    RequestIdentity,
    require_authenticated_identity,
    require_permission,
)
from app.services.refresh_token_service import (
    issue_refresh_token,
    revoke_tokens_for_session,
    revoke_tokens_for_user,
    rotate_refresh_token,
)
from app.services.security_event_service import record_security_event
from app.services.session_service import (
    create_login_session,
    list_user_sessions,
    revoke_all_sessions_for_user,
    revoke_session,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
    db: Session = Depends(get_db),
) -> LoginResponse:
    tenant_id = (x_tenant_id or "").strip() or "default"
    identity = authenticate_user_db(
        db,
        request.username,
        request.password,
        tenant_id=tenant_id,
    )
    if not identity:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    session = create_login_session(db, identity.user_id, tenant_id)
    identity.session_id = session.session_id
    access_token = create_access_token(identity)

    # Issue a persisted refresh token. Raw value is returned once to the client;
    # only the SHA-256 hash is stored in the DB.
    # INVARIANT: raw_refresh_token must never be logged or stored elsewhere.
    raw_refresh_token, _ = issue_refresh_token(
        db,
        user_id=identity.user_id,
        tenant_id=tenant_id,
        session_id=session.session_id,
    )
    record_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=identity.user_id,
        event_type="REFRESH_TOKEN.ISSUED",
        resource_type="refresh_token",
        resource_id=session.session_id,
        detail="login",
    )
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=raw_refresh_token,
        user=AuthUser(
            user_id=identity.user_id,
            username=identity.username,
            email=identity.email,
            tenant_id=identity.tenant_id,
            role_code=identity.role_code,
            session_id=identity.session_id,
        ),
    )


@router.post("/refresh", response_model=LoginResponse)
def refresh(
    request: RefreshRequest,
    x_tenant_id: str = Header("default", alias="X-Tenant-ID"),
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Rotate a persisted refresh token and return a new access + refresh pair.

    INVARIANT: Identity is derived from the persisted token record, NOT from
    client-supplied claims. The client cannot elevate privileges via refresh.

    Option A: The old Bearer-token-only refresh path is removed. This endpoint
    requires a refresh_token body field (Pydantic validates at the boundary).
    """
    tenant_id = (x_tenant_id or "").strip() or "default"

    # rotate_refresh_token validates (expired/revoked/rotated/unknown = None)
    # then atomically marks the old token as rotated and issues a new one.
    result = rotate_refresh_token(db, raw_token=request.refresh_token, tenant_id=tenant_id)
    if result is None:
        # Emit reuse-rejection event regardless of failure reason — timing
        # uniformity prevents distinguishing expired vs rotated vs unknown.
        record_security_event(
            db,
            tenant_id=tenant_id,
            actor_user_id=None,
            event_type="REFRESH_TOKEN.REUSE_REJECTED",
            resource_type="refresh_token",
            resource_id=None,
            detail="invalid_or_expired",
        )
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_raw_token, new_record = result

    # INVARIANT: Identity is fully re-derived from the DB using user_id and
    # tenant_id from the persisted record. Client-supplied X-Tenant-ID was only
    # used to scope the token lookup; it cannot override the record's tenant.
    identity = get_identity_by_user_id(db, new_record.user_id, new_record.tenant_id)
    if identity is None:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    identity.session_id = new_record.session_id
    access_token = create_access_token(identity)

    record_security_event(
        db,
        tenant_id=new_record.tenant_id,
        actor_user_id=identity.user_id,
        event_type="REFRESH_TOKEN.ROTATED",
        resource_type="refresh_token",
        resource_id=new_record.token_id,
        detail="rotated",
    )
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=new_raw_token,
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
    # Revoke all refresh tokens linked to this session so they cannot be used
    # after the session is explicitly terminated.
    revoke_tokens_for_session(
        db,
        session_id=identity.session_id,
        tenant_id=identity.tenant_id,
        reason="logout",
    )
    db.commit()
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
    # Revoke all refresh tokens for the user across all sessions.
    revoke_tokens_for_user(
        db,
        user_id=identity.user_id,
        tenant_id=identity.tenant_id,
        reason="logout_all",
    )
    db.commit()
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
        for item in list_user_sessions(
            db, user_id=identity.user_id, tenant_id=identity.tenant_id
        )
    ]
    return SessionListResponse(sessions=sessions)


@router.post("/sessions/{session_id}/revoke")
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


# Backward-compatible alias for older clients.
@router.delete("/sessions/{session_id}")
def admin_revoke_session_legacy(
    session_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("ADMIN")),
):
    return admin_revoke_session(session_id=session_id, db=db, identity=identity)
