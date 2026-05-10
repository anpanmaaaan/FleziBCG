from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import (
    ClosureStatusEnum,
    Operation,
    ProductionOrder,
    StatusEnum,
    WorkOrder,
)
from app.models.station_session import StationSession
from app.security.dependencies import RequestIdentity

_PREFIX = "TEST-ABORT-API-01"
_TENANT_ID = "default"
_ACTOR = f"{_PREFIX}-ACTOR"
_OTHER_ACTOR = f"{_PREFIX}-OTHER"
_REASON_CODE = "ABORT"

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_abort_auth_dependency():
    abort_route = cast(
        Any,
        next(
            route
            for route in app.routes
            if getattr(route, "path", "") == "/api/v1/operations/{operation_id}/abort"
        ),
    )
    require_permission_dependency = next(
        dep.call
        for dep in abort_route.dependant.dependencies
        if getattr(dep.call, "__name__", "") == "dependency"
    )

    def _override(request: Request) -> RequestIdentity:
        role_code = (request.headers.get("X-Role-Code") or "OPR").strip().upper()
        user_id = (request.headers.get("X-User-Id") or _ACTOR).strip()
        tenant_id = (request.headers.get("X-Tenant-Id") or _TENANT_ID).strip()

        if role_code not in {"OPR", "SUP", "QCI", "QAL"}:
            raise HTTPException(status_code=403, detail="Missing required permission")

        return RequestIdentity(
            user_id=user_id,
            username=user_id,
            email=None,
            tenant_id=tenant_id,
            role_code=role_code,
            acting_role_code=None,
            is_authenticated=True,
            session_id=f"{_PREFIX}-SESSION",
        )

    app.dependency_overrides[require_permission_dependency] = _override
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_permission_dependency, None)


def _headers(*, user_id: str = _ACTOR, role_code: str = "OPR") -> dict[str, str]:
    return {
        "Authorization": f"Bearer test-token-for-{role_code}",
        "X-Role-Code": role_code,
        "X-User-Id": user_id,
    }


def _purge(db) -> None:
    po_ids = list(
        db.scalars(
            select(ProductionOrder.id).where(
                ProductionOrder.order_number.like(f"{_PREFIX}-%")
            )
        )
    )
    if po_ids:
        wo_ids = list(
            db.scalars(
                select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids))
            )
        )
        if wo_ids:
            op_ids = list(
                db.scalars(
                    select(Operation.id).where(Operation.work_order_id.in_(wo_ids))
                )
            )
            if op_ids:
                db.execute(
                    delete(ExecutionEvent).where(
                        ExecutionEvent.operation_id.in_(op_ids)
                    )
                )
                db.execute(delete(Operation).where(Operation.id.in_(op_ids)))
            db.execute(delete(WorkOrder).where(WorkOrder.id.in_(wo_ids)))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id.in_(po_ids)))

    db.execute(
        delete(StationSession).where(
            StationSession.tenant_id == _TENANT_ID,
            StationSession.station_id.like(f"{_PREFIX}-%"),
        )
    )
    db.commit()


@pytest.fixture
def db_session():
    init_db()
    db = SessionLocal()
    try:
        _purge(db)
        yield db
    finally:
        _purge(db)
        db.close()


def _seed_operation(
    db,
    *,
    suffix: str,
    status: str,
    closure_status: str = ClosureStatusEnum.open.value,
    station_scope_value: str,
) -> Operation:
    po = ProductionOrder(
        order_number=f"{_PREFIX}-PO-{suffix}",
        route_id=f"{_PREFIX}-R-{suffix}",
        product_name="abort-api",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 12, 1, 8, 0, 0),
        planned_end=datetime(2099, 12, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 12, 1, 8, 0, 0),
        planned_end=datetime(2099, 12, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    operation = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="abort-api-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        status=status,
        closure_status=closure_status,
        station_scope_value=station_scope_value,
        quantity=10,
    )
    db.add(operation)
    db.flush()

    if status in {StatusEnum.in_progress.value, StatusEnum.paused.value}:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=operation.id,
                payload={"operator_id": _ACTOR},
                tenant_id=_TENANT_ID,
            )
        )

    db.commit()
    db.refresh(operation)
    return operation


def _insert_session(
    db,
    *,
    station_id: str,
    operator_user_id: str,
    status: str = "OPEN",
    closed: bool = False,
) -> None:
    db.add(
        StationSession(
            session_id=uuid4().hex,
            tenant_id=_TENANT_ID,
            station_id=station_id,
            operator_user_id=operator_user_id,
            status=status,
            opened_at=datetime.now(timezone.utc),
            closed_at=datetime.now(timezone.utc) if closed else None,
        )
    )
    db.commit()


def _event_count(db, operation_id: int) -> int:
    return len(
        list(
            db.scalars(
                select(ExecutionEvent.id).where(
                    ExecutionEvent.operation_id == operation_id
                )
            )
        )
    )


def _latest_event_type(db, operation_id: int) -> str | None:
    return db.scalar(
        select(ExecutionEvent.event_type)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )


def test_abort_api_01_missing_station_session_rejected_and_no_abort_event(db_session):
    station_id = f"{_PREFIX}-NO-SESSION"
    operation = _seed_operation(
        db_session,
        suffix="NO-SESSION",
        status=StatusEnum.in_progress.value,
        station_scope_value=station_id,
    )

    before_count = _event_count(db_session, operation.id)

    response = client.post(
        f"/api/v1/operations/{operation.id}/abort",
        json={"operator_id": _ACTOR, "reason_code": _REASON_CODE},
        headers=_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "STATION_SESSION_REQUIRED"
    assert _event_count(db_session, operation.id) == before_count


def test_abort_api_02_operator_mismatch_rejected_and_no_abort_event(db_session):
    station_id = f"{_PREFIX}-OP-MISMATCH"
    operation = _seed_operation(
        db_session,
        suffix="OP-MISMATCH",
        status=StatusEnum.in_progress.value,
        station_scope_value=station_id,
    )
    _insert_session(db_session, station_id=station_id, operator_user_id=_OTHER_ACTOR)

    before_count = _event_count(db_session, operation.id)

    response = client.post(
        f"/api/v1/operations/{operation.id}/abort",
        json={"operator_id": _ACTOR, "reason_code": _REASON_CODE},
        headers=_headers(),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "STATION_SESSION_OPERATOR_MISMATCH"
    assert _event_count(db_session, operation.id) == before_count


def test_abort_api_03_closed_station_session_rejected_and_no_abort_event(db_session):
    station_id = f"{_PREFIX}-CLOSED-SESSION"
    operation = _seed_operation(
        db_session,
        suffix="CLOSED-SESSION",
        status=StatusEnum.in_progress.value,
        station_scope_value=station_id,
    )
    _insert_session(
        db_session,
        station_id=station_id,
        operator_user_id=_ACTOR,
        status="CLOSED",
        closed=True,
    )

    before_count = _event_count(db_session, operation.id)

    response = client.post(
        f"/api/v1/operations/{operation.id}/abort",
        json={"operator_id": _ACTOR, "reason_code": _REASON_CODE},
        headers=_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "STATION_SESSION_CLOSED"
    assert _event_count(db_session, operation.id) == before_count


def test_abort_api_04_valid_station_session_succeeds_and_appends_abort_event(
    db_session,
):
    station_id = f"{_PREFIX}-SUCCESS"
    operation = _seed_operation(
        db_session,
        suffix="SUCCESS",
        status=StatusEnum.in_progress.value,
        station_scope_value=station_id,
    )
    _insert_session(db_session, station_id=station_id, operator_user_id=_ACTOR)

    before_count = _event_count(db_session, operation.id)

    response = client.post(
        f"/api/v1/operations/{operation.id}/abort",
        json={"operator_id": _ACTOR, "reason_code": _REASON_CODE},
        headers=_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == operation.id
    assert payload["status"] == StatusEnum.aborted.value
    assert _event_count(db_session, operation.id) == before_count + 1
    assert (
        _latest_event_type(db_session, operation.id)
        == ExecutionEventType.OP_ABORTED.value
    )


def test_abort_api_05_closed_record_still_blocked_and_no_abort_event(db_session):
    station_id = f"{_PREFIX}-CLOSED-RECORD"
    operation = _seed_operation(
        db_session,
        suffix="CLOSED-RECORD",
        status=StatusEnum.in_progress.value,
        closure_status=ClosureStatusEnum.closed.value,
        station_scope_value=station_id,
    )
    _insert_session(db_session, station_id=station_id, operator_user_id=_ACTOR)

    before_count = _event_count(db_session, operation.id)

    response = client.post(
        f"/api/v1/operations/{operation.id}/abort",
        json={"operator_id": _ACTOR, "reason_code": _REASON_CODE},
        headers=_headers(),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "STATE_CLOSED_RECORD"
    assert _event_count(db_session, operation.id) == before_count
