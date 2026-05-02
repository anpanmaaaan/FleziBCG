from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


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
    # WHY: refresh_token is only present at issuance/rotation time. It is
    # optional (None) so the schema works for both login and other responses
    # that historically did not include it.
    refresh_token: str | None = None
    user: AuthUser
