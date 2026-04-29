from pydantic import BaseModel


class UserLifecycleItem(BaseModel):
    user_id: str
    username: str
    email: str | None = None
    tenant_id: str
    is_active: bool


class UserLifecycleListResponse(BaseModel):
    users: list[UserLifecycleItem]


class UserLifecycleActionResponse(BaseModel):
    status: str
    user_id: str
    tenant_id: str
    is_active: bool
    action: str
