from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product_version import ProductVersion


def list_product_versions_by_product(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
) -> list[ProductVersion]:
    return list(
        db.scalars(
            select(ProductVersion)
            .where(
                ProductVersion.tenant_id == tenant_id,
                ProductVersion.product_id == product_id,
            )
            .order_by(
                ProductVersion.version_code.asc(),
                ProductVersion.product_version_id.asc(),
            )
        )
    )


def get_product_version_by_id(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    product_version_id: str,
) -> ProductVersion | None:
    return db.scalar(
        select(ProductVersion).where(
            ProductVersion.tenant_id == tenant_id,
            ProductVersion.product_id == product_id,
            ProductVersion.product_version_id == product_version_id,
        )
    )


def get_product_version_by_code(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    version_code: str,
) -> ProductVersion | None:
    return db.scalar(
        select(ProductVersion).where(
            ProductVersion.tenant_id == tenant_id,
            ProductVersion.product_id == product_id,
            ProductVersion.version_code == version_code,
        )
    )


def create_product_version(db: Session, *, row: ProductVersion) -> ProductVersion:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_product_version(db: Session, *, row: ProductVersion) -> ProductVersion:
    db.commit()
    db.refresh(row)
    return row
