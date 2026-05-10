"""P0-A-15F: Approval decision API specificity precedence and wildcard fallback coverage.

API-layer coverage proving that rule specificity precedence from P0-A-14 / P0-A-15B
is honored at the HTTP decision boundary:

- Scope-specific rule (score +4) beats no-scope rule (score 0).
- Scope-specific rule beats tenant wildcard *.
- Governed resource/action specificity beats less-specific rule.
- Wrong scope is incompatible with scope rule → safe fallback to no-scope rule.
- Wrong governed_action_type is incompatible with governed rule → fallback to legacy.
- Wildcard fallback still decides legacy requests.
- Tenant isolation holds even when specificity rules exist in another tenant.
- Priority tie-breaking includes all tied-score roles in allowed_roles set.
- SecurityEventLog taxonomy unchanged (APPROVED / REJECTED only).
- APPROVAL.CANCELLED not introduced.
- Governed action registry not enforced.

Scoring reference (P0-A-14 §7 / P0-A-15B):
  +8  tenant-specific rule (tenant_id != "*")
  +4  rule.scope_ref set AND matches request governed_resource_scope_ref
  +2  rule.governed_resource_type set AND matches request governed_resource_type
  +1  rule.governed_action_type set (governed rules more specific than legacy)

Incompatibility (P0-A-14 §8):
  rule.scope_ref non-null AND does not equal request scope_ref → excluded
  rule.governed_resource_type non-null AND does not equal request governed_resource_type → excluded

ApprovalRule UniqueConstraint: (action_type, approver_role_code, tenant_id).
Different approver_role_codes allow multiple rules for the same action_type + tenant.
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
    scope_ref: str | None = None,
    governed_resource_type: str | None = None,
    governed_action_type: str | None = None,
    priority: int | None = None,
) -> ApprovalRule:
    return ApprovalRule(
        action_type=action_type,
        approver_role_code=approver_role_code,
        tenant_id=tenant_id,
        scope_ref=scope_ref,
        governed_resource_type=governed_resource_type,
        governed_action_type=governed_action_type,
        priority=priority,
        is_active=True,
    )


def _seed(db: Session, *rules: ApprovalRule) -> None:
    for r in rules:
        db.add(r)
    db.commit()


# ── Payload helpers ──────────────────────────────────────────────────────────


def _governed_payload(
    *,
    action_type: str = "QC_HOLD",
    scope_ref: str = "plant:LINE-1",
    governed_resource_type: str = "WORK_ORDER",
    governed_action_type: str = "quality.work_order.qc_hold",
) -> dict[str, Any]:
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "specificity test",
        "governed_resource_type": governed_resource_type,
        "governed_resource_id": "wo-001",
        "governed_resource_display_ref": "WO-001",
        "governed_resource_tenant_id": "tenant-a",
        "governed_resource_scope_ref": scope_ref,
        "governed_action_type": governed_action_type,
    }


def _legacy_payload(action_type: str = "QC_HOLD") -> dict[str, Any]:
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "legacy fallback test",
    }


def _create_and_get_id(client: TestClient, payload: dict[str, Any]) -> int:
    resp = client.post("/api/v1/approvals", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def _decide(client: TestClient, req_id: int, decision: str = "APPROVED") -> TestClient:
    return client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": decision}
    )


# ── T-SPEC-API-01 ─────────────────────────────────────────────────────────────


def test_tspecapi01_scope_specific_rule_beats_no_scope_rule() -> None:
    """T-SPEC-API-01: Scope-specific rule (score+4) beats no-scope rule (score 0).

    Rules:
      (QC_HOLD, QAL, *, scope_ref=plant:LINE-1)  score=4
      (QC_HOLD, PMG, *, scope_ref=None)           score=0
    Request with governed_resource_scope_ref=plant:LINE-1 → max score=4 → only QAL allowed.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="PMG"),  # no scope
    )
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_tspecapi01b_non_scope_role_is_forbidden_when_scope_rule_wins() -> None:
    """T-SPEC-API-01 (negative): Decider with PMG role is 403 when scope-specific QAL rule wins."""
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="PMG"),
    )
    create_identity = _make_create_identity()
    decide_pmg = _make_decide_identity(role_code="PMG")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-SPEC-API-02 ─────────────────────────────────────────────────────────────


def test_tspecapi02_scope_specific_rule_beats_tenant_wildcard() -> None:
    """T-SPEC-API-02: Scope-specific tenant-specific rule (score 8+4=12) beats wildcard (score 0).

    Rules:
      (QC_HOLD, QAL, tenant-a, scope_ref=plant:LINE-1)  score=12
      (QC_HOLD, PMG, *,        scope_ref=None)           score=0
    Request from tenant-a with scope_ref=plant:LINE-1 → max score=12 → QAL allowed only.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="PMG"),  # wildcard, no scope
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-SPEC-API-03 ─────────────────────────────────────────────────────────────


def test_tspecapi03_governed_rule_beats_scope_only_rule() -> None:
    """T-SPEC-API-03: Full governed rule (scope+resource+action, score 4+2+1=7)
    beats scope-only rule (score 4).

    Rules:
      (QC_HOLD, QAL, *, scope_ref=LINE-1, governed_resource_type=WORK_ORDER,
       governed_action_type=quality.qc_hold)  score=7  (governed rule, routed via governed_action_type)
      (QC_HOLD, PMG, *, scope_ref=LINE-1)                                      score=4  (legacy rule)
    Request with governed_action_type=quality.qc_hold, governed_resource_type=WORK_ORDER, scope_ref=LINE-1:
      Both rules are action-compatible; max score=7 → QAL allowed only.
    """
    db = _make_session()
    _seed(
        db,
        _rule(
            approver_role_code="QAL",
            scope_ref="plant:LINE-1",
            governed_resource_type="WORK_ORDER",
            governed_action_type="quality.qc_hold",
        ),
        _rule(approver_role_code="PMG", scope_ref="plant:LINE-1"),  # legacy, score=4
    )
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(
        client,
        _governed_payload(
            scope_ref="plant:LINE-1",
            governed_resource_type="WORK_ORDER",
            governed_action_type="quality.qc_hold",
        ),
    )
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_tspecapi03b_lower_specificity_role_forbidden_when_governed_rule_wins() -> None:
    """T-SPEC-API-03 (negative): PMG (score 4 rule) is 403 when governed QAL rule wins (score 7)."""
    db = _make_session()
    _seed(
        db,
        _rule(
            approver_role_code="QAL",
            scope_ref="plant:LINE-1",
            governed_resource_type="WORK_ORDER",
            governed_action_type="quality.qc_hold",
        ),
        _rule(approver_role_code="PMG", scope_ref="plant:LINE-1"),
    )
    create_identity = _make_create_identity()
    decide_pmg = _make_decide_identity(role_code="PMG")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(
        client,
        _governed_payload(
            scope_ref="plant:LINE-1",
            governed_resource_type="WORK_ORDER",
            governed_action_type="quality.qc_hold",
        ),
    )
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-SPEC-API-04 ─────────────────────────────────────────────────────────────


def test_tspecapi04_tenant_governed_action_rule_beats_tenant_legacy_rule() -> None:
    """T-SPEC-API-04: Tenant-specific governed rule (score 8+1=9) beats tenant-specific
    legacy rule (score 8) when no scope-specific rule exists.

    Rules:
      (QC_HOLD, QAL, tenant-a, governed_action_type=quality.qc_hold)  score=9
      (QC_HOLD, PMG, tenant-a)                                         score=8
    Request: tenant-a, governed_action_type=quality.qc_hold, no scope/resource_type.
    Both action-compatible; max score=9 → QAL allowed only.
    """
    db = _make_session()
    _seed(
        db,
        _rule(
            approver_role_code="QAL",
            tenant_id="tenant-a",
            governed_action_type="quality.qc_hold",
        ),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    # Payload has governed_action_type but no scope_ref or governed_resource_type.
    payload = {
        "action_type": "QC_HOLD",
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "tenant governed rule beats legacy",
        "governed_action_type": "quality.qc_hold",
    }
    req_id = _create_and_get_id(client, payload)
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-SPEC-API-05 ─────────────────────────────────────────────────────────────


def test_tspecapi05_wrong_scope_falls_back_to_no_scope_rule() -> None:
    """T-SPEC-API-05: Request scope_ref=plant:LINE-2 is incompatible with the
    scope_ref=plant:LINE-1 rule; safe fallback to no-scope rule.

    Rules:
      (QC_HOLD, QAL, *, scope_ref=plant:LINE-1)  → incompatible (scope mismatch → excluded)
      (QC_HOLD, PMG, *, scope_ref=None)           → compatible, score=0
    Request scope_ref=plant:LINE-2 → allowed_roles={PMG}.
    """
    db = _make_session()
    _seed(
        db,
        _rule(
            approver_role_code="QAL", scope_ref="plant:LINE-1"
        ),  # specific, will be excluded
        _rule(approver_role_code="PMG"),  # no scope constraint, fallback
    )
    create_identity = _make_create_identity()
    decide_pmg = _make_decide_identity(role_code="PMG")
    client = _build_app(db, create_identity, decide_pmg)

    # Request carries a DIFFERENT scope than the specific rule.
    req_id = _create_and_get_id(
        client,
        _governed_payload(scope_ref="plant:LINE-2"),
    )
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_tspecapi05b_qal_is_forbidden_when_scope_rule_excluded_on_mismatch() -> None:
    """T-SPEC-API-05 (negative): QAL is 403 because its scope rule is excluded by mismatch."""
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="PMG"),
    )
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(
        client,
        _governed_payload(scope_ref="plant:LINE-2"),  # mismatch with QAL rule
    )
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-SPEC-API-06 ─────────────────────────────────────────────────────────────


def test_tspecapi06_wrong_governed_action_type_falls_back_to_legacy_rule() -> None:
    """T-SPEC-API-06: Request's governed_action_type does not match governed rule;
    governed rule is not action-compatible; fallback to legacy action_type rule.

    Rules:
      (QC_HOLD, QAL, *, governed_action_type=quality.qc_hold)  governed rule — not compatible
      (QC_HOLD, PMG, *)                                         legacy rule — compatible, score=0
    Request governed_action_type=some.other.type → allowed_roles={PMG}.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", governed_action_type="quality.qc_hold"),
        _rule(approver_role_code="PMG"),
    )
    create_identity = _make_create_identity()
    decide_pmg = _make_decide_identity(role_code="PMG")
    client = _build_app(db, create_identity, decide_pmg)

    # Request carries a DIFFERENT governed_action_type than QAL's rule.
    payload = {
        "action_type": "QC_HOLD",
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "fallback test",
        "governed_action_type": "some.other.type",
    }
    req_id = _create_and_get_id(client, payload)
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_tspecapi06b_qal_is_forbidden_when_governed_rule_not_compatible() -> None:
    """T-SPEC-API-06 (negative): QAL is 403 because governed rule is not action-compatible."""
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", governed_action_type="quality.qc_hold"),
        _rule(approver_role_code="PMG"),
    )
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    payload = {
        "action_type": "QC_HOLD",
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "negative fallback test",
        "governed_action_type": "some.other.type",
    }
    req_id = _create_and_get_id(client, payload)
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-SPEC-API-07 ─────────────────────────────────────────────────────────────


def test_tspecapi07_wildcard_fallback_decides_legacy_request() -> None:
    """T-SPEC-API-07: Wildcard legacy rule still decides a legacy request (no governed context)."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL"))  # wildcard, no scope, no governed dims
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload("QC_HOLD"))
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-SPEC-API-08 ─────────────────────────────────────────────────────────────


def test_tspecapi08_tenant_isolation_with_specificity_rules_in_other_tenant() -> None:
    """T-SPEC-API-08: Specificity rules for tenant-b do not affect tenant-a decisions.

    Rules:
      (QC_HOLD, MGR, tenant-b, scope_ref=plant:LINE-1)  — tenant-b specific
      (QC_HOLD, QAL, *)                                  — wildcard fallback
    Request from tenant-a:
      Query: tenant_id in [tenant-a, *] → tenant-b rule NOT fetched.
      Only wildcard rule applies → allowed_roles={QAL}.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="MGR", tenant_id="tenant-b", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="QAL"),  # wildcard for all tenants
    )
    # Requester and decider both in tenant-a.
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    # QAL (from wildcard) can decide; MGR (tenant-b specific) not in allowed_roles for tenant-a.
    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_tspecapi08b_mgr_is_forbidden_in_tenant_a_when_its_rule_is_tenant_b_only() -> (
    None
):
    """T-SPEC-API-08 (negative): MGR is 403 for tenant-a because its rule is tenant-b only."""
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="MGR", tenant_id="tenant-b", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="QAL"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_mgr = _make_decide_identity(role_code="MGR", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_mgr)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-SPEC-API-09 ─────────────────────────────────────────────────────────────


def test_tspecapi09a_priority_tie_includes_all_tied_roles_qal() -> None:
    """T-SPEC-API-09a: When two rules tie at max score, both role_codes are in allowed_roles.
    Verify QAL (priority=1) can decide.

    Rules:
      (QC_HOLD, QAL, *, scope_ref=LINE-1, priority=1)  score=4
      (QC_HOLD, MGR, *, scope_ref=LINE-1, priority=2)  score=4
    Both rules tied → allowed_roles={QAL, MGR} → QAL decider → 200.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", scope_ref="plant:LINE-1", priority=1),
        _rule(approver_role_code="MGR", scope_ref="plant:LINE-1", priority=2),
    )
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_tspecapi09b_priority_tie_includes_all_tied_roles_mgr() -> None:
    """T-SPEC-API-09b: When two rules tie at max score, MGR (priority=2) can also decide.

    Uses a separate DB to confirm both tied roles are independently valid.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", scope_ref="plant:LINE-1", priority=1),
        _rule(approver_role_code="MGR", scope_ref="plant:LINE-1", priority=2),
    )
    create_identity = _make_create_identity()
    decide_mgr = _make_decide_identity(role_code="MGR")
    client = _build_app(db, create_identity, decide_mgr)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-SPEC-API-10 ─────────────────────────────────────────────────────────────


def test_tspecapi10_security_event_log_emits_approved_only() -> None:
    """T-SPEC-API-10a: After APPROVED decision, SecurityEventLog contains exactly APPROVAL.APPROVED."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", scope_ref="plant:LINE-1"))
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
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


def test_tspecapi10b_security_event_log_emits_rejected_only() -> None:
    """T-SPEC-API-10b: After REJECTED decision, SecurityEventLog contains exactly APPROVAL.REJECTED."""
    db = _make_session()
    _seed(db, _rule(approver_role_code="QAL", scope_ref="plant:LINE-1"))
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _governed_payload(scope_ref="plant:LINE-1"))
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


# ── T-SPEC-API-11 ─────────────────────────────────────────────────────────────


def test_tspecapi11_no_approval_cancelled_event_or_path_introduced() -> None:
    """T-SPEC-API-11: APPROVAL.CANCELLED is not implemented; no service function or event."""
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


# ── T-SPEC-API-12 ─────────────────────────────────────────────────────────────


def test_tspecapi12_arbitrary_governed_action_type_no_registry_enforcement() -> None:
    """T-SPEC-API-12: Arbitrary governed_action_type is context-only; no registry enforcement.

    A rule with any governed_action_type string, combined with a matching request,
    must decide successfully without any registry validation.
    """
    db = _make_session()
    arbitrary = "completely.arbitrary.unregistered.action"
    _seed(db, _rule(approver_role_code="QAL", governed_action_type=arbitrary))
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
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
