from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ApprovalStatus = Literal["PENDING", "APPROVED", "REJECTED", "CANCELLED"]
ApprovalDecisionType = Literal["APPROVED", "REJECTED"]


class ApprovalCreateRequest(BaseModel):
    action_type: str = Field(..., min_length=1, max_length=64)
    subject_type: str | None = Field(default=None, max_length=64)
    subject_ref: str | None = Field(default=None, max_length=256)
    reason: str = Field(..., min_length=1, max_length=512)

    @field_validator("action_type")
    @classmethod
    def normalize_action_type(cls, v: str) -> str:
        return v.strip().upper()


class ApprovalDecideRequest(BaseModel):
    decision: ApprovalDecisionType
    comment: str | None = Field(default=None, max_length=512)


class ApprovalRuleResponse(BaseModel):
    id: int
    action_type: str
    approver_role_code: str
    tenant_id: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalDecisionResponse(BaseModel):
    id: int
    request_id: int
    decider_id: str
    decider_role_code: str | None
    decision: str
    comment: str | None
    impersonation_session_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalRequestResponse(BaseModel):
    id: int
    tenant_id: str
    action_type: str
    requester_id: str
    requester_role_code: str | None
    subject_type: str | None
    subject_ref: str | None
    # P0-A-13: Governed resource identity fields (optional, for future generic approval adoption)
    governed_resource_type: str | None
    governed_resource_id: str | None
    governed_resource_display_ref: str | None
    governed_resource_tenant_id: str | None
    governed_resource_scope_ref: str | None
    governed_action_type: str | None
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
