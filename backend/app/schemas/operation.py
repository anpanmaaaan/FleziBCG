from datetime import datetime

from pydantic import BaseModel


class OperationListItem(BaseModel):
    id: int
    operation_number: str
    name: str
    sequence: int
    status: str
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    quantity: int
    completed_qty: int = 0
    progress: int = 0

    class Config:
        from_attributes = True


class OperationDetail(OperationListItem):
    work_order_id: int
    work_order_number: str
    production_order_id: int
    production_order_number: str
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    good_qty: int = 0
    scrap_qty: int = 0
    qc_required: bool = False


class OperationStartRequest(BaseModel):
    operator_id: str | None = None
    started_at: datetime | None = None


class OperationReportQuantityRequest(BaseModel):
    good_qty: int
    scrap_qty: int = 0
    operator_id: str | None = None


class OperationCompleteRequest(BaseModel):
    operator_id: str | None = None
