from sqlalchemy.orm import Session

from app.repositories.downtime_reason_repository import list_active_downtime_reasons
from app.schemas.downtime_reason import DowntimeReasonItem


def list_downtime_reasons(db: Session, *, tenant_id: str) -> list[DowntimeReasonItem]:
    rows = list_active_downtime_reasons(db, tenant_id=tenant_id)
    return [DowntimeReasonItem.model_validate(row) for row in rows]