import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException, Request
from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import uuid4
from sqlalchemy import delete

from app.main import app
from app.db.session import SessionLocal
from app.models.master import Operation, ProductionOrder, StatusEnum, WorkOrder
from app.models.execution import ExecutionEvent
from app.models.rbac import Scope
from app.models.station_claim import OperationClaim
from app.models.execution import DowntimeReasonClass
from app.security.dependencies import RequestIdentity

client = TestClient(app)


# Utility: create a user token with a given role and permissions (mock or fixture)
def make_auth_headers(role_code="OPR", action_codes=None):
    # This is a placeholder. In a real test, use your auth system or fixtures.
    # For now, simulate a JWT with role_code and action_codes in headers.
    headers = {
        "Authorization": f"Bearer test-token-for-{role_code}",
        "X-Role-Code": role_code,
    }
    if action_codes:
        headers["X-Action-Codes"] = ",".join(action_codes)
    return headers


@pytest.fixture(autouse=True)
def override_start_downtime_auth_dependency():
    start_downtime_route = cast(
        Any,
        next(
            route
            for route in app.routes
            if getattr(route, "path", "")
            == "/api/v1/operations/{operation_id}/start-downtime"
        ),
    )
    require_action_dependency = next(
        dep.call
        for dep in start_downtime_route.dependant.dependencies
        if getattr(dep.call, "__name__", "") == "dependency"
    )

    def _override(request: Request) -> RequestIdentity:
        role_code = (request.headers.get("X-Role-Code") or "").strip().upper()
        raw_actions = request.headers.get("X-Action-Codes") or ""
        action_codes = {code.strip() for code in raw_actions.split(",") if code.strip()}

        if "execution.start_downtime" not in action_codes:
            raise HTTPException(
                status_code=403,
                detail="Missing required action: execution.start_downtime",
            )

        if role_code not in {"OPR", "SUP"}:
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
def seeded_operation():
    db = SessionLocal()
    unique = uuid4().hex[:8].upper()
    scope = Scope(
        tenant_id="default",
        scope_type="station",
        scope_value=f"TEST-DT-AUTH-{unique}",
    )
    db.add(scope)
    db.flush()

    po = ProductionOrder(
        order_number=f"TEST-DT-AUTH-PO-{unique}",
        route_id=f"R-{unique}",
        product_name="Downtime Auth Test",
        quantity=1,
        status=StatusEnum.planned.value,
        tenant_id="default",
    )
    db.add(po)
    db.flush()

    wo = WorkOrder(
        production_order_id=po.id,
        work_order_number=f"TEST-DT-AUTH-WO-{unique}",
        status=StatusEnum.in_progress.value,
        tenant_id="default",
    )
    db.add(wo)
    db.flush()

    op = Operation(
        operation_number=f"TEST-DT-AUTH-OP-{unique}",
        name="Test Operation",
        status=StatusEnum.in_progress.value,
        tenant_id="default",
        work_order_id=wo.id,
        sequence=1,
        station_scope_value=scope.scope_value,
    )
    db.add(op)
    db.flush()

    now = datetime.now(timezone.utc)
    db.add(
        OperationClaim(
            tenant_id="default",
            operation_id=op.id,
            station_scope_id=scope.id,
            claimed_by_user_id="test-user",
            claimed_at=now,
            expires_at=now + timedelta(hours=1),
        )
    )
    db.commit()
    db.refresh(op)

    try:
        yield op
    finally:
        db.execute(delete(ExecutionEvent).where(ExecutionEvent.operation_id == op.id))
        db.execute(delete(OperationClaim).where(OperationClaim.operation_id == op.id))
        db.execute(delete(Operation).where(Operation.id == op.id))
        db.execute(delete(WorkOrder).where(WorkOrder.id == wo.id))
        db.execute(delete(ProductionOrder).where(ProductionOrder.id == po.id))
        db.execute(delete(Scope).where(Scope.id == scope.id))
        db.commit()
        db.close()


@pytest.mark.parametrize(
    "role_code,action_codes,expected_status",
    [
        ("OPR", ["execution.start_downtime"], 200),
        ("OPR", [], 403),
        ("SUP", ["execution.start_downtime"], 200),
        ("QCI", ["execution.start_downtime"], 403),
        ("OPR", ["execution.pause"], 403),
    ],
)
def test_start_downtime_auth(
    seeded_operation, role_code, action_codes, expected_status
):
    op = seeded_operation
    payload = {
        "reason_class": DowntimeReasonClass.PLANNED_MAINTENANCE.value,
        "note": "Routine check",
    }
    headers = make_auth_headers(role_code, action_codes)
    url = f"/api/v1/operations/{op.id}/start-downtime"
    response = client.post(url, json=payload, headers=headers)
    assert response.status_code == expected_status
    if expected_status == 403:
        assert (
            "Missing required action" in response.text or "permission" in response.text
        )
    if expected_status == 200:
        assert response.json()["id"] == op.id
