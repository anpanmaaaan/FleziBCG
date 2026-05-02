from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


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


def validate_product_type(value: str) -> str:
    normalized = value.strip().upper()
    if normalized not in _ALLOWED_PRODUCT_TYPES:
        raise ValueError("Invalid product_type")
    return normalized


_ALLOWED_VERSION_LIFECYCLE_STATUSES = {"DRAFT", "RELEASED", "RETIRED"}


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
    created_at: datetime
    updated_at: datetime
