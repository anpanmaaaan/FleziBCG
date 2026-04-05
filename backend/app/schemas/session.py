from datetime import datetime

from pydantic import BaseModel


class SessionItem(BaseModel):
    session_id: str
    user_id: str
    tenant_id: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None
    revoke_reason: str | None = None


class SessionListResponse(BaseModel):
    sessions: list[SessionItem]
