"""P0-A-15B: ApprovalRule scope-aware matching runtime activation tests.

Tests T-SA-01 through T-SA-12 as required by P0-A-14 §14 and the P0-A-15B
implementation specification.

Test scope:
  - T-SA-01 to T-SA-09: Repository-level matching precedence tests (in-memory SQLite)
  - T-SA-10 to T-SA-12: Service-level backward compat / negative tests

Matching precedence implemented per P0-A-14 §7 (scoring algorithm):
  +8  tenant-specific rule (not wildcard)
  +4  scope_ref match
  +2  governed_resource_type match
  +1  governed_action_type present (governed > legacy)
  Max-score group wins; ties broken by priority ascending.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.approval import (
    ApprovalAuditLog,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRule,
)
from app.models.impersonation import ImpersonationSession
from app.models.security_event import SecurityEventLog
from app.repositories.approval_repository import get_rules_for_action
from app.schemas.approval import ApprovalCreateRequest, ApprovalDecideRequest
from app.services.approval_service import (
    VALID_ACTION_TYPES,
    create_approval_request,
    decide_approval_request,
)


# ---------------------------------------------------------------------------
# Session factories
# ---------------------------------------------------------------------------


def _make_repo_db() -> Session:
    """In-memory SQLite session with just the ApprovalRule table."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    ApprovalRule.__table__.create(bind=engine)
    return sessionmaker(bind=engine, autoflush=False)()


def _make_service_db() -> Session:
    """In-memory SQLite session with all approval + security tables."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    ImpersonationSession.__table__.create(bind=engine)
    ApprovalRule.__table__.create(bind=engine)
    ApprovalRequest.__table__.create(bind=engine)
    ApprovalDecision.__table__.create(bind=engine)
    ApprovalAuditLog.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    return sessionmaker(bind=engine, autoflush=False)()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _add_rule(
    db: Session,
    *,
    action_type: str,
    approver_role_code: str,
    tenant_id: str,
    is_active: bool = True,
    scope_ref: str | None = None,
    governed_resource_type: str | None = None,
    governed_action_type: str | None = None,
    priority: int | None = None,
) -> ApprovalRule:
    rule = ApprovalRule(
        action_type=action_type,
        approver_role_code=approver_role_code,
        tenant_id=tenant_id,
        is_active=is_active,
        scope_ref=scope_ref,
        governed_resource_type=governed_resource_type,
        governed_action_type=governed_action_type,
        priority=priority,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


# ---------------------------------------------------------------------------
# T-SA-01: Legacy tenant + action_type rule still matches without scope context
# ---------------------------------------------------------------------------


def test_tsa01_legacy_tenant_action_type_rule_matches_without_scope_context() -> None:
    """T-SA-01: Existing tenant + action_type rule still matches without scope context."""
    db = _make_repo_db()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="tenant-a")

    rules = get_rules_for_action(db, "QC_HOLD", "tenant-a")

    assert len(rules) == 1
    assert rules[0].approver_role_code == "QAL"


# ---------------------------------------------------------------------------
# T-SA-02: Wildcard * fallback still matches when no specific rule exists
# ---------------------------------------------------------------------------


def test_tsa02_wildcard_fallback_matches_when_no_tenant_specific_rule() -> None:
    """T-SA-02: Existing wildcard * fallback still matches when no tenant-specific rule exists."""
    db = _make_repo_db()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")

    rules = get_rules_for_action(db, "QC_HOLD", "tenant-a")

    assert len(rules) == 1
    assert rules[0].approver_role_code == "QAL"
    assert rules[0].tenant_id == "*"


# ---------------------------------------------------------------------------
# T-SA-03: Scope-specific rule beats tenant + action_type rule when scope_ref provided
# ---------------------------------------------------------------------------


def test_tsa03_scope_specific_rule_beats_legacy_when_scope_ref_provided() -> None:
    """T-SA-03: Scope-specific rule beats tenant + action_type rule when scope_ref is provided."""
    db = _make_repo_db()
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="LEGACY_ROLE",
        tenant_id="tenant-a",
    )
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="SCOPE_ROLE",
        tenant_id="tenant-a",
        scope_ref="plant/01",
    )

    rules = get_rules_for_action(db, "QC_HOLD", "tenant-a", scope_ref="plant/01")
    role_codes = {r.approver_role_code for r in rules}

    assert "SCOPE_ROLE" in role_codes
    assert "LEGACY_ROLE" not in role_codes


# ---------------------------------------------------------------------------
# T-SA-04: Most specific rule (scope + grt + gat) beats all less specific rules
# ---------------------------------------------------------------------------


def test_tsa04_most_specific_rule_wins_over_less_specific() -> None:
    """T-SA-04: Exact governed resource + governed action + scope rule beats less specific rules."""
    db = _make_repo_db()
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="LEGACY_ROLE",
        tenant_id="tenant-a",
    )
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="SCOPE_ROLE",
        tenant_id="tenant-a",
        scope_ref="plant/01",
    )
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="FULL_SPECIFIC_ROLE",
        tenant_id="tenant-a",
        scope_ref="plant/01",
        governed_resource_type="WORK_ORDER",
        governed_action_type="quality.work_order.qc_hold",
    )

    rules = get_rules_for_action(
        db,
        "QC_HOLD",
        "tenant-a",
        scope_ref="plant/01",
        governed_resource_type="WORK_ORDER",
        governed_action_type="quality.work_order.qc_hold",
    )
    role_codes = {r.approver_role_code for r in rules}

    assert "FULL_SPECIFIC_ROLE" in role_codes
    assert "SCOPE_ROLE" not in role_codes
    assert "LEGACY_ROLE" not in role_codes


# ---------------------------------------------------------------------------
# T-SA-05: Governed resource/action rule beats legacy when no scope-specific rule exists
# ---------------------------------------------------------------------------


def test_tsa05_governed_resource_action_rule_beats_legacy_without_scope() -> None:
    """T-SA-05: Tenant + governed resource/action rule beats tenant + action rule when no scope-specific rule."""
    db = _make_repo_db()
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="LEGACY_ROLE",
        tenant_id="tenant-a",
    )
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="GOVERNED_ROLE",
        tenant_id="tenant-a",
        governed_resource_type="WORK_ORDER",
        governed_action_type="quality.work_order.qc_hold",
    )

    rules = get_rules_for_action(
        db,
        "QC_HOLD",
        "tenant-a",
        governed_resource_type="WORK_ORDER",
        governed_action_type="quality.work_order.qc_hold",
    )
    role_codes = {r.approver_role_code for r in rules}

    assert "GOVERNED_ROLE" in role_codes
    assert "LEGACY_ROLE" not in role_codes


# ---------------------------------------------------------------------------
# T-SA-06: Wrong scope excludes scope-specific rule and falls back to legacy
# ---------------------------------------------------------------------------


def test_tsa06_wrong_scope_excludes_scope_rule_falls_back_to_legacy() -> None:
    """T-SA-06: Wrong scope does not match scope-specific rule; falls back to tenant/action rule."""
    db = _make_repo_db()
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="LEGACY_ROLE",
        tenant_id="tenant-a",
    )
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="SCOPE_ROLE",
        tenant_id="tenant-a",
        scope_ref="plant/01",
    )

    # Request scope is plant/02 — does NOT match the scope rule for plant/01
    rules = get_rules_for_action(db, "QC_HOLD", "tenant-a", scope_ref="plant/02")
    role_codes = {r.approver_role_code for r in rules}

    assert "LEGACY_ROLE" in role_codes
    assert "SCOPE_ROLE" not in role_codes


# ---------------------------------------------------------------------------
# T-SA-07: Wrong governed resource type excludes governed rule and falls back
# ---------------------------------------------------------------------------


def test_tsa07_wrong_governed_resource_excludes_governed_rule_falls_back() -> None:
    """T-SA-07: Wrong governed resource type does not match governed-specific rule; falls back safely."""
    db = _make_repo_db()
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="LEGACY_ROLE",
        tenant_id="tenant-a",
    )
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="GOVERNED_ROLE",
        tenant_id="tenant-a",
        governed_resource_type="WORK_ORDER",
        governed_action_type="quality.work_order.qc_hold",
    )

    # Request has BATCH_LOT — does NOT match the WORK_ORDER rule
    rules = get_rules_for_action(
        db,
        "QC_HOLD",
        "tenant-a",
        governed_resource_type="BATCH_LOT",
        governed_action_type="quality.work_order.qc_hold",
    )
    role_codes = {r.approver_role_code for r in rules}

    assert "LEGACY_ROLE" in role_codes
    assert "GOVERNED_ROLE" not in role_codes


# ---------------------------------------------------------------------------
# T-SA-08: Matching is tenant-isolated
# ---------------------------------------------------------------------------


def test_tsa08_matching_is_tenant_isolated() -> None:
    """T-SA-08: Rules from tenant-b are not returned when querying tenant-a."""
    db = _make_repo_db()
    _add_rule(
        db, action_type="QC_HOLD", approver_role_code="ROLE_A", tenant_id="tenant-a"
    )
    _add_rule(
        db, action_type="QC_HOLD", approver_role_code="ROLE_B", tenant_id="tenant-b"
    )

    rules_a = get_rules_for_action(db, "QC_HOLD", "tenant-a")
    rules_b = get_rules_for_action(db, "QC_HOLD", "tenant-b")

    assert {r.approver_role_code for r in rules_a} == {"ROLE_A"}
    assert {r.approver_role_code for r in rules_b} == {"ROLE_B"}


# ---------------------------------------------------------------------------
# T-SA-09: Priority tie-breaking is deterministic
# ---------------------------------------------------------------------------


def test_tsa09_priority_tie_breaking_is_deterministic() -> None:
    """T-SA-09: When multiple rules share the same specificity score, priority ASC orders them."""
    db = _make_repo_db()
    # Two legacy rules at same score (tenant-specific, no scope/governed fields)
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="LOW_PRIO_ROLE",
        tenant_id="tenant-a",
        priority=2,
    )
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="HIGH_PRIO_ROLE",
        tenant_id="tenant-a",
        priority=1,
    )

    rules = get_rules_for_action(db, "QC_HOLD", "tenant-a")

    assert len(rules) == 2
    # priority=1 (higher priority) must be first
    assert rules[0].approver_role_code == "HIGH_PRIO_ROLE"
    assert rules[1].approver_role_code == "LOW_PRIO_ROLE"


# ---------------------------------------------------------------------------
# T-SA-10: Existing approval request/decision behavior remains compatible with legacy rules
# ---------------------------------------------------------------------------


def test_tsa10_legacy_approval_request_decision_behavior_remains_compatible() -> None:
    """T-SA-10: Full create+decide cycle with legacy rules continues to work after P0-A-15B."""
    db = _make_service_db()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="tenant-a")

    request = create_approval_request(
        db,
        requester_id="user-1",
        requester_role_code="OPR",
        tenant_id="tenant-a",
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            subject_type="operation",
            subject_ref="op-001",
            reason="legacy backward compat test",
        ),
    )
    assert request.status == "PENDING"
    # governed fields are NULL for this legacy request
    assert request.governed_resource_scope_ref is None
    assert request.governed_resource_type is None
    assert request.governed_action_type is None

    decision = decide_approval_request(
        db,
        request_id=request.id,
        decider_user_id="approver-1",
        decider_role_code="QAL",
        tenant_id="tenant-a",
        decide_data=ApprovalDecideRequest(decision="APPROVED", comment="ok"),
    )
    assert decision.decision == "APPROVED"


# ---------------------------------------------------------------------------
# T-SA-11: No runtime governed action registry enforcement occurs yet
# ---------------------------------------------------------------------------


def test_tsa11_no_governed_action_registry_enforcement() -> None:
    """T-SA-11: A governed_action_type value not in any registry is accepted without error."""
    db = _make_repo_db()
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="SPECIAL_ROLE",
        tenant_id="tenant-a",
        governed_action_type="nonexistent.action.type.not.in.any.registry",
    )

    # No exception should be raised — no registry validation
    rules = get_rules_for_action(
        db,
        "QC_HOLD",
        "tenant-a",
        governed_action_type="nonexistent.action.type.not.in.any.registry",
    )
    assert len(rules) == 1
    assert rules[0].approver_role_code == "SPECIAL_ROLE"


# ---------------------------------------------------------------------------
# T-SA-12: No APPROVAL.CANCELLED path is introduced
# ---------------------------------------------------------------------------


def test_tsa12_no_approval_cancelled_path_introduced() -> None:
    """T-SA-12: VALID_ACTION_TYPES is unchanged; CANCELLED is not a valid decision."""
    # VALID_ACTION_TYPES unchanged
    assert VALID_ACTION_TYPES == frozenset(
        {"QC_HOLD", "QC_RELEASE", "SCRAP", "REWORK", "WO_SPLIT", "WO_MERGE"}
    )
    assert "CANCELLED" not in VALID_ACTION_TYPES

    # Pydantic schema rejects CANCELLED as a decision value
    with pytest.raises(Exception):
        ApprovalDecideRequest(decision="CANCELLED", comment=None)  # type: ignore[arg-type]
