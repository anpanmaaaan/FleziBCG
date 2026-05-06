"""P0-A-17: Approval decision API same-score role group determinism coverage.

API-layer coverage proving that when multiple approval rules have matching
action_type and tenant scope, all their role_codes are included in the
allowed_roles set and each is consistently accepted at the HTTP decision boundary.

P0-A-17B (deferred completion on autocode after P0-A-15A/B merge):
  T-TIE-API-02 (scope-specific tie), T-TIE-API-03 (governed_resource_type tie),
  and T-TIE-API-05 (lower-score wildcard rejected) have been completed in this file.
  Prerequisites confirmed present on autocode: ApprovalRule.scope_ref /
  governed_resource_type / governed_action_type / priority (P0-A-15A) and the
  _score_rule / get_rules_for_action scoring system (P0-A-15B).

  The full 15-test suite (01a/b, 02a/b, 03a/b, 04, 05, 06–12) covers:
  multi-rule allowed_roles membership, scope-specific tie groups, governed resource
  tie groups, lower-score wildcard rejection, role exclusion, stability across fresh
  requests, tenant isolation, SoD, terminal guard, and SecurityEventLog taxonomy.

Current matching behavior (approval_repository.py as of P0-A-17):
  get_rules_for_action returns ALL active rules where:
    action_type = <action_type>
    tenant_id IN (<tenant_id>, "*")
  get_approver_role_codes returns the UNION of all matching role_codes.
  Multiple rules with different approver_role_codes for the same action_type+tenant
  ALL contribute to allowed_roles (equivalent to "all at same score" in current model).

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
import app.services.approval_service as approval_service_module
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


# ── Rule seeder ──────────────────────────────────────────────────────────────


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
    """Create an ApprovalRule with optional scope applicability fields (P0-A-15A)."""
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


# ── Payload helper ───────────────────────────────────────────────────────────


def _legacy_payload(action_type: str = "QC_HOLD") -> dict[str, Any]:
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "same-score determinism test",
    }


def _scope_payload(
    *,
    action_type: str = "QC_HOLD",
    scope_ref: str = "plant:LINE-1",
) -> dict[str, Any]:
    """Payload carrying governed_resource_scope_ref so scope rules are matched."""
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "scope-specific tie test",
        "governed_resource_scope_ref": scope_ref,
    }


def _governed_resource_payload(
    *,
    action_type: str = "QC_HOLD",
    governed_resource_type: str = "WORK_ORDER",
) -> dict[str, Any]:
    """Payload carrying governed_resource_type so governed-resource rules are matched."""
    return {
        "action_type": action_type,
        "subject_type": "work_order",
        "subject_ref": "wo-001",
        "reason": "governed-resource tie test",
        "governed_resource_type": governed_resource_type,
        "governed_resource_id": "wo-001",
    }


def _create_and_get_id(client: TestClient, payload: dict[str, Any]) -> int:
    resp = client.post("/api/v1/approvals", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def _decide(
    client: TestClient, req_id: int, decision: str = "APPROVED"
) -> TestClient:
    return client.post(
        f"/api/v1/approvals/{req_id}/decide", json={"decision": decision}
    )


# ── T-TIE-API-01 ─────────────────────────────────────────────────────────────
# Tests both wildcard rules at the same matching level → both roles accepted.


def test_ttieapi01a_multi_rule_same_scope_qal_accepted() -> None:
    """T-TIE-API-01a: Two wildcard rules with different role_codes — QAL accepted.

    Rules:
      (QC_HOLD, QAL, *)   — wildcard
      (QC_HOLD, PMG, *)   — wildcard
    Both rules match for tenant-a → allowed_roles={QAL, PMG}. QAL decider → 200.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL"),
        _rule(approver_role_code="PMG"),
    )
    create_identity = _make_create_identity()
    decide_qal = _make_decide_identity(role_code="QAL")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_ttieapi01b_multi_rule_same_scope_pmg_accepted() -> None:
    """T-TIE-API-01b: Two wildcard rules with different role_codes — PMG accepted.

    Fresh DB with identical rule setup proves the multi-rule group is symmetric:
    PMG is also authorized.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL"),
        _rule(approver_role_code="PMG"),
    )
    create_identity = _make_create_identity()
    decide_pmg = _make_decide_identity(role_code="PMG")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-TIE-API-02 ─────────────────────────────────────────────────────────────


def test_ttieapi02a_scope_specific_tie_qal_accepted() -> None:
    """T-TIE-API-02a: Two scope-specific rules (same scope_ref) in same-score group — QAL accepted.

    Rules:
      (QC_HOLD, QAL, tenant-a, scope_ref="plant:LINE-1")  → score = 8 + 4 = 12
      (QC_HOLD, PMG, tenant-a, scope_ref="plant:LINE-1")  → score = 8 + 4 = 12
    Both rules are at max_score=12 → allowed_roles={QAL, PMG}.
    Request carries governed_resource_scope_ref="plant:LINE-1" so scope rules match.
    QAL decider → 200.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a", scope_ref="plant:LINE-1"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _scope_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_ttieapi02b_scope_specific_tie_pmg_accepted() -> None:
    """T-TIE-API-02b: Two scope-specific rules (same scope_ref) in same-score group — PMG accepted.

    Identical rule setup to 02a on a fresh DB, proving both roles in the
    scope-specific same-score group are independently authorized.
    PMG decider → 200.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a", scope_ref="plant:LINE-1"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a", scope_ref="plant:LINE-1"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_pmg = _make_decide_identity(role_code="PMG", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(client, _scope_payload(scope_ref="plant:LINE-1"))
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-TIE-API-03 ─────────────────────────────────────────────────────────────


def test_ttieapi03a_governed_resource_tie_qal_accepted() -> None:
    """T-TIE-API-03a: Two governed-resource rules (same governed_resource_type) in same-score group — QAL accepted.

    Rules:
      (QC_HOLD, QAL, tenant-a, governed_resource_type="WORK_ORDER")  → score = 8 + 2 = 10
      (QC_HOLD, PMG, tenant-a, governed_resource_type="WORK_ORDER")  → score = 8 + 2 = 10
    Both rules are at max_score=10 → allowed_roles={QAL, PMG}.
    Request carries governed_resource_type="WORK_ORDER" so governed rules match.
    QAL decider → 200.
    """
    db = _make_session()
    _seed(
        db,
        _rule(
            approver_role_code="QAL",
            tenant_id="tenant-a",
            governed_resource_type="WORK_ORDER",
        ),
        _rule(
            approver_role_code="PMG",
            tenant_id="tenant-a",
            governed_resource_type="WORK_ORDER",
        ),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(
        client, _governed_resource_payload(governed_resource_type="WORK_ORDER")
    )
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


def test_ttieapi03b_governed_resource_tie_pmg_accepted() -> None:
    """T-TIE-API-03b: Two governed-resource rules (same governed_resource_type) in same-score group — PMG accepted.

    Identical rule setup to 03a on a fresh DB, proving both roles in the
    governed-resource same-score group are independently authorized.
    PMG decider → 200.
    """
    db = _make_session()
    _seed(
        db,
        _rule(
            approver_role_code="QAL",
            tenant_id="tenant-a",
            governed_resource_type="WORK_ORDER",
        ),
        _rule(
            approver_role_code="PMG",
            tenant_id="tenant-a",
            governed_resource_type="WORK_ORDER",
        ),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_pmg = _make_decide_identity(role_code="PMG", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(
        client, _governed_resource_payload(governed_resource_type="WORK_ORDER")
    )
    resp = _decide(client, req_id)

    assert resp.status_code == 200
    assert resp.json()["decision"] == "APPROVED"


# ── T-TIE-API-04 ─────────────────────────────────────────────────────────────


def test_ttieapi04_role_not_in_any_rule_is_forbidden() -> None:
    """T-TIE-API-04: A role with no matching rule is rejected (403).

    Rules:
      (QC_HOLD, QAL, tenant-a)
      (QC_HOLD, PMG, tenant-a)
    WRK has no rule at all → not in allowed_roles → PermissionError → 403.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_wrk = _make_decide_identity(role_code="WRK", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_wrk)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-TIE-API-05 ─────────────────────────────────────────────────────────────


def test_ttieapi05_lower_score_wildcard_rejected_when_higher_score_group_exists() -> None:
    """T-TIE-API-05: Lower-score wildcard role is rejected when a higher-score same-score group exists.

    "First non-empty level wins" (P0-A-14 §7 / P0-A-15B):
    When tenant-specific rules exist (score=8), the wildcard rule (score=0) is
    excluded from allowed_roles even though WRK has a valid wildcard rule.

    Rules:
      (QC_HOLD, QAL, tenant-a)  → score = 8  ← max group
      (QC_HOLD, PMG, tenant-a)  → score = 8  ← max group
      (QC_HOLD, WRK, "*")       → score = 0  ← excluded: not in max group
    max_score = 8 → allowed_roles = {QAL, PMG}.
    WRK is NOT in allowed_roles → PermissionError → 403.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
        _rule(approver_role_code="WRK", tenant_id="*"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_wrk = _make_decide_identity(role_code="WRK", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_wrk)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 403


# ── T-TIE-API-06 ─────────────────────────────────────────────────────────────


def test_ttieapi06_repeated_fresh_requests_produce_stable_results() -> None:
    """T-TIE-API-06: Repeated fresh requests with identical multi-rule setup behave consistently.

    Creates three approval requests within the same DB/rule config:
      - Request 1 decided by QAL → 200
      - Request 2 decided by PMG → 200
      - Request 3 decided by QAL again → 200

    Proves that multi-rule allowed_roles membership is stable across repeated
    fresh requests (no stochastic or ordering-dependent exclusion).

    Rules:
      (QC_HOLD, QAL, tenant-a)
      (QC_HOLD, PMG, tenant-a)
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(
        user_id="decider-1", role_code="QAL", tenant_id="tenant-a"
    )
    decide_pmg = _make_decide_identity(
        user_id="decider-2", role_code="PMG", tenant_id="tenant-a"
    )
    client_qal = _build_app(db, create_identity, decide_qal)
    client_pmg = _build_app(db, create_identity, decide_pmg)

    # First fresh request → QAL → 200
    req1_id = _create_and_get_id(client_qal, _legacy_payload())
    resp1 = _decide(client_qal, req1_id)
    assert resp1.status_code == 200
    assert resp1.json()["decision"] == "APPROVED"

    # Second fresh request → PMG → 200
    req2_id = _create_and_get_id(client_pmg, _legacy_payload())
    resp2 = _decide(client_pmg, req2_id)
    assert resp2.status_code == 200
    assert resp2.json()["decision"] == "APPROVED"

    # Third fresh request → QAL again → 200 (stability)
    req3_id = _create_and_get_id(client_qal, _legacy_payload())
    resp3 = _decide(client_qal, req3_id)
    assert resp3.status_code == 200
    assert resp3.json()["decision"] == "APPROVED"


# ── T-TIE-API-07 ─────────────────────────────────────────────────────────────


def test_ttieapi07_multi_rule_group_is_tenant_isolated() -> None:
    """T-TIE-API-07: Multi-rule group is tenant-isolated.

    Request created in tenant-a; decider identity is tenant-b.
    get_request_by_id filters by tenant_id → not found → LookupError → 404.
    Even if matching rules exist for tenant-b, a tenant-b identity cannot
    access tenant-a's approval requests.

    Rules:
      (QC_HOLD, QAL, tenant-a), (QC_HOLD, PMG, tenant-a)  — tenant-a group
      (QC_HOLD, QAL, tenant-b), (QC_HOLD, PMG, tenant-b)  — mirror for isolation proof
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
        _rule(approver_role_code="QAL", tenant_id="tenant-b"),
        _rule(approver_role_code="PMG", tenant_id="tenant-b"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_tenant_b = _make_decide_identity(role_code="QAL", tenant_id="tenant-b")
    client = _build_app(db, create_identity, decide_tenant_b)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id)

    assert resp.status_code == 404


# ── T-TIE-API-08 ─────────────────────────────────────────────────────────────


def test_ttieapi08_terminal_request_cannot_be_decided_twice_in_multi_rule_setup() -> None:
    """T-TIE-API-08: Terminal request cannot be decided twice in a multi-rule setup.

    Rules:
      (QC_HOLD, QAL, tenant-a)
      (QC_HOLD, PMG, tenant-a)
    First APPROVED decision → status=APPROVED (terminal).
    Second decide attempt → ValueError "not pending" → 400.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_qal = _make_decide_identity(role_code="QAL", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_qal)

    req_id = _create_and_get_id(client, _legacy_payload())
    first = _decide(client, req_id, "APPROVED")
    assert first.status_code == 200

    second = _decide(client, req_id, "APPROVED")
    assert second.status_code == 400
    assert "not pending" in second.json()["detail"].lower()


# ── T-TIE-API-09 ─────────────────────────────────────────────────────────────


def test_ttieapi09_requester_cannot_approve_own_request_in_multi_rule_setup() -> None:
    """T-TIE-API-09: SoD — requester cannot APPROVE own request in multi-rule setup.

    Rules:
      (QC_HOLD, QAL, tenant-a)
      (QC_HOLD, PMG, tenant-a)
    Same user creates and tries to approve → ValueError "requester" → 400.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
    same_user_id = "user-shared-9"
    create_identity = _make_create_identity(user_id=same_user_id, tenant_id="tenant-a")
    decide_identity = _make_decide_identity(
        user_id=same_user_id, role_code="QAL", tenant_id="tenant-a"
    )
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id, "APPROVED")

    assert resp.status_code == 400
    assert "requester" in resp.json()["detail"].lower()


# ── T-TIE-API-10 ─────────────────────────────────────────────────────────────


def test_ttieapi10_requester_cannot_reject_own_request_in_multi_rule_setup() -> None:
    """T-TIE-API-10: SoD — requester cannot REJECT own request in multi-rule setup.

    Rules:
      (QC_HOLD, QAL, tenant-a)
      (QC_HOLD, PMG, tenant-a)
    Same user creates and tries to reject → ValueError "requester" → 400.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
    same_user_id = "user-shared-10"
    create_identity = _make_create_identity(user_id=same_user_id, tenant_id="tenant-a")
    decide_identity = _make_decide_identity(
        user_id=same_user_id, role_code="QAL", tenant_id="tenant-a"
    )
    client = _build_app(db, create_identity, decide_identity)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id, "REJECTED")

    assert resp.status_code == 400
    assert "requester" in resp.json()["detail"].lower()


# ── T-TIE-API-11 ─────────────────────────────────────────────────────────────


def test_ttieapi11_security_event_log_taxonomy_unchanged_after_multi_rule_decision() -> None:
    """T-TIE-API-11: SecurityEventLog emits only APPROVAL.APPROVED or APPROVAL.REJECTED
    after a decision in a multi-rule setup. No new event type is introduced.

    After an APPROVED decision:
      - Exactly one decision event in the log.
      - Event type is APPROVAL.APPROVED.
      - No APPROVAL.CANCELLED event is present.
    """
    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
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


# ── T-TIE-API-12 ─────────────────────────────────────────────────────────────


def test_ttieapi12_no_approval_cancelled_event_path_exists() -> None:
    """T-TIE-API-12: No APPROVAL.CANCELLED event path is introduced.

    APPROVAL.CANCELLED remains unimplemented: no service function, no route,
    and no SecurityEventLog entry of that type after a multi-rule decision lifecycle.

    Verifies:
      - approval_service does not expose cancel_approval_request.
      - No APPROVAL.CANCELLED entry in SecurityEventLog after a full decision cycle.
    """
    assert not hasattr(approval_service_module, "cancel_approval_request")

    db = _make_session()
    _seed(
        db,
        _rule(approver_role_code="QAL", tenant_id="tenant-a"),
        _rule(approver_role_code="PMG", tenant_id="tenant-a"),
    )
    create_identity = _make_create_identity(tenant_id="tenant-a")
    decide_pmg = _make_decide_identity(role_code="PMG", tenant_id="tenant-a")
    client = _build_app(db, create_identity, decide_pmg)

    req_id = _create_and_get_id(client, _legacy_payload())
    resp = _decide(client, req_id, "REJECTED")
    assert resp.status_code == 200

    cancelled_events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.CANCELLED"
            )
        )
    )
    assert len(cancelled_events) == 0
