from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.operation_repository import get_operation_by_id
from app.schemas.operation import (
    OperationAbortRequest,
    OperationCompleteRequest,
    OperationDetail,
    OperationEndDowntimeRequest,
    OperationPauseRequest,
    OperationReportQuantityRequest,
    OperationResumeRequest,
    OperationStartRequest,
    OperationStartDowntimeRequest,
)
from app.security.dependencies import RequestIdentity, require_action, require_permission
from app.services.operation_service import (
    CompleteOperationConflictError,
    EndDowntimeConflictError,
    PauseExecutionConflictError,
    ResumeExecutionConflictError,
    StartOperationConflictError,
    abort_operation,
    complete_operation,
    derive_operation_detail,
    end_downtime,
    pause_operation,
    report_quantity,
    resume_operation,
    start_operation,
    start_downtime,
)
from app.services.station_claim_service import ensure_operation_claim_owned_by_identity

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
    identity: RequestIdentity = Depends(require_action("execution.start")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        ensure_operation_claim_owned_by_identity(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    try:
        return start_operation(db, operation, request, tenant_id=identity.tenant_id)
    except StartOperationConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/report-quantity", response_model=OperationDetail)
def report_quantity_endpoint(
    operation_id: int,
    request: OperationReportQuantityRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("execution.report_quantity")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        ensure_operation_claim_owned_by_identity(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    try:
        return report_quantity(db, operation, request, tenant_id=identity.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/pause", response_model=OperationDetail)
def pause_operation_endpoint(
    operation_id: int,
    request: OperationPauseRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("execution.pause")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        ensure_operation_claim_owned_by_identity(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    try:
        return pause_operation(
            db,
            operation,
            request,
            actor_user_id=identity.user_id,
            tenant_id=identity.tenant_id,
        )
    except PauseExecutionConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/resume", response_model=OperationDetail)
def resume_operation_endpoint(
    operation_id: int,
    request: OperationResumeRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("execution.resume")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        ensure_operation_claim_owned_by_identity(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    try:
        return resume_operation(
            db,
            operation,
            request,
            actor_user_id=identity.user_id,
            tenant_id=identity.tenant_id,
        )
    except ResumeExecutionConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/complete", response_model=OperationDetail)
def complete_operation_endpoint(
    operation_id: int,
    request: OperationCompleteRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("execution.complete")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        ensure_operation_claim_owned_by_identity(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    try:
        return complete_operation(db, operation, request, tenant_id=identity.tenant_id)
    except CompleteOperationConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
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


@router.post("/operations/{operation_id}/start-downtime", response_model=OperationDetail)
def start_downtime_endpoint(
    operation_id: int,
    request: OperationStartDowntimeRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("execution.start_downtime")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        ensure_operation_claim_owned_by_identity(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    from app.services.operation_service import start_downtime, StartDowntimeConflictError

    try:
        return start_downtime(
            db,
            operation,
            request,
            actor_user_id=identity.user_id,
            tenant_id=identity.tenant_id,
        )
    except StartDowntimeConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/operations/{operation_id}/end-downtime", response_model=OperationDetail)
def end_downtime_endpoint(
    operation_id: int,
    request: OperationEndDowntimeRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_action("execution.end_downtime")),
):
    operation = get_operation_by_id(db, operation_id)
    if not operation or operation.tenant_id != identity.tenant_id:
        raise HTTPException(status_code=404, detail="Operation not found")

    try:
        ensure_operation_claim_owned_by_identity(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    try:
        return end_downtime(
            db,
            operation,
            request,
            actor_user_id=identity.user_id,
            tenant_id=identity.tenant_id,
        )
    except EndDowntimeConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

