from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.operation import OperationDetail
from app.schemas.station import (
    StationQueueItem,
    StationQueueResponse,
)
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.operation_service import derive_operation_detail
from app.services.station_queue_service import (
    get_station_scoped_operation,
    get_station_queue,
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
