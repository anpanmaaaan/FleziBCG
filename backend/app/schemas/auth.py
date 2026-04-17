from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    user_id: str
    username: str
    email: str | None = None
    tenant_id: str
    role_code: str | None = None
    session_id: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser
