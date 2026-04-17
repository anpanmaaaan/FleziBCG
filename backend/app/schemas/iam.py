from datetime import datetime

from pydantic import BaseModel

from app.schemas.auth import AuthUser


class ScopeSummary(BaseModel):
    id: int
    tenant_id: str
    scope_type: str
    scope_value: str
    parent_scope_id: int | None = None


class RoleAssignmentSummary(BaseModel):
    assignment_id: int | None = None
    role_code: str
    is_primary: bool = False
    is_active: bool = True
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    scope: ScopeSummary


class ImpersonationSummary(BaseModel):
    active: bool
    session_id: int | None = None
    acting_role_code: str | None = None
    expires_at: datetime | None = None


# INTENT: MeCapabilitiesResponse bundles user identity + role assignments +
# impersonation state in one response — avoids multiple round-trips for
# frontend persona hydration.
class MeCapabilitiesResponse(BaseModel):
    user: AuthUser
    assignments: list[RoleAssignmentSummary]
    primary_assignment: RoleAssignmentSummary | None = None
    impersonation: ImpersonationSummary


class CreateCustomRoleRequest(BaseModel):
    code: str
    name: str
    description: str | None = None
    base_role_code: str
    # EDGE: allow_action_codes defaults to empty list — a custom role with no
    # explicit actions inherits only the base role's permission family.
    allow_action_codes: list[str] = []


class CustomRoleResponse(BaseModel):
    id: int
    code: str
    tenant_id: str
    role_type: str
    base_role_id: int | None = None
    owner_user_id: str | None = None
    is_active: bool
