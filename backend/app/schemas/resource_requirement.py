from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ResourceRequirementCreateRequest(BaseModel):
    required_resource_type: str
    required_capability_code: str
    quantity_required: int = 1
    notes: str | None = None
    metadata_json: str | None = None


class ResourceRequirementUpdateRequest(BaseModel):
    required_resource_type: str | None = None
    required_capability_code: str | None = None
    quantity_required: int | None = None
    notes: str | None = None
    metadata_json: str | None = None


class ResourceRequirementItem(BaseModel):
    requirement_id: str
    tenant_id: str
    routing_id: str
    operation_id: str
    required_resource_type: str
    required_capability_code: str
    quantity_required: int
    notes: str | None = None
    metadata_json: str | None = None
    created_at: datetime
    updated_at: datetime
