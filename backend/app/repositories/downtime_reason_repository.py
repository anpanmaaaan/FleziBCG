from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.downtime_reason import DowntimeReason


def get_downtime_reason_by_code(
    db: Session,
    *,
    tenant_id: str,
    reason_code: str,
) -> DowntimeReason | None:
    """
    Resolve a downtime reason master row for a tenant by reason_code.

    Baseline scope resolution is tenant-only; per-scope overrides
    (plant/area/line/station) are master-data debt tracked in the refactor
    review note and resolved in a later iteration.
    """
    statement = select(DowntimeReason).where(
        DowntimeReason.tenant_id == tenant_id,
        DowntimeReason.reason_code == reason_code,
    )
    return db.scalar(statement)


def list_active_downtime_reasons(
    db: Session,
    *,
    tenant_id: str,
) -> list[DowntimeReason]:
    """
    Return active downtime reasons for a tenant, ordered deterministically
    by `(sort_order, reason_code)`. Inactive rows are excluded so callers
    can treat the result as the FE-visible catalog.
    """
    statement = (
        select(DowntimeReason)
        .where(
            DowntimeReason.tenant_id == tenant_id,
            DowntimeReason.active_flag.is_(True),
        )
        .order_by(DowntimeReason.sort_order, DowntimeReason.reason_code)
    )
    return list(db.scalars(statement))


def upsert_downtime_reason(
    db: Session,
    *,
    tenant_id: str,
    reason_code: str,
    reason_name: str,
    reason_group: str,
    planned_flag: bool,
    default_block_mode: str,
    requires_comment: bool,
    requires_supervisor_review: bool,
    sort_order: int,
) -> DowntimeReason:
    row = get_downtime_reason_by_code(db, tenant_id=tenant_id, reason_code=reason_code)
    if row is None:
        row = DowntimeReason(
            tenant_id=tenant_id,
            reason_code=reason_code,
            reason_name=reason_name,
            reason_group=reason_group,
            planned_flag=planned_flag,
            default_block_mode=default_block_mode,
            requires_comment=requires_comment,
            requires_supervisor_review=requires_supervisor_review,
            active_flag=True,
            sort_order=sort_order,
        )
        db.add(row)
    else:
        row.reason_name = reason_name
        row.reason_group = reason_group
        row.planned_flag = planned_flag
        row.default_block_mode = default_block_mode
        row.requires_comment = requires_comment
        row.requires_supervisor_review = requires_supervisor_review
        row.active_flag = True
        row.sort_order = sort_order

    db.commit()
    db.refresh(row)
    return row


def deactivate_downtime_reason(
    db: Session,
    *,
    tenant_id: str,
    reason_code: str,
) -> DowntimeReason | None:
    row = get_downtime_reason_by_code(db, tenant_id=tenant_id, reason_code=reason_code)
    if row is None:
        return None
    row.active_flag = False
    db.commit()
    db.refresh(row)
    return row
