from typing import get_args

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.services.approval_service as approval_service
from app.models.approval import (
    ApprovalAuditLog,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRule,
)
from app.models.impersonation import ImpersonationSession
from app.models.security_event import SecurityEventLog
from app.schemas.approval import (
    ApprovalCreateRequest,
    ApprovalDecideRequest,
    ApprovalStatus,
)
from app.services.approval_service import (
    VALID_ACTION_TYPES,
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
    action_type: str,
    approver_role_code: str,
    tenant_id: str,
    is_active: bool = True,
) -> ApprovalRule:
    rule = ApprovalRule(
        action_type=action_type,
        approver_role_code=approver_role_code,
        tenant_id=tenant_id,
        is_active=is_active,
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
    reason: str = "Need governed decision",
) -> ApprovalRequest:
    return create_approval_request(
        db,
        requester_id=requester_id,
        requester_role_code=requester_role_code,
        tenant_id=tenant_id,
        request_data=ApprovalCreateRequest(
            action_type=action_type,
            subject_type="operation",
            subject_ref="op-001",
            reason=reason,
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


def test_valid_action_types_exactly_match_current_supported_actions() -> None:
    assert VALID_ACTION_TYPES == frozenset(
        {
            "QC_HOLD",
            "QC_RELEASE",
            "SCRAP",
            "REWORK",
            "WO_SPLIT",
            "WO_MERGE",
        }
    )


def test_invalid_action_type_is_rejected() -> None:
    db = _make_session()

    with pytest.raises(ValueError, match="Unknown action_type"):
        create_approval_request(
            db,
            requester_id="requester-1",
            requester_role_code="OPR",
            tenant_id="tenant-a",
            request_data=ApprovalCreateRequest(
                action_type="master_data_release",
                subject_type="product",
                subject_ref="p-001",
                reason="not supported",
            ),
        )


def test_approval_request_can_be_created_for_supported_action_with_audit_row() -> None:
    db = _make_session()

    request = _create_request(db, action_type="QC_HOLD")
    audit_rows = list(
        db.scalars(
            select(ApprovalAuditLog)
            .where(ApprovalAuditLog.request_id == request.id)
            .order_by(ApprovalAuditLog.id.asc())
        )
    )

    assert request.id > 0
    assert request.action_type == "QC_HOLD"
    assert request.status == "PENDING"
    assert len(audit_rows) == 1
    assert audit_rows[0].event_type == "REQUEST_CREATED"
    assert audit_rows[0].user_id == "requester-1"


@pytest.mark.parametrize("decision", ["APPROVED", "REJECTED"])
def test_pending_approval_can_be_decided_by_valid_approver_role(decision: str) -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_HOLD")

    decision_row = _decide_request(
        db,
        request_id=request.id,
        decider_user_id="approver-1",
        decider_role_code="QAL",
        decision=decision,
    )
    refreshed_request = db.scalar(
        select(ApprovalRequest).where(ApprovalRequest.id == request.id)
    )
    audit_rows = list(
        db.scalars(
            select(ApprovalAuditLog)
            .where(ApprovalAuditLog.request_id == request.id)
            .order_by(ApprovalAuditLog.id.asc())
        )
    )

    assert decision_row.id > 0
    assert decision_row.decision == decision
    assert refreshed_request is not None
    assert refreshed_request.status == decision
    assert [row.event_type for row in audit_rows] == ["REQUEST_CREATED", "DECISION_MADE"]


@pytest.mark.parametrize("decision", ["APPROVED", "REJECTED"])
def test_requester_cannot_decide_own_request(decision: str) -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(
        db,
        action_type="QC_HOLD",
        requester_id="same-user",
        requester_role_code="OPR",
    )

    with pytest.raises(ValueError, match="Requester cannot approve their own request"):
        _decide_request(
            db,
            request_id=request.id,
            decider_user_id="same-user",
            decider_role_code="QAL",
            decision=decision,
        )


@pytest.mark.parametrize("first_decision", ["APPROVED", "REJECTED"])
def test_terminal_approval_cannot_be_decided_twice(first_decision: str) -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_HOLD")
    _decide_request(
        db,
        request_id=request.id,
        decider_user_id="approver-1",
        decider_role_code="QAL",
        decision=first_decision,
    )

    with pytest.raises(ValueError, match="is not pending"):
        _decide_request(
            db,
            request_id=request.id,
            decider_user_id="approver-2",
            decider_role_code="QAL",
            decision="APPROVED",
        )


def test_tenant_specific_rule_is_respected() -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="PMG", tenant_id="tenant-a")
    request = _create_request(db, action_type="QC_HOLD", tenant_id="tenant-a")

    decision_row = _decide_request(
        db,
        request_id=request.id,
        tenant_id="tenant-a",
        decider_user_id="approver-1",
        decider_role_code="PMG",
        decision="APPROVED",
    )

    assert decision_row.decision == "APPROVED"
    assert decision_row.decider_role_code == "PMG"


def test_wildcard_rule_fallback_works_when_no_tenant_specific_rule_exists() -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_RELEASE", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_RELEASE", tenant_id="tenant-b")

    decision_row = _decide_request(
        db,
        request_id=request.id,
        tenant_id="tenant-b",
        decider_user_id="approver-1",
        decider_role_code="QAL",
        decision="APPROVED",
    )

    assert decision_row.decision == "APPROVED"
    assert decision_row.decider_role_code == "QAL"


def test_wrong_approver_role_is_rejected() -> None:
    db = _make_session()
    _add_rule(db, action_type="SCRAP", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="SCRAP")

    with pytest.raises(PermissionError, match="is not authorized to decide"):
        _decide_request(
            db,
            request_id=request.id,
            decider_user_id="approver-1",
            decider_role_code="PMG",
            decision="APPROVED",
        )


def test_missing_rule_for_supported_action_is_rejected() -> None:
    db = _make_session()
    request = _create_request(db, action_type="WO_SPLIT")

    with pytest.raises(ValueError, match="No approval rules defined"):
        _decide_request(
            db,
            request_id=request.id,
            decider_user_id="approver-1",
            decider_role_code="PMG",
            decision="APPROVED",
        )


def test_request_lookup_is_tenant_scoped() -> None:
    db = _make_session()
    _add_rule(db, action_type="QC_HOLD", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="QC_HOLD", tenant_id="tenant-a")

    with pytest.raises(LookupError, match="not found"):
        _decide_request(
            db,
            request_id=request.id,
            tenant_id="tenant-b",
            decider_user_id="approver-1",
            decider_role_code="QAL",
            decision="APPROVED",
        )


def test_decision_records_impersonation_context_when_provided() -> None:
    db = _make_session()
    _add_rule(db, action_type="REWORK", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="REWORK", requester_id="operator-1")

    decision_row = _decide_request(
        db,
        request_id=request.id,
        decider_user_id="admin-real-user",
        decider_role_code="QAL",
        decision="APPROVED",
        impersonation_session_id=123,
    )

    assert decision_row.impersonation_session_id == 123
    assert decision_row.decider_id == "admin-real-user"


def test_impersonation_path_preserves_real_user_sod() -> None:
    db = _make_session()
    _add_rule(db, action_type="REWORK", approver_role_code="QAL", tenant_id="*")
    request = _create_request(db, action_type="REWORK", requester_id="admin-real-user")

    with pytest.raises(ValueError, match="Requester cannot approve their own request"):
        _decide_request(
            db,
            request_id=request.id,
            decider_user_id="admin-real-user",
            decider_role_code="QAL",
            decision="APPROVED",
            impersonation_session_id=456,
        )


def test_cancelled_remains_schema_only_debt() -> None:
    assert "CANCELLED" in get_args(ApprovalStatus)
    with pytest.raises(Exception):
        ApprovalDecideRequest(decision="CANCELLED", comment="not supported")
    assert not hasattr(approval_service, "cancel_approval_request")