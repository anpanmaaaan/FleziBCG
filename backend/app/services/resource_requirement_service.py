from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.resource_requirement import ResourceRequirement
from app.repositories.resource_requirement_repository import (
    create_resource_requirement as create_resource_requirement_row,
    delete_resource_requirement as delete_resource_requirement_row,
    get_resource_requirement_by_id as get_resource_requirement_row,
    get_resource_requirement_by_unique_key,
    list_resource_requirements_by_operation,
    update_resource_requirement as update_resource_requirement_row,
)
from app.repositories.routing_repository import (
    get_routing_by_id as get_routing_row,
    get_routing_operation_by_id,
)
from app.schemas.resource_requirement import (
    ResourceRequirementCreateRequest,
    ResourceRequirementItem,
    ResourceRequirementUpdateRequest,
)
from app.services.security_event_service import record_security_event

_ALLOWED_RESOURCE_TYPES = {
    "WORK_CENTER",
    "STATION_CAPABILITY",
    "EQUIPMENT_CAPABILITY",
    "OPERATOR_SKILL",
    "TOOLING",
}


def _routing_not_found() -> LookupError:
    return LookupError("Routing not found")


def _operation_not_found() -> LookupError:
    return LookupError("Routing operation not found")


def _requirement_not_found() -> LookupError:
    return LookupError("Resource requirement not found")


def _normalize_required(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _normalize_optional_non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    return normalized


def _validate_resource_type(value: str) -> str:
    normalized = _normalize_required(value, field_name="required_resource_type")
    if normalized not in _ALLOWED_RESOURCE_TYPES:
        raise ValueError("Invalid required_resource_type")
    return normalized


def _validate_quantity(value: int) -> int:
    if value <= 0:
        raise ValueError("quantity_required must be positive")
    return value


def _load_routing_and_operation_for_mutation(
    db: Session,
    *,
    tenant_id: str,
    routing_id: str,
    operation_id: str,
) -> tuple[object, object]:
    routing = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if routing is None:
        raise _routing_not_found()

    operation = get_routing_operation_by_id(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )
    if operation is None:
        raise _operation_not_found()

    if routing.lifecycle_status != "DRAFT":
        raise ValueError("Resource requirements can be modified only in DRAFT")

    return routing, operation


def _to_item(row: ResourceRequirement) -> ResourceRequirementItem:
    return ResourceRequirementItem(
        requirement_id=row.requirement_id,
        tenant_id=row.tenant_id,
        routing_id=row.routing_id,
        operation_id=row.operation_id,
        required_resource_type=row.required_resource_type,
        required_capability_code=row.required_capability_code,
        quantity_required=row.quantity_required,
        notes=row.notes,
        metadata_json=row.metadata_json,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _emit_requirement_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    row: ResourceRequirement,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "tenant_id": tenant_id,
            "requirement_id": row.requirement_id,
            "routing_id": row.routing_id,
            "operation_id": row.operation_id,
            "required_resource_type": row.required_resource_type,
            "required_capability_code": row.required_capability_code,
            "changed_fields": changed_fields,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "event_name_status": [
                "CANONICAL_FOR_P0_B_RESOURCE_REQUIREMENT",
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
        resource_type="resource_requirement",
        resource_id=row.requirement_id,
        detail=detail,
    )


def list_resource_requirements(
    db: Session,
    *,
    tenant_id: str,
    routing_id: str,
    operation_id: str,
) -> list[ResourceRequirementItem]:
    rows = list_resource_requirements_by_operation(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )
    return [_to_item(row) for row in rows]


def get_resource_requirement_by_id(
    db: Session,
    *,
    tenant_id: str,
    routing_id: str,
    operation_id: str,
    requirement_id: str,
) -> ResourceRequirementItem | None:
    row = get_resource_requirement_row(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
        requirement_id=requirement_id,
    )
    if row is None:
        return None
    return _to_item(row)


def create_resource_requirement(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
    operation_id: str,
    payload: ResourceRequirementCreateRequest,
) -> ResourceRequirementItem:
    _load_routing_and_operation_for_mutation(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )

    required_resource_type = _validate_resource_type(payload.required_resource_type)
    required_capability_code = _normalize_required(
        payload.required_capability_code,
        field_name="required_capability_code",
    )
    quantity_required = _validate_quantity(payload.quantity_required)

    existing = get_resource_requirement_by_unique_key(
        db,
        tenant_id=tenant_id,
        operation_id=operation_id,
        required_resource_type=required_resource_type,
        required_capability_code=required_capability_code,
    )
    if existing is not None:
        raise ValueError("Duplicate resource requirement in operation")

    row = ResourceRequirement(
        requirement_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
        required_resource_type=required_resource_type,
        required_capability_code=required_capability_code,
        quantity_required=quantity_required,
        notes=payload.notes,
        metadata_json=payload.metadata_json,
    )
    row = create_resource_requirement_row(db, row=row)
    _emit_requirement_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="RESOURCE_REQUIREMENT.CREATED",
        row=row,
        changed_fields=[
            "required_resource_type",
            "required_capability_code",
            "quantity_required",
            "notes",
            "metadata_json",
        ],
    )
    return _to_item(row)


def update_resource_requirement(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
    operation_id: str,
    requirement_id: str,
    payload: ResourceRequirementUpdateRequest,
) -> ResourceRequirementItem:
    _load_routing_and_operation_for_mutation(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )

    row = get_resource_requirement_row(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
        requirement_id=requirement_id,
    )
    if row is None:
        raise _requirement_not_found()

    changed_fields: list[str] = []

    next_resource_type = row.required_resource_type
    next_capability_code = row.required_capability_code

    if payload.required_resource_type is not None:
        validated_type = _validate_resource_type(payload.required_resource_type)
        if validated_type != row.required_resource_type:
            next_resource_type = validated_type
            changed_fields.append("required_resource_type")

    if payload.required_capability_code is not None:
        validated_capability = _normalize_optional_non_empty(
            payload.required_capability_code,
            field_name="required_capability_code",
        )
        if validated_capability != row.required_capability_code:
            next_capability_code = validated_capability
            changed_fields.append("required_capability_code")

    if payload.quantity_required is not None:
        validated_quantity = _validate_quantity(payload.quantity_required)
        if validated_quantity != row.quantity_required:
            row.quantity_required = validated_quantity
            changed_fields.append("quantity_required")

    if payload.notes is not None and payload.notes != row.notes:
        row.notes = payload.notes
        changed_fields.append("notes")

    if payload.metadata_json is not None and payload.metadata_json != row.metadata_json:
        row.metadata_json = payload.metadata_json
        changed_fields.append("metadata_json")

    unique_changed = (
        next_resource_type != row.required_resource_type
        or next_capability_code != row.required_capability_code
    )

    if unique_changed:
        conflict = get_resource_requirement_by_unique_key(
            db,
            tenant_id=tenant_id,
            operation_id=operation_id,
            required_resource_type=next_resource_type,
            required_capability_code=next_capability_code,
        )
        if conflict is not None and conflict.requirement_id != row.requirement_id:
            raise ValueError("Duplicate resource requirement in operation")

        row.required_resource_type = next_resource_type
        row.required_capability_code = next_capability_code

    if not changed_fields and not unique_changed:
        return _to_item(row)

    row = update_resource_requirement_row(db, row=row)
    _emit_requirement_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="RESOURCE_REQUIREMENT.UPDATED",
        row=row,
        changed_fields=changed_fields,
    )
    return _to_item(row)


def delete_resource_requirement(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
    operation_id: str,
    requirement_id: str,
) -> ResourceRequirementItem:
    _load_routing_and_operation_for_mutation(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )

    row = get_resource_requirement_row(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
        requirement_id=requirement_id,
    )
    if row is None:
        raise _requirement_not_found()

    item = _to_item(row)
    _emit_requirement_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="RESOURCE_REQUIREMENT.REMOVED",
        row=row,
        changed_fields=["requirement_id"],
    )
    delete_resource_requirement_row(db, row=row)
    return item
