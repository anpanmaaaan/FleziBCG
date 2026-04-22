from datetime import datetime, timezone
from typing import Any, cast
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.main import app
from app.models.execution import ExecutionEvent, ExecutionEventType
from app.models.master import ClosureStatusEnum, Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.rbac import Scope
from app.security.dependencies import RequestIdentity

client = TestClient(app)


def make_auth_headers(role_code: str = "SUP", action_codes: list[str] | None = None):
    headers = {
        "Authorization": f"Bearer test-token-for-{role_code}",
        "X-Role-Code": role_code,
    }
    if action_codes:
        headers["X-Action-Codes"] = ",".join(action_codes)
    return headers


@pytest.fixture(autouse=True)
def override_close_auth_dependency():
    close_route = cast(
        Any,
        next(
            route
            for route in app.routes
            if getattr(route, "path", "") == "/api/v1/operations/{operation_id}/close"
        ),
    )
    require_action_dependency = next(
        dep.call
        for dep in close_route.dependant.dependencies
        if getattr(dep.call, "__name__", "") == "dependency"
    )

    def _override(request: Request) -> RequestIdentity:
        role_code = (request.headers.get("X-Role-Code") or "").strip().upper()
        raw_actions = request.headers.get("X-Action-Codes") or ""
        action_codes = {code.strip() for code in raw_actions.split(",") if code.strip()}

        if "execution.close" not in action_codes:
            raise HTTPException(
                status_code=403,
                detail="Missing required action: execution.close",
            )

        if role_code not in {"OPR", "SUP", "QCI", "QAL"}:
            raise HTTPException(status_code=403, detail="Missing required permission")

        return RequestIdentity(
            user_id="test-user",
            username="test-user",
            email=None,
            tenant_id="default",
            role_code=role_code,
            is_authenticated=True,
            session_id="test-session",
        )

    app.dependency_overrides[require_action_dependency] = _override
    try:
        yield
    finally:
        app.dependency_overrides.pop(require_action_dependency, None)


@pytest.fixture
def seeded_completed_operation():
    db = SessionLocal()
    unique = uuid4().hex[:8].upper()

    scope = Scope(
        tenant_id="default",
        scope_type="station",
        scope_value=f"TEST-CLOSE-AUTH-{unique}",
    )
    db.add(scope)
    db.flush()

    po = ProductionOrder(
        order_number=f"TEST-CLOSE-AUTH-PO-{unique}",
        route_id=f"R-{unique}",
        product_name="Close Auth Test",
        quantity=1,
        status=StatusEnum.planned.value,
        tenant_id="default",
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"TEST-CLOSE-AUTH-WO-{unique}",
        status=StatusEnum.completed.value,
        tenant_id="default",
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"TEST-CLOSE-AUTH-OP-{unique}",
        name="Close Auth Operation",
        status=StatusEnum.completed.value,
        closure_status=ClosureStatusEnum.open.value,
        tenant_id="default",
        work_order_id=wo.id,
        sequence=1,
        station_scope_value=scope.scope_value,
    )
    db.add(op)
    db.flush()

    db.add_all(
        [
            ExecutionEvent(
                event_type=ExecutionEventType.OP_STARTED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"started_at": datetime(2099, 9, 1, 9, 0, 0).isoformat()},
                tenant_id="default",
            ),
            ExecutionEvent(
                event_type=ExecutionEventType.OP_COMPLETED.value,
                production_order_id=po.id,
                work_order_id=wo.id,
                operation_id=op.id,
                payload={"completed_at": datetime(2099, 9, 1, 9, 30, 0).isoformat()},
                tenant_id="default",
            ),
        ]
    )
    db.commit()
    db.refresh(op)

    try:
        yield op
    finally:
        db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id == op.id))
        db.execute(delete(Operation).where(Operation.id == op.id))
        db.execute(delete(WorkOrder).where(WorkOrder.id == wo.id))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id == po.id))
        db.execute(delete(Scope).where(Scope.id == scope.id))
        db.commit()
        db.close()


@pytest.mark.parametrize(
    "role_code,action_codes,expected_status,expected_detail_substring",
    [
        ("SUP", ["execution.close"], 200, None),
        ("OPR", ["execution.close"], 403, "Missing required role for close_operation: SUP"),
        ("SUP", [], 403, "Missing required action: execution.close"),
        ("QCI", ["execution.close"], 403, "Missing required role for close_operation: SUP"),
    ],
)
def test_close_operation_authorization(
    seeded_completed_operation,
    role_code,
    action_codes,
    expected_status,
    expected_detail_substring,
):
    op = seeded_completed_operation
    response = client.post(
        f"/api/v1/operations/{op.id}/close",
        json={"note": "close auth test"},
        headers=make_auth_headers(role_code, action_codes),
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        payload = response.json()
        assert payload["id"] == op.id
        assert payload["closure_status"] == "CLOSED"
        assert payload["status"] == "COMPLETED"
        return

    detail = response.json().get("detail", "")
    assert expected_detail_substring is not None
    assert expected_detail_substring in detail

