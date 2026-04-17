from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# WHY: CANCELLED is a terminal state distinct from REJECTED — a requester
# can cancel their own pending request before a decision is made.
ApprovalStatus = Literal["PENDING", "APPROVED", "REJECTED", "CANCELLED"]
ApprovalDecisionType = Literal["APPROVED", "REJECTED"]


class ApprovalCreateRequest(BaseModel):
    action_type: str = Field(..., min_length=1, max_length=64)
    # EDGE: subject_type and subject_ref are Optional — not all approval
    # actions reference a specific entity (e.g., config-change approvals).
    subject_type: str | None = Field(default=None, max_length=64)
    subject_ref: str | None = Field(default=None, max_length=256)
    reason: str = Field(..., min_length=1, max_length=512)

    # INTENT: Normalize to uppercase for case-insensitive matching against
    # approval_rules — the DB stores action_type in uppercase.
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
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
