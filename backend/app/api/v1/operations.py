from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.operation_repository import get_operation_by_id
from app.schemas.operation import (
    OperationAbortRequest,
    OperationCompleteRequest,
    OperationDetail,
    OperationReportQuantityRequest,
    OperationStartRequest,
)
from app.security.dependencies import RequestIdentity, require_permission
from app.services.operation_service import abort_operation, derive_operation_detail, start_operation, report_quantity, complete_operation

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/operations/{operation_id}", response_model=OperationDetail)
def read_operation(
    operation_id: int,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("VIEW")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")
    return derive_operation_detail(db, operation)


@router.post("/operations/{operation_id}/start", response_model=OperationDetail)
def start_operation_endpoint(
    operation_id: int,
    request: OperationStartRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("EXECUTE")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        return start_operation(db, operation, request, tenant_id=identity.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/report-quantity", response_model=OperationDetail)
def report_quantity_endpoint(
    operation_id: int,
    request: OperationReportQuantityRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("EXECUTE")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        return report_quantity(db, operation, request, tenant_id=identity.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/complete", response_model=OperationDetail)
def complete_operation_endpoint(
    operation_id: int,
    request: OperationCompleteRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("EXECUTE")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        return complete_operation(db, operation, request, tenant_id=identity.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/abort", response_model=OperationDetail)
def abort_operation_endpoint(
    operation_id: int,
    request: OperationAbortRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("EXECUTE")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        return abort_operation(db, operation, request, tenant_id=identity.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

