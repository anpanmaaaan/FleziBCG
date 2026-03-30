from app.repositories.operation_repository import count_operations, count_operations_by_status
from app.repositories.production_order_repository import count_production_orders, count_work_orders
from app.schemas.dashboard import DashboardSummary
from app.models.master import StatusEnum


def get_dashboard_summary(db) -> DashboardSummary:
    return DashboardSummary(
        total_production_orders=count_production_orders(db),
        total_work_orders=count_work_orders(db),
        total_operations=count_operations(db),
        operations_in_progress=count_operations_by_status(db, StatusEnum.in_progress.value),
        operations_completed=count_operations_by_status(db, StatusEnum.completed.value),
        operations_pending=count_operations_by_status(db, StatusEnum.pending.value),
    )
