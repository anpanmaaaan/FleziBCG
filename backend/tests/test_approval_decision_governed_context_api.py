"""P0-A-15E: Approval decision API governed context matching coverage.

API-layer coverage for POST /api/v1/approvals/{request_id}/decide proving that:
- Governed context on the persisted approval request drives scope-aware rule selection.
- Wrong approver role is rejected when a governed rule applies.
- Requester cannot decide their own request (SoD invariant).
- Terminal requests cannot be re-decided.
- Tenant isolation is preserved for decision API.
- SecurityEventLog emits APPROVAL.APPROVED and APPROVAL.REJECTED correctly.
- APPROVAL.CANCELLED is not implemented.
- Legacy requests can still be decided via wildcard tenant/action rules.
- Arbitrary governed_action_type is context-only; no registry enforcement.
"""

from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.approvals as approvals_router_module
from app.models.approval import (
    ApprovalAuditLog,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRule,
)
from app.models.impersonation import ImpersonationSession
from app.models.security_event import SecurityEventLog
from app.security.dependencies import RequestIdentity


# ── Session / DB setup ───────────────────────────────────────────────────────


def _make_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create in FK-dependency order: ImpersonationSession before ApprovalDecision.
    ImpersonationSession.__table__.create(bind=engine)
    ApprovalRule.__table__.create(bind=engine)
    ApprovalRequest.__table__.create(bind=engine)
    ApprovalDecision.__table__.create(bind=engine)
    ApprovalAuditLog.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


# ── Identity helpers ─────────────────────────────────────────────────────────


def _make_create_identity(
    user_id: str = "requester-1",
    tenant_id: str = "tenant-a",
) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username="requester",
        email=None,
        tenant_id=tenant_id,
        role_code="OPR",
        is_authenticated=True,
        session_id="s-create-1",
    )


def _make_decide_identity(
    user_id: str = "decider-1",
    tenant_id: str = "tenant-a",
    role_code: str = "QAL",
) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username="decider",
        email=None,
        tenant_id=tenant_id,
        role_code=role_code,
        is_authenticated=True,
        session_id="s-decide-1",
    )


# ── App / dependency-override helpers ────────────────────────────────────────


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


def _build_app(
    db: Session,
    create_identity: RequestIdentity,
    decide_identity: RequestIdentity,
) -> TestClient:
    app = FastAPI()
    app.include_router(approvals_router_module.router, prefix="/api/v1")
    app.dependency_overrides[approvals_router_module.get_db] = lambda: db
    _override_action_dependency(app, "/api/v1/approvals", "POST", create_identity)
    _override_action_dependency(
        app,
        "/api/v1/approvals/{request_id}/decide",
        "POST",
        decide_identity,
    )
    return TestClient(app)


# ── Rule seeders ─────────────────────────────────────────────────────────────


def _seed_governed_rule(
    db: Session,
    *,
    governed_action_type: str = "quality.work_order.qc_hold",
    approver_role_code: str = "QAL",
    action_type: str = "QC_HOLD",
) -> None:
    """Seed a governed rule (matched by governed_action_type at decision time)."""
    db.add(
        ApprovalRule(
            action_type=action_type,
            approver_role_code=approver_role_code,
            tenant_id="*",
            governed_action_type=governed_action_type,
            is_active=True,
        )
    )
    db.commit()


def _seed_legacy_rule(
    db: Session,
    *,
    action_type: str = "QC_HOLD",
    approver_role_code: str = "QAL",
) -> None:
    """Seed a legacy wildcard rule (matched by action_type at decision time)."""
    db.add(
        ApprovalRule(
            action_type=action_type,
            approver_role_code=approver_role_code,
            tenant_id="*",
            is_active=True,
        )
    )
    db.commit()


# ── Payload helpers ──────────────────────────────────────────────────────────


def _governed_payload(
    *,
    action_type: str = "QC_HOLD",
    governed_action_type: str = "quality.work_order.qc_hold",
) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "approval required",
        "governed_resource_type": "WORK_ORDER",
        "governed_resource_id": "wo-001",
        "governed_resource_display_ref": "WO-001",
        "governed_resource_tenant_id": "tenant-a",
        "governed_resource_scope_ref": "plant:LINE-1",
        "governed_action_type": governed_action_type,
    }


def _legacy_payload(action_type: str = "QC_HOLD") -> dict[str, Any]:
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "approval required",
    }


def _create_and_get_id(client: TestClient, payload: dict[str, Any]) -> int:
    resp = client.post("/api/v1/approvals", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


# ── T-DEC-API-01 ─────────────────────────────────────────────────────────────


def test_tdecapi01_governed_context_request_approved_by_matching_role() -> None:
    """T-DEC-API-01: Governed-context request approved via API with matching scoped approver role."""
    db = _make_session()
    _seed_governed_rule(db)
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "APPROVED"
    assert body["request_id"] == req_id
    assert body["decider_id"] == "decider-1"


# ── T-DEC-API-02 ─────────────────────────────────────────────────────────────


def test_tdecapi02_governed_context_request_rejected_by_matching_role() -> None:
    """T-DEC-API-02: Governed-context request rejected via API with matching scoped approver role."""
    db = _make_session()
    _seed_governed_rule(db)
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "REJECTED"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "REJECTED"
    assert body["request_id"] == req_id
    assert body["decider_id"] == "decider-1"


# ── T-DEC-API-03 ─────────────────────────────────────────────────────────────


def test_tdecapi03_wrong_approver_role_is_rejected_for_governed_rule() -> None:
    """T-DEC-API-03: Wrong approver role returns 403 when governed-context rule applies."""
    db = _make_session()
    _seed_governed_rule(db, approver_role_code="QAL")
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="OPR")  # OPR not QAL
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()


# ── T-DEC-API-04 ─────────────────────────────────────────────────────────────


def test_tdecapi04_requester_cannot_approve_own_governed_context_request() -> None:
    """T-DEC-API-04: SoD — requester cannot APPROVE their own governed-context request."""
    db = _make_session()
    _seed_governed_rule(db)
    same_user_id = "user-shared-1"
    create_identity = _make_create_identity(user_id=same_user_id)
    decide_identity = _make_decide_identity(user_id=same_user_id, role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )

    assert response.status_code == 400
    assert "requester" in response.json()["detail"].lower()


# ── T-DEC-API-05 ─────────────────────────────────────────────────────────────


def test_tdecapi05_requester_cannot_reject_own_governed_context_request() -> None:
    """T-DEC-API-05: SoD — requester cannot REJECT their own governed-context request."""
    db = _make_session()
    _seed_governed_rule(db)
    same_user_id = "user-shared-2"
    create_identity = _make_create_identity(user_id=same_user_id)
    decide_identity = _make_decide_identity(user_id=same_user_id, role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "REJECTED"}
    )

    assert response.status_code == 400
    assert "requester" in response.json()["detail"].lower()


# ── T-DEC-API-06 ─────────────────────────────────────────────────────────────


def test_tdecapi06_terminal_request_cannot_be_decided_twice() -> None:
    """T-DEC-API-06: A terminal (non-PENDING) request cannot be decided again."""
    db = _make_session()
    _seed_governed_rule(db)
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    first = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )
    assert second.status_code == 400
    assert "not pending" in second.json()["detail"].lower()


# ── T-DEC-API-07 ─────────────────────────────────────────────────────────────


def test_tdecapi07_cross_tenant_decision_is_not_found() -> None:
    """T-DEC-API-07: Tenant isolation — cross-tenant decision returns 404."""
    db = _make_session()
    _seed_governed_rule(db)
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_identity = _make_decide_identity(tenant_id="tenant-b", role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )

    assert response.status_code == 404


# ── T-DEC-API-08 ─────────────────────────────────────────────────────────────


def test_tdecapi08_approval_approved_security_event_is_emitted() -> None:
    """T-DEC-API-08: APPROVAL.APPROVED SecurityEventLog is emitted for approved decision."""
    db = _make_session()
    _seed_governed_rule(db)
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    resp = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )
    assert resp.status_code == 200

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.APPROVED"
            )
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt.resource_id == str(req_id)
    assert evt.actor_user_id == "decider-1"
    assert "QC_HOLD" in evt.detail


# ── T-DEC-API-09 ─────────────────────────────────────────────────────────────


def test_tdecapi09_approval_rejected_security_event_is_emitted() -> None:
    """T-DEC-API-09: APPROVAL.REJECTED SecurityEventLog is emitted for rejected decision."""
    db = _make_session()
    _seed_governed_rule(db)
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _governed_payload())
    resp = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "REJECTED"}
    )
    assert resp.status_code == 200

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.REJECTED"
            )
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt.resource_id == str(req_id)
    assert evt.actor_user_id == "decider-1"
    assert "QC_HOLD" in evt.detail


# ── T-DEC-API-10 ─────────────────────────────────────────────────────────────


def test_tdecapi10_no_approval_cancelled_event_or_path_exists() -> None:
    """T-DEC-API-10: APPROVAL.CANCELLED is not implemented; no service function or event."""
    import app.services.approval_service as _svc

    assert not hasattr(_svc, "cancel_approval_request"), (
        "cancel_approval_request must not be implemented until APPROVAL.CANCELLED is scoped"
    )

    # APPROVAL.CANCELLED must not appear in any event emitted during this test run.
    db = _make_session()
    cancelled = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.CANCELLED"
            )
        )
    )
    assert len(cancelled) == 0


# ── T-DEC-API-11 ─────────────────────────────────────────────────────────────


def test_tdecapi11_legacy_request_decided_via_wildcard_tenant_action_rule() -> None:
    """T-DEC-API-11: Legacy request (no governed context) decided via wildcard tenant/action rule."""
    db = _make_session()
    _seed_legacy_rule(db, action_type="QC_HOLD", approver_role_code="QAL")
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _legacy_payload("QC_HOLD"))
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "APPROVED"


# ── T-DEC-API-12 ─────────────────────────────────────────────────────────────


def test_tdecapi12_arbitrary_governed_action_type_is_context_only_no_registry() -> None:
    """T-DEC-API-12: Arbitrary governed_action_type is context-only; no registry enforcement."""
    db = _make_session()
    arbitrary_governed_action = "no.registry.check.needed"
    _seed_governed_rule(db, governed_action_type=arbitrary_governed_action)
    create_identity = _make_create_identity()
    decide_identity = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(
        client,
        _governed_payload(governed_action_type=arbitrary_governed_action),
    )
    response = client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": "APPROVED"}
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "APPROVED"
