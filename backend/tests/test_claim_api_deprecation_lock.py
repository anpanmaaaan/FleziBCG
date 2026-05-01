from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.v1 import station as station_router_module
from app.api.v1 import station_sessions as station_sessions_router_module
from app.main import app
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _identity() -> RequestIdentity:
    return RequestIdentity(
        user_id="test-opr",
        username="test-opr",
        email=None,
        tenant_id="default",
        role_code="OPR",
        is_authenticated=True,
        session_id="session-test",
    )


def _assert_claim_deprecation_headers(response) -> None:
    assert response.headers.get("Deprecation") == "true"
    assert (
        response.headers.get("X-FleziBCG-Deprecation-Status")
        == "compatibility-only"
    )
    assert response.headers.get("X-FleziBCG-Replacement") == "StationSession"


def _assert_no_claim_deprecation_headers(response) -> None:
    assert "Deprecation" not in response.headers
    assert "X-FleziBCG-Deprecation-Status" not in response.headers
    assert "X-FleziBCG-Replacement" not in response.headers


def test_claim_endpoint_returns_compatibility_deprecation_headers(monkeypatch):
    app.dependency_overrides[require_authenticated_identity] = _identity
    app.dependency_overrides[station_router_module.get_db] = lambda: None

    now = datetime.now(timezone.utc)
    fake_claim = SimpleNamespace(
        operation_id=101,
        claimed_by_user_id="test-opr",
        claimed_at=now,
        expires_at=now,
    )

    monkeypatch.setattr(
        station_router_module,
        "claim_operation",
        lambda db, identity, operation_id, reason=None, duration_minutes=None: (
            fake_claim,
            "STATION_01",
        ),
    )

    client = TestClient(app)
    resp = client.post(
        "/api/v1/station/queue/101/claim",
        json={"reason": "compat", "duration_minutes": 30},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["operation_id"] == 101
    assert body["state"] == "mine"
    _assert_claim_deprecation_headers(resp)

    app.dependency_overrides.clear()


def test_release_endpoint_returns_compatibility_deprecation_headers(monkeypatch):
    app.dependency_overrides[require_authenticated_identity] = _identity
    app.dependency_overrides[station_router_module.get_db] = lambda: None

    now = datetime.now(timezone.utc)
    fake_claim = SimpleNamespace(
        operation_id=102,
        claimed_by_user_id="test-opr",
        claimed_at=now,
        expires_at=now,
    )

    monkeypatch.setattr(
        station_router_module,
        "release_operation_claim",
        lambda db, identity, operation_id, reason=None: (fake_claim, "STATION_01"),
    )

    client = TestClient(app)
    resp = client.post(
        "/api/v1/station/queue/102/release",
        json={"reason": "done"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["operation_id"] == 102
    assert body["state"] == "none"
    _assert_claim_deprecation_headers(resp)

    app.dependency_overrides.clear()


def test_claim_status_endpoint_returns_compatibility_deprecation_headers(monkeypatch):
    app.dependency_overrides[require_authenticated_identity] = _identity
    app.dependency_overrides[station_router_module.get_db] = lambda: None

    monkeypatch.setattr(
        station_router_module,
        "get_operation_claim_status",
        lambda db, identity, operation_id: {
            "state": "mine",
            "expires_at": None,
            "claimed_by_user_id": "test-opr",
            "station_scope_value": "STATION_01",
        },
    )

    client = TestClient(app)
    resp = client.get("/api/v1/station/queue/103/claim")

    assert resp.status_code == 200
    assert resp.json()["state"] == "mine"
    _assert_claim_deprecation_headers(resp)

    app.dependency_overrides.clear()


def test_station_queue_endpoint_remains_non_deprecated_with_compat_claim_payload(
    monkeypatch,
):
    app.dependency_overrides[require_authenticated_identity] = _identity
    app.dependency_overrides[station_router_module.get_db] = lambda: None

    now = datetime.now(timezone.utc)
    monkeypatch.setattr(
        station_router_module,
        "get_station_queue",
        lambda db, identity: (
            "STATION_01",
            [
                {
                    "operation_id": 200,
                    "operation_number": "OP-200",
                    "name": "Operation",
                    "work_order_number": "WO-200",
                    "production_order_number": "PO-200",
                    "status": "planned",
                    "planned_start": now,
                    "planned_end": now,
                    "claim": {
                        "state": "none",
                        "expires_at": None,
                        "claimed_by_user_id": None,
                    },
                    "ownership": {
                        "target_owner_type": "station_session",
                        "ownership_migration_status": "TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT",
                        "session_id": None,
                        "station_id": None,
                        "session_status": None,
                        "operator_user_id": None,
                        "owner_state": "none",
                        "has_open_session": False,
                    },
                    "downtime_open": False,
                }
            ],
        ),
    )

    client = TestClient(app)
    resp = client.get("/api/v1/station/queue")

    assert resp.status_code == 200
    body = resp.json()
    assert body["items"][0]["ownership"]["target_owner_type"] == "station_session"
    assert body["items"][0]["claim"]["state"] == "none"
    _assert_no_claim_deprecation_headers(resp)

    app.dependency_overrides.clear()


def test_station_session_endpoint_does_not_receive_claim_deprecation_headers(monkeypatch):
    app.dependency_overrides[require_authenticated_identity] = _identity
    app.dependency_overrides[station_sessions_router_module.get_db] = lambda: None

    monkeypatch.setattr(
        station_sessions_router_module,
        "get_current_station_session",
        lambda db, identity, station_id: None,
    )

    client = TestClient(app)
    resp = client.get("/api/v1/station/sessions/current", params={"station_id": "STATION_01"})

    assert resp.status_code == 200
    assert resp.json() == {"session": None}
    _assert_no_claim_deprecation_headers(resp)

    app.dependency_overrides.clear()
