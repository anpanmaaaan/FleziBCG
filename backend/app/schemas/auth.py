from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUser(BaseModel):
    user_id: str
    username: str
    email: str | None = None
    tenant_id: str
    # WHY: role_code is Optional — it is a display hint carried in the JWT,
    # not a security gate. Authorization is checked per-request via
    # has_permission().
    role_code: str | None = None
    # EDGE: session_id is Optional for backward compatibility — JWTs issued
    # before session tracking was introduced do not carry this field.
    session_id: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUser
