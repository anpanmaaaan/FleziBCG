from fastapi import APIRouter, Depends, HTTPException

from app.schemas.auth import AuthUser, LoginRequest, LoginResponse
from app.security.auth import authenticate_user, create_access_token
from app.security.dependencies import RequestIdentity, require_authenticated_identity

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    identity = authenticate_user(request.username, request.password)
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
