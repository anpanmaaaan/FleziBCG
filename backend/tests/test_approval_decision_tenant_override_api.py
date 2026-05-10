"""P0-A-16: Approval decision API tenant-specific rule override coverage.

API-layer coverage proving that tenant-specific approval rules override wildcard/global
fallback rules at the HTTP decision boundary, closing the last remaining P0-A-14 §7
specificity dimension.

Scoring reference (P0-A-14 §7 / P0-A-15B):
  +8  tenant-specific rule (tenant_id != "*")
  +4  rule.scope_ref set AND matches request governed_resource_scope_ref
  +2  rule.governed_resource_type set AND matches request governed_resource_type
  +1  rule.governed_action_type set (governed rules more specific than legacy)

Key behaviors under test:
  - Tenant-specific rule (score 8) beats wildcard rule (score 0) for same action_type.
  - Tenant-specific rule for DIFFERENT role than wildcard → wildcard role is forbidden.
  - Other-tenant rules are NOT fetched (query: tenant_id.in_([tenant_id, "*"])).
  - Wildcard fallback still applies when no tenant-specific rule exists.
  - SoD, terminal-state guard, tenant isolation, and SecurityEventLog remain correct.

ApprovalRule UniqueConstraint: (action_type, approver_role_code, tenant_id).
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
    """Create an isolated in-memory SQLite session for a single test."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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
    role_code: str = "OPR",
) -> RequestIdentity:
    return RequestIdentity(
        user_id=user_id,
        username="requester",
        email=None,
        tenant_id=tenant_id,
        role_code=role_code,
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


def _rule(
    *,
    action_type: str = "QC_HOLD",
    approver_role_code: str,
    tenant_id: str = "*",
    governed_action_type: str | None = None,
) -> ApprovalRule:
    return ApprovalRule(
        action_type=action_type,
        approver_role_code=approver_role_code,
        tenant_id=tenant_id,
        governed_action_type=governed_action_type,
        is_active=True,
    )


def _seed(db: Session, *rules: ApprovalRule) -> None:
    for r in rules:
        db.add(r)
    db.commit()


# ── Payload helpers ──────────────────────────────────────────────────────────


def _legacy_payload(action_type: str = "QC_HOLD") -> dict[str, Any]:
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "tenant override test",
    }


def _create_and_get_id(client: TestClient, payload: dict[str, Any]) -> int:
    resp = client.post("/api/v1/approvals", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def _decide(client: TestClient, req_id: int, decision: str = "APPROVED") -> TestClient:
    return client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": decision}
    )


# ── T-TENANT-API-01 ──────────────────────────────────────────────────────────


def test_ttenantapi01_tenant_specific_rule_beats_wildcard() -> None:
    """T-TENANT-API-01: Tenant-specific rule (score 8) beats wildcard (score 0).

    Rules:
      (QC_HOLD, QAL, tenant-a)   score=8  — tenant-specific
      (QC_HOLD, PMG, *)          score=0  — wildcard
    Request from tenant-a → max score=8 → allowed_roles={QAL}.
    QAL decider → 200.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG"),  # wildcard
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-TENANT-API-02 ──────────────────────────────────────────────────────────


def test_ttenantapi02_tenant_specific_beats_multiple_wildcard_rules() -> None:
    """T-TENANT-API-02: Tenant-specific rule wins even when multiple wildcard rules exist.

    Rules:
      (QC_HOLD, QAL, tenant-a)   score=8
      (QC_HOLD, PMG, *)          score=0
      (QC_HOLD, WRK, *)          score=0  — second wildcard candidate
    max score=8 → allowed_roles={QAL}; PMG and WRK are in the lower-score group.
    QAL can decide; PMG cannot.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG"),
        _rule(approver_role_code="WRK"),  # second wildcard
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_ttenantapi02b_wildcard_role_forbidden_when_tenant_specific_rule_wins() -> None:
    """T-TENANT-API-02 (negative): PMG (wildcard role) is 403 when tenant-specific QAL rule wins."""
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG"),
        _rule(approver_role_code="WRK"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_pmg = _make_decide_identity(role_code="PMG", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-TENANT-API-03 ──────────────────────────────────────────────────────────


def test_ttenantapi03_other_tenant_rule_does_not_match_current_tenant() -> None:
    """T-TENANT-API-03: Other-tenant rule is not fetched for current tenant request.

    Rules:
      (QC_HOLD, QAL, tenant-b)  — tenant-b specific; NOT fetched for tenant-a requests
    No rules exist for tenant-a or wildcard.
    → get_approver_role_codes returns empty set → ValueError("No approval rules defined") → 400.
    """
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", tenant_id="tenant-b"))
    # No wildcard, no tenant-a rule.
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    # 400 because no rules found for tenant-a → empty allowed_roles → ValueError
    assert resp.status_code == 400
    assert "no approval rules" in resp.json()["detail"].lower()


# ── T-TENANT-API-04 ──────────────────────────────────────────────────────────


def test_ttenantapi04_wildcard_role_rejected_when_tenant_specific_rule_exists() -> None:
    """T-TENANT-API-04: Wildcard role (PMG) is forbidden when tenant-specific QAL rule wins.

    max score=8 → allowed_roles={QAL}; PMG (score 0) is in lower group → excluded.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_pmg = _make_decide_identity(role_code="PMG", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 403
    assert "not authorized" in resp.json()["detail"].lower()


# ── T-TENANT-API-05 ──────────────────────────────────────────────────────────


def test_ttenantapi05_wildcard_fallback_when_no_tenant_specific_rule() -> None:
    """T-TENANT-API-05: Wildcard fallback still decides request when no tenant-specific rule exists.

    Rules:
      (QC_HOLD, QAL, *)  — wildcard only
    No tenant-a specific rule → max score=0 → allowed_roles={QAL} → 200.
    """
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL"))  # wildcard only
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-TENANT-API-06 ──────────────────────────────────────────────────────────


def test_ttenantapi06_cross_tenant_decision_returns_404() -> None:
    """T-TENANT-API-06: Tenant isolation — cross-tenant decider gets 404 (request not found).

    Request created by tenant-a; decider identity is tenant-b.
    get_request_by_id filters by tenant_id → not found → LookupError → 404.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="QAL", tenant_id="tenant-b"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_tenant_b = _make_decide_identity(role_code="QAL", tenant_id="tenant-b")
    client = _build_app(db, create_identity, decide_tenant_b)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 404


# ── T-TENANT-API-07 ──────────────────────────────────────────────────────────


def test_ttenantapi07_requester_cannot_approve_own_request_under_tenant_specific_rule() -> (
    None
):
    """T-TENANT-API-07: SoD — requester cannot APPROVE own request even under tenant-specific rule."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", tenant_id="tenant-a"))
    same_user_id = "user-shared-7"
    create_identity = _make_create_identity(user_id=same_user_id, tenant_id="tenant-a")
    decide_identity = _make_decide_identity(
        user_id=same_user_id, role_code="QAL", tenant_id="tenant-a"
    )
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id, "APPROVED")

    assert resp.status_code == 400
    assert "requester" in resp.json()["detail"].lower()


# ── T-TENANT-API-08 ──────────────────────────────────────────────────────────


def test_ttenantapi08_requester_cannot_reject_own_request_under_tenant_specific_rule() -> (
    None
):
    """T-TENANT-API-08: SoD — requester cannot REJECT own request even under tenant-specific rule."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", tenant_id="tenant-a"))
    same_user_id = "user-shared-8"
    create_identity = _make_create_identity(user_id=same_user_id, tenant_id="tenant-a")
    decide_identity = _make_decide_identity(
        user_id=same_user_id, role_code="QAL", tenant_id="tenant-a"
    )
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id, "REJECTED")

    assert resp.status_code == 400
    assert "requester" in resp.json()["detail"].lower()


# ── T-TENANT-API-09 ──────────────────────────────────────────────────────────


def test_ttenantapi09_terminal_request_cannot_be_decided_twice() -> None:
    """T-TENANT-API-09: Terminal request cannot be decided twice under tenant-specific rule."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", tenant_id="tenant-a"))
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    first = _decide(client, req_id, "APPROVED")
    assert first.status_code == 200

    second = _decide(client, req_id, "APPROVED")
    assert second.status_code == 400
    assert "not pending" in second.json()["detail"].lower()


# ── T-TENANT-API-10 ──────────────────────────────────────────────────────────


def test_ttenantapi10_security_event_approved_only() -> None:
    """T-TENANT-API-10a: After APPROVED decision under tenant-specific rule, exactly APPROVAL.APPROVED emitted."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", tenant_id="tenant-a"))
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id, "APPROVED")
    assert resp.status_code == 200

    decision_events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type.in_(
                    ["APPROVAL.APPROVED", "APPROVAL.REJECTED", "APPROVAL.CANCELLED"]
                )
            )
        )
    )
    assert len(decision_events) == 1
    assert decision_events[0].event_type == "APPROVAL.APPROVED"


def test_ttenantapi10b_security_event_rejected_only() -> None:
    """T-TENANT-API-10b: After REJECTED decision under tenant-specific rule, exactly APPROVAL.REJECTED emitted."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", tenant_id="tenant-a"))
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id, "REJECTED")
    assert resp.status_code == 200

    decision_events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type.in_(
                    ["APPROVAL.APPROVED", "APPROVAL.REJECTED", "APPROVAL.CANCELLED"]
                )
            )
        )
    )
    assert len(decision_events) == 1
    assert decision_events[0].event_type == "APPROVAL.REJECTED"


# ── T-TENANT-API-11 ──────────────────────────────────────────────────────────


def test_ttenantapi11_no_approval_cancelled_event_or_path() -> None:
    """T-TENANT-API-11: APPROVAL.CANCELLED is not implemented; no service function or event."""
    import app.services.approval_service as _svc

    assert not hasattr(_svc, "cancel_approval_request"), (
        "cancel_approval_request must not be implemented until APPROVAL.CANCELLED is scoped"
    )

    db = _make_session()
    cancelled = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.CANCELLED"
            )
        )
    )
    assert len(cancelled) == 0


# ── T-TENANT-API-12 ──────────────────────────────────────────────────────────


def test_ttenantapi12_no_governed_action_registry_enforcement() -> None:
    """T-TENANT-API-12: Arbitrary governed_action_type is context-only; no registry enforcement.

    Tenant-specific governed rule with arbitrary string still decides correctly.
    """
    db = _make_session()
    arbitrary = "no.registry.for.tenant.specific"
    _seed(
        db,
        _rule(
            approver_role_code="QAL",
            tenant_id="tenant-a",
            governed_action_type=arbitrary,
        ),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    payload = {
        "action_type": "QC_HOLD",
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "registry enforcement test",
        "governed_action_type": arbitrary,
    }
    req_id = _create_and_get_id(client, payload)
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"
