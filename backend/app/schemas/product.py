from __future__ import annotations

from datetime import datetime
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
