from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.station_session import (
    BindEquipmentRequest,
    IdentifyOperatorRequest,
    OpenStationSessionRequest,
    StationSessionCurrentResponse,
    StationSessionItem,
)
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.station_session_service import (
    StationSessionConflictError,
    bind_equipment_to_station_session,
    close_station_session,
    get_current_station_session,
    identify_operator_at_station,
    open_station_session,
)

router = APIRouter(prefix="/station/sessions", tags=["station-sessions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=StationSessionItem)
def create_station_session(
    payload: OpenStationSessionRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> StationSessionItem:
    try:
        return StationSessionItem.model_validate(
            open_station_session(
                db,
                identity,
                station_id=payload.station_id,
                payload=payload,
            )
        )
    except StationSessionConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/current", response_model=StationSessionCurrentResponse)
def read_current_station_session(
    station_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> StationSessionCurrentResponse:
    try:
        row = get_current_station_session(
            db,
            identity,
            station_id=station_id,
        )
        if row is None:
            return StationSessionCurrentResponse(session=None)
        return StationSessionCurrentResponse(
            session=StationSessionItem.model_validate(row)
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{session_id}/identify-operator", response_model=StationSessionItem)
def identify_station_session_operator(
    session_id: str,
    payload: IdentifyOperatorRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> StationSessionItem:
    try:
        return StationSessionItem.model_validate(
            identify_operator_at_station(
                db,
                identity,
                session_id=session_id,
                operator_user_id=payload.operator_user_id,
            )
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{session_id}/bind-equipment", response_model=StationSessionItem)
def bind_station_session_equipment(
    session_id: str,
    payload: BindEquipmentRequest,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> StationSessionItem:
    try:
        return StationSessionItem.model_validate(
            bind_equipment_to_station_session(
                db,
                identity,
                session_id=session_id,
                equipment_id=payload.equipment_id,
            )
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{session_id}/close", response_model=StationSessionItem)
def close_station_session_route(
    session_id: str,
    db: Session = Depends(get_db),
    identity: RequestIdentity = Depends(require_authenticated_identity),
) -> StationSessionItem:
    try:
        return StationSessionItem.model_validate(
            close_station_session(db, identity, session_id=session_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
