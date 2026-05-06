from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


_ALLOWED_PRODUCT_TYPES = {"FINISHED_GOOD", "SEMI_FINISHED", "COMPONENT"}


class ProductCreateRequest(BaseModel):
    product_code: str
    product_name: str
    product_type: str
    description: str | None = None
    display_metadata: dict[str, Any] | None = None


class ProductUpdateRequest(BaseModel):
    product_code: str | None = None
    product_name: str | None = None
    product_type: str | None = None
    description: str | None = None
    display_metadata: dict[str, Any] | None = None


class ProductVersionProductCapabilities(BaseModel):
    can_create: bool


class ProductBomCapabilities(BaseModel):
    can_create: bool


class ProductItem(BaseModel):
    product_id: str
    tenant_id: str
    product_code: str
    product_name: str
    product_type: str
    lifecycle_status: str
    description: str | None = None
    display_metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    product_version_capabilities: ProductVersionProductCapabilities
    bom_capabilities: ProductBomCapabilities


def validate_product_type(value: str) -> str:
    normalized = value.strip().upper()
    if normalized not in _ALLOWED_PRODUCT_TYPES:
        raise ValueError("Invalid product_type")
    return normalized


_ALLOWED_VERSION_LIFECYCLE_STATUSES = {"DRAFT", "RELEASED", "RETIRED"}


class ProductVersionAllowedActions(BaseModel):
    can_update: bool
    can_release: bool
    can_retire: bool
    can_create_sibling: bool


class ProductVersionItem(BaseModel):
    product_version_id: str
    tenant_id: str
    product_id: str
    version_code: str
    version_name: str | None = None
    lifecycle_status: str
    is_current: bool
    effective_from: date | None = None
    effective_to: date | None = None
    description: str | None = None
    bom_binding_required_for_release: bool = False
    created_at: datetime
    updated_at: datetime
    allowed_actions: ProductVersionAllowedActions


class ProductVersionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_code: str
    version_name: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    description: str | None = None
    bom_binding_required_for_release: bool = False


class ProductVersionUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_name: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    description: str | None = None
    bom_binding_required_for_release: bool | None = None


# ─── BOM Binding schemas — MMD-BE-14 ─────────────────────────────────────────


class BomBindingCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bom_id: str
    notes: str | None = None


class ProductVersionBomBindingAllowedActions(BaseModel):
    can_remove: bool


class ProductVersionBomBindingResponse(BaseModel):
    binding_id: str
    tenant_id: str
    product_id: str
    product_version_id: str
    bom_id: str
    binding_type: str
    binding_status: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str | None = None
    allowed_actions: ProductVersionBomBindingAllowedActions
