from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RoutingOperationCreateRequest(BaseModel):
    operation_code: str
    operation_name: str
    sequence_no: int
    standard_cycle_time: float | None = None
    required_resource_type: str | None = None


class RoutingOperationUpdateRequest(BaseModel):
    operation_code: str | None = None
    operation_name: str | None = None
    sequence_no: int | None = None
    standard_cycle_time: float | None = None
    required_resource_type: str | None = None


class RoutingCreateRequest(BaseModel):
    product_id: str
    routing_code: str
    routing_name: str


class RoutingUpdateRequest(BaseModel):
    product_id: str | None = None
    routing_code: str | None = None
    routing_name: str | None = None


class RoutingOperationItem(BaseModel):
    operation_id: str
    routing_id: str
    operation_code: str
    operation_name: str
    sequence_no: int
    standard_cycle_time: float | None = None
    required_resource_type: str | None = None
    created_at: datetime
    updated_at: datetime


class RoutingItem(BaseModel):
    routing_id: str
    tenant_id: str
    product_id: str
    routing_code: str
    routing_name: str
    lifecycle_status: str
    operations: list[RoutingOperationItem]
    created_at: datetime
    updated_at: datetime
