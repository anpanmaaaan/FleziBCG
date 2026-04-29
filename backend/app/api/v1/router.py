from fastapi import APIRouter

from app.api.v1 import (
    access,
    approvals,
    auth,
    dashboard,
    downtime_reasons,
    execution_timeline,
    iam,
    impersonations,
    operations,
    products,
    production_orders,
    routings,
    security_events,
    station,
    users,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(access.router)
api_router.include_router(dashboard.router)
api_router.include_router(production_orders.router)
api_router.include_router(operations.router)
api_router.include_router(execution_timeline.router)
api_router.include_router(impersonations.router)
api_router.include_router(approvals.router)
api_router.include_router(iam.router)
api_router.include_router(users.router)
api_router.include_router(station.router)
api_router.include_router(downtime_reasons.router)
api_router.include_router(products.router)
api_router.include_router(routings.router)
api_router.include_router(security_events.router)


@api_router.get("/ping")
def ping():
    return {"message": "pong"}
