from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.product_repository import (
    create_product as create_product_row,
    get_product_by_code,
    get_product_by_id as get_product_row,
    list_products_by_tenant,
    update_product as update_product_row,
)
from app.schemas.product import (
    ProductBomCapabilities,
    ProductCreateRequest,
    ProductItem,
    ProductUpdateRequest,
    ProductVersionProductCapabilities,
    validate_product_type,
)
from app.services.security_event_service import record_security_event


def _serialize_display_metadata(value: dict[str, Any] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _deserialize_display_metadata(value: str | None) -> dict[str, Any] | None:
    if value is None or value == "":
        return None
    return json.loads(value)


def _to_item(row: Product, has_manage: bool = False, has_bom_manage: bool = False) -> ProductItem:
    return ProductItem(
        product_id=row.product_id,
        tenant_id=row.tenant_id,
        product_code=row.product_code,
        product_name=row.product_name,
        product_type=row.product_type,
        lifecycle_status=row.lifecycle_status,
        description=row.description,
        display_metadata=_deserialize_display_metadata(row.display_metadata),
        created_at=row.created_at,
        updated_at=row.updated_at,
        product_version_capabilities=ProductVersionProductCapabilities(can_create=has_manage),
        bom_capabilities=ProductBomCapabilities(can_create=has_bom_manage),
    )


def _not_found() -> LookupError:
    return LookupError("Product not found")


def _emit_product_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    row: Product,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "product_id": row.product_id,
            "product_code": row.product_code,
            "lifecycle_status": row.lifecycle_status,
            "changed_fields": changed_fields,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "event_name_status": [
                "CANONICAL_FOR_P0_B",
            ],
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    record_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type=event_type,
        resource_type="product",
        resource_id=row.product_id,
        detail=detail,
    )


def list_products(
    db: Session, *, tenant_id: str, has_manage_permission: bool = False, has_bom_manage_permission: bool = False
) -> list[ProductItem]:
    return [
        _to_item(row, has_manage=has_manage_permission, has_bom_manage=has_bom_manage_permission)
        for row in list_products_by_tenant(db, tenant_id=tenant_id)
    ]


def get_product_by_id(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    has_manage_permission: bool = False,
    has_bom_manage_permission: bool = False,
) -> ProductItem | None:
    row = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if row is None:
        return None
    return _to_item(row, has_manage=has_manage_permission, has_bom_manage=has_bom_manage_permission)


def create_product(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: ProductCreateRequest,
    has_pv_manage: bool = False,
    has_bom_manage: bool = False,
) -> ProductItem:
    product_code = payload.product_code.strip()
    if not product_code:
        raise ValueError("product_code is required")

    product_name = payload.product_name.strip()
    if not product_name:
        raise ValueError("product_name is required")

    product_type = validate_product_type(payload.product_type)

    existing = get_product_by_code(db, tenant_id=tenant_id, product_code=product_code)
    if existing is not None:
        raise ValueError("Duplicate product_code in tenant")

    row = Product(
        product_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_code=product_code,
        product_name=product_name,
        product_type=product_type,
        lifecycle_status="DRAFT",
        description=payload.description,
        display_metadata=_serialize_display_metadata(payload.display_metadata),
    )
    row = create_product_row(db, row=row)
    _emit_product_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT.CREATED",
        row=row,
        changed_fields=[
            "product_code",
            "product_name",
            "product_type",
            "description",
            "display_metadata",
            "lifecycle_status",
        ],
    )
    return _to_item(row, has_manage=has_pv_manage, has_bom_manage=has_bom_manage)


def update_product(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    payload: ProductUpdateRequest,
    has_pv_manage: bool = False,
    has_bom_manage: bool = False,
) -> ProductItem:
    row = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if row is None:
        raise _not_found()

    if row.lifecycle_status == "RETIRED":
        raise ValueError("RETIRED product cannot be updated")

    changed_fields: list[str] = []

    if payload.product_code is not None:
        next_code = payload.product_code.strip()
        if not next_code:
            raise ValueError("product_code cannot be empty")
        if row.lifecycle_status == "RELEASED":
            raise ValueError("RELEASED product structural update is not allowed")
        if next_code != row.product_code:
            conflict = get_product_by_code(db, tenant_id=tenant_id, product_code=next_code)
            if conflict is not None and conflict.product_id != row.product_id:
                raise ValueError("Duplicate product_code in tenant")
            row.product_code = next_code
            changed_fields.append("product_code")

    if payload.product_type is not None:
        next_type = validate_product_type(payload.product_type)
        if row.lifecycle_status == "RELEASED":
            raise ValueError("RELEASED product structural update is not allowed")
        if next_type != row.product_type:
            row.product_type = next_type
            changed_fields.append("product_type")

    if payload.product_name is not None:
        next_name = payload.product_name.strip()
        if not next_name:
            raise ValueError("product_name cannot be empty")
        if next_name != row.product_name:
            row.product_name = next_name
            changed_fields.append("product_name")

    if payload.description is not None and payload.description != row.description:
        row.description = payload.description
        changed_fields.append("description")

    if payload.display_metadata is not None:
        serialized = _serialize_display_metadata(payload.display_metadata)
        if serialized != row.display_metadata:
            row.display_metadata = serialized
            changed_fields.append("display_metadata")

    if not changed_fields:
        return _to_item(row, has_manage=has_pv_manage, has_bom_manage=has_bom_manage)

    row = update_product_row(db, row=row)
    _emit_product_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT.UPDATED",
        row=row,
        changed_fields=changed_fields,
    )
    return _to_item(row, has_manage=has_pv_manage, has_bom_manage=has_bom_manage)


def release_product(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    has_pv_manage: bool = False,
    has_bom_manage: bool = False,
) -> ProductItem:
    row = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if row is None:
        raise _not_found()

    if row.lifecycle_status != "DRAFT":
        raise ValueError("Only DRAFT products can be released")

    row.lifecycle_status = "RELEASED"
    row = update_product_row(db, row=row)
    _emit_product_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT.RELEASED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_item(row, has_manage=has_pv_manage, has_bom_manage=has_bom_manage)


def retire_product(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    has_pv_manage: bool = False,
    has_bom_manage: bool = False,
) -> ProductItem:
    row = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if row is None:
        raise _not_found()

    if row.lifecycle_status == "RETIRED":
        raise ValueError("Product is already RETIRED")

    row.lifecycle_status = "RETIRED"
    row = update_product_row(db, row=row)
    _emit_product_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="PRODUCT.RETIRED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_item(row, has_manage=has_pv_manage, has_bom_manage=has_bom_manage)
