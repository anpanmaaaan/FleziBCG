from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def list_products_by_tenant(db: Session, *, tenant_id: str) -> list[Product]:
    return list(
        db.scalars(
            select(Product)
            .where(Product.tenant_id == tenant_id)
            .order_by(Product.product_code.asc(), Product.product_id.asc())
        )
    )


def get_product_by_id(db: Session, *, tenant_id: str, product_id: str) -> Product | None:
    return db.scalar(
        select(Product).where(
            Product.tenant_id == tenant_id,
            Product.product_id == product_id,
        )
    )


def get_product_by_code(db: Session, *, tenant_id: str, product_code: str) -> Product | None:
    return db.scalar(
        select(Product).where(
            Product.tenant_id == tenant_id,
            Product.product_code == product_code,
        )
    )


def create_product(db: Session, *, row: Product) -> Product:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_product(db: Session, *, row: Product) -> Product:
    db.commit()
    db.refresh(row)
    return row
