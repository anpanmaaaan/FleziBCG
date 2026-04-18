from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Role, Scope, UserRoleAssignment
from app.models.station_claim import OperationClaim, OperationClaimAuditLog
from app.security.dependencies import RequestIdentity


class ClaimConflictError(Exception):
    pass


@dataclass
class StationScopeContext:
    scope_id: int
    scope_value: str


def _normalize_role(role_code: str | None) -> str:
    if not role_code:
        return ""
    return role_code.strip().upper()


# INTENT: Resolves the effective role for station access, preferring the
# impersonated (acting) role over the user's own role.
def _effective_role(identity: RequestIdentity) -> str:
    acting_role = _normalize_role(identity.acting_role_code)
    if acting_role:
        return acting_role
    return _normalize_role(identity.role_code)


def ensure_operator_context(identity: RequestIdentity) -> None:
    if _effective_role(identity) != "OPR":
        raise PermissionError(
            "Station queue and claims are only available to OPR context."
        )


# EDGE: Station scope is resolved from UserRoleAssignment, isolating the
# operator to their assigned station(s) within the tenant.
def resolve_station_scope(
    db: Session, identity: RequestIdentity
) -> StationScopeContext:
    statement = (
        select(UserRoleAssignment, Scope)
        .join(Role, Role.id == UserRoleAssignment.role_id)
        .join(Scope, Scope.id == UserRoleAssignment.scope_id)
        .where(
            UserRoleAssignment.user_id == identity.user_id,
            UserRoleAssignment.is_active.is_(True),
            Role.code == "OPR",
            Scope.tenant_id == identity.tenant_id,
            Scope.scope_type == "station",
        )
        .order_by(UserRoleAssignment.is_primary.desc(), UserRoleAssignment.id.asc())
    )
    rows = list(db.execute(statement))
    now = datetime.now(timezone.utc)
    for assignment, scope in rows:
        if assignment.valid_from is not None and assignment.valid_from > now:
            continue
        if assignment.valid_to is not None and assignment.valid_to < now:
            continue
        return StationScopeContext(scope_id=scope.id, scope_value=scope.scope_value)

    raise ValueError("No station scope assigned")


def _log_claim_event(
    db: Session,
    *,
    event_type: str,
    identity: RequestIdentity,
    operation_id: int,
    station_scope_id: int,
    reason: str | None,
    claim_id: int | None = None,
) -> None:
    db.add(
        OperationClaimAuditLog(
            claim_id=claim_id,
            tenant_id=identity.tenant_id,
            operation_id=operation_id,
            station_scope_id=station_scope_id,
            actor_user_id=identity.user_id,
            acting_role_code=identity.acting_role_code,
            event_type=event_type,
            reason=reason,
        )
    )


# INVARIANT: SELECT FOR UPDATE prevents concurrent claims on the same
# operation. The row lock is held until the transaction commits.
def _get_unreleased_claim_for_update(
    db: Session, tenant_id: str, operation_id: int
) -> OperationClaim | None:
    statement = (
        select(OperationClaim)
        .where(
            OperationClaim.tenant_id == tenant_id,
            OperationClaim.operation_id == operation_id,
            OperationClaim.released_at.is_(None),
        )
        .with_for_update()
    )
    return db.scalar(statement)


# WHY: Claim expiry is evaluated lazily on every read/write access, not via
# a background timer. This eliminates clock-skew race conditions between
# a scheduler and the request path. The trade-off is a slightly stale
# "expires_at" display until the next access.
def _expire_claim_if_needed(
    db: Session,
    claim: OperationClaim | None,
    *,
    identity: RequestIdentity,
) -> OperationClaim | None:
    if claim is None:
        return None

    now = datetime.now(timezone.utc)
    if claim.expires_at > now:
        return claim

    claim.released_at = now
    claim.release_reason = "expired"
    _log_claim_event(
        db,
        event_type="CLAIM_EXPIRED",
        identity=identity,
        operation_id=claim.operation_id,
        station_scope_id=claim.station_scope_id,
        reason="expired",
        claim_id=claim.id,
    )
    db.flush()
    return None


def _validate_operation_for_station(
    db: Session,
    *,
    identity: RequestIdentity,
    station_scope: StationScopeContext,
    operation_id: int,
) -> Operation:
    operation = db.scalar(
        select(Operation).where(
            Operation.id == operation_id,
            Operation.tenant_id == identity.tenant_id,
        )
    )
    if operation is None:
        raise LookupError("Operation not found")

    if operation.station_scope_value != station_scope.scope_value:
        raise PermissionError("Operation is outside your station scope")

    if operation.status not in (StatusEnum.planned.value, StatusEnum.in_progress.value):
        raise ValueError("Operation is not claimable in current status")

    return operation


def get_station_scoped_operation(
    db: Session,
    identity: RequestIdentity,
    operation_id: int,
) -> Operation:
    ensure_operator_context(identity)
    station_scope = resolve_station_scope(db, identity)

    operation = db.scalar(
        select(Operation).where(
            Operation.id == operation_id,
            Operation.tenant_id == identity.tenant_id,
        )
    )
    if operation is None:
        raise LookupError("Operation not found")

    if operation.station_scope_value != station_scope.scope_value:
        raise PermissionError("Operation is outside your station scope")

    return operation


def _to_claim_state(
    identity: RequestIdentity, claim: OperationClaim | None
) -> tuple[str, datetime | None, str | None]:
    if claim is None:
        return ("none", None, None)
    if claim.claimed_by_user_id == identity.user_id:
        return ("mine", claim.expires_at, claim.claimed_by_user_id)
    return ("other", claim.expires_at, claim.claimed_by_user_id)


def get_station_queue(db: Session, identity: RequestIdentity) -> tuple[str, list[dict]]:
    ensure_operator_context(identity)
    station_scope = resolve_station_scope(db, identity)

    statement = (
        select(Operation, WorkOrder, ProductionOrder)
        .join(WorkOrder, WorkOrder.id == Operation.work_order_id)
        .join(ProductionOrder, ProductionOrder.id == WorkOrder.production_order_id)
        .where(
            Operation.tenant_id == identity.tenant_id,
            Operation.station_scope_value == station_scope.scope_value,
            Operation.status.in_(
                [StatusEnum.planned.value, StatusEnum.in_progress.value]
            ),
        )
        .order_by(
            Operation.planned_start.asc().nullslast(),
            Operation.planned_end.asc().nullslast(),
            Operation.id.asc(),
        )
    )

    rows = list(db.execute(statement))
    operation_ids = [operation.id for operation, _wo, _po in rows]
    claims = {}
    if operation_ids:
        claim_rows = list(
            db.scalars(
                select(OperationClaim).where(
                    OperationClaim.tenant_id == identity.tenant_id,
                    OperationClaim.operation_id.in_(operation_ids),
                    OperationClaim.released_at.is_(None),
                )
            )
        )
        for claim in claim_rows:
            claims[claim.operation_id] = _expire_claim_if_needed(
                db, claim, identity=identity
            )

    db.commit()

    items: list[dict] = []
    for operation, work_order, production_order in rows:
        state, expires_at, claimed_by_user_id = _to_claim_state(
            identity, claims.get(operation.id)
        )
        items.append(
            {
                "operation_id": operation.id,
                "operation_number": operation.operation_number,
                "name": operation.name,
                "work_order_number": work_order.work_order_number,
                "production_order_number": production_order.order_number,
                "status": operation.status,
                "planned_start": operation.planned_start,
                "planned_end": operation.planned_end,
                "claim": {
                    "state": state,
                    "expires_at": expires_at,
                    "claimed_by_user_id": claimed_by_user_id,
                },
            }
        )

    return station_scope.scope_value, items


def claim_operation(
    db: Session,
    identity: RequestIdentity,
    operation_id: int,
    *,
    reason: str | None = None,
    duration_minutes: int | None = None,
) -> tuple[OperationClaim, str]:
    ensure_operator_context(identity)
    station_scope = resolve_station_scope(db, identity)
    _validate_operation_for_station(
        db, identity=identity, station_scope=station_scope, operation_id=operation_id
    )

    ttl = (
        duration_minutes
        if duration_minutes is not None
        else settings.claim_default_ttl_minutes
    )
    if ttl <= 0:
        raise ValueError("duration_minutes must be greater than zero")
    if ttl > settings.claim_max_ttl_minutes:
        raise ValueError(
            f"duration_minutes exceeds max allowed ({settings.claim_max_ttl_minutes})"
        )

    claim = _get_unreleased_claim_for_update(db, identity.tenant_id, operation_id)
    claim = _expire_claim_if_needed(db, claim, identity=identity)

    if claim is not None:
        if claim.claimed_by_user_id == identity.user_id:
            db.commit()
            return claim, station_scope.scope_value
        raise ClaimConflictError("Operation already claimed by another operator")

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=ttl)
    claim = OperationClaim(
        tenant_id=identity.tenant_id,
        operation_id=operation_id,
        station_scope_id=station_scope.scope_id,
        claimed_by_user_id=identity.user_id,
        claimed_at=now,
        expires_at=expires_at,
    )
    db.add(claim)
    db.flush()

    _log_claim_event(
        db,
        event_type="CLAIM_CREATED",
        identity=identity,
        operation_id=operation_id,
        station_scope_id=station_scope.scope_id,
        reason=(reason or "")[:512] or None,
        claim_id=claim.id,
    )
    db.commit()
    db.refresh(claim)
    return claim, station_scope.scope_value


# EDGE: Admin/OTS impersonating OPR can release any claim at the station,
# not just their own. This is the only claim operation where impersonation
# breaks the normal ownership constraint.
def _has_admin_support_override(identity: RequestIdentity) -> bool:
    role = _normalize_role(identity.role_code)
    acting = _normalize_role(identity.acting_role_code)
    return role in {"ADM", "OTS"} and acting == "OPR"


def release_operation_claim(
    db: Session,
    identity: RequestIdentity,
    operation_id: int,
    *,
    reason: str,
) -> tuple[OperationClaim, str]:
    ensure_operator_context(identity)
    station_scope = resolve_station_scope(db, identity)
    _validate_operation_for_station(
        db, identity=identity, station_scope=station_scope, operation_id=operation_id
    )

    claim = _get_unreleased_claim_for_update(db, identity.tenant_id, operation_id)
    claim = _expire_claim_if_needed(db, claim, identity=identity)
    if claim is None:
        raise LookupError("No active claim to release")

    if claim.claimed_by_user_id != identity.user_id and not _has_admin_support_override(
        identity
    ):
        raise PermissionError("Only the claim owner may release this claim")

    now = datetime.now(timezone.utc)
    claim.released_at = now
    claim.release_reason = reason[:256]
    _log_claim_event(
        db,
        event_type="CLAIM_RELEASED",
        identity=identity,
        operation_id=operation_id,
        station_scope_id=claim.station_scope_id,
        reason=reason[:512],
        claim_id=claim.id,
    )
    db.commit()
    db.refresh(claim)
    return claim, station_scope.scope_value


def get_operation_claim_status(
    db: Session, identity: RequestIdentity, operation_id: int
) -> dict:
    ensure_operator_context(identity)
    station_scope = resolve_station_scope(db, identity)
    _validate_operation_for_station(
        db, identity=identity, station_scope=station_scope, operation_id=operation_id
    )

    claim = _get_unreleased_claim_for_update(db, identity.tenant_id, operation_id)
    claim = _expire_claim_if_needed(db, claim, identity=identity)
    db.commit()

    state, expires_at, claimed_by_user_id = _to_claim_state(identity, claim)
    return {
        "state": state,
        "expires_at": expires_at,
        "claimed_by_user_id": claimed_by_user_id,
        "station_scope_value": station_scope.scope_value,
    }


def ensure_operation_claim_owned_by_identity(
    db: Session,
    identity: RequestIdentity,
    operation_id: int,
) -> None:
    claim = _get_unreleased_claim_for_update(db, identity.tenant_id, operation_id)
    claim = _expire_claim_if_needed(db, claim, identity=identity)
    if claim is None or claim.claimed_by_user_id != identity.user_id:
        db.commit()
        raise PermissionError(
            "Operation must be claimed by you before execution actions."
        )
    db.commit()
