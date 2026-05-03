"""P0-A-12: Approval SecurityEventLog Emission Tests

Verifies that approval request creation and decision emit platform SecurityEventLog
events (APPROVAL.REQUESTED, APPROVAL.APPROVED, APPROVAL.REJECTED) in addition to
the existing ApprovalAuditLog rows.

Contract reference: docs/design/01_foundation/governed-action-approval-applicability-contract.md §10
Taxonomy:
  APPROVAL.REQUESTED — emitted when a request is created
  APPROVAL.APPROVED  — emitted when a request is approved
  APPROVAL.REJECTED  — emitted when a request is rejected
  APPROVAL.CANCELLED — NOT implemented (no service path; schema-only debt)
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
    create_approval_request,
    decide_approval_request,
)


def _make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    ImpersonationSession.__table__.create(bind=engine)
    ApprovalRule.__table__.create(bind=engine)
    ApprovalRequest.__table__.create(bind=engine)
    ApprovalDecision.__table__.create(bind=engine)
    ApprovalAuditLog.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _add_rule(
    db: Session,
    *,
    action_type: str = "QC_HOLD",
    approver_role_code: str = "QAL",
    tenant_id: str = "*",
) -> ApprovalRule:
    rule = ApprovalRule(
        action_type=action_type,
        approver_role_code=approver_role_code,
        tenant_id=tenant_id,
        is_active=True,
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
) -> ApprovalRequest:
    return create_approval_request(
        db,
        requester_id=requester_id,
        requester_role_code=requester_role_code,
        tenant_id=tenant_id,
        request_data=ApprovalCreateRequest(
            action_type=action_type,
            subject_type="work_order",
            subject_ref="wo-001",
            reason="governed decision required",
        ),
    )


def _decide_request(
    db: Session,
    *,
    request_id: int,
    tenant_id: str = "tenant-a",
    decider_user_id: str = "approver-1",
    decider_role_code: str | None = "QAL",
    decision: str = "APPROVED",
    impersonation_session_id: int | None = None,
) -> ApprovalDecision:
    return decide_approval_request(
        db,
        request_id=request_id,
        decider_user_id=decider_user_id,
        decider_role_code=decider_role_code,
        tenant_id=tenant_id,
        decide_data=ApprovalDecideRequest(decision=decision, comment="reviewed"),
        impersonation_session_id=impersonation_session_id,
    )


def test_create_request_emits_approval_requested_security_event() -> None:
    db = _make_session()
    request = _create_request(db, action_type="QC_HOLD", requester_id="requester-1", tenant_id="tenant-a")

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.tenant_id == "tenant-a",
                SecurityEventLog.event_type == "APPROVAL.REQUESTED",
            )
        )
    )

    assert len(events) == 1
    evt = events[0]
    assert evt.event_type == "APPROVAL.REQUESTED"
    assert evt.tenant_id == "tenant-a"
    assert evt.actor_user_id == "requester-1"
    assert evt.resource_type == "APPROVAL_REQUEST"
    assert evt.resource_id == str(request.id)
    assert evt.detail is not None
    assert "QC_HOLD" in evt.detail


def test_decide_approved_emits_approval_approved_security_event() -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_HOLD", requester_id="requester-1")

    _decide_request(
        db,
        request_id=request.id,
        decider_user_id="approver-1",
        decider_role_code="QAL",
        decision="APPROVED",
    )

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.APPROVED",
            )
        )
    )

    assert len(events) == 1
    evt = events[0]
    assert evt.actor_user_id == "approver-1"
    assert evt.resource_type == "APPROVAL_REQUEST"
    assert evt.resource_id == str(request.id)
    assert "QC_HOLD" in evt.detail
    assert "QAL" in evt.detail


def test_decide_rejected_emits_approval_rejected_security_event() -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_HOLD", requester_id="requester-1")

    _decide_request(
        db,
        request_id=request.id,
        decider_user_id="approver-1",
        decider_role_code="QAL",
        decision="REJECTED",
    )

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.REJECTED",
            )
        )
    )

    assert len(events) == 1
    evt = events[0]
    assert evt.actor_user_id == "approver-1"
    assert evt.resource_type == "APPROVAL_REQUEST"
    assert evt.resource_id == str(request.id)


def test_approval_audit_log_is_preserved_alongside_security_event() -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_HOLD")
    _decide_request(db, request_id=request.id, decision="APPROVED")

    audit_rows = list(
        db.scalars(
            select(ApprovalAuditLog)
            .where(ApprovalAuditLog.request_id == request.id)
            .order_by(ApprovalAuditLog.id.asc())
        )
    )
    security_events = list(db.scalars(select(SecurityEventLog)))

    # Approval-local audit rows still present
    assert [row.event_type for row in audit_rows] == ["REQUEST_CREATED", "DECISION_MADE"]
    # Platform security events added
    assert {evt.event_type for evt in security_events} == {"APPROVAL.REQUESTED", "APPROVAL.APPROVED"}


def test_impersonation_context_is_captured_in_approval_decision_event() -> None:
    db = _make_session()
    _add_rule(db, action_type="REWORK", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="REWORK", requester_id="operator-1")

    _decide_request(
        db,
        request_id=request.id,
        decider_user_id="admin-real-user",
        decider_role_code="QAL",
        decision="APPROVED",
        impersonation_session_id=999,
    )

    events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.APPROVED",
            )
        )
    )

    assert len(events) == 1
    evt = events[0]
    assert evt.actor_user_id == "admin-real-user"
    assert "999" in (evt.detail or "")


def test_approval_cancelled_event_is_never_emitted() -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_HOLD")
    _decide_request(db, request_id=request.id, decision="APPROVED")

    cancelled_events = list(
        db.scalars(
            select(SecurityEventLog).where(
                SecurityEventLog.event_type == "APPROVAL.CANCELLED",
            )
        )
    )

    assert len(cancelled_events) == 0
