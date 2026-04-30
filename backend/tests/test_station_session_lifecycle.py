from __future__ import annotations

import json
from sqlalchemy import delete, select

import pytest

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.security_event import SecurityEventLog
from app.models.station_session import StationSession
from app.security.dependencies import RequestIdentity
from app.services.station_session_service import (
    StationSessionConflictError,
    bind_equipment_to_station_session,
    close_station_session,
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

_PREFIX = "TEST-STATION-SESSION"
_TENANT_ID = "default"
_OTHER_TENANT_ID = "tenant-b"
_STATION_A = f"{_PREFIX}-A"
_STATION_B = f"{_PREFIX}-B"
_ACTOR_MULTI = f"{_PREFIX}-ACTOR-MULTI"
_ACTOR_A_ONLY = f"{_PREFIX}-ACTOR-A-ONLY"
_OPERATOR_A = f"{_PREFIX}-OPR-A"
_OPERATOR_B = f"{_PREFIX}-OPR-B"


def _identity(user_id: str, tenant_id: str = _TENANT_ID) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username=user_id,
        email=None,
        tenant_id=tenant_id,
        role_code="OPR",
        acting_role_code=None,
        is_authenticated=True,
    )


def _ensure_opr_role(db) -> Role:
    role = db.scalar(select(Role).where(Role.code == "OPR"))
    if role is not None:
        return role
    role = Role(code="OPR", name="Operator", role_type="system", is_system=True)
    db.add(role)
    db.flush()
    return role


def _purge(db) -> None:
    db.execute(
        delete(SecurityEventLog).where(
            SecurityEventLog.resource_type == "station_session",
            SecurityEventLog.resource_id.like(f"{_PREFIX}-%"),
        )
    )
    db.execute(
        delete(StationSession).where(
            StationSession.station_id.in_([_STATION_A, _STATION_B]),
            StationSession.tenant_id == _TENANT_ID,
        )
    )
    db.execute(
        delete(UserRoleAssignment).where(
            UserRoleAssignment.user_id.in_(
                [_ACTOR_MULTI, _ACTOR_A_ONLY, _OPERATOR_A, _OPERATOR_B]
            )
        )
    )
    db.execute(
        delete(Scope).where(
            Scope.scope_value.in_([_STATION_A, _STATION_B]),
            Scope.tenant_id.in_([_TENANT_ID, _OTHER_TENANT_ID]),
        )
    )
    db.commit()


@pytest.fixture
def station_session_fixture():
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        opr_role = _ensure_opr_role(db)

        scope_a = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=_STATION_A,
        )
        scope_b = Scope(
            tenant_id=_TENANT_ID,
            scope_type="station",
            scope_value=_STATION_B,
        )
        db.add_all([scope_a, scope_b])
        db.flush()

        db.add_all(
            [
                UserRoleAssignment(
                    user_id=_ACTOR_MULTI,
                    role_id=opr_role.id,
                    scope_id=scope_a.id,
                    is_primary=True,
                    is_active=True,
                ),
                UserRoleAssignment(
                    user_id=_ACTOR_MULTI,
                    role_id=opr_role.id,
                    scope_id=scope_b.id,
                    is_primary=False,
                    is_active=True,
                ),
                UserRoleAssignment(
                    user_id=_ACTOR_A_ONLY,
                    role_id=opr_role.id,
                    scope_id=scope_a.id,
                    is_primary=True,
                    is_active=True,
                ),
                UserRoleAssignment(
                    user_id=_OPERATOR_A,
                    role_id=opr_role.id,
                    scope_id=scope_a.id,
                    is_primary=True,
                    is_active=True,
                ),
                UserRoleAssignment(
                    user_id=_OPERATOR_B,
                    role_id=opr_role.id,
                    scope_id=scope_b.id,
                    is_primary=True,
                    is_active=True,
                ),
            ]
        )
        db.commit()
        yield db
    finally:
        _purge(db)
        db.close()


def test_open_station_session_happy_path_emits_candidate_event(station_session_fixture):
    db = station_session_fixture

    session = open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)

    assert session.session_id
    assert session.tenant_id == _TENANT_ID
    assert session.station_id == _STATION_A
    assert session.status == "OPEN"
    assert session.operator_user_id is None

    event = db.scalar(
        select(SecurityEventLog)
        .where(SecurityEventLog.resource_id == session.session_id)
        .order_by(SecurityEventLog.id.desc())
    )
    assert event is not None
    assert event.event_type == "STATION_SESSION.OPENED"
    detail = json.loads(event.detail or "{}")
    assert "CANONICAL_FOR_P0_C_STATION_SESSION" in detail.get("event_name_status", [])


def test_reject_second_active_session_for_same_station(station_session_fixture):
    db = station_session_fixture

    open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)

    with pytest.raises(
        StationSessionConflictError,
        match="already has an active OPEN session",
    ):
        open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)


def test_allow_active_sessions_for_different_stations(station_session_fixture):
    db = station_session_fixture

    first = open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)
    second = open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_B)

    assert first.status == "OPEN"
    assert second.status == "OPEN"
    assert first.station_id != second.station_id


def test_identify_operator_happy_path(station_session_fixture):
    db = station_session_fixture

    opened = open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)
    identified = identify_operator_at_station(
        db,
        _identity(_ACTOR_MULTI),
        session_id=opened.session_id,
        operator_user_id=_OPERATOR_A,
    )

    assert identified.operator_user_id == _OPERATOR_A


def test_bind_equipment_happy_path(station_session_fixture):
    db = station_session_fixture

    opened = open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)
    bound = bind_equipment_to_station_session(
        db,
        _identity(_ACTOR_MULTI),
        session_id=opened.session_id,
        equipment_id="EQ-01",
    )

    assert bound.equipment_id == "EQ-01"


def test_close_session_and_closed_terminal_rules(station_session_fixture):
    db = station_session_fixture

    opened = open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)
    closed = close_station_session(db, _identity(_ACTOR_MULTI), session_id=opened.session_id)

    assert closed.status == "CLOSED"
    assert closed.closed_at is not None

    with pytest.raises(ValueError, match="CLOSED"):
        identify_operator_at_station(
            db,
            _identity(_ACTOR_MULTI),
            session_id=opened.session_id,
            operator_user_id=_OPERATOR_A,
        )

    with pytest.raises(ValueError, match="CLOSED"):
        bind_equipment_to_station_session(
            db,
            _identity(_ACTOR_MULTI),
            session_id=opened.session_id,
            equipment_id="EQ-02",
        )

    with pytest.raises(ValueError, match="already CLOSED"):
        close_station_session(db, _identity(_ACTOR_MULTI), session_id=opened.session_id)


def test_tenant_mismatch_rejected(station_session_fixture):
    db = station_session_fixture

    with pytest.raises(PermissionError, match="outside your station scope"):
        open_station_session(
            db,
            _identity(_ACTOR_MULTI, tenant_id=_OTHER_TENANT_ID),
            station_id=_STATION_A,
        )


def test_station_mismatch_rejected(station_session_fixture):
    db = station_session_fixture

    with pytest.raises(PermissionError, match="outside your station scope"):
        open_station_session(db, _identity(_ACTOR_A_ONLY), station_id=_STATION_B)


def test_get_current_station_session_returns_open_session(station_session_fixture):
    db = station_session_fixture

    opened = open_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)
    current = get_current_station_session(db, _identity(_ACTOR_MULTI), station_id=_STATION_A)

    assert current is not None
    assert current.session_id == opened.session_id
