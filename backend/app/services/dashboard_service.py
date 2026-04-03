from datetime import datetime, timedelta, timezone

from app.repositories.dashboard_repository import (
    get_blocked_operation_counts_by_work_order,
    get_operation_status_counts_for_dashboard,
    get_work_orders_for_dashboard,
)
from app.schemas.dashboard import (
    AlertSeverityCode,
    BottleneckScopeType,
    BottleneckStatusCode,
    DashboardAlertsSummary,
    DashboardBottleneckItem,
    DashboardContext,
    DashboardHealthResponse,
    DashboardOperationsSummary,
    DashboardRiskWorkOrderItem,
    DashboardSummaryResponse,
    DashboardWorkOrdersSummary,
    RiskLevelCode,
    RiskReasonCode,
)

RISK_WINDOW_MINUTES = 120


def _normalize_datetime_for_diff(value: datetime, reference: datetime) -> datetime:
    if value.tzinfo is None and reference.tzinfo is not None:
        return value.replace(tzinfo=reference.tzinfo)
    if value.tzinfo is not None and reference.tzinfo is None:
        return value.replace(tzinfo=None)
    return value


def _is_late_work_order(work_order, now: datetime) -> bool:
    if work_order.status == "LATE":
        return True

    if work_order.planned_end is None:
        return False

    planned_end = _normalize_datetime_for_diff(work_order.planned_end, now)

    if work_order.status != "COMPLETED" and planned_end < now:
        return True

    if work_order.status == "COMPLETED" and work_order.actual_end is not None:
        actual_end = _normalize_datetime_for_diff(work_order.actual_end, planned_end)
        return actual_end > planned_end

    return False


def _is_at_risk_work_order(work_order, now: datetime) -> bool:
    if work_order.status != "IN_PROGRESS":
        return False

    if work_order.planned_end is None:
        return False

    planned_end = _normalize_datetime_for_diff(work_order.planned_end, now)
    risk_deadline = now + timedelta(minutes=RISK_WINDOW_MINUTES)
    return now <= planned_end <= risk_deadline


def _derive_shift_code(now: datetime) -> str:
    hour = now.hour
    if 6 <= hour < 14:
        return "A"
    if 14 <= hour < 22:
        return "B"
    return "C"


def get_dashboard_summary(db, tenant_id: str, shift: str | None = None) -> DashboardSummaryResponse:
    now = datetime.now(timezone.utc)
    work_orders = get_work_orders_for_dashboard(db, tenant_id=tenant_id)
    operation_status_counts = get_operation_status_counts_for_dashboard(db, tenant_id=tenant_id)

    late_count = sum(1 for work_order in work_orders if _is_late_work_order(work_order, now))
    at_risk_count = sum(1 for work_order in work_orders if _is_at_risk_work_order(work_order, now))
    total_count = len(work_orders)
    on_time_count = max(total_count - late_count - at_risk_count, 0)

    blocked_operations = int(operation_status_counts.get("BLOCKED", 0))
    in_progress_operations = int(operation_status_counts.get("IN_PROGRESS", 0))

    alert_count = late_count + at_risk_count + blocked_operations
    highest_severity = AlertSeverityCode.LOW
    if late_count > 0 or blocked_operations > 0:
        highest_severity = AlertSeverityCode.HIGH
    elif at_risk_count > 0:
        highest_severity = AlertSeverityCode.MEDIUM

    return DashboardSummaryResponse(
        context=DashboardContext(
            date=now.date().isoformat(),
            shift=shift or _derive_shift_code(now),
        ),
        work_orders=DashboardWorkOrdersSummary(
            total=total_count,
            on_time=on_time_count,
            at_risk=at_risk_count,
            late=late_count,
        ),
        operations=DashboardOperationsSummary(
            in_progress=in_progress_operations,
            blocked=blocked_operations,
        ),
        alerts=DashboardAlertsSummary(
            count=alert_count,
            highest_severity=highest_severity,
        ),
    )


def get_dashboard_health(db, tenant_id: str) -> DashboardHealthResponse:
    now = datetime.now(timezone.utc)
    work_orders = get_work_orders_for_dashboard(db, tenant_id=tenant_id)
    blocked_counts_by_work_order = get_blocked_operation_counts_by_work_order(db, tenant_id=tenant_id)

    bottlenecks: list[DashboardBottleneckItem] = []
    risks: list[DashboardRiskWorkOrderItem] = []

    # TODO: Add work-center aggregation when work-center code is available in domain model.
    for work_order in work_orders:
        blocked_count = int(blocked_counts_by_work_order.get(work_order.work_order_number, 0))
        is_late = _is_late_work_order(work_order, now)
        is_at_risk = _is_at_risk_work_order(work_order, now)

        if blocked_count > 0:
            bottlenecks.append(
                DashboardBottleneckItem(
                    scope_type=BottleneckScopeType.WORK_ORDER,
                    scope_code=work_order.work_order_number,
                    status=BottleneckStatusCode.BLOCKED,
                    affected_work_orders=1,
                )
            )
            risks.append(
                DashboardRiskWorkOrderItem(
                    work_order_number=work_order.work_order_number,
                    risk_level=RiskLevelCode.HIGH,
                    reason_code=RiskReasonCode.BLOCKED_OPERATION,
                )
            )
            continue

        if is_late:
            bottlenecks.append(
                DashboardBottleneckItem(
                    scope_type=BottleneckScopeType.WORK_ORDER,
                    scope_code=work_order.work_order_number,
                    status=BottleneckStatusCode.DELAYED,
                    affected_work_orders=1,
                )
            )
            risks.append(
                DashboardRiskWorkOrderItem(
                    work_order_number=work_order.work_order_number,
                    risk_level=RiskLevelCode.HIGH,
                    reason_code=RiskReasonCode.LATE_SCHEDULE,
                )
            )
            continue

        if is_at_risk:
            risks.append(
                DashboardRiskWorkOrderItem(
                    work_order_number=work_order.work_order_number,
                    risk_level=RiskLevelCode.MEDIUM,
                    reason_code=RiskReasonCode.UPSTREAM_DELAY,
                )
            )

    return DashboardHealthResponse(
        bottlenecks=bottlenecks,
        risk_work_orders=risks,
    )
