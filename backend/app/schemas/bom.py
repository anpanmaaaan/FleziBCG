from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator


_ALLOWED_BOM_LIFECYCLE_STATUSES = {"DRAFT", "RELEASED", "RETIRED"}


# ─── Write request schemas ────────────────────────────────────────────────────

class BomCreateRequest(BaseModel):
    """Request schema for POST /products/{product_id}/boms.

    Boundary lock (MMD-BE-12):
    - lifecycle_status, bom_id, tenant_id, product_id, product_version_id,
      created_at, updated_at are all forbidden.
    - extra="forbid" ensures unrecognised fields are rejected (422).
    """

    model_config = ConfigDict(extra="forbid")

    bom_code: str
    bom_name: str
    effective_from: date | None = None
    effective_to: date | None = None
    description: str | None = None

    @model_validator(mode="after")
    def _validate_effective_date_range(self) -> "BomCreateRequest":
        if self.effective_from and self.effective_to:
            if self.effective_from > self.effective_to:
                raise ValueError("effective_from must be <= effective_to")
        return self


class BomUpdateRequest(BaseModel):
    """Request schema for PATCH /products/{product_id}/boms/{bom_id}.

    Boundary lock (MMD-BE-12):
    - bom_code is immutable after creation — not present in this schema.
    - lifecycle_status is forbidden (lifecycle transitions are explicit commands).
    - product_version_id, bom_id, tenant_id, product_id, created_at, updated_at forbidden.
    - All fields are optional; no-op update returns current state.
    """

    model_config = ConfigDict(extra="forbid")

    bom_name: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    description: str | None = None

    @model_validator(mode="after")
    def _validate_effective_date_range(self) -> "BomUpdateRequest":
        if self.effective_from and self.effective_to:
            if self.effective_from > self.effective_to:
                raise ValueError("effective_from must be <= effective_to")
        return self


class BomItemCreateRequest(BaseModel):
    """Request schema for POST /products/{product_id}/boms/{bom_id}/items.

    Boundary lock (MMD-BE-12):
    - bom_item_id, bom_id, tenant_id, created_at, updated_at forbidden.
    - No material_reservation, lot_id, backflush, or inventory fields.
    """

    model_config = ConfigDict(extra="forbid")

    component_product_id: str
    line_no: int
    quantity: float
    unit_of_measure: str
    scrap_factor: float | None = None
    reference_designator: str | None = None
    notes: str | None = None


class BomItemUpdateRequest(BaseModel):
    """Request schema for PATCH /products/{product_id}/boms/{bom_id}/items/{bom_item_id}.

    Boundary lock (MMD-BE-12):
    - component_product_id and line_no are immutable after item creation (governance contract).
    - bom_item_id, bom_id, tenant_id, created_at, updated_at forbidden.
    """

    model_config = ConfigDict(extra="forbid")

    quantity: float | None = None
    unit_of_measure: str | None = None
    scrap_factor: float | None = None
    reference_designator: str | None = None
    notes: str | None = None


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
