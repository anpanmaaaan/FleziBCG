from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.quality import (
    QualityGateDefinitionCreateRequest,
    QualityGateDefinitionResponse,
    QualityGateInstanceOpenRequest,
    QualityGateInstanceResponse,
    QualityDispositionRequest,
    QualityDispositionResponse,
    QualityHoldItem,
    QualityMeasurementSubmitRequest,
    QualityMeasurementSubmitResponse,
    QualityOperationRequirementsResponse,
    QualityDeviationRequestCreate,
    QualityDeviationResolveRequest,
    QualityDeviationRequestItem,
    QualityNonconformanceCreateRequest,
    QualityNonconformanceItem,
)
from app.security.dependencies import (
    RequestIdentity,
    require_authenticated_identity,
    require_permission,
)
from app.services.quality_service import (
    QualityConflictError,
    create_quality_gate_definition_service,
    get_quality_measurement_requirements,
    list_quality_holds,
    list_quality_deviation_requests,
    list_quality_nonconformances,
    list_quality_gate_definitions_service,
    open_quality_gate_instance_service,
    record_quality_disposition,
    submit_qc_measurement,
    request_quality_deviation,
    resolve_quality_deviation,
    create_quality_nonconformance,
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


@router.get(
    "/quality/gates/definitions",
    response_model=list[QualityGateDefinitionResponse],
)
def list_quality_gate_definitions_endpoint(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    return list_quality_gate_definitions_service(
        db,
        tenant_id=identity.tenant_id,
    )


@router.post(
    "/quality/gates/definitions",
    response_model=QualityGateDefinitionResponse,
    status_code=201,
)
def create_quality_gate_definition_endpoint(
    payload: QualityGateDefinitionCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("APPROVE")),
):
    try:
        return create_quality_gate_definition_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except ValueError as exc:
        if str(exc) == "Duplicate quality gate code in tenant":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/quality/gates/instances/open",
    response_model=QualityGateInstanceResponse,
    status_code=201,
)
def open_quality_gate_instance_endpoint(
    payload: QualityGateInstanceOpenRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("APPROVE")),
):
    try:
        return open_quality_gate_instance_service(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except QualityConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


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
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
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


@router.get("/quality/deviations", response_model=list[QualityDeviationRequestItem])
def list_quality_deviations_endpoint(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    return list_quality_deviation_requests(db, tenant_id=identity.tenant_id)


@router.post(
    "/quality/holds/{hold_id}/deviations",
    response_model=QualityDeviationRequestItem,
    status_code=201,
)
def request_quality_deviation_endpoint(
    hold_id: int,
    payload: QualityDeviationRequestCreate,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        return request_quality_deviation(
            db,
            hold_id=hold_id,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except QualityConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/quality/deviations/{deviation_request_id}/resolve",
    response_model=QualityDeviationRequestItem,
)
def resolve_quality_deviation_endpoint(
    deviation_request_id: int,
    payload: QualityDeviationResolveRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_permission("APPROVE")),
):
    effective_role = identity.acting_role_code or identity.role_code
    try:
        return resolve_quality_deviation(
            db,
            deviation_request_id=deviation_request_id,
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


@router.get("/quality/nonconformances", response_model=list[QualityNonconformanceItem])
def list_quality_nonconformances_endpoint(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    return list_quality_nonconformances(db, tenant_id=identity.tenant_id)


@router.post(
    "/quality/nonconformances",
    response_model=QualityNonconformanceItem,
    status_code=201,
)
def create_quality_nonconformance_endpoint(
    payload: QualityNonconformanceCreateRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        return create_quality_nonconformance(
            db,
            tenant_id=identity.tenant_id,
            actor_user_id=identity.user_id,
            payload=payload,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except QualityConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        if str(exc) == "Duplicate nonconformance code in tenant":
            raise HTTPException(status_code=409, detail=str(exc))
        raise HTTPException(status_code=400, detail=str(exc))


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
