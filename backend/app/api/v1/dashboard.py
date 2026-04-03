from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.dashboard import DashboardHealthResponse, DashboardSummaryResponse
from app.security.dependencies import RequestIdentity, require_permission
from app.services.dashboard_service import get_dashboard_health, get_dashboard_summary

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def read_dashboard_legacy(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("VIEW")),
):
    # Backward-compatible alias to summary endpoint.
    return get_dashboard_summary(db, tenant_id=identity.tenant_id)


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def read_dashboard_summary(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("VIEW")),
):
    return get_dashboard_summary(db, tenant_id=identity.tenant_id)


@router.get("/dashboard/health", response_model=DashboardHealthResponse)
def read_dashboard_health(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("VIEW")),
):
    return get_dashboard_health(db, tenant_id=identity.tenant_id)
