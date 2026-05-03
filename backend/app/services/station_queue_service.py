from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.repositories.station_session_repository import (
    get_active_station_session_for_station,
)
from app.security.dependencies import RequestIdentity
from app.services.operation_service import derive_operation_runtime_projection_for_ids


@dataclass
class StationScopeContext:
    scope_id: int
    scope_value: str


def _normalize_role(role_code: str | None) -> str:
    if not role_code:
        return ""
    return role_code.strip().upper()


# INTENT: Resolves the effective role for station access, preferring the
# impersonated (acting) role over the user's own role.
def _effective_role(identity: RequestIdentity) -> str:
    acting_role = _normalize_role(identity.acting_role_code)
    if acting_role:
        return acting_role
    return _normalize_role(identity.role_code)


def ensure_operator_context(identity: RequestIdentity) -> None:
    if _effective_role(identity) != "OPR":
        raise PermissionError(
            "Station queue is only available to OPR context."
        )


# EDGE: Station scope is resolved from UserRoleAssignment, isolating the
# operator to their assigned station(s) within the tenant.
def resolve_station_scope(
    db: Session, identity: RequestIdentity
) -> StationScopeContext:
    statement = (
        select(UserRoleAssignment, Scope)
        .join(Role, Role.id == UserRoleAssignment.role_id)
        .join(Scope, Scope.id == UserRoleAssignment.scope_id)
        .where(
            UserRoleAssignment.user_id == identity.user_id,
            UserRoleAssignment.is_active.is_(True),
            Role.code == "OPR",
            Scope.tenant_id == identity.tenant_id,
            Scope.scope_type == "station",
        )
        .order_by(UserRoleAssignment.is_primary.desc(), UserRoleAssignment.id.asc())
    )
    rows = list(db.execute(statement))
    now = datetime.now(timezone.utc)
    for assignment, scope in rows:
        if assignment.valid_from is not None and assignment.valid_from > now:
            continue
        if assignment.valid_to is not None and assignment.valid_to < now:
            continue
        return StationScopeContext(scope_id=scope.id, scope_value=scope.scope_value)

    raise ValueError("No station scope assigned")


def get_station_scoped_operation(
    db: Session,
    identity: RequestIdentity,
    operation_id: int,
) -> Operation:
    ensure_operator_context(identity)
    station_scope = resolve_station_scope(db, identity)

    operation = db.scalar(
        select(Operation).where(
            Operation.id == operation_id,
            Operation.tenant_id == identity.tenant_id,
        )
    )
    if operation is None:
        raise LookupError("Operation not found")

    if operation.station_scope_value != station_scope.scope_value:
        raise PermissionError("Operation is outside your station scope")

    return operation


def _to_session_owner_state(identity: RequestIdentity, operator_user_id: str | None) -> str:
    if not operator_user_id:
        return "unassigned"
    if operator_user_id == identity.user_id:
        return "mine"
    return "other"


def get_station_queue(db: Session, identity: RequestIdentity) -> tuple[str, list[dict]]:
    ensure_operator_context(identity)
    station_scope = resolve_station_scope(db, identity)

    # Active non-terminal runtime states the operator must still see.
    # Canonical per station-execution-state-matrix.md — terminal states
    # (COMPLETED, COMPLETED_LATE, ABORTED) are deliberately excluded so the
    # queue stays a "what can I still act on" list. PAUSED and BLOCKED are
    # included because pause_execution / start_downtime would otherwise make
    # an in-flight operation vanish from the picker (SE-AUDIT-OPERATION-
    # SELECTION-LIST-001). Runtime status source of truth is append-only
    # event derivation; Operation.status is projection only.
    active_queue_statuses = {
        StatusEnum.planned.value,
        StatusEnum.in_progress.value,
        StatusEnum.paused.value,
        StatusEnum.blocked.value,
    }

    statement = (
        select(Operation, WorkOrder, ProductionOrder)
        .join(WorkOrder, WorkOrder.id == Operation.work_order_id)
        .join(ProductionOrder, ProductionOrder.id == WorkOrder.production_order_id)
        .where(
            Operation.tenant_id == identity.tenant_id,
            Operation.station_scope_value == station_scope.scope_value,
        )
        .order_by(
            Operation.planned_start.asc().nullslast(),
            Operation.planned_end.asc().nullslast(),
            Operation.id.asc(),
        )
    )

    rows = list(db.execute(statement))
    operation_ids = [operation.id for operation, _wo, _po in rows]
    runtime_projection_by_operation_id = derive_operation_runtime_projection_for_ids(
        db,
        tenant_id=identity.tenant_id,
        operation_ids=operation_ids,
    )
    active_rows = [
        row
        for row in rows
        if runtime_projection_by_operation_id.get(row[0].id) is not None
        and runtime_projection_by_operation_id[row[0].id].status in active_queue_statuses
    ]

    active_station_session = get_active_station_session_for_station(
        db,
        tenant_id=identity.tenant_id,
        station_id=station_scope.scope_value,
    )

    db.commit()

    items: list[dict] = []
    for operation, work_order, production_order in active_rows:
        runtime_projection = runtime_projection_by_operation_id[operation.id]
        items.append(
            {
                "operation_id": operation.id,
                "operation_number": operation.operation_number,
                "name": operation.name,
                "work_order_number": work_order.work_order_number,
                "production_order_number": production_order.order_number,
                "status": runtime_projection.status,
                "planned_start": operation.planned_start,
                "planned_end": operation.planned_end,
                "ownership": {
                    "target_owner_type": "station_session",
                    "session_id": (
                        active_station_session.session_id
                        if active_station_session is not None
                        else None
                    ),
                    "station_id": (
                        active_station_session.station_id
                        if active_station_session is not None
                        else None
                    ),
                    "session_status": (
                        active_station_session.status
                        if active_station_session is not None
                        else None
                    ),
                    "operator_user_id": (
                        active_station_session.operator_user_id
                        if active_station_session is not None
                        else None
                    ),
                    "owner_state": _to_session_owner_state(
                        identity,
                        (
                            active_station_session.operator_user_id
                            if active_station_session is not None
                            else None
                        ),
                    )
                    if active_station_session is not None
                    else "none",
                    "has_open_session": active_station_session is not None,
                },
                "downtime_open": runtime_projection.downtime_open,
            }
        )

    return station_scope.scope_value, items