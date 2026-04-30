"""
P0-C-04C: Diagnostic Session Context Bridge.

A non-blocking, read-only helper that detects whether an OPEN StationSession
exists for a given tenant/station context.

Contract:
- Returns a structured context object; never raises, never rejects a command.
- Missing session == NO_ACTIVE_SESSION readiness signal only.
- Callers decide what to do with the result — execution commands do NOT use
  this helper as a guard in P0-C-04C (that is P0-C-04D scope).
- Tenant isolation is mandatory: every lookup filters by tenant_id.
- Station context is derived from verified server-side data (operation.station_scope_value
  or caller-supplied station_id), never from raw user input.

Design authority: docs/design/02_domain/execution/station-session-ownership-contract.md
Slice: P0-C-04C (Diagnostic Session Context Bridge)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.station_session_repository import (
    get_active_station_session_for_station,
)


class SessionReadiness(str, Enum):
    OPEN = "OPEN"
    NO_ACTIVE_SESSION = "NO_ACTIVE_SESSION"


@dataclass(frozen=True)
class StationSessionDiagnostic:
    """
    Read-only context snapshot for a tenant/station pair.

    Attributes:
        readiness: OPEN if an active StationSession was found, otherwise
                   NO_ACTIVE_SESSION.
        session_id: UUID of the active session, or None.
        operator_user_id: Identified operator at the session, or None if
                          session is absent or operator not yet identified.
    """

    readiness: SessionReadiness
    session_id: Optional[str]
    operator_user_id: Optional[str]


_DIAGNOSTIC_NO_SESSION = StationSessionDiagnostic(
    readiness=SessionReadiness.NO_ACTIVE_SESSION,
    session_id=None,
    operator_user_id=None,
)


def get_station_session_diagnostic(
    db: Session,
    *,
    tenant_id: str,
    station_id: str,
) -> StationSessionDiagnostic:
    """
    Return diagnostic context for the current station session state.

    Never raises. Missing or closed session is represented by
    SessionReadiness.NO_ACTIVE_SESSION.

    Args:
        db: Active SQLAlchemy session.
        tenant_id: Tenant scope. Must be verified by caller.
        station_id: Station identifier (station_scope_value).

    Returns:
        StationSessionDiagnostic — always returns an instance, never None.
    """
    session = get_active_station_session_for_station(
        db, tenant_id=tenant_id, station_id=station_id
    )
    if session is None:
        return _DIAGNOSTIC_NO_SESSION

    return StationSessionDiagnostic(
        readiness=SessionReadiness.OPEN,
        session_id=str(session.session_id),
        operator_user_id=session.operator_user_id,
    )
