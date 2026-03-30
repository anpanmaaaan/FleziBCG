from datetime import datetime
from typing import List

from pydantic import Field

from app.schemas.common import BaseSchema


class WorkOrderSummary(BaseSchema):
    id: int
    work_order_number: str
    status: str
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    operations_count: int = 0
    overall_progress: int = 0


class ProductionOrderSummary(BaseSchema):
    id: int
    order_number: str
    product_name: str
    quantity: int
    status: str
    serial_number: str | None = None
    lot_id: str | None = None
    customer: str | None = None
    priority: str | None = None
    machine_number: str | None = None
    route_id: str | None = None
    material_code: str | None = None
    assignee: str | None = None
    department: str | None = None
    released_date: datetime | None = None
    planned_start_date: datetime | None = None
    planned_completion_date: datetime | None = None
    actual_start_date: datetime | None = None
    actual_completion_date: datetime | None = None
    progress: int | None = None


class ProductionOrderDetail(ProductionOrderSummary):
    work_orders: List[WorkOrderSummary] = Field(default_factory=list)
