from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import (
    ApprovalAuditLog,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRule,
)


def get_rules_for_action(
    db: Session,
    action_type: str,
    tenant_id: str,
) -> list[ApprovalRule]:
    """Return active rules for the given action, checking tenant-specific and wildcard."""
    # INTENT: Match both tenant-specific rules AND wildcard ("*") rules in a
    # single query. Wildcard rules act as defaults for all tenants.
    statement = (
        select(ApprovalRule)
        .where(
            ApprovalRule.action_type == action_type,
            ApprovalRule.is_active.is_(True),
            ApprovalRule.tenant_id.in_([tenant_id, "*"]),
        )
        # WHY: DESC ordering puts tenant-specific rules (e.g., "tenant-A")
        # before the wildcard ("*"), so callers see overrides first.
        .order_by(ApprovalRule.tenant_id.desc())  # tenant-specific before wildcard
    )
    return list(db.scalars(statement).all())


def get_approver_role_codes(
    db: Session,
    action_type: str,
    tenant_id: str,
) -> set[str]:
    """Return set of role codes authorized to decide this action_type."""
    rules = get_rules_for_action(db, action_type, tenant_id)
    return {r.approver_role_code for r in rules}


def get_request_by_id(
    db: Session,
    request_id: int,
    tenant_id: str,
) -> ApprovalRequest | None:
    return db.scalar(
        select(ApprovalRequest).where(
            ApprovalRequest.id == request_id,
            ApprovalRequest.tenant_id == tenant_id,
        )
    )


def get_pending_requests(
    db: Session,
    tenant_id: str,
    action_type: str | None = None,
) -> list[ApprovalRequest]:
    stmt = (
        select(ApprovalRequest)
        .where(
            ApprovalRequest.tenant_id == tenant_id,
            ApprovalRequest.status == "PENDING",
        )
        .order_by(ApprovalRequest.created_at.desc())
    )
    if action_type:
        stmt = stmt.where(ApprovalRequest.action_type == action_type)
    return list(db.scalars(stmt).all())


def get_audit_logs_for_request(
    db: Session,
    request_id: int,
) -> list[ApprovalAuditLog]:
    return list(
        db.scalars(
            select(ApprovalAuditLog)
            .where(ApprovalAuditLog.request_id == request_id)
            .order_by(ApprovalAuditLog.created_at.asc())
        ).all()
    )


def get_decisions_for_request(
    db: Session,
    request_id: int,
) -> list[ApprovalDecision]:
    return list(
        db.scalars(
            select(ApprovalDecision)
            .where(ApprovalDecision.request_id == request_id)
            .order_by(ApprovalDecision.created_at.asc())
        ).all()
    )
