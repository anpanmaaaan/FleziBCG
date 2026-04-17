from datetime import datetime

from pydantic import BaseModel


# INTENT: SessionItem is a flat read-only projection — exposes session
# metadata for the /auth/sessions list, not for session manipulation.
class SessionItem(BaseModel):
    session_id: str
    user_id: str
    tenant_id: str
    issued_at: datetime
    expires_at: datetime
    # EDGE: revoked_at / revoke_reason are None for active sessions —
    # presence of revoked_at is the canonical signal that a session is
    # no longer valid.
    revoked_at: datetime | None = None
    revoke_reason: str | None = None


class SessionListResponse(BaseModel):
    sessions: list[SessionItem]
