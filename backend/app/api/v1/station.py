from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.operation import OperationDetail
from app.schemas.station import ClaimRequest, ClaimResponse, ReleaseClaimRequest, StationQueueItem, StationQueueResponse
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.operation_service import derive_operation_detail
from app.services.station_claim_service import (
    ClaimConflictError,
    claim_operation,
    get_station_scoped_operation,
    get_operation_claim_status,
    get_station_queue,
    release_operation_claim,
)

router = APIRouter(prefix="/station", tags=["station"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/queue", response_model=StationQueueResponse)
def read_station_queue(
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        station_scope_value, items = get_station_queue(db, identity)
        return StationQueueResponse(
            items=[StationQueueItem.model_validate(item) for item in items],
            station_scope_value=station_scope_value,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/queue/{operation_id}/claim", response_model=ClaimResponse)
def claim_station_operation(
    operation_id: int,
    request: ClaimRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        claim, station_scope_value = claim_operation(
            db,
            identity,
            operation_id,
            reason=request.reason,
            duration_minutes=request.duration_minutes,
        )
        return ClaimResponse(
            operation_id=claim.operation_id,
            station_scope_value=station_scope_value,
            claimed_by_user_id=claim.claimed_by_user_id,
            claimed_at=claim.claimed_at,
            expires_at=claim.expires_at,
            state="mine" if claim.claimed_by_user_id == identity.user_id else "other",
        )
    except ClaimConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/queue/{operation_id}/release", response_model=ClaimResponse)
def release_station_operation(
    operation_id: int,
    request: ReleaseClaimRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        claim, station_scope_value = release_operation_claim(
            db,
            identity,
            operation_id,
            reason=request.reason,
        )
        return ClaimResponse(
            operation_id=claim.operation_id,
            station_scope_value=station_scope_value,
            claimed_by_user_id=claim.claimed_by_user_id,
            claimed_at=claim.claimed_at,
            expires_at=claim.expires_at,
            state="none",
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/queue/{operation_id}/claim")
def get_station_claim_status(
    operation_id: int,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        return get_operation_claim_status(db, identity, operation_id)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/queue/{operation_id}/detail", response_model=OperationDetail)
def get_station_operation_detail(
    operation_id: int,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
):
    try:
        operation = get_station_scoped_operation(db, identity, operation_id)
        return derive_operation_detail(db, operation)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
