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
