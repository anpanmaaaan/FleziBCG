"""P0-A-15D: Approval governed context API integration coverage.

API-layer coverage for POST /api/v1/approvals proving governed context bridge
behavior through the HTTP boundary.
"""

from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.approvals as approvals_router_module
from app.models.approval import ApprovalAuditLog, ApprovalRequest
from app.models.security_event import SecurityEventLog
from app.security.dependencies import RequestIdentity


def _make_identity(tenant_id: str = "tenant-a") -> RequestIdentity:
    return RequestIdentity(
        user_id="requester-1",
        username="requester",
        email=None,
        tenant_id=tenant_id,
        role_code="OPR",
        is_authenticated=True,
        session_id="s-requester-1",
    )


def _make_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ApprovalRequest.__table__.create(bind=engine)
    ApprovalAuditLog.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


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


def _build_app(db: Session, identity: RequestIdentity) -> TestClient:
    app = FastAPI()
    app.include_router(approvals_router_module.router, prefix="/api/v1")
    app.dependency_overrides[approvals_router_module.get_db] = lambda: db
    _override_action_dependency(app, "/api/v1/approvals", "POST", identity)
    return TestClient(app)


def _legacy_payload(action_type: str = "QC_HOLD") -> dict[str, Any]:
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "approval required",
    }


def _governed_payload(
    *,
    action_type: str = "QC_HOLD",
    governed_action_type: str = "quality.work_order.qc_hold",
) -> dict[str, Any]:
    payload = _legacy_payload(action_type)
    payload.update(
        {
            "governed_resource_type": "WORK_ORDER",
            "governed_resource_id": "wo-001",
            "governed_resource_display_ref": "WO-001",
            "governed_resource_tenant_id": "tenant-a",
            "governed_resource_scope_ref": "plant:LINE-1",
            "governed_action_type": governed_action_type,
        }
    )
    return payload


def test_tapi01_post_approvals_legacy_payload_succeeds() -> None:
    """T-API-01: Legacy payload without governed context succeeds."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    response = client.post("/api/v1/approvals", json=_legacy_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["action_type"] == "QC_HOLD"
    assert body["status"] == "PENDING"
    assert body["governed_resource_type"] is None
    assert body["governed_action_type"] is None


def test_tapi02_post_approvals_with_governed_context_succeeds() -> None:
    """T-API-02: Payload with all governed context fields succeeds."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    response = client.post("/api/v1/approvals", json=_governed_payload())

    assert response.status_code == 201


def test_tapi03_api_response_includes_all_governed_context_fields() -> None:
    """T-API-03: API response includes all governed context fields."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    response = client.post("/api/v1/approvals", json=_governed_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["governed_resource_type"] == "WORK_ORDER"
    assert body["governed_resource_id"] == "wo-001"
    assert body["governed_resource_display_ref"] == "WO-001"
    assert body["governed_resource_tenant_id"] == "tenant-a"
    assert body["governed_resource_scope_ref"] == "plant:LINE-1"
    assert body["governed_action_type"] == "quality.work_order.qc_hold"


def test_tapi04_persisted_approval_request_stores_governed_context() -> None:
    """T-API-04: Persisted ApprovalRequest stores governed context from API payload."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    response = client.post("/api/v1/approvals", json=_governed_payload())

    assert response.status_code == 201
    req_id = response.json()["id"]
    row = db.scalar(select(ApprovalRequest).where(ApprovalRequest.id == req_id))
    assert row is not None
    assert row.governed_resource_type == "WORK_ORDER"
    assert row.governed_resource_id == "wo-001"
    assert row.governed_resource_display_ref == "WO-001"
    assert row.governed_resource_tenant_id == "tenant-a"
    assert row.governed_resource_scope_ref == "plant:LINE-1"
    assert row.governed_action_type == "quality.work_order.qc_hold"


def test_tapi05_requested_security_event_includes_governed_context() -> None:
    """T-API-05: APPROVAL.REQUESTED event detail includes governed context from API payload."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    response = client.post("/api/v1/approvals", json=_governed_payload())

    assert response.status_code == 201
    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.REQUESTED"
            )
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt.detail is not None
    assert "governed_resource_type=WORK_ORDER" in evt.detail
    assert "governed_resource_scope_ref=plant:LINE-1" in evt.detail
    assert "governed_action_type=quality.work_order.qc_hold" in evt.detail


def test_tapi06_invalid_legacy_action_type_is_rejected() -> None:
    """T-API-06: Invalid legacy action_type is still rejected."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    response = client.post("/api/v1/approvals", json=_legacy_payload("MASTER_DATA"))

    assert response.status_code == 400
    assert "Unknown action_type" in response.json()["detail"]


def test_tapi07_arbitrary_governed_action_type_is_accepted() -> None:
    """T-API-07: No governed action registry enforcement; arbitrary value accepted."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    payload = _governed_payload(
        governed_action_type="future.action.not.in.registry.yet"
    )
    response = client.post("/api/v1/approvals", json=payload)

    assert response.status_code == 201
    assert response.json()["governed_action_type"] == "future.action.not.in.registry.yet"


def test_tapi08_subject_type_and_subject_ref_unchanged_in_response() -> None:
    """T-API-08: subject_type and subject_ref remain present and unchanged."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    payload = _governed_payload()
    payload["subject_type"] = "operation"
    payload["subject_ref"] = "op-777"
    response = client.post("/api/v1/approvals", json=payload)

    assert response.status_code == 201
    assert response.json()["subject_type"] == "operation"
    assert response.json()["subject_ref"] == "op-777"


def test_tapi09_no_cancelled_path_or_event_is_introduced() -> None:
    """T-API-09: No cancel endpoint/event is introduced in this slice."""
    db = _make_session()
    client = _build_app(db, _make_identity())

    create_response = client.post("/api/v1/approvals", json=_legacy_payload())
    assert create_response.status_code == 201

    cancel_response = client.post("/api/v1/approvals/1/cancel", json={})
    assert cancel_response.status_code == 404

    cancelled_events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.CANCELLED"
            )
        )
    )
    assert cancelled_events == []
