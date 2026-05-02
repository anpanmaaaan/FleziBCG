from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.routing import Routing, RoutingOperation
from app.repositories.product_repository import get_product_by_id as get_product_row
from app.repositories.routing_repository import (
    create_routing as create_routing_row,
    create_routing_operation as create_routing_operation_row,
    delete_routing_operation as delete_routing_operation_row,
    get_routing_by_code,
    get_routing_by_id as get_routing_row,
    get_routing_operation_by_id,
    get_routing_operation_by_sequence,
    list_routings_by_tenant,
    update_routing as update_routing_row,
    update_routing_operation as update_routing_operation_row,
)
from app.schemas.routing import (
    RoutingCreateRequest,
    RoutingItem,
    RoutingOperationCreateRequest,
    RoutingOperationItem,
    RoutingOperationUpdateRequest,
    RoutingUpdateRequest,
)
from app.services.security_event_service import record_security_event


def _not_found() -> LookupError:
    return LookupError("Routing not found")


def _operation_not_found() -> LookupError:
    return LookupError("Routing operation not found")


def _normalize_non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _normalize_non_empty_optional(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty")
    return normalized


def _validate_product_link(db: Session, *, tenant_id: str, product_id: str) -> Product:
    row = get_product_row(db, tenant_id=tenant_id, product_id=product_id)
    if row is None:
        raise ValueError("Invalid product_id for tenant")
    if row.lifecycle_status == "RETIRED":
        raise ValueError("RETIRED product cannot be newly linked")
    return row


def _to_operation_item(row: RoutingOperation) -> RoutingOperationItem:
    return RoutingOperationItem(
        operation_id=row.operation_id,
        routing_id=row.routing_id,
        operation_code=row.operation_code,
        operation_name=row.operation_name,
        sequence_no=row.sequence_no,
        standard_cycle_time=row.standard_cycle_time,
        required_resource_type=row.required_resource_type,
        # v1.2 contract boundary patch — read-only projection of extended fields.
        setup_time=row.setup_time,
        run_time_per_unit=row.run_time_per_unit,
        work_center_code=row.work_center_code,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_item(row: Routing) -> RoutingItem:
    ordered_operations = sorted(row.operations, key=lambda op: (op.sequence_no, op.operation_id))
    return RoutingItem(
        routing_id=row.routing_id,
        tenant_id=row.tenant_id,
        product_id=row.product_id,
        routing_code=row.routing_code,
        routing_name=row.routing_name,
        lifecycle_status=row.lifecycle_status,
        operations=[_to_operation_item(op) for op in ordered_operations],
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _emit_routing_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    row: Routing,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "routing_id": row.routing_id,
            "routing_code": row.routing_code,
            "product_id": row.product_id,
            "lifecycle_status": row.lifecycle_status,
            "changed_fields": changed_fields,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "event_name_status": [
                "CANONICAL_FOR_P0_B_ROUTING",
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
        resource_type="routing",
        resource_id=row.routing_id,
        detail=detail,
    )


def _emit_routing_operation_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    event_type: str,
    routing: Routing,
    operation: RoutingOperation,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "routing_id": routing.routing_id,
            "routing_code": routing.routing_code,
            "product_id": routing.product_id,
            "operation_id": operation.operation_id,
            "lifecycle_status": routing.lifecycle_status,
            "changed_fields": changed_fields,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "event_name_status": [
                "CANONICAL_FOR_P0_B_ROUTING",
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
        resource_type="routing_operation",
        resource_id=operation.operation_id,
        detail=detail,
    )


def _ensure_draft_for_operation_mutation(row: Routing) -> None:
    if row.lifecycle_status != "DRAFT":
        raise ValueError("Routing operations can be modified only in DRAFT")


def list_routings(db: Session, *, tenant_id: str) -> list[RoutingItem]:
    return [_to_item(row) for row in list_routings_by_tenant(db, tenant_id=tenant_id)]


def get_routing_by_id(db: Session, *, tenant_id: str, routing_id: str) -> RoutingItem | None:
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if row is None:
        return None
    return _to_item(row)


def create_routing(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: RoutingCreateRequest,
) -> RoutingItem:
    routing_code = _normalize_non_empty(payload.routing_code, field_name="routing_code")
    routing_name = _normalize_non_empty(payload.routing_name, field_name="routing_name")
    _validate_product_link(db, tenant_id=tenant_id, product_id=payload.product_id)

    existing = get_routing_by_code(db, tenant_id=tenant_id, routing_code=routing_code)
    if existing is not None:
        raise ValueError("Duplicate routing_code in tenant")

    row = Routing(
        routing_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        product_id=payload.product_id,
        routing_code=routing_code,
        routing_name=routing_name,
        lifecycle_status="DRAFT",
    )
    row = create_routing_row(db, row=row)
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=row.routing_id)
    _emit_routing_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ROUTING.CREATED",
        row=row,
        changed_fields=["product_id", "routing_code", "routing_name", "lifecycle_status"],
    )
    return _to_item(row)


def update_routing(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
    payload: RoutingUpdateRequest,
) -> RoutingItem:
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if row is None:
        raise _not_found()

    if row.lifecycle_status == "RETIRED":
        raise ValueError("RETIRED routing cannot be updated")

    changed_fields: list[str] = []

    if payload.routing_code is not None:
        next_code = _normalize_non_empty_optional(payload.routing_code, field_name="routing_code")
        if row.lifecycle_status == "RELEASED":
            raise ValueError("RELEASED routing structural update is not allowed")
        if next_code != row.routing_code:
            conflict = get_routing_by_code(db, tenant_id=tenant_id, routing_code=next_code)
            if conflict is not None and conflict.routing_id != row.routing_id:
                raise ValueError("Duplicate routing_code in tenant")
            row.routing_code = next_code
            changed_fields.append("routing_code")

    if payload.product_id is not None:
        if row.lifecycle_status == "RELEASED":
            raise ValueError("RELEASED routing structural update is not allowed")
        if payload.product_id != row.product_id:
            _validate_product_link(db, tenant_id=tenant_id, product_id=payload.product_id)
            row.product_id = payload.product_id
            changed_fields.append("product_id")

    if payload.routing_name is not None:
        next_name = _normalize_non_empty_optional(payload.routing_name, field_name="routing_name")
        if next_name != row.routing_name:
            row.routing_name = next_name
            changed_fields.append("routing_name")

    if not changed_fields:
        return _to_item(row)

    row = update_routing_row(db, row=row)
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=row.routing_id)
    _emit_routing_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ROUTING.UPDATED",
        row=row,
        changed_fields=changed_fields,
    )
    return _to_item(row)


def add_routing_operation(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
    payload: RoutingOperationCreateRequest,
) -> RoutingItem:
    routing = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if routing is None:
        raise _not_found()

    _ensure_draft_for_operation_mutation(routing)

    operation_code = _normalize_non_empty(payload.operation_code, field_name="operation_code")
    operation_name = _normalize_non_empty(payload.operation_name, field_name="operation_name")

    if get_routing_operation_by_sequence(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        sequence_no=payload.sequence_no,
    ) is not None:
        raise ValueError("Duplicate sequence_no in routing")

    op_row = RoutingOperation(
        operation_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_code=operation_code,
        operation_name=operation_name,
        sequence_no=payload.sequence_no,
        standard_cycle_time=payload.standard_cycle_time,
        required_resource_type=payload.required_resource_type,
    )
    op_row = create_routing_operation_row(db, row=op_row)
    routing = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    _emit_routing_operation_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ROUTING.OPERATION_ADDED",
        routing=routing,
        operation=op_row,
        changed_fields=[
            "operation_code",
            "operation_name",
            "sequence_no",
            "standard_cycle_time",
            "required_resource_type",
        ],
    )
    return _to_item(routing)


def update_routing_operation(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
    operation_id: str,
    payload: RoutingOperationUpdateRequest,
) -> RoutingItem:
    routing = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if routing is None:
        raise _not_found()

    _ensure_draft_for_operation_mutation(routing)

    op_row = get_routing_operation_by_id(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )
    if op_row is None:
        raise _operation_not_found()

    changed_fields: list[str] = []

    if payload.operation_code is not None:
        next_code = _normalize_non_empty_optional(payload.operation_code, field_name="operation_code")
        if next_code != op_row.operation_code:
            op_row.operation_code = next_code
            changed_fields.append("operation_code")

    if payload.operation_name is not None:
        next_name = _normalize_non_empty_optional(payload.operation_name, field_name="operation_name")
        if next_name != op_row.operation_name:
            op_row.operation_name = next_name
            changed_fields.append("operation_name")

    if payload.sequence_no is not None and payload.sequence_no != op_row.sequence_no:
        conflict = get_routing_operation_by_sequence(
            db,
            tenant_id=tenant_id,
            routing_id=routing_id,
            sequence_no=payload.sequence_no,
        )
        if conflict is not None and conflict.operation_id != op_row.operation_id:
            raise ValueError("Duplicate sequence_no in routing")
        op_row.sequence_no = payload.sequence_no
        changed_fields.append("sequence_no")

    if payload.standard_cycle_time is not None and payload.standard_cycle_time != op_row.standard_cycle_time:
        op_row.standard_cycle_time = payload.standard_cycle_time
        changed_fields.append("standard_cycle_time")

    if payload.required_resource_type is not None and payload.required_resource_type != op_row.required_resource_type:
        op_row.required_resource_type = payload.required_resource_type
        changed_fields.append("required_resource_type")

    if not changed_fields:
        return _to_item(routing)

    op_row = update_routing_operation_row(db, row=op_row)
    routing = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    _emit_routing_operation_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ROUTING.OPERATION_UPDATED",
        routing=routing,
        operation=op_row,
        changed_fields=changed_fields,
    )
    return _to_item(routing)


def remove_routing_operation(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
    operation_id: str,
) -> RoutingItem:
    routing = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if routing is None:
        raise _not_found()

    _ensure_draft_for_operation_mutation(routing)

    op_row = get_routing_operation_by_id(
        db,
        tenant_id=tenant_id,
        routing_id=routing_id,
        operation_id=operation_id,
    )
    if op_row is None:
        raise _operation_not_found()

    removed_operation_id = op_row.operation_id
    delete_routing_operation_row(db, row=op_row)
    routing = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    _emit_routing_operation_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ROUTING.OPERATION_REMOVED",
        routing=routing,
        operation=RoutingOperation(
            operation_id=removed_operation_id,
            tenant_id=tenant_id,
            routing_id=routing_id,
            operation_code="removed",
            operation_name="removed",
            sequence_no=0,
        ),
        changed_fields=["operation_id"],
    )
    return _to_item(routing)


def release_routing(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
) -> RoutingItem:
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if row is None:
        raise _not_found()

    if row.lifecycle_status == "RETIRED":
        raise ValueError("RETIRED routing cannot be released")
    if row.lifecycle_status != "DRAFT":
        raise ValueError("Only DRAFT routings can be released")

    _validate_product_link(db, tenant_id=tenant_id, product_id=row.product_id)

    row.lifecycle_status = "RELEASED"
    row = update_routing_row(db, row=row)
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=row.routing_id)
    _emit_routing_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ROUTING.RELEASED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_item(row)


def retire_routing(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    routing_id: str,
) -> RoutingItem:
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=routing_id)
    if row is None:
        raise _not_found()

    if row.lifecycle_status == "RETIRED":
        raise ValueError("Routing is already RETIRED")

    row.lifecycle_status = "RETIRED"
    row = update_routing_row(db, row=row)
    row = get_routing_row(db, tenant_id=tenant_id, routing_id=row.routing_id)
    _emit_routing_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="ROUTING.RETIRED",
        row=row,
        changed_fields=["lifecycle_status"],
    )
    return _to_item(row)
