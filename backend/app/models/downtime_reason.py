from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


# Platform-level downtime classification taxonomy. Not plant-configurable.
# Each `downtime_reasons` master row is tagged with one of these groups for
# aggregation/analytics; selectable reasons themselves live in the master
# table, not in this enum.
class DowntimeReasonGroup(str, Enum):
    BREAKDOWN = "BREAKDOWN"
    MATERIAL = "MATERIAL"
    QUALITY = "QUALITY"
    CHANGEOVER = "CHANGEOVER"
    PLANNED_STOP = "PLANNED_STOP"
    UTILITIES = "UTILITIES"
    OTHER = "OTHER"


class DowntimeReason(Base):
    __tablename__ = "downtime_reasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False)
    # Scope hierarchy columns — nullable; a NULL column means "applies broader".
    # Present today to preserve tenant→plant→area→line→station direction; the
    # baseline resolver only uses tenant_id + reason_code. Narrower scoped
    # rows are master-data debt tracked in the refactor review note.
    plant_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    area_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    line_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    station_scope_value: Mapped[str | None] = mapped_column(String(128), nullable=True)

    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_name: Mapped[str] = mapped_column(String(128), nullable=False)
    reason_group: Mapped[str] = mapped_column(String(32), nullable=False)

    planned_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_block_mode: Mapped[str] = mapped_column(
        String(32), nullable=False, default="BLOCK"
    )
    requires_comment: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    requires_supervisor_review: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    active_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
