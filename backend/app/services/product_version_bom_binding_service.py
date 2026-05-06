from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.product_version_bom_binding import ProductVersionBomBinding
from app.repositories.bom_repository import get_bom_by_id as get_bom_row
from app.repositories.product_version_bom_binding_repository import (
    create_binding,
    get_active_binding_by_version,
    update_binding,
)
from app.repositories.product_version_repository import (
    get_product_version_by_id as get_product_version_row,
)
from app.schemas.product import (
    BomBindingCreateRequest,
    ProductVersionBomBindingAllowedActions,
    ProductVersionBomBindingResponse,
)
from app.services.security_event_service import record_security_event

_ALLOWED_PV_BIND_STATUSES = {"DRAFT"}
_FORBIDDEN_BOM_BIND_STATUSES = {"RETIRED"}


def _compute_allowed_actions(
    pv_lifecycle: str, has_both_permissions: bool
) -> ProductVersionBomBindingAllowedActions:
    if not has_both_permissions:
        return ProductVersionBomBindingAllowedActions(can_remove=False)
    return ProductVersionBomBindingAllowedActions(
        can_remove=(pv_lifecycle == "DRAFT"),
    )


def _to_binding_response(
    row: ProductVersionBomBinding,
    pv_lifecycle: str,
    has_both_permissions: bool,
) -> ProductVersionBomBindingResponse:
    return ProductVersionBomBindingResponse(
        binding_id=row.binding_id,
        tenant_id=row.tenant_id,
        product_id=row.product_id,
        product_version_id=row.product_version_id,
        bom_id=row.bom_id,
        binding_type=row.binding_type,
        binding_status=row.binding_status,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
        created_by=row.created_by,
        updated_by=row.updated_by,
        allowed_actions=_compute_allowed_actions(pv_lifecycle, has_both_permissions),
    )


def _emit_binding_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    row: ProductVersionBomBinding,
) -> None:
    detail = json.dumps(
        {
            "binding_id": row.binding_id,
            "product_id": row.product_id,
            "product_version_id": row.product_version_id,
            "bom_id": row.bom_id,
            "binding_type": row.binding_type,
            "binding_status": row.binding_status,
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
        resource_type="product_version_bom_binding",
        resource_id=row.binding_id,
        detail=detail,
    )


def get_product_version_bom_binding(
    db: Session,
    *,
    tenant_id: str,
    product_id: str,
    product_version_id: str,
    has_both_permissions: bool = False,
) -> ProductVersionBomBindingResponse:
    """Return the current ACTIVE binding for a Product Version.

    Raises LookupError if PV not found or no active binding exists.
    """
    pv = get_product_version_row(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    if pv is None:
        raise LookupError("Product version not found")

    row = get_active_binding_by_version(
        db, tenant_id=tenant_id, product_version_id=product_version_id
    )
    if row is None:
        raise LookupError("No active BOM binding for this product version")

    return _to_binding_response(row, pv.lifecycle_status, has_both_permissions)


def bind_bom_to_product_version(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    product_version_id: str,
    payload: BomBindingCreateRequest,
) -> ProductVersionBomBindingResponse:
    """Bind a BOM to a Product Version.

    Invariants enforced (governance contract §6, §7, §10):
    - PV must exist (tenant + product scope).
    - BOM must exist (tenant + product scope — same product_id as PV).
    - PV lifecycle must be DRAFT.
    - BOM lifecycle must not be RETIRED.
    - No existing ACTIVE PRIMARY binding for this PV (cardinality 0 or 1).
    """
    pv = get_product_version_row(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    if pv is None:
        raise LookupError("Product version not found")

    bom = get_bom_row(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        bom_id=payload.bom_id,
    )
    if bom is None:
        raise LookupError("BOM not found")

    if pv.lifecycle_status not in _ALLOWED_PV_BIND_STATUSES:
        raise ValueError(
            f"Product Version must be DRAFT to add a binding; "
            f"current status: {pv.lifecycle_status}"
        )

    if bom.lifecycle_status in _FORBIDDEN_BOM_BIND_STATUSES:
        raise ValueError(
            f"BOM with status {bom.lifecycle_status} cannot be newly bound"
        )

    existing = get_active_binding_by_version(
        db, tenant_id=tenant_id, product_version_id=product_version_id
    )
    if existing is not None:
        raise ValueError(
            "An ACTIVE PRIMARY BOM binding already exists for this product version"
        )

    row = ProductVersionBomBinding(
        binding_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
        bom_id=payload.bom_id,
        binding_type="PRIMARY",
        binding_status="ACTIVE",
        notes=payload.notes,
        created_by=actor_user_id,
    )
    row = create_binding(db, row=row)

    _emit_binding_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ProductVersionBomBinding.CREATED",
        row=row,
    )

    return _to_binding_response(row, pv.lifecycle_status, has_both_permissions=True)


def unbind_bom_from_product_version(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    product_id: str,
    product_version_id: str,
) -> None:
    """Remove the ACTIVE PRIMARY BOM binding from a Product Version.

    Invariants enforced (governance contract §7):
    - PV must exist (tenant + product scope).
    - PV lifecycle must be DRAFT (unbind forbidden for RELEASED/RETIRED).
    - An ACTIVE binding must exist.
    """
    pv = get_product_version_row(
        db,
        tenant_id=tenant_id,
        product_id=product_id,
        product_version_id=product_version_id,
    )
    if pv is None:
        raise LookupError("Product version not found")

    if pv.lifecycle_status not in _ALLOWED_PV_BIND_STATUSES:
        raise ValueError(
            f"Product Version must be DRAFT to remove a binding; "
            f"current status: {pv.lifecycle_status}"
        )

    existing = get_active_binding_by_version(
        db, tenant_id=tenant_id, product_version_id=product_version_id
    )
    if existing is None:
        raise LookupError("No active BOM binding found for this product version")

    existing.binding_status = "REMOVED"
    existing.updated_by = actor_user_id
    update_binding(db, row=existing)

    _emit_binding_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ProductVersionBomBinding.REMOVED",
        row=existing,
    )
