from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.station_session import StationSession


def get_station_session_by_id(
    db: Session,
    *,
    tenant_id: str,
    session_id: str,
) -> StationSession | None:
    return db.scalar(
        select(StationSession).where(
            StationSession.tenant_id == tenant_id,
            StationSession.session_id == session_id,
        )
    )


def get_active_station_session_for_station(
    db: Session,
    *,
    tenant_id: str,
    station_id: str,
    for_update: bool = False,
) -> StationSession | None:
    statement = select(StationSession).where(
        StationSession.tenant_id == tenant_id,
        StationSession.station_id == station_id,
        StationSession.status == "OPEN",
        StationSession.closed_at.is_(None),
    )
    if for_update:
        statement = statement.with_for_update()
    return db.scalar(statement)


def create_station_session(db: Session, *, row: StationSession) -> StationSession:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_station_session(db: Session, *, row: StationSession) -> StationSession:
    db.commit()
    db.refresh(row)
    return row
