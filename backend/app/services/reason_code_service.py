from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.reason_code import ReasonCode
from app.repositories.reason_code_repository import (
    create_reason_code_row,
    get_reason_code_by_code,
    get_reason_code_by_id as get_reason_code_row,
    list_reason_codes_by_tenant,
    update_reason_code_row,
)
from app.schemas.reason_code import (
    ReasonCodeCreateRequest,
    ReasonCodeItem,
    ReasonCodeUpdateRequest,
)
from app.services.security_event_service import record_security_event


def _to_item(row: ReasonCode) -> ReasonCodeItem:
    """Convert ORM model to read schema."""
    return ReasonCodeItem(
        reason_code_id=row.reason_code_id,
        tenant_id=row.tenant_id,
        reason_domain=row.reason_domain,
        reason_category=row.reason_category,
        reason_code=row.reason_code,
        reason_name=row.reason_name,
        description=row.description,
        lifecycle_status=row.lifecycle_status,
        requires_comment=row.requires_comment,
        is_active=row.is_active,
        sort_order=row.sort_order,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _emit_reason_code_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    row: ReasonCode,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "reason_code_id": row.reason_code_id,
            "reason_code": row.reason_code,
            "reason_domain": row.reason_domain,
            "lifecycle_status": row.lifecycle_status,
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
        resource_type="reason_code",
        resource_id=row.reason_code_id,
        detail=detail,
    )


def _get_or_404(db: Session, *, tenant_id: str, reason_code_id: str) -> ReasonCode:
    row = get_reason_code_row(db, tenant_id=tenant_id, reason_code_id=reason_code_id)
    if row is None:
        raise LookupError(f"Reason code not found: {reason_code_id}")
    return row


# ─── Read commands ────────────────────────────────────────────────────────────

def list_reason_codes(
    db: Session,
    *,
    tenant_id: str,
    reason_domain: str | None = None,
    reason_category: str | None = None,
    lifecycle_status: str | None = None,
    include_inactive: bool = False,
) -> list[ReasonCodeItem]:
    rows = list_reason_codes_by_tenant(
        db,
        tenant_id=tenant_id,
        reason_domain=reason_domain,
        reason_category=reason_category,
        lifecycle_status=lifecycle_status,
        include_inactive=include_inactive,
    )
    return [_to_item(row) for row in rows]


def get_reason_code(
    db: Session,
    *,
    tenant_id: str,
    reason_code_id: str,
) -> ReasonCodeItem | None:
    row = get_reason_code_row(db, tenant_id=tenant_id, reason_code_id=reason_code_id)
    if row is None:
        return None
    return _to_item(row)


# ─── Write commands ───────────────────────────────────────────────────────────

def create_reason_code(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: ReasonCodeCreateRequest,
) -> ReasonCodeItem:
    reason_code_val = payload.reason_code.strip()
    if not reason_code_val:
        raise ValueError("reason_code is required")

    reason_name_val = payload.reason_name.strip()
    if not reason_name_val:
        raise ValueError("reason_name is required")

    reason_domain_val = payload.reason_domain.strip().upper()
    if not reason_domain_val:
        raise ValueError("reason_domain is required")

    reason_category_val = payload.reason_category.strip()
    if not reason_category_val:
        raise ValueError("reason_category is required")

    existing = get_reason_code_by_code(
        db,
        tenant_id=tenant_id,
        reason_domain=reason_domain_val,
        reason_code=reason_code_val,
    )
    if existing is not None:
        raise ValueError(
            f"Duplicate reason_code '{reason_code_val}' in domain '{reason_domain_val}' for tenant"
        )

    row = ReasonCode(
        reason_code_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        reason_domain=reason_domain_val,
        reason_category=reason_category_val,
        reason_code=reason_code_val,
        reason_name=reason_name_val,
        description=payload.description,
        lifecycle_status="DRAFT",
        requires_comment=payload.requires_comment,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
    )
    row = create_reason_code_row(db, row=row)
    _emit_reason_code_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="REASONCODE.CREATED",
        row=row,
        changed_fields=["reason_code", "reason_name", "reason_domain", "lifecycle_status"],
    )
    return _to_item(row)


def update_reason_code(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    reason_code_id: str,
    payload: ReasonCodeUpdateRequest,
) -> ReasonCodeItem:
    row = _get_or_404(db, tenant_id=tenant_id, reason_code_id=reason_code_id)

    if row.lifecycle_status != "DRAFT":
        raise ValueError(
            f"{row.lifecycle_status} Reason Code metadata cannot be updated"
        )

    changed_fields: list[str] = []

    if payload.reason_name is not None:
        next_name = payload.reason_name.strip()
        if not next_name:
            raise ValueError("reason_name cannot be empty")
        if next_name != row.reason_name:
            row.reason_name = next_name
            changed_fields.append("reason_name")

    if "description" in payload.model_fields_set:
        if payload.description != row.description:
            row.description = payload.description
            changed_fields.append("description")

    if payload.requires_comment is not None and payload.requires_comment != row.requires_comment:
        row.requires_comment = payload.requires_comment
        changed_fields.append("requires_comment")

    if payload.sort_order is not None and payload.sort_order != row.sort_order:
        row.sort_order = payload.sort_order
        changed_fields.append("sort_order")

    if payload.is_active is not None and payload.is_active != row.is_active:
        row.is_active = payload.is_active
        changed_fields.append("is_active")

    if not changed_fields:
        return _to_item(row)

    row = update_reason_code_row(db, row=row)
    _emit_reason_code_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="REASONCODE.UPDATED",
        row=row,
        changed_fields=changed_fields,
    )
    return _to_item(row)


def release_reason_code(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    reason_code_id: str,
) -> ReasonCodeItem:
    row = _get_or_404(db, tenant_id=tenant_id, reason_code_id=reason_code_id)

    if row.lifecycle_status == "RETIRED":
        raise ValueError("RETIRED Reason Code cannot be released")
    if row.lifecycle_status != "DRAFT":
        raise ValueError("Only DRAFT Reason Codes can be released")

    row.lifecycle_status = "RELEASED"
    row = update_reason_code_row(db, row=row)
    _emit_reason_code_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="REASONCODE.RELEASED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_item(row)


def retire_reason_code(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    reason_code_id: str,
) -> ReasonCodeItem:
    row = _get_or_404(db, tenant_id=tenant_id, reason_code_id=reason_code_id)

    if row.lifecycle_status == "RETIRED":
        raise ValueError("Reason Code is already RETIRED")

    row.lifecycle_status = "RETIRED"
    row = update_reason_code_row(db, row=row)
    _emit_reason_code_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="REASONCODE.RETIRED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_item(row)
