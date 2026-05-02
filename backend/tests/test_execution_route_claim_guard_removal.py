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
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.station_session import StationSession
from app.security.dependencies import RequestIdentity

_PREFIX = "TEST-P0C08H4"
_TENANT_ID = "default"
_ACTOR = f"{_PREFIX}-ACTOR"
_OTHER_ACTOR = f"{_PREFIX}-OTHER"
_REASON_CODE = "MATERIAL_SHORTAGE"

client = TestClient(app)

_ROUTE_ACTIONS: dict[str, str] = {
    "/api/v1/operations/{operation_id}/start": "execution.start",
    "/api/v1/operations/{operation_id}/pause": "execution.pause",
    "/api/v1/operations/{operation_id}/resume": "execution.resume",
    "/api/v1/operations/{operation_id}/report-quantity": "execution.report_quantity",
    "/api/v1/operations/{operation_id}/start-downtime": "execution.start_downtime",
    "/api/v1/operations/{operation_id}/end-downtime": "execution.end_downtime",
    "/api/v1/operations/{operation_id}/complete": "execution.complete",
    "/api/v1/operations/{operation_id}/close": "execution.close",
    "/api/v1/operations/{operation_id}/reopen": "execution.reopen",
}


@pytest.fixture(autouse=True)
def override_operation_auth_dependencies():
    def _build_override(required_action: str):
        def _override(request: Request) -> RequestIdentity:
            role_code = (request.headers.get("X-Role-Code") or "OPR").strip().upper()
            user_id = (request.headers.get("X-User-Id") or _ACTOR).strip()
            tenant_id = (request.headers.get("X-Tenant-Id") or _TENANT_ID).strip()
            raw_actions = request.headers.get("X-Action-Codes") or ""
            action_codes = {code.strip() for code in raw_actions.split(",") if code.strip()}

            if required_action not in action_codes:
                raise HTTPException(
                    status_code=403,
                    detail=f"Missing required action: {required_action}",
                )

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

        return _override

    overridden_deps: list[Any] = []
    for path, required_action in _ROUTE_ACTIONS.items():
        route = cast(
            Any,
            next(route for route in app.routes if getattr(route, "path", "") == path),
        )
        dep_call = next(
            dep.call
            for dep in route.dependant.dependencies
            if getattr(dep.call, "__name__", "") == "dependency"
        )
        app.dependency_overrides[dep_call] = _build_override(required_action)
        overridden_deps.append(dep_call)

    try:
        yield
    finally:
        for dep_call in overridden_deps:
            app.dependency_overrides.pop(dep_call, None)


def _headers(*, action: str, user_id: str = _ACTOR, role_code: str = "OPR") -> dict[str, str]:
    return {
        "Authorization": f"Bearer test-token-for-{role_code}",
        "X-Role-Code": role_code,
        "X-User-Id": user_id,
        "X-Action-Codes": action,
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
            db.scalars(select(WorkOrder.id).where(WorkOrder.production_order_id.in_(po_ids)))
        )
        if wo_ids:
            op_ids = list(db.scalars(select(Operation.id).where(Operation.work_order_id.in_(wo_ids))))
            if op_ids:
                db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id.in_(op_ids)))
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
        product_name="p0c08h4",
        quantity=10,
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 11, 1, 8, 0, 0),
        planned_end=datetime(2099, 11, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"{_PREFIX}-WO-{suffix}",
        status=StatusEnum.planned.value,
        planned_start=datetime(2099, 11, 1, 8, 0, 0),
        planned_end=datetime(2099, 11, 1, 17, 0, 0),
        tenant_id=_TENANT_ID,
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"{_PREFIX}-OP-{suffix}",
        name="p0c08h4-op",
        sequence=10,
        work_order_id=wo.id,
        tenant_id=_TENANT_ID,
        status=status,
        closure_status=closure_status,
        station_scope_value=station_scope_value,
        quantity=10,
    )
    db.add(op)
    db.flush()
    return op


def _add_runtime_events(db, operation: Operation, status: str) -> None:
    work_order = db.get(WorkOrder, operation.work_order_id)
    assert work_order is not None

    if status in {
        StatusEnum.in_progress.value,
        StatusEnum.paused.value,
        StatusEnum.blocked.value,
        StatusEnum.completed.value,
    }:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=work_order.production_order_id,
                work_order_id=work_order.id,
                operation_id=operation.id,
                payload={"operator_id": _ACTOR},
                tenant_id=_TENANT_ID,
            )
        )

    if status == StatusEnum.paused.value:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.EXECUTION_PAUSED.value,
                production_order_id=work_order.production_order_id,
                work_order_id=work_order.id,
                operation_id=operation.id,
                payload={"paused_at": datetime(2099, 11, 1, 9, 10, 0).isoformat()},
                tenant_id=_TENANT_ID,
            )
        )

    if status == StatusEnum.blocked.value:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.DOWNTIME_STARTED.value,
                production_order_id=work_order.production_order_id,
                work_order_id=work_order.id,
                operation_id=operation.id,
                payload={"reason_code": _REASON_CODE},
                tenant_id=_TENANT_ID,
            )
        )

    if status == StatusEnum.completed.value:
        db.add(
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=work_order.production_order_id,
                work_order_id=work_order.id,
                operation_id=operation.id,
                payload={"operator_id": _ACTOR},
                tenant_id=_TENANT_ID,
            )
        )

    db.commit()


def _insert_open_session(db, *, station_id: str, operator_user_id: str) -> None:
    db.add(
        StationSession(
            session_id=uuid4().hex,
            tenant_id=_TENANT_ID,
            station_id=station_id,
            operator_user_id=operator_user_id,
            status="OPEN",
            opened_at=datetime.now(timezone.utc),
            closed_at=None,
        )
    )
    db.commit()


def _event_count(db, operation_id: int) -> int:
    return len(
        list(db.scalars(select(ExecutionEvent.id).where(ExecutionEvent.operation_id == operation_id)))
    )


def _latest_event_type(db, operation_id: int) -> str | None:
    return db.scalar(
        select(ExecutionEvent.event_type)
        .where(ExecutionEvent.operation_id == operation_id)
        .order_by(ExecutionEvent.id.desc())
        .limit(1)
    )


@pytest.mark.parametrize(
    ("name", "path_suffix", "action", "seed_status", "payload", "expected_event"),
    [
        (
            "start_operation",
            "start",
            "execution.start",
            StatusEnum.planned.value,
            {"operator_id": _ACTOR},
            ExecutionEventType.OP_STARTED.value,
        ),
        (
            "pause_operation",
            "pause",
            "execution.pause",
            StatusEnum.in_progress.value,
            {"reason_code": "BREAK", "note": "pause"},
            ExecutionEventType.EXECUTION_PAUSED.value,
        ),
        (
            "resume_operation",
            "resume",
            "execution.resume",
            StatusEnum.paused.value,
            {"note": "resume"},
            ExecutionEventType.EXECUTION_RESUMED.value,
        ),
        (
            "report_quantity",
            "report-quantity",
            "execution.report_quantity",
            StatusEnum.in_progress.value,
            {"good_qty": 2, "scrap_qty": 0, "operator_id": _ACTOR},
            ExecutionEventType.QTY_REPORTED.value,
        ),
        (
            "start_downtime",
            "start-downtime",
            "execution.start_downtime",
            StatusEnum.in_progress.value,
            {"reason_code": _REASON_CODE, "note": "start dt"},
            ExecutionEventType.DOWNTIME_STARTED.value,
        ),
        (
            "end_downtime",
            "end-downtime",
            "execution.end_downtime",
            StatusEnum.blocked.value,
            {"note": "end dt"},
            ExecutionEventType.DOWNTIME_ENDED.value,
        ),
        (
            "complete_operation",
            "complete",
            "execution.complete",
            StatusEnum.in_progress.value,
            {"operator_id": _ACTOR},
            ExecutionEventType.OP_COMPLETED.value,
        ),
    ],
)
def test_valid_station_session_without_claim_succeeds_for_h4_commands(
    db_session,
    name,
    path_suffix,
    action,
    seed_status,
    payload,
    expected_event,
):
    station_id = f"{_PREFIX}-{name}-ST"
    operation = _seed_operation(
        db_session,
        suffix=f"SUCCESS-{name}",
        status=seed_status,
        station_scope_value=station_id,
    )
    _add_runtime_events(db_session, operation, seed_status)
    _insert_open_session(db_session, station_id=station_id, operator_user_id=_ACTOR)

    before_count = _event_count(db_session, operation.id)

    response = client.post(
        f"/api/v1/operations/{operation.id}/{path_suffix}",
        json=payload,
        headers=_headers(action=action),
    )

    assert response.status_code == 200
    assert response.json()["id"] == operation.id
    assert _event_count(db_session, operation.id) == before_count + 1
    assert _latest_event_type(db_session, operation.id) == expected_event


def test_missing_station_session_rejects_start_even_without_claim(db_session):
    station_id = f"{_PREFIX}-BYPASS-ST"
    operation = _seed_operation(
        db_session,
        suffix="MISSING-SESSION-WITH-CLAIM",
        status=StatusEnum.planned.value,
        station_scope_value=station_id,
    )
    db_session.commit()

    before_count = _event_count(db_session, operation.id)
    response = client.post(
        f"/api/v1/operations/{operation.id}/start",
        json={"operator_id": _ACTOR},
        headers=_headers(action="execution.start"),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "STATION_SESSION_REQUIRED"
    assert _event_count(db_session, operation.id) == before_count


def test_invalid_state_guard_still_works_after_station_session_passes(db_session):
    station_id = f"{_PREFIX}-INVALID-STATE-ST"
    operation = _seed_operation(
        db_session,
        suffix="INVALID-STATE",
        status=StatusEnum.in_progress.value,
        station_scope_value=station_id,
    )
    _add_runtime_events(db_session, operation, StatusEnum.in_progress.value)
    _insert_open_session(db_session, station_id=station_id, operator_user_id=_ACTOR)

    response = client.post(
        f"/api/v1/operations/{operation.id}/start",
        json={"operator_id": _ACTOR},
        headers=_headers(action="execution.start"),
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert "Operation must be PLANNED to start." in detail
    assert "Operation must be claimed by you before execution actions." not in detail


def test_failed_station_session_guard_emits_no_command_event(db_session):
    station_id = f"{_PREFIX}-NO-SESSION-ST"
    operation = _seed_operation(
        db_session,
        suffix="NO-SESSION-EVENT",
        status=StatusEnum.in_progress.value,
        station_scope_value=station_id,
    )
    _add_runtime_events(db_session, operation, StatusEnum.in_progress.value)

    before_count = _event_count(db_session, operation.id)

    response = client.post(
        f"/api/v1/operations/{operation.id}/report-quantity",
        json={"good_qty": 1, "scrap_qty": 0, "operator_id": _ACTOR},
        headers=_headers(action="execution.report_quantity"),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "STATION_SESSION_REQUIRED"
    assert _event_count(db_session, operation.id) == before_count


def test_close_and_reopen_routes_remain_unchanged(db_session):
    station_id = f"{_PREFIX}-CLOSE-REOPEN-ST"
    operation = _seed_operation(
        db_session,
        suffix="CLOSE-REOPEN",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.open.value,
        station_scope_value=station_id,
    )
    _add_runtime_events(db_session, operation, StatusEnum.completed.value)

    non_sup_close = client.post(
        f"/api/v1/operations/{operation.id}/close",
        json={"note": "close attempt"},
        headers=_headers(action="execution.close", role_code="OPR"),
    )
    assert non_sup_close.status_code == 403
    assert "Missing required role for close_operation: SUP" in non_sup_close.json()["detail"]

    sup_close = client.post(
        f"/api/v1/operations/{operation.id}/close",
        json={"note": "close as sup"},
        headers=_headers(action="execution.close", role_code="SUP", user_id="sup-1"),
    )
    assert sup_close.status_code == 200
    assert sup_close.json()["closure_status"] == "CLOSED"

    sup_reopen = client.post(
        f"/api/v1/operations/{operation.id}/reopen",
        json={"reason": "validation"},
        headers=_headers(action="execution.reopen", role_code="SUP", user_id="sup-1"),
    )
    assert sup_reopen.status_code == 200
    assert sup_reopen.json()["closure_status"] == "OPEN"
