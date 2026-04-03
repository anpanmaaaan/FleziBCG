from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse
from app.security.auth import authenticate_user_db, create_access_token
from app.security.dependencies import RequestIdentity, require_authenticated_identity

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
    )
