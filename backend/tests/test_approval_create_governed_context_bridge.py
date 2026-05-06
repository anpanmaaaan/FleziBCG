"""P0-A-15C: ApprovalCreateRequest Governed Context Bridge Tests.

Tests T-CB-01 through T-CB-10 as required by P0-A-15C spec.

Verifies that:
- ApprovalCreateRequest optionally accepts all 6 governed context fields
- create_approval_request persists those fields to ApprovalRequest
- APPROVAL.REQUESTED SecurityEventLog detail includes governed context if provided
- Decision-time scope-aware matching works end-to-end when governed context is persisted
- Backward compatibility: legacy create requests without governed context remain valid
- VALID_ACTION_TYPES and subject_type/subject_ref remain unchanged

Design references:
  docs/design/01_foundation/governed-action-approval-applicability-contract.md
  docs/design/01_foundation/approval-rule-scope-applicability-contract.md
  docs/audit/p0-a-15b-01-approval-rule-scope-aware-matching-closeout-report.md
"""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.approval import (
    ApprovalAuditLog,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRule,
)
from app.models.impersonation import ImpersonationSession
from app.models.security_event import SecurityEventLog
from app.schemas.approval import ApprovalCreateRequest, ApprovalDecideRequest
from app.services.approval_service import (
    VALID_ACTION_TYPES,
    create_approval_request,
    decide_approval_request,
)


# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------


def _make_db() -> Session:
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
    action_type: str = "QC_HOLD",
    approver_role_code: str = "QAL",
    tenant_id: str = "*",
    scope_ref: str | None = None,
    governed_resource_type: str | None = None,
    governed_action_type: str | None = None,
) -> ApprovalRule:
    rule = ApprovalRule(
        action_type=action_type,
        approver_role_code=approver_role_code,
        tenant_id=tenant_id,
        is_active=True,
        scope_ref=scope_ref,
        governed_resource_type=governed_resource_type,
        governed_action_type=governed_action_type,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def _create_request(
    db: Session,
    *,
    action_type: str = "QC_HOLD",
    requester_id: str = "requester-1",
    requester_role_code: str | None = "OPR",
    tenant_id: str = "tenant-a",
    subject_type: str | None = "work_order",
    subject_ref: str | None = "wo-001",
    governed_resource_type: str | None = None,
    governed_resource_id: str | None = None,
    governed_resource_display_ref: str | None = None,
    governed_resource_tenant_id: str | None = None,
    governed_resource_scope_ref: str | None = None,
    governed_action_type: str | None = None,
) -> ApprovalRequest:
    return create_approval_request(
        db,
        requester_id=requester_id,
        requester_role_code=requester_role_code,
        tenant_id=tenant_id,
        request_data=ApprovalCreateRequest(
            action_type=action_type,
            subject_type=subject_type,
            subject_ref=subject_ref,
            reason="test reason",
            governed_resource_type=governed_resource_type,
            governed_resource_id=governed_resource_id,
            governed_resource_display_ref=governed_resource_display_ref,
            governed_resource_tenant_id=governed_resource_tenant_id,
            governed_resource_scope_ref=governed_resource_scope_ref,
            governed_action_type=governed_action_type,
        ),
    )


# ---------------------------------------------------------------------------
# T-CB-01: Legacy create (no governed fields) still works
# ---------------------------------------------------------------------------


def test_legacy_create_without_governed_context_succeeds() -> None:
    """T-CB-01: Legacy ApprovalCreateRequest without governed fields still creates request."""
    db = _make_db()
    req = create_approval_request(
        db,
        requester_id="u1",
        requester_role_code="OPR",
        tenant_id="tenant-a",
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            reason="legacy reason",
        ),
    )

    assert req.id is not None
    assert req.status == "PENDING"
    assert req.action_type == "QC_HOLD"
    # All governed fields default to None
    assert req.governed_resource_type is None
    assert req.governed_resource_id is None
    assert req.governed_resource_display_ref is None
    assert req.governed_resource_tenant_id is None
    assert req.governed_resource_scope_ref is None
    assert req.governed_action_type is None


# ---------------------------------------------------------------------------
# T-CB-02: Create with governed context persists all 6 fields
# ---------------------------------------------------------------------------


def test_create_with_governed_context_persists_all_fields() -> None:
    """T-CB-02: Create request with governed context persists all optional governed fields."""
    db = _make_db()
    req = _create_request(
        db,
        governed_resource_type="OPERATION",
        governed_resource_id="op-456",
        governed_resource_display_ref="OP-456",
        governed_resource_tenant_id="tenant-a",
        governed_resource_scope_ref="plant:LINE-1",
        governed_action_type="QC_HOLD",
    )

    assert req.governed_resource_type == "OPERATION"
    assert req.governed_resource_id == "op-456"
    assert req.governed_resource_display_ref == "OP-456"
    assert req.governed_resource_tenant_id == "tenant-a"
    assert req.governed_resource_scope_ref == "plant:LINE-1"
    assert req.governed_action_type == "QC_HOLD"


# ---------------------------------------------------------------------------
# T-CB-03: Response schema exposes governed context fields after create
# ---------------------------------------------------------------------------


def test_response_schema_exposes_governed_context_fields() -> None:
    """T-CB-03: ApprovalRequestResponse exposes governed context fields after create."""
    from app.schemas.approval import ApprovalRequestResponse

    db = _make_db()
    req = _create_request(
        db,
        governed_resource_type="OPERATION",
        governed_resource_id="op-789",
        governed_resource_display_ref="OP-789",
        governed_resource_tenant_id="tenant-a",
        governed_resource_scope_ref="plant:LINE-2",
        governed_action_type="QC_HOLD",
    )

    response = ApprovalRequestResponse.model_validate(req)
    assert response.governed_resource_type == "OPERATION"
    assert response.governed_resource_id == "op-789"
    assert response.governed_resource_display_ref == "OP-789"
    assert response.governed_resource_tenant_id == "tenant-a"
    assert response.governed_resource_scope_ref == "plant:LINE-2"
    assert response.governed_action_type == "QC_HOLD"


# ---------------------------------------------------------------------------
# T-CB-04: APPROVAL.REQUESTED SecurityEventLog includes governed context if provided
# ---------------------------------------------------------------------------


def test_approval_requested_event_includes_governed_context_when_provided() -> None:
    """T-CB-04: APPROVAL.REQUESTED SecurityEventLog detail includes governed context if provided."""
    db = _make_db()
    _create_request(
        db,
        tenant_id="tenant-a",
        governed_resource_type="OPERATION",
        governed_resource_scope_ref="plant:LINE-1",
        governed_action_type="QC_HOLD",
    )

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.REQUESTED",
            )
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt.detail is not None
    assert "governed_resource_type=OPERATION" in evt.detail
    assert "governed_resource_scope_ref=plant:LINE-1" in evt.detail
    assert "governed_action_type=QC_HOLD" in evt.detail


def test_approval_requested_event_without_governed_context_is_clean() -> None:
    """T-CB-04 (negative): APPROVAL.REQUESTED detail does NOT include governed keys when not provided."""
    db = _make_db()
    _create_request(db)  # no governed context

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.REQUESTED",
            )
        )
    )
    assert len(events) == 1
    evt = events[0]
    assert evt.detail is not None
    assert "governed_resource_type" not in evt.detail
    assert "governed_resource_scope_ref" not in evt.detail
    assert "governed_action_type" not in evt.detail


# ---------------------------------------------------------------------------
# T-CB-05: Decision-time matching uses persisted governed context end-to-end
# ---------------------------------------------------------------------------


def test_end_to_end_scope_aware_matching_with_persisted_governed_context() -> None:
    """T-CB-05: Scope-aware rule matched end-to-end when governed context is persisted."""
    db = _make_db()

    # Scope-specific rule: only LINE-1 scope, only SPECIALIST role
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="SPECIALIST",
        tenant_id="*",
        scope_ref="plant:LINE-1",
        governed_resource_type="OPERATION",
    )
    # Generic fallback rule: any scope, QAL role
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")

    req = _create_request(
        db,
        action_type="QC_HOLD",
        requester_id="requester-1",
        governed_resource_type="OPERATION",
        governed_resource_scope_ref="plant:LINE-1",
    )

    # SPECIALIST can decide (scope-specific rule wins)
    decision = decide_approval_request(
        db,
        request_id=req.id,
        decider_user_id="approver-specialist",
        decider_role_code="SPECIALIST",
        tenant_id="tenant-a",
        decide_data=ApprovalDecideRequest(decision="APPROVED", comment="ok"),
    )
    assert decision.decision == "APPROVED"


def test_end_to_end_scope_aware_matching_rejects_wrong_role() -> None:
    """T-CB-05 (negative): Wrong role rejected when scope-specific rule is active."""
    db = _make_db()

    # Only scope-specific rule exists — no generic fallback
    _add_rule(
        db,
        action_type="QC_HOLD",
        approver_role_code="SPECIALIST",
        tenant_id="*",
        scope_ref="plant:LINE-1",
        governed_resource_type="OPERATION",
    )

    req = _create_request(
        db,
        action_type="QC_HOLD",
        requester_id="requester-1",
        governed_resource_type="OPERATION",
        governed_resource_scope_ref="plant:LINE-1",
    )

    with pytest.raises(PermissionError):
        decide_approval_request(
            db,
            request_id=req.id,
            decider_user_id="approver-qal",
            decider_role_code="QAL",
            tenant_id="tenant-a",
            decide_data=ApprovalDecideRequest(decision="APPROVED", comment="ok"),
        )


# ---------------------------------------------------------------------------
# T-CB-06: subject_type / subject_ref remain unchanged and still present
# ---------------------------------------------------------------------------


def test_subject_type_and_subject_ref_remain_present_and_correct() -> None:
    """T-CB-06: subject_type and subject_ref are unchanged and still persisted correctly."""
    db = _make_db()
    req = _create_request(
        db,
        subject_type="work_order",
        subject_ref="wo-999",
        governed_resource_type="OPERATION",
    )

    assert req.subject_type == "work_order"
    assert req.subject_ref == "wo-999"


# ---------------------------------------------------------------------------
# T-CB-07: No governed action registry enforcement; arbitrary governed_action_type accepted
# ---------------------------------------------------------------------------


def test_arbitrary_governed_action_type_is_accepted_without_registry_enforcement() -> (
    None
):
    """T-CB-07: governed_action_type is stored as nullable context; no registry validation."""
    db = _make_db()
    req = _create_request(
        db,
        governed_action_type="SOME_FUTURE_GOVERNED_ACTION_NOT_IN_ANY_REGISTRY",
    )

    assert req.governed_action_type == "SOME_FUTURE_GOVERNED_ACTION_NOT_IN_ANY_REGISTRY"
    assert req.id is not None


# ---------------------------------------------------------------------------
# T-CB-08: VALID_ACTION_TYPES unchanged; legacy action_type validation authoritative
# ---------------------------------------------------------------------------


def test_valid_action_types_unchanged() -> None:
    """T-CB-08: VALID_ACTION_TYPES set is unchanged by P0-A-15C."""
    assert VALID_ACTION_TYPES == frozenset(
        {"QC_HOLD", "QC_RELEASE", "SCRAP", "REWORK", "WO_SPLIT", "WO_MERGE"}
    )


def test_unknown_action_type_raises_value_error() -> None:
    """T-CB-08: Unknown action_type still raises ValueError regardless of governed context."""
    db = _make_db()
    with pytest.raises(ValueError, match="Unknown action_type"):
        create_approval_request(
            db,
            requester_id="u1",
            requester_role_code="OPR",
            tenant_id="tenant-a",
            request_data=ApprovalCreateRequest(
                action_type="MASTER_DATA",
                reason="should fail",
                governed_resource_type="OPERATION",
            ),
        )


# ---------------------------------------------------------------------------
# T-CB-09: No APPROVAL.CANCELLED path introduced
# ---------------------------------------------------------------------------


def test_no_cancel_approval_request_function_exists() -> None:
    """T-CB-09: cancel_approval_request is NOT implemented in approval_service."""
    import app.services.approval_service as svc

    assert not hasattr(svc, "cancel_approval_request"), (
        "cancel_approval_request must not be added in P0-A-15C. "
        "APPROVAL.CANCELLED is schema-only debt."
    )


# ---------------------------------------------------------------------------
# T-CB-10: Existing approval current behavior suite remains green (cross-file reference)
# ---------------------------------------------------------------------------


def test_existing_approval_service_create_behavior_is_unaffected() -> None:
    """T-CB-10: Service correctly handles a complete lifecycle with no governed context regression."""
    db = _make_db()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")

    # Create legacy-style request (no governed context)
    req = create_approval_request(
        db,
        requester_id="requester-legacy",
        requester_role_code="OPR",
        tenant_id="tenant-legacy",
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            subject_type="work_order",
            subject_ref="wo-legacy",
            reason="legacy test",
        ),
    )

    assert req.status == "PENDING"
    assert req.action_type == "QC_HOLD"
    assert req.governed_resource_type is None

    # Decide
    decision = decide_approval_request(
        db,
        request_id=req.id,
        decider_user_id="approver-qal",
        decider_role_code="QAL",
        tenant_id="tenant-legacy",
        decide_data=ApprovalDecideRequest(decision="APPROVED", comment="all good"),
    )
    assert decision.decision == "APPROVED"
