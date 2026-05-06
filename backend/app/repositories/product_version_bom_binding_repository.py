from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product_version_bom_binding import ProductVersionBomBinding


def get_active_binding_by_version(
    db: Session,
    *,
    tenant_id: str,
    product_version_id: str,
) -> ProductVersionBomBinding | None:
    return db.scalar(
        select(ProductVersionBomBinding).where(
            ProductVersionBomBinding.tenant_id == tenant_id,
            ProductVersionBomBinding.product_version_id == product_version_id,
            ProductVersionBomBinding.binding_status == "ACTIVE",
        )
    )


def create_binding(
    db: Session, *, row: ProductVersionBomBinding
) -> ProductVersionBomBinding:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_binding(
    db: Session, *, row: ProductVersionBomBinding
) -> ProductVersionBomBinding:
    db.commit()
    db.refresh(row)
    return row
