from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval import (
    ApprovalAuditLog,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalRule,
)


def _score_rule(
    rule: ApprovalRule,
    scope_ref: str | None,
    governed_resource_type: str | None,
) -> int | None:
    """Compute specificity score for a rule against request context.

    Returns None if the rule is incompatible with the request context
    (i.e. the rule has a non-null dimension field that does not match).
    Higher score = more specific match wins (per P0-A-14 §7).

    Scoring:
      +8  rule.tenant_id is tenant-specific (not wildcard "*")
      +4  rule.scope_ref is set AND matches request scope_ref
      +2  rule.governed_resource_type is set AND matches request governed_resource_type
      +1  rule.governed_action_type is set (governed rules are more specific than legacy)

    Incompatibility rules (per P0-A-14 §8):
      - rule.scope_ref IS NOT NULL and does NOT equal request scope_ref → excluded
      - rule.governed_resource_type IS NOT NULL and does NOT equal request governed_resource_type → excluded
    """
    score = 0

    # Tenant-specific rules outrank wildcard across all precedence levels.
    if rule.tenant_id != "*":
        score += 8

    # Scope dimension: non-null rule field must match; NULL means "any scope".
    if rule.scope_ref is not None:
        if rule.scope_ref != scope_ref:
            return None  # incompatible
        score += 4

    # Governed resource type dimension: non-null must match; NULL means "any resource".
    if rule.governed_resource_type is not None:
        if rule.governed_resource_type != governed_resource_type:
            return None  # incompatible
        score += 2

    # Governed action type presence adds specificity (compatibility already
    # checked in the action-routing step before _score_rule is called).
    if rule.governed_action_type is not None:
        score += 1

    return score


def get_rules_for_action(
    db: Session,
    action_type: str,
    tenant_id: str,
    *,
    scope_ref: str | None = None,
    governed_resource_type: str | None = None,
    governed_action_type: str | None = None,
) -> list[ApprovalRule]:
    """Return active rules for the given action, applying scope-aware precedence.

    Scope-aware matching (P0-A-15B): When optional context is provided, rules are
    scored by specificity per P0-A-14 §7. The highest-specificity group is returned
    ("first non-empty level wins"). Legacy tenant + action_type rules serve as
    fallback when no scope/governed context is provided or no specific rule matches.

    Scoring per P0-A-14 §7:
      +8  tenant-specific rule (not wildcard)
      +4  scope_ref match
      +2  governed_resource_type match
      +1  governed_action_type present (governed rules are more specific)

    A rule field that is non-null MUST match the corresponding request context
    to remain a candidate. NULL rule fields match any request value (backward compat).

    All new parameters are keyword-only with default=None for full backward compat.
    Existing callers without scope context receive identical legacy behavior.
    """
    # Fetch all active rules for the tenant (specific + wildcard) in one query.
    all_candidates = list(
        db.scalars(
            select(ApprovalRule).where(
                ApprovalRule.is_active.is_(True),
                ApprovalRule.tenant_id.in_([tenant_id, "*"]),
            )
        ).all()
    )

    # Action-type routing: governed rules (governed_action_type set) only match
    # on governed_action_type; legacy rules (governed_action_type None) match action_type.
    action_compatible: list[ApprovalRule] = []
    for rule in all_candidates:
        if rule.governed_action_type is not None:
            # Governed rule — route via governed_action_type namespace.
            if rule.governed_action_type == governed_action_type:
                action_compatible.append(rule)
        else:
            # Legacy rule — route via action_type.
            if rule.action_type == action_type:
                action_compatible.append(rule)

    # Score each compatible rule for scope/resource specificity.
    scored: list[tuple[int, ApprovalRule]] = []
    for rule in action_compatible:
        score = _score_rule(rule, scope_ref, governed_resource_type)
        if score is not None:
            scored.append((score, rule))

    if not scored:
        return []

    # "First non-empty level wins": return all rules at the maximum score,
    # sorted by priority ascending (lower priority number = higher priority).
    max_score = max(s for s, _ in scored)
    best_rules = [r for s, r in scored if s == max_score]
    return sorted(
        best_rules,
        key=lambda r: r.priority if r.priority is not None else 2**31,
    )


def get_approver_role_codes(
    db: Session,
    action_type: str,
    tenant_id: str,
    *,
    scope_ref: str | None = None,
    governed_resource_type: str | None = None,
    governed_action_type: str | None = None,
) -> set[str]:
    """Return set of role codes authorized to decide this action_type."""
    rules = get_rules_for_action(
        db,
        action_type,
        tenant_id,
        scope_ref=scope_ref,
        governed_resource_type=governed_resource_type,
        governed_action_type=governed_action_type,
    )
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
