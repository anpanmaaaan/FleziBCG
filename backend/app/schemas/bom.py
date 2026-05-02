from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


_ALLOWED_BOM_LIFECYCLE_STATUSES = {"DRAFT", "RELEASED", "RETIRED"}


class BomComponentItem(BaseModel):
    bom_item_id: str
    tenant_id: str
    bom_id: str
    component_product_id: str
    line_no: int
    quantity: float
    unit_of_measure: str
    scrap_factor: float | None = None
    reference_designator: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class BomItem(BaseModel):
    bom_id: str
    tenant_id: str
    product_id: str
    bom_code: str
    bom_name: str
    lifecycle_status: str
    effective_from: date | None = None
    effective_to: date | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class BomDetail(BomItem):
    items: list[BomComponentItem]
