from enum import Enum

from app.schemas.common import BaseSchema


class AlertSeverityCode(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BottleneckScopeType(str, Enum):
    WORK_ORDER = "WORK_ORDER"


class BottleneckStatusCode(str, Enum):
    NORMAL = "NORMAL"
    DELAYED = "DELAYED"
    BLOCKED = "BLOCKED"


class RiskLevelCode(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskReasonCode(str, Enum):
    LATE_SCHEDULE = "LATE_SCHEDULE"
    UPSTREAM_DELAY = "UPSTREAM_DELAY"
    BLOCKED_OPERATION = "BLOCKED_OPERATION"


class DashboardContext(BaseSchema):
    date: str
    shift: str


class DashboardWorkOrdersSummary(BaseSchema):
    total: int
    on_time: int
    at_risk: int
    late: int


class DashboardOperationsSummary(BaseSchema):
    in_progress: int
    blocked: int


class DashboardAlertsSummary(BaseSchema):
    count: int
    highest_severity: AlertSeverityCode


class DashboardSummaryResponse(BaseSchema):
    context: DashboardContext
    work_orders: DashboardWorkOrdersSummary
    operations: DashboardOperationsSummary
    alerts: DashboardAlertsSummary


class DashboardBottleneckItem(BaseSchema):
    scope_type: BottleneckScopeType
    scope_code: str
    status: BottleneckStatusCode
    affected_work_orders: int


class DashboardRiskWorkOrderItem(BaseSchema):
    work_order_number: str
    risk_level: RiskLevelCode
    reason_code: RiskReasonCode


class DashboardHealthResponse(BaseSchema):
    bottlenecks: list[DashboardBottleneckItem]
    risk_work_orders: list[DashboardRiskWorkOrderItem]

