from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class OpenStationSessionRequest(BaseModel):
    station_id: str
    operator_user_id: str | None = None
    equipment_id: str | None = None
    current_operation_id: int | None = None


class IdentifyOperatorRequest(BaseModel):
    operator_user_id: str


class BindEquipmentRequest(BaseModel):
    equipment_id: str


class StationSessionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    tenant_id: str
    station_id: str
    operator_user_id: str | None = None
    opened_at: datetime
    closed_at: datetime | None = None
    status: str
    equipment_id: str | None = None
    current_operation_id: int | None = None
    created_at: datetime
    updated_at: datetime


class StationSessionCurrentResponse(BaseModel):
    session: StationSessionItem | None
