from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReasonCodeAllowedActions(BaseModel):
    """Server-derived Reason Code write capability guard (MMD-FULLSTACK-13B).

    Rules:
    - If user lacks admin.master_data.reason_code.manage, all actions are false.
    - DRAFT + manage: can_update, can_release, can_retire, can_create_sibling all true.
    - RELEASED + manage: can_retire, can_create_sibling true; others false.
    - RETIRED + manage: can_create_sibling true; others false.
    can_create_sibling = user can create another Reason Code (NOT clone/copy/bulk).
    """

    can_update: bool
    can_release: bool
    can_retire: bool
    can_create_sibling: bool


class ReasonCodeItem(BaseModel):
    """Read-only response schema for a single reason code."""

    reason_code_id: str
    tenant_id: str
    reason_domain: str
    reason_category: str
    reason_code: str
    reason_name: str
    description: str | None = None
    lifecycle_status: str
    requires_comment: bool
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    allowed_actions: ReasonCodeAllowedActions


class ReasonCodeCreateRequest(BaseModel):
    """Write schema for creating a Reason Code (always creates as DRAFT).

    Invariants enforced by extra="forbid":
    - tenant_id must NOT be sent by client (server derives from JWT)
    - lifecycle_status must NOT be sent by client (server always sets DRAFT)
    - reason_code_id must NOT be sent by client (server generates)
    - downtime_reason_id and any policy binding fields are forbidden
    """

    model_config = ConfigDict(extra="forbid")

    reason_domain: str
    reason_category: str
    reason_code: str
    reason_name: str
    description: str | None = None
    requires_comment: bool = False
    sort_order: int = 0
    is_active: bool = True


class ReasonCodeUpdateRequest(BaseModel):
    """Write schema for updating DRAFT Reason Code metadata.

    Invariants enforced by extra="forbid":
    - reason_code is immutable — not present
    - reason_domain is immutable — not present
    - reason_category is immutable — not present
    - lifecycle_status must NOT be set via PATCH
    - tenant_id must NOT be sent by client
    - downtime_reason_id and policy binding fields are forbidden
    """

    model_config = ConfigDict(extra="forbid")

    reason_name: str | None = None
    description: str | None = None
    requires_comment: bool | None = None
    sort_order: int | None = None
    is_active: bool | None = None
