"""
08D station queue migration tests.

These tests lock session-aware control fields while preserving
queue compatibility shape.
"""

from __future__ import annotations

import test_station_queue_active_states as legacy_queue
from test_station_queue_active_states import station_queue_fixture  # noqa: F401

from app.services.station_queue_service import get_station_queue
from app.services.station_session_service import close_station_session, get_current_station_session


def test_station_queue_includes_session_ownership_summary(station_queue_fixture):
    db, ops = station_queue_fixture

    scope_value, items = get_station_queue(db, legacy_queue._identity())
    assert scope_value == legacy_queue._STATION_SCOPE_VALUE

    by_id = legacy_queue._items_by_op_id(items)
    ownership = by_id[ops["planned"].id]["ownership"]

    assert ownership["target_owner_type"] == "station_session"
    assert ownership["has_open_session"] is True
    assert ownership["station_id"] == legacy_queue._STATION_SCOPE_VALUE
    assert ownership["session_status"] == "OPEN"
    assert ownership["operator_user_id"] == legacy_queue._USER_ID
    assert ownership["owner_state"] == "mine"
    assert ownership["session_id"] is not None


def test_station_queue_ownership_summary_handles_no_open_session(station_queue_fixture):
    db, ops = station_queue_fixture

    identity = legacy_queue._identity()
    session = get_current_station_session(
        db,
        identity,
        station_id=legacy_queue._STATION_SCOPE_VALUE,
    )
    assert session is not None
    close_station_session(db, identity, session_id=session.session_id)

    _, items = get_station_queue(db, identity)
    by_id = legacy_queue._items_by_op_id(items)
    ownership = by_id[ops["planned"].id]["ownership"]

    assert ownership["target_owner_type"] == "station_session"
    assert ownership["has_open_session"] is False
    assert ownership["session_id"] is None
    assert ownership["station_id"] is None
    assert ownership["session_status"] is None
    assert ownership["operator_user_id"] is None
    assert ownership["owner_state"] == "none"
