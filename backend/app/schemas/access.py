from pydantic import BaseModel


class RoleAssignmentRequest(BaseModel):
    user_id: str
    role_code: str
    is_active: bool = True


class RoleAssignmentResponse(BaseModel):
    id: int
    user_id: str
    role_code: str
    tenant_id: str
    is_active: bool


class ScopeAssignmentRequest(BaseModel):
    user_id: str
    role_code: str
    scope_type: str
    scope_value: str
    is_primary: bool = False


class ScopeAssignmentResponse(BaseModel):
    assignment_id: int
    user_id: str
    role_code: str
    scope_id: int
    tenant_id: str
    scope_type: str
    scope_value: str
    is_primary: bool
