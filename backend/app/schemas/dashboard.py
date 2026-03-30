from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_production_orders: int
    total_work_orders: int
    total_operations: int
    operations_in_progress: int
    operations_completed: int
    operations_pending: int
