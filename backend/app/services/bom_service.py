from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.bom import Bom, BomItem as BomItemRow
from app.repositories.bom_repository import get_bom_by_id as get_bom_row
from app.repositories.bom_repository import list_boms_by_product
from app.repositories.product_repository import get_product_by_id as get_product_row
from app.schemas.bom import BomComponentItem, BomDetail, BomItem


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

    row = get_bom_row(db, tenant_id=tenant_id, product_id=product_id, bom_id=bom_id)
    if row is None:
        raise LookupError("BOM not found")

    return _to_bom_detail(row)
