import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.master import Operation, StatusEnum
from app.models.execution import DowntimeReasonClass
from app.schemas.operation import OperationStartDowntimeRequest

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

@pytest.fixture
def seeded_operation():
    db = SessionLocal()
    op = Operation(
        operation_number="T100",
        name="Test Operation",
        status=StatusEnum.in_progress.value,
        tenant_id="default",
        work_order_id=1,
        work_center="A1",
        production_order_id=1,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    yield op
    db.delete(op)
    db.commit()
    db.close()

@pytest.mark.parametrize("role_code,action_codes,expected_status", [
    ("OPR", ["execution.start_downtime"], 200),
    ("OPR", [], 403),
    ("SUP", ["execution.start_downtime"], 200),
    ("QCI", ["execution.start_downtime"], 403),
    ("OPR", ["execution.pause"], 403),
])
def test_start_downtime_auth(seeded_operation, role_code, action_codes, expected_status):
    op = seeded_operation
    payload = {
        "reason_class": DowntimeReasonClass.PLANNED_MAINTENANCE,
        "note": "Routine check"
    }
    headers = make_auth_headers(role_code, action_codes)
    url = f"/operations/{op.id}/start-downtime"
    response = client.post(url, json=payload, headers=headers)
    assert response.status_code == expected_status
    if expected_status == 403:
        assert "Missing required action" in response.text or "permission" in response.text
    if expected_status == 200:
        assert response.json()["id"] == op.id
