from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ImpersonationCreateRequest(BaseModel):
    acting_role_code: str = Field(..., min_length=1, max_length=32)
    reason: str = Field(..., min_length=1, max_length=512)
    # INVARIANT: duration_minutes bounded [1, 480] — max 8 hours per
    # governance rules. Default 60 min for short impersonation sessions.
    duration_minutes: int = Field(default=60, ge=1, le=480)

    # INTENT: Normalize to uppercase to match the role_code registry —
    # prevents case mismatch against FORBIDDEN_ACTING_ROLES in the service.
    @field_validator("acting_role_code")
    @classmethod
    def normalize_acting_role_code(cls, v: str) -> str:
        return v.strip().upper()


class ImpersonationResponse(BaseModel):
    id: int
    real_user_id: str
    real_role_code: str
    acting_role_code: str
    tenant_id: str
    reason: str
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    # WHY: is_active is a computed property surfaced in the response — it
    # reflects (not revoked AND not expired), not a stored DB column.
    is_active: bool

    model_config = {"from_attributes": True}


class ImpersonationAuditLogResponse(BaseModel):
    id: int
    session_id: int
    real_user_id: str
    acting_role_code: str
    tenant_id: str
    event_type: str
    permission_family: str | None
    endpoint: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
