from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.product_version import ProductVersion
from app.repositories.product_repository import get_product_by_id as get_product_row
from app.repositories.product_version_repository import (
    create_product_version as create_product_version_row,
    get_product_version_by_code,
    get_product_version_by_id as get_product_version_row,
    list_product_versions_by_product,
    update_product_version as update_product_version_row,
)
from app.schemas.product import (
    ProductVersionCreateRequest,
    ProductVersionItem,
    ProductVersionUpdateRequest,
)
from app.services.security_event_service import record_security_event


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


def _validate_effective_date_range(effective_from, effective_to) -> None:
    if effective_from is not None and effective_to is not None and effective_from > effective_to:
        raise ValueError("effective_from must be less than or equal to effective_to")


def _emit_product_version_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    row: ProductVersion,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "product_id": row.product_id,
            "product_version_id": row.product_version_id,
            "version_code": row.version_code,
            "lifecycle_status": row.lifecycle_status,
            "is_current": row.is_current,
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
        resource_type="product_version",
        resource_id=row.product_version_id,
        detail=detail,
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


def create_product_version(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    payload: ProductVersionCreateRequest,
) -> ProductVersionItem:
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")

    version_code = payload.version_code.strip()
    if not version_code:
        raise ValueError("version_code is required")

    _validate_effective_date_range(payload.effective_from, payload.effective_to)

    existing = get_product_version_by_code(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        version_code=version_code,
    )
    if existing is not None:
        raise ValueError("Duplicate version_code in product")

    row = ProductVersion(
        product_version_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        version_code=version_code,
        version_name=payload.version_name,
        lifecycle_status="DRAFT",
        is_current=False,
        effective_from=payload.effective_from,
        effective_to=payload.effective_to,
        description=payload.description,
    )
    row = create_product_version_row(db, row=row)
    _emit_product_version_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT_VERSION.CREATED",
        row=row,
        changed_fields=[
            "version_code",
            "version_name",
            "effective_from",
            "effective_to",
            "description",
            "lifecycle_status",
            "is_current",
        ],
    )
    return _to_version_item(row)


def update_product_version(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    product_version_id: str,
    payload: ProductVersionUpdateRequest,
) -> ProductVersionItem:
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")

    row = get_product_version_row(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    if row is None:
        raise _version_not_found()

    if row.lifecycle_status != "DRAFT":
        raise ValueError("Only DRAFT product versions can be updated")

    next_effective_from = payload.effective_from if payload.effective_from is not None else row.effective_from
    next_effective_to = payload.effective_to if payload.effective_to is not None else row.effective_to
    _validate_effective_date_range(next_effective_from, next_effective_to)

    changed_fields: list[str] = []

    if payload.version_name is not None and payload.version_name != row.version_name:
        row.version_name = payload.version_name
        changed_fields.append("version_name")

    if payload.effective_from is not None and payload.effective_from != row.effective_from:
        row.effective_from = payload.effective_from
        changed_fields.append("effective_from")

    if payload.effective_to is not None and payload.effective_to != row.effective_to:
        row.effective_to = payload.effective_to
        changed_fields.append("effective_to")

    if payload.description is not None and payload.description != row.description:
        row.description = payload.description
        changed_fields.append("description")

    if not changed_fields:
        return _to_version_item(row)

    row = update_product_version_row(db, row=row)
    _emit_product_version_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT_VERSION.UPDATED",
        row=row,
        changed_fields=changed_fields,
    )
    return _to_version_item(row)


def release_product_version(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    product_version_id: str,
) -> ProductVersionItem:
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")

    row = get_product_version_row(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    if row is None:
        raise _version_not_found()

    if row.lifecycle_status != "DRAFT":
        raise ValueError("Only DRAFT product versions can be released")

    row.lifecycle_status = "RELEASED"
    row = update_product_version_row(db, row=row)
    _emit_product_version_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT_VERSION.RELEASED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_version_item(row)


def retire_product_version(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    product_version_id: str,
) -> ProductVersionItem:
    product = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if product is None:
        raise LookupError("Product not found")

    row = get_product_version_row(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    if row is None:
        raise _version_not_found()

    if row.lifecycle_status == "RETIRED":
        raise ValueError("Product version is already RETIRED")

    if row.is_current:
        raise ValueError("Current product version cannot be retired")

    if row.lifecycle_status not in {"DRAFT", "RELEASED"}:
        raise ValueError("Only DRAFT or RELEASED product versions can be retired")

    row.lifecycle_status = "RETIRED"
    row = update_product_version_row(db, row=row)
    _emit_product_version_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT_VERSION.RETIRED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_version_item(row)
