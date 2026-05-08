from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.quality import (
    QualityDispositionRequest,
    QualityDispositionResponse,
    QualityHoldItem,
    QualityMeasurementSubmitRequest,
    QualityMeasurementSubmitResponse,
    QualityOperationRequirementsResponse,
)
from app.security.dependencies import (
    RequestIdentity,
    require_authenticated_identity,
    require_permission,
)
from app.services.quality_service import (
    QualityConflictError,
    get_quality_measurement_requirements,
    list_quality_holds,
    record_quality_disposition,
    submit_qc_measurement,
)


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/quality/operations/{operation_id}/requirements",
    response_model=QualityOperationRequirementsResponse,
)
def get_quality_measurement_requirements_endpoint(
    operation_id: int,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        return get_quality_measurement_requirements(
            db,
            tenant_id=identity.tenant_id,
            operation_id=operation_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post(
    "/quality/measurements",
    response_model=QualityMeasurementSubmitResponse,
)
def submit_quality_measurement_endpoint(
    payload: QualityMeasurementSubmitRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        return submit_qc_measurement(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except QualityConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/quality/holds", response_model=list[QualityHoldItem])
def list_quality_holds_endpoint(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    return list_quality_holds(db, tenant_id=identity.tenant_id)


@router.post(
    "/quality/reviews/{review_id}/disposition",
    response_model=QualityDispositionResponse,
)
def record_quality_disposition_endpoint(
    review_id: int,
    payload: QualityDispositionRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("APPROVE")),
):
    effective_role = identity.acting_role_code or identity.role_code
    try:
        return record_quality_disposition(
            db,
            hold_id=review_id,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            actor_role_code=effective_role,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except QualityConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
