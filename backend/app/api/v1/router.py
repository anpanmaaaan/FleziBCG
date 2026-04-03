from fastapi import APIRouter

from app.api.v1 import auth, dashboard, execution_timeline, operations, production_orders

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(production_orders.router)
api_router.include_router(operations.router)
api_router.include_router(execution_timeline.router)

@api_router.get("/ping")
def ping():
    return {"message": "pong"}