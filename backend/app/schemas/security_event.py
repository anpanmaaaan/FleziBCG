from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SecurityEventItem(BaseModel):
    tenant_id: str
    actor_user_id: str | None = None
    event_type: str
    resource_type: str | None = None
    resource_id: str | None = None
    detail: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
