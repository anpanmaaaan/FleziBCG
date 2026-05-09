from __future__ import annotations

from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.v1.quality as quality_router_module
from app.schemas.quality import (
    QualityGateDefinitionResponse,
    QualityGateInstanceResponse,
    QualityDeviationRequestItem,
    QualityNonconformanceItem,
)
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _make_identity() -> RequestIdentity:
    return RequestIdentity(
        user_id="qal-user",
        username="qal-user",
        email=None,
        tenant_id="tenant_a",
        role_code="QAL",
        is_authenticated=True,
        session_id="s-qal-1",
    )


def _build_app(identity: RequestIdentity) -> FastAPI:
    from app.api.v1.quality import get_db

    app = FastAPI()
    app.include_router(quality_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: None
    return app


def _override_action_dependency(
    app: FastAPI, path: str, method: str, identity: RequestIdentity
) -> Any:
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == path and method in (r.methods or set())
        ),
    )
    action_dependency = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[action_dependency] = lambda: identity
    return action_dependency


def test_list_quality_gate_definitions_returns_200(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)

    monkeypatch.setattr(
        quality_router_module,
        "list_quality_gate_definitions_service",
        lambda db, tenant_id: [
            QualityGateDefinitionResponse(
                gate_definition_id=1,
                code="GATE-A",
                name="Gate A",
                status="DRAFT",
                gate_type="PRE_ACCEPTANCE",
                rule_set_version="v1",
                applicability_scope_type="STATION",
                applicability_scope_value="ST-01",
                tenant_id=tenant_id,
                created_by="qal-user",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/quality/gates/definitions")

    assert response.status_code == 200
    assert response.json()[0]["code"] == "GATE-A"


def test_create_quality_gate_definition_returns_201(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)
    _override_action_dependency(app, "/api/v1/quality/gates/definitions", "POST", identity)

    monkeypatch.setattr(
        quality_router_module,
        "create_quality_gate_definition_service",
        lambda db, tenant_id, actor_user_id, payload: QualityGateDefinitionResponse(
            gate_definition_id=2,
            code=payload.code,
            name=payload.name,
            status="DRAFT",
            gate_type=payload.gate_type,
            rule_set_version=payload.rule_set_version,
            applicability_scope_type=payload.applicability_scope_type,
            applicability_scope_value=payload.applicability_scope_value,
            tenant_id=tenant_id,
            created_by=actor_user_id,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/gates/definitions",
        json={
            "code": "GATE-B",
            "name": "Gate B",
            "gate_type": "PRE_ACCEPTANCE",
            "rule_set_version": "v1",
            "applicability_scope_type": "STATION",
            "applicability_scope_value": "ST-02",
        },
    )

    assert response.status_code == 201
    assert response.json()["code"] == "GATE-B"


def test_create_quality_gate_definition_duplicate_returns_409(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)
    _override_action_dependency(app, "/api/v1/quality/gates/definitions", "POST", identity)

    def _raise(*args, **kwargs):
        raise ValueError("Duplicate quality gate code in tenant")

    monkeypatch.setattr(quality_router_module, "create_quality_gate_definition_service", _raise)

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/gates/definitions",
        json={
            "code": "GATE-B",
            "name": "Gate B",
            "gate_type": "PRE_ACCEPTANCE",
            "rule_set_version": "v1",
            "applicability_scope_type": "STATION",
            "applicability_scope_value": "ST-02",
        },
    )

    assert response.status_code == 409


def test_open_quality_gate_instance_conflict_returns_409(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)
    _override_action_dependency(app, "/api/v1/quality/gates/instances/open", "POST", identity)

    monkeypatch.setattr(
        quality_router_module,
        "open_quality_gate_instance_service",
        lambda db, tenant_id, actor_user_id, payload: (_ for _ in ()).throw(
            quality_router_module.QualityConflictError("QUALITY_GATE_INSTANCE_ALREADY_ACTIVE")
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/gates/instances/open",
        json={"operation_id": 101, "gate_definition_id": 22},
    )

    assert response.status_code == 409


def test_open_quality_gate_instance_returns_201(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)
    _override_action_dependency(app, "/api/v1/quality/gates/instances/open", "POST", identity)

    monkeypatch.setattr(
        quality_router_module,
        "open_quality_gate_instance_service",
        lambda db, tenant_id, actor_user_id, payload: QualityGateInstanceResponse(
            gate_instance_id=77,
            gate_definition_id=payload.gate_definition_id,
            operation_id=payload.operation_id,
            status="PENDING_MEASUREMENT",
            review_status="NO_REVIEW",
            opened_by=actor_user_id,
            closed_by=None,
            tenant_id=tenant_id,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z",
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/gates/instances/open",
        json={"operation_id": 101, "gate_definition_id": 22},
    )

    assert response.status_code == 201
    assert response.json()["gate_instance_id"] == 77


def test_submit_quality_measurement_missing_gate_instance_returns_404(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)

    monkeypatch.setattr(
        quality_router_module,
        "submit_qc_measurement",
        lambda db, tenant_id, actor_user_id, payload: (_ for _ in ()).throw(
            LookupError("Quality gate instance not found")
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/measurements",
        json={
            "operation_id": 101,
            "gate_instance_id": 999,
            "measurements": [{"item_code": "DIM_A", "measured_value": 10.1}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Quality gate instance not found"


def test_list_quality_deviations_returns_200(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)

    monkeypatch.setattr(
        quality_router_module,
        "list_quality_deviation_requests",
        lambda db, tenant_id: [
            QualityDeviationRequestItem(
                deviation_request_id=1,
                hold_id=10,
                gate_instance_id=33,
                status="OPEN",
                requested_by="qal-user",
                reason="Need approval",
                requested_at="2026-01-01T00:00:00Z",
                resolved_by=None,
                resolved_at=None,
                resolution_comment=None,
            )
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/quality/deviations")

    assert response.status_code == 200
    assert response.json()[0]["status"] == "OPEN"


def test_request_quality_deviation_conflict_returns_409(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)

    monkeypatch.setattr(
        quality_router_module,
        "request_quality_deviation",
        lambda db, hold_id, tenant_id, actor_user_id, payload: (_ for _ in ()).throw(
            quality_router_module.QualityConflictError("DEVIATION_REQUEST_ALREADY_OPEN")
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/holds/10/deviations",
        json={"reason": "Need deviation"},
    )

    assert response.status_code == 409


def test_list_quality_nonconformances_returns_200(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)

    monkeypatch.setattr(
        quality_router_module,
        "list_quality_nonconformances",
        lambda db, tenant_id: [
            QualityNonconformanceItem(
                nonconformance_id=1,
                nc_code="NC-001",
                operation_id=101,
                hold_id=10,
                status="OPEN",
                severity="MAJOR",
                description="Dimension out of tolerance",
                disposition_code=None,
                reported_by="qal-user",
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ],
    )

    client = TestClient(app)
    response = client.get("/api/v1/quality/nonconformances")

    assert response.status_code == 200
    assert response.json()[0]["nc_code"] == "NC-001"


def test_create_quality_nonconformance_duplicate_returns_409(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)

    monkeypatch.setattr(
        quality_router_module,
        "create_quality_nonconformance",
        lambda db, tenant_id, actor_user_id, payload: (_ for _ in ()).throw(
            ValueError("Duplicate nonconformance code in tenant")
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/nonconformances",
        json={
            "operation_id": 101,
            "nc_code": "NC-001",
            "hold_id": 10,
            "severity": "MAJOR",
            "description": "Dimension out of tolerance",
        },
    )

    assert response.status_code == 409


def test_resolve_quality_deviation_conflict_returns_409(monkeypatch):
    identity = _make_identity()
    app = _build_app(identity)
    _override_action_dependency(
        app,
        "/api/v1/quality/deviations/{deviation_request_id}/resolve",
        "POST",
        identity,
    )

    monkeypatch.setattr(
        quality_router_module,
        "resolve_quality_deviation",
        lambda db, deviation_request_id, tenant_id, actor_user_id, actor_role_code, payload: (_ for _ in ()).throw(
            quality_router_module.QualityConflictError("DEVIATION_REQUEST_NOT_OPEN")
        ),
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/quality/deviations/11/resolve",
        json={"resolution_status": "APPROVED", "resolution_comment": "approved"},
    )

    assert response.status_code == 409
