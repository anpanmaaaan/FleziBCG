from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.bom import Bom


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
