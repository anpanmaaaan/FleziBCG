from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.v1.station as station_router_module
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _identity() -> RequestIdentity:
    return RequestIdentity(
        user_id="sup-001",
        username="sup-001",
        email=None,
        tenant_id="default",
        role_code="SUP",
        is_authenticated=True,
    )


def test_station_line_monitor_endpoint_returns_projection(monkeypatch):
    from app.api.v1.station import get_db

    app = FastAPI()
    app.include_router(station_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: _identity()
    app.dependency_overrides[get_db] = lambda: None

    captured_line_code = {"value": None}

    def _fake_service(db, identity, line_code=None):
        captured_line_code["value"] = line_code
        return [
            {
                "station_id": "ST-A",
                "station_name": "Station A",
                "line_code": "LINE-A",
                "line_name": "Line A",
                "status": "RUNNING",
                "operator_user_id": "opr-a",
                "current_operation_id": 101,
                "current_operation_number": "OP-101",
                "current_operation_name": "Operation 101",
                "wip_count": 2,
                "downtime_open": False,
            }
        ]

    monkeypatch.setattr(station_router_module, "get_line_monitor_projection", _fake_service)

    client = TestClient(app)
    response = client.get("/api/v1/station/line-monitor?line_code=LINE-A")

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["station_id"] == "ST-A"
    assert payload["items"][0]["status"] == "RUNNING"
    assert captured_line_code["value"] == "LINE-A"
