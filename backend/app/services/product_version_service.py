from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.product_version import ProductVersion
from app.repositories.product_repository import get_product_by_id as get_product_row
from app.repositories.product_version_repository import (
    get_product_version_by_id as get_product_version_row,
    list_product_versions_by_product,
)
from app.schemas.product import ProductVersionItem


def _version_not_found() -> LookupError:
    return LookupError("Product version not found")


def _to_version_item(row: ProductVersion) -> ProductVersionItem:
    return ProductVersionItem(
        product_version_id=row.product_version_id,
        tenant_id=row.tenant_id,
        product_id=row.product_id,
        version_code=row.version_code,
        version_name=row.version_name,
        lifecycle_status=row.lifecycle_status,
        is_current=row.is_current,
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        description=row.description,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def list_product_versions(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
) -> list[ProductVersionItem]:
    """Return all versions for a product within the tenant.

    Raises LookupError if the parent product does not exist (or belongs to
    a different tenant).
    """
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")
    rows = list_product_versions_by_product(db, tenant_id=tenant_id, product_id=product_id)
    return [_to_version_item(r) for r in rows]


def get_product_version(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    product_version_id: str,
) -> ProductVersionItem:
    """Return a single product version by ID.

    Raises LookupError if the parent product or the version does not exist,
    or if either belongs to a different tenant.
    """
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")
    row = get_product_version_row(
        db, tenant_id=tenant_id, product_id=product_id, product_version_id=product_version_id
    )
    if row is None:
        raise _version_not_found()
    return _to_version_item(row)
