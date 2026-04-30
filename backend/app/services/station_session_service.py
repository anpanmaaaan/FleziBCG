from __future__ import annotations

import json
from datetime import datetime, timezone
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.rbac import Scope, UserRoleAssignment
from app.models.station_session import StationSession
from app.repositories.station_session_repository import (
    create_station_session,
    get_active_station_session_for_station,
    get_station_session_by_id,
    update_station_session,
)
from app.schemas.station_session import (
    BindEquipmentRequest,
    OpenStationSessionRequest,
    IdentifyOperatorRequest,
)
from app.security.dependencies import RequestIdentity
from app.services.security_event_service import record_security_event

_CANONICAL_EVENT_STATUS = [
    "CANONICAL_FOR_P0_C_STATION_SESSION",
]


class StationSessionConflictError(Exception):
    pass


def _normalize_non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _require_station_scope_access(
    db: Session,
    *,
    identity: RequestIdentity,
    station_id: str,
) -> Scope:
    station_scope = db.scalar(
        select(Scope)
        .join(UserRoleAssignment, UserRoleAssignment.scope_id == Scope.id)
        .where(
            Scope.tenant_id == identity.tenant_id,
            Scope.scope_type == "station",
            Scope.scope_value == station_id,
            UserRoleAssignment.user_id == identity.user_id,
            UserRoleAssignment.is_active.is_(True),
        )
        .order_by(UserRoleAssignment.is_primary.desc(), UserRoleAssignment.id.asc())
    )
    if station_scope is None:
        raise PermissionError("Station is outside your station scope")
    return station_scope


def _require_operator_eligible_for_station(
    db: Session,
    *,
    tenant_id: str,
    station_id: str,
    operator_user_id: str,
) -> None:
    operator_scope = db.scalar(
        select(Scope)
        .join(UserRoleAssignment, UserRoleAssignment.scope_id == Scope.id)
        .where(
            Scope.tenant_id == tenant_id,
            Scope.scope_type == "station",
            Scope.scope_value == station_id,
            UserRoleAssignment.user_id == operator_user_id,
            UserRoleAssignment.is_active.is_(True),
        )
        .order_by(UserRoleAssignment.is_primary.desc(), UserRoleAssignment.id.asc())
    )
    if operator_scope is None:
        raise ValueError("operator_user_id is not active for station scope")


def _ensure_open_mutable(row: StationSession) -> None:
    if row.status == "CLOSED" or row.closed_at is not None:
        raise ValueError("Station session is CLOSED")


def _emit_station_session_event(
    db: Session,
    *,
    event_type: str,
    identity: RequestIdentity,
    session: StationSession,
    changed_fields: list[str],
) -> None:
    detail = json.dumps(
        {
            "session_id": session.session_id,
            "tenant_id": session.tenant_id,
            "station_id": session.station_id,
            "operator_user_id": session.operator_user_id,
            "equipment_id": session.equipment_id,
            "current_operation_id": session.current_operation_id,
            "status": session.status,
            "changed_fields": changed_fields,
            "event_name_status": _CANONICAL_EVENT_STATUS,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    record_security_event(
        db,
        tenant_id=identity.tenant_id,
        actor_user_id=identity.user_id,
        event_type=event_type,
        resource_type="station_session",
        resource_id=session.session_id,
        detail=detail,
    )


def open_station_session(
    db: Session,
    identity: RequestIdentity,
    *,
    station_id: str,
    payload: OpenStationSessionRequest | None = None,
) -> StationSession:
    normalized_station = _normalize_non_empty(station_id, field_name="station_id")
    _require_station_scope_access(db, identity=identity, station_id=normalized_station)

    active = get_active_station_session_for_station(
        db,
        tenant_id=identity.tenant_id,
        station_id=normalized_station,
        for_update=True,
    )
    if active is not None:
        raise StationSessionConflictError(
            "Station already has an active OPEN session"
        )

    operator_user_id = None
    equipment_id = None
    current_operation_id = None
    if payload is not None:
        operator_user_id = payload.operator_user_id
        equipment_id = payload.equipment_id
        current_operation_id = payload.current_operation_id

    if operator_user_id is not None:
        operator_user_id = _normalize_non_empty(
            operator_user_id,
            field_name="operator_user_id",
        )
        _require_operator_eligible_for_station(
            db,
            tenant_id=identity.tenant_id,
            station_id=normalized_station,
            operator_user_id=operator_user_id,
        )

    session = StationSession(
        session_id=uuid.uuid4().hex,
        tenant_id=identity.tenant_id,
        station_id=normalized_station,
        operator_user_id=operator_user_id,
        status="OPEN",
        equipment_id=equipment_id,
        current_operation_id=current_operation_id,
        event_name_status=json.dumps(_CANONICAL_EVENT_STATUS, separators=(",", ":")),
    )
    try:
        session = create_station_session(db, row=session)
    except IntegrityError as exc:
        db.rollback()
        raise StationSessionConflictError(
            "Station already has an active OPEN session"
        ) from exc

    _emit_station_session_event(
        db,
        event_type="STATION_SESSION.OPENED",
        identity=identity,
        session=session,
        changed_fields=[
            "station_id",
            "operator_user_id",
            "status",
            "equipment_id",
            "current_operation_id",
        ],
    )
    return get_station_session_by_id(
        db,
        tenant_id=identity.tenant_id,
        session_id=session.session_id,
    )


def get_current_station_session(
    db: Session,
    identity: RequestIdentity,
    *,
    station_id: str,
) -> StationSession | None:
    normalized_station = _normalize_non_empty(station_id, field_name="station_id")
    _require_station_scope_access(db, identity=identity, station_id=normalized_station)
    return get_active_station_session_for_station(
        db,
        tenant_id=identity.tenant_id,
        station_id=normalized_station,
    )


def identify_operator_at_station(
    db: Session,
    identity: RequestIdentity,
    *,
    session_id: str,
    operator_user_id: str,
) -> StationSession:
    normalized_operator = _normalize_non_empty(
        operator_user_id,
        field_name="operator_user_id",
    )
    row = get_station_session_by_id(
        db,
        tenant_id=identity.tenant_id,
        session_id=session_id,
    )
    if row is None:
        raise LookupError("Station session not found")

    _require_station_scope_access(db, identity=identity, station_id=row.station_id)
    _ensure_open_mutable(row)
    _require_operator_eligible_for_station(
        db,
        tenant_id=identity.tenant_id,
        station_id=row.station_id,
        operator_user_id=normalized_operator,
    )

    row.operator_user_id = normalized_operator
    row = update_station_session(db, row=row)
    _emit_station_session_event(
        db,
        event_type="STATION_SESSION.OPERATOR_IDENTIFIED",
        identity=identity,
        session=row,
        changed_fields=["operator_user_id"],
    )
    return get_station_session_by_id(
        db,
        tenant_id=identity.tenant_id,
        session_id=row.session_id,
    )


def bind_equipment_to_station_session(
    db: Session,
    identity: RequestIdentity,
    *,
    session_id: str,
    equipment_id: str,
) -> StationSession:
    normalized_equipment = _normalize_non_empty(
        equipment_id,
        field_name="equipment_id",
    )
    row = get_station_session_by_id(
        db,
        tenant_id=identity.tenant_id,
        session_id=session_id,
    )
    if row is None:
        raise LookupError("Station session not found")

    _require_station_scope_access(db, identity=identity, station_id=row.station_id)
    _ensure_open_mutable(row)

    row.equipment_id = normalized_equipment
    row = update_station_session(db, row=row)
    _emit_station_session_event(
        db,
        event_type="STATION_SESSION.EQUIPMENT_BOUND",
        identity=identity,
        session=row,
        changed_fields=["equipment_id"],
    )
    return get_station_session_by_id(
        db,
        tenant_id=identity.tenant_id,
        session_id=row.session_id,
    )


def close_station_session(
    db: Session,
    identity: RequestIdentity,
    *,
    session_id: str,
) -> StationSession:
    row = get_station_session_by_id(
        db,
        tenant_id=identity.tenant_id,
        session_id=session_id,
    )
    if row is None:
        raise LookupError("Station session not found")

    _require_station_scope_access(db, identity=identity, station_id=row.station_id)
    if row.status == "CLOSED" or row.closed_at is not None:
        raise ValueError("Station session is already CLOSED")

    row.status = "CLOSED"
    row.closed_at = datetime.now(timezone.utc)
    row = update_station_session(db, row=row)
    _emit_station_session_event(
        db,
        event_type="STATION_SESSION.CLOSED",
        identity=identity,
        session=row,
        changed_fields=["status", "closed_at"],
    )
    return get_station_session_by_id(
        db,
        tenant_id=identity.tenant_id,
        session_id=row.session_id,
    )
