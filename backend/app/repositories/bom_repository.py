from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.bom import Bom, BomItem


def list_boms_by_product(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
) -> list[Bom]:
    return list(
        db.scalars(
            select(Bom)
            .where(
                Bom.tenant_id == tenant_id,
                Bom.product_id == product_id,
            )
            .order_by(Bom.bom_code.asc(), Bom.bom_id.asc())
        )
    )


def get_bom_by_id(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    bom_id: str,
) -> Bom | None:
    return db.scalar(
        select(Bom)
        .options(selectinload(Bom.items))
        .where(
            Bom.tenant_id == tenant_id,
            Bom.product_id == product_id,
            Bom.bom_id == bom_id,
        )
    )


def get_bom_by_code(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    bom_code: str,
) -> Bom | None:
    return db.scalar(
        select(Bom).where(
            Bom.tenant_id == tenant_id,
            Bom.product_id == product_id,
            Bom.bom_code == bom_code,
        )
    )


def get_bom_row(
    db: Session,
    *,
    tenant_id: str,
    bom_id: str,
) -> Bom | None:
    """Load a BOM by bom_id + tenant (no product scope; for internal service use)."""
    return db.scalar(
        select(Bom)
        .options(selectinload(Bom.items))
        .where(
            Bom.tenant_id == tenant_id,
            Bom.bom_id == bom_id,
        )
    )


def create_bom_row(db: Session, *, row: Bom) -> Bom:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_bom_row(db: Session, *, row: Bom) -> Bom:
    db.commit()
    db.refresh(row)
    return row


# ─── BOM Item repository helpers ─────────────────────────────────────────────

def get_bom_item_by_id(
    db: Session,
    *,
    tenant_id: str,
    bom_id: str,
    bom_item_id: str,
) -> BomItem | None:
    return db.scalar(
        select(BomItem).where(
            BomItem.tenant_id == tenant_id,
            BomItem.bom_id == bom_id,
            BomItem.bom_item_id == bom_item_id,
        )
    )


def get_bom_item_by_line_no(
    db: Session,
    *,
    tenant_id: str,
    bom_id: str,
    line_no: int,
) -> BomItem | None:
    return db.scalar(
        select(BomItem).where(
            BomItem.tenant_id == tenant_id,
            BomItem.bom_id == bom_id,
            BomItem.line_no == line_no,
        )
    )


def create_bom_item_row(db: Session, *, row: BomItem) -> BomItem:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_bom_item_row(db: Session, *, row: BomItem) -> BomItem:
    db.commit()
    db.refresh(row)
    return row


def delete_bom_item_row(db: Session, *, row: BomItem) -> None:
    db.delete(row)
    db.commit()
