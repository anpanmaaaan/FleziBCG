from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.bom import Bom, BomItem as BomItemRow
from app.repositories.bom_repository import (
    create_bom_item_row,
    create_bom_row,
    delete_bom_item_row,
    get_bom_by_code,
    get_bom_by_id as get_bom_row_with_product,
    get_bom_item_by_id,
    get_bom_item_by_line_no,
    get_bom_row,
    list_boms_by_product,
    update_bom_item_row,
    update_bom_row,
)
from app.repositories.product_repository import get_product_by_id as get_product_row
from app.schemas.bom import (
    BomComponentItem,
    BomCreateRequest,
    BomDetail,
    BomItem,
    BomItemCreateRequest,
    BomItemUpdateRequest,
    BomUpdateRequest,
)
from app.services.security_event_service import record_security_event


def _to_component_item(row: BomItemRow) -> BomComponentItem:
    return BomComponentItem(
        bom_item_id=row.bom_item_id,
        tenant_id=row.tenant_id,
        bom_id=row.bom_id,
        component_product_id=row.component_product_id,
        line_no=row.line_no,
        quantity=row.quantity,
        unit_of_measure=row.unit_of_measure,
        scrap_factor=row.scrap_factor,
        reference_designator=row.reference_designator,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_bom_item(row: Bom) -> BomItem:
    return BomItem(
        bom_id=row.bom_id,
        tenant_id=row.tenant_id,
        product_id=row.product_id,
        bom_code=row.bom_code,
        bom_name=row.bom_name,
        lifecycle_status=row.lifecycle_status,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        description=row.description,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_bom_detail(row: Bom) -> BomDetail:
    ordered_items = sorted(row.items, key=lambda x: (x.line_no, x.bom_item_id))
    return BomDetail(
        bom_id=row.bom_id,
        tenant_id=row.tenant_id,
        product_id=row.product_id,
        bom_code=row.bom_code,
        bom_name=row.bom_name,
        lifecycle_status=row.lifecycle_status,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        description=row.description,
        items=[_to_component_item(item) for item in ordered_items],
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def list_boms(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
) -> list[BomItem]:
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")

    rows = list_boms_by_product(db, tenant_id=tenant_id, product_id=product_id)
    return [_to_bom_item(row) for row in rows]


def get_bom(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    bom_id: str,
) -> BomDetail:
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")

    row = get_bom_row_with_product(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)
    if row is None:
        raise LookupError("BOM not found")

    return _to_bom_detail(row)


# ─── Private helpers ──────────────────────────────────────────────────────────

def _assert_product_exists(db: Session, *, tenant_id: str, product_id: str) -> None:
    if get_product_row(db, tenant_id=tenant_id, product_id=product_id) is None:
        raise LookupError("Product not found")


def _get_bom_or_404(db: Session, *, tenant_id: str, product_id: str, bom_id: str) -> Bom:
    row = get_bom_row(db, tenant_id=tenant_id, bom_id=bom_id)
    if row is None or row.product_id != product_id:
        raise LookupError("BOM not found")
    return row


def _emit_bom_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    row: Bom,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "bom_id": row.bom_id,
            "bom_code": row.bom_code,
            "product_id": row.product_id,
            "lifecycle_status": row.lifecycle_status,
            "changed_fields": changed_fields,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    record_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type=event_type,
        resource_type="bom",
        resource_id=row.bom_id,
        detail=detail,
    )


def _emit_bom_item_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    item_row: BomItemRow,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "bom_item_id": item_row.bom_item_id,
            "bom_id": item_row.bom_id,
            "component_product_id": item_row.component_product_id,
            "line_no": item_row.line_no,
            "changed_fields": changed_fields,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    record_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type=event_type,
        resource_type="bom_item",
        resource_id=item_row.bom_item_id,
        detail=detail,
    )


# ─── BOM write commands ───────────────────────────────────────────────────────

def create_bom(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    payload: BomCreateRequest,
) -> BomItem:
    _assert_product_exists(db, tenant_id=tenant_id, product_id=product_id)

    bom_code = payload.bom_code.strip()
    if not bom_code:
        raise ValueError("bom_code is required")

    bom_name = payload.bom_name.strip()
    if not bom_name:
        raise ValueError("bom_name is required")

    existing = get_bom_by_code(db, tenant_id=tenant_id, product_id=product_id, bom_code=bom_code)
    if existing is not None:
        raise ValueError("Duplicate bom_code for product in tenant")

    row = Bom(
        bom_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        bom_code=bom_code,
        bom_name=bom_name,
        lifecycle_status="DRAFT",
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        description=payload.description,
    )
    row = create_bom_row(db, row=row)
    _emit_bom_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="BOM.CREATED",
        row=row,
        changed_fields=["bom_code", "bom_name", "lifecycle_status"],
    )
    return _to_bom_item(row)


def update_bom(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    bom_id: str,
    payload: BomUpdateRequest,
) -> BomItem:
    row = _get_bom_or_404(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)

    if row.lifecycle_status != "DRAFT":
        raise ValueError(f"{row.lifecycle_status} BOM metadata cannot be updated")

    changed_fields: list[str] = []

    if payload.bom_name is not None:
        next_name = payload.bom_name.strip()
        if not next_name:
            raise ValueError("bom_name cannot be empty")
        if next_name != row.bom_name:
            row.bom_name = next_name
            changed_fields.append("bom_name")

    if payload.effective_from is not None and payload.effective_from != row.effective_from:
        row.effective_from = payload.effective_from
        changed_fields.append("effective_from")

    if payload.effective_to is not None and payload.effective_to != row.effective_to:
        row.effective_to = payload.effective_to
        changed_fields.append("effective_to")

    if "description" in payload.model_fields_set:
        if payload.description != row.description:
            row.description = payload.description
            changed_fields.append("description")

    if not changed_fields:
        return _to_bom_item(row)

    row = update_bom_row(db, row=row)
    _emit_bom_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="BOM.UPDATED",
        row=row,
        changed_fields=changed_fields,
    )
    return _to_bom_item(row)


def release_bom(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    bom_id: str,
) -> BomItem:
    row = _get_bom_or_404(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)

    if row.lifecycle_status == "RETIRED":
        raise ValueError("RETIRED BOM cannot be released")
    if row.lifecycle_status != "DRAFT":
        raise ValueError("Only DRAFT BOMs can be released")

    if not row.items:
        raise ValueError("BOM must have at least one item before release")

    row.lifecycle_status = "RELEASED"
    row = update_bom_row(db, row=row)
    _emit_bom_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="BOM.RELEASED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_bom_item(row)


def retire_bom(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    bom_id: str,
) -> BomItem:
    row = _get_bom_or_404(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)

    if row.lifecycle_status == "RETIRED":
        raise ValueError("BOM is already RETIRED")

    row.lifecycle_status = "RETIRED"
    row = update_bom_row(db, row=row)
    _emit_bom_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="BOM.RETIRED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_bom_item(row)


# ─── BOM Item write commands ──────────────────────────────────────────────────

def add_bom_item(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    bom_id: str,
    payload: BomItemCreateRequest,
) -> BomComponentItem:
    row = _get_bom_or_404(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)

    if row.lifecycle_status != "DRAFT":
        raise ValueError("BOM items can only be added while parent BOM is DRAFT")

    if payload.quantity <= 0:
        raise ValueError("quantity must be greater than zero")

    if payload.scrap_factor is not None and payload.scrap_factor < 0:
        raise ValueError("scrap_factor must be non-negative")

    uom = payload.unit_of_measure.strip()
    if not uom:
        raise ValueError("unit_of_measure is required")

    component = get_product_row(db, tenant_id=tenant_id, product_id=payload.component_product_id)
    if component is None:
        raise LookupError("Component product not found in tenant")

    if payload.component_product_id == product_id:
        raise ValueError("component_product_id cannot be the same as the parent product_id")

    duplicate_line = get_bom_item_by_line_no(
        db, tenant_id=tenant_id, bom_id=bom_id, line_no=payload.line_no
    )
    if duplicate_line is not None:
        raise ValueError("Duplicate line_no within BOM")

    item_row = BomItemRow(
        bom_item_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        bom_id=bom_id,
        component_product_id=payload.component_product_id,
        line_no=payload.line_no,
        quantity=payload.quantity,
        unit_of_measure=uom,
        scrap_factor=payload.scrap_factor,
        reference_designator=payload.reference_designator,
        notes=payload.notes,
    )
    item_row = create_bom_item_row(db, row=item_row)
    _emit_bom_item_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="BOM_ITEM.ADDED",
        item_row=item_row,
        changed_fields=["component_product_id", "line_no", "quantity", "unit_of_measure"],
    )
    return _to_component_item(item_row)


def update_bom_item(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    bom_id: str,
    bom_item_id: str,
    payload: BomItemUpdateRequest,
) -> BomComponentItem:
    bom_row = _get_bom_or_404(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)

    if bom_row.lifecycle_status != "DRAFT":
        raise ValueError("BOM items can only be updated while parent BOM is DRAFT")

    item_row = get_bom_item_by_id(
        db, tenant_id=tenant_id, bom_id=bom_id, bom_item_id=bom_item_id
    )
    if item_row is None:
        raise LookupError("BOM item not found")

    changed_fields: list[str] = []

    if payload.quantity is not None:
        if payload.quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        if payload.quantity != item_row.quantity:
            item_row.quantity = payload.quantity
            changed_fields.append("quantity")

    if payload.unit_of_measure is not None:
        uom = payload.unit_of_measure.strip()
        if not uom:
            raise ValueError("unit_of_measure cannot be empty")
        if uom != item_row.unit_of_measure:
            item_row.unit_of_measure = uom
            changed_fields.append("unit_of_measure")

    if payload.scrap_factor is not None:
        if payload.scrap_factor < 0:
            raise ValueError("scrap_factor must be non-negative")
        if payload.scrap_factor != item_row.scrap_factor:
            item_row.scrap_factor = payload.scrap_factor
            changed_fields.append("scrap_factor")

    if "reference_designator" in payload.model_fields_set:
        if payload.reference_designator != item_row.reference_designator:
            item_row.reference_designator = payload.reference_designator
            changed_fields.append("reference_designator")

    if "notes" in payload.model_fields_set:
        if payload.notes != item_row.notes:
            item_row.notes = payload.notes
            changed_fields.append("notes")

    if not changed_fields:
        return _to_component_item(item_row)

    item_row = update_bom_item_row(db, row=item_row)
    _emit_bom_item_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="BOM_ITEM.UPDATED",
        item_row=item_row,
        changed_fields=changed_fields,
    )
    return _to_component_item(item_row)


def remove_bom_item(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    bom_id: str,
    bom_item_id: str,
) -> None:
    bom_row = _get_bom_or_404(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)

    if bom_row.lifecycle_status != "DRAFT":
        raise ValueError("BOM items can only be removed while parent BOM is DRAFT")

    item_row = get_bom_item_by_id(
        db, tenant_id=tenant_id, bom_id=bom_id, bom_item_id=bom_item_id
    )
    if item_row is None:
        raise LookupError("BOM item not found")

    _emit_bom_item_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="BOM_ITEM.REMOVED",
        item_row=item_row,
        changed_fields=["removed"],
    )
    delete_bom_item_row(db, row=item_row)
