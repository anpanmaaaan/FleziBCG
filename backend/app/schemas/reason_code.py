from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


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
