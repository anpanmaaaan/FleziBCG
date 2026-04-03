import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import ApprovalAuditLog, ApprovalDecision, ApprovalRequest, ApprovalRule
from app.repositories.approval_repository import (
    get_approver_role_codes,
    get_pending_requests,
    get_request_by_id,
)
from app.schemas.approval import ApprovalCreateRequest, ApprovalDecideRequest

logger = logging.getLogger(__name__)

VALID_ACTION_TYPES = frozenset({
    "QC_HOLD", "QC_RELEASE", "SCRAP", "REWORK", "WO_SPLIT", "WO_MERGE",
})

# Default rules: (action_type, approver_role_code), tenant_id="*"
_DEFAULT_RULES: list[tuple[str, str]] = [
    ("QC_HOLD", "QAL"),
    ("QC_RELEASE", "QAL"),
    ("SCRAP", "QAL"),
    ("SCRAP", "PMG"),
    ("REWORK", "QAL"),
    ("WO_SPLIT", "PMG"),
    ("WO_MERGE", "PMG"),
]


def seed_approval_rules(db: Session) -> None:
    for action_type, approver_role_code in _DEFAULT_RULES:
        existing = db.scalar(
            select(ApprovalRule).where(
                ApprovalRule.action_type == action_type,
                ApprovalRule.approver_role_code == approver_role_code,
                ApprovalRule.tenant_id == "*",
            )
        )
        if existing:
            continue
        db.add(
            ApprovalRule(
                action_type=action_type,
                approver_role_code=approver_role_code,
                tenant_id="*",
                is_active=True,
            )
        )
    db.commit()
    logger.info("Approval rules seeded.")


def _log_event(
    db: Session,
    request: ApprovalRequest,
    user_id: str,
    role_code: str | None,
    event_type: str,
    detail: str | None = None,
) -> None:
    db.add(
        ApprovalAuditLog(
            request_id=request.id,
            user_id=user_id,
            role_code=role_code,
            tenant_id=request.tenant_id,
            event_type=event_type,
            detail=detail[:512] if detail else None,
        )
    )


def create_approval_request(
    db: Session,
    requester_id: str,
    requester_role_code: str | None,
    tenant_id: str,
    request_data: ApprovalCreateRequest,
) -> ApprovalRequest:
    action_type = request_data.action_type  # already normalized by Pydantic validator

    if action_type not in VALID_ACTION_TYPES:
        raise ValueError(
            f"Unknown action_type {action_type!r}. "
            f"Valid types: {sorted(VALID_ACTION_TYPES)}"
        )

    appr_req = ApprovalRequest(
        tenant_id=tenant_id,
        action_type=action_type,
        requester_id=requester_id,
        requester_role_code=requester_role_code,
        subject_type=request_data.subject_type,
        subject_ref=request_data.subject_ref,
        reason=request_data.reason.strip(),
        status="PENDING",
    )
    db.add(appr_req)
    db.flush()

    _log_event(
        db,
        appr_req,
        user_id=requester_id,
        role_code=requester_role_code,
        event_type="REQUEST_CREATED",
        detail=f"action_type={action_type}",
    )

    db.commit()
    db.refresh(appr_req)

    logger.info(
        "Approval request created: id=%d tenant=%s action=%s requester=%s",
        appr_req.id,
        tenant_id,
        action_type,
        requester_id,
    )
    return appr_req


def decide_approval_request(
    db: Session,
    request_id: int,
    decider_user_id: str,
    decider_role_code: str | None,
    tenant_id: str,
    decide_data: ApprovalDecideRequest,
    impersonation_session_id: int | None = None,
) -> ApprovalDecision:
    appr_req = get_request_by_id(db, request_id, tenant_id)
    if appr_req is None:
        raise LookupError(f"Approval request {request_id} not found")

    if appr_req.status != "PENDING":
        raise ValueError(
            f"Request {request_id} is not pending (status={appr_req.status!r})"
        )

    # Requester-equals-decider check uses real user_id — impersonation does not bypass this.
    if appr_req.requester_id == decider_user_id:
        raise ValueError("Requester cannot approve their own request")

    allowed_roles = get_approver_role_codes(db, appr_req.action_type, tenant_id)
    if not allowed_roles:
        raise ValueError(
            f"No approval rules defined for action_type={appr_req.action_type!r}"
        )

    if decider_role_code not in allowed_roles:
        raise PermissionError(
            f"Role {decider_role_code!r} is not authorized to decide "
            f"{appr_req.action_type!r} requests. Allowed: {sorted(allowed_roles)}"
        )

    decision_value = decide_data.decision
    appr_req.status = decision_value
    appr_req.updated_at = datetime.now(timezone.utc)

    decision_record = ApprovalDecision(
        request_id=appr_req.id,
        decider_id=decider_user_id,
        decider_role_code=decider_role_code,
        decision=decision_value,
        comment=decide_data.comment,
        impersonation_session_id=impersonation_session_id,
    )
    db.add(decision_record)
    db.flush()

    _log_event(
        db,
        appr_req,
        user_id=decider_user_id,
        role_code=decider_role_code,
        event_type="DECISION_MADE",
        detail=f"decision={decision_value} session={impersonation_session_id}",
    )

    db.commit()
    db.refresh(decision_record)

    logger.info(
        "Approval decision made: request_id=%d decision=%s decider=%s role=%s",
        appr_req.id,
        decision_value,
        decider_user_id,
        decider_role_code,
    )
    return decision_record


def get_pending_approval_requests(
    db: Session,
    tenant_id: str,
    action_type: str | None = None,
) -> list[ApprovalRequest]:
    return get_pending_requests(db, tenant_id, action_type)
