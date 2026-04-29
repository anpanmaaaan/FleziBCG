from sqlalchemy.orm import Session

from app.repositories.downtime_reason_repository import (
    deactivate_downtime_reason as deactivate_downtime_reason_row,
    list_active_downtime_reasons,
    upsert_downtime_reason as upsert_downtime_reason_row,
)
from app.schemas.downtime_reason import (
    DowntimeReasonAdminItem,
    DowntimeReasonItem,
    DowntimeReasonUpsertRequest,
)
from app.services.security_event_service import record_security_event


def list_downtime_reasons(db: Session, *, tenant_id: str) -> list[DowntimeReasonItem]:
    rows = list_active_downtime_reasons(db, tenant_id=tenant_id)
    return [DowntimeReasonItem.model_validate(row) for row in rows]


def upsert_downtime_reason(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    payload: DowntimeReasonUpsertRequest,
) -> DowntimeReasonAdminItem:
    row = upsert_downtime_reason_row(
        db,
        tenant_id=tenant_id,
        reason_code=payload.reason_code.strip(),
        reason_name=payload.reason_name.strip(),
        reason_group=payload.reason_group.strip().upper(),
        planned_flag=payload.planned_flag,
        default_block_mode=payload.default_block_mode.strip().upper(),
        requires_comment=payload.requires_comment,
        requires_supervisor_review=payload.requires_supervisor_review,
        sort_order=payload.sort_order,
    )
    record_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="MASTER.DOWNTIME_REASON_UPSERT",
        resource_type="downtime_reason",
        resource_id=row.reason_code,
        detail=row.reason_name,
    )
    return DowntimeReasonAdminItem.model_validate(row)


def deactivate_downtime_reason(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str,
    reason_code: str,
) -> DowntimeReasonAdminItem | None:
    row = deactivate_downtime_reason_row(
        db,
        tenant_id=tenant_id,
        reason_code=reason_code,
    )
    if row is None:
        return None
    record_security_event(
        db,
        tenant_id=tenant_id,
        actor_user_id=actor_user_id,
        event_type="MASTER.DOWNTIME_REASON_DEACTIVATE",
        resource_type="downtime_reason",
        resource_id=row.reason_code,
        detail=row.reason_name,
    )
    return DowntimeReasonAdminItem.model_validate(row)