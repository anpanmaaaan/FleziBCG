"""
Covers GET /api/v1/downtime-reasons.

Scope:
- returns active reasons for the authenticated tenant
- excludes inactive rows
- deterministic ordering by (sort_order, reason_code)
- response shape matches the DowntimeReasonItem contract
- tenant isolation (rows for a different tenant are not returned)
- auth: authenticated access is enforced
"""

from __future__ import annotations

from typing import Any, cast
from uuid import uuid4

import pytest
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.main import app
from app.models.downtime_reason import DowntimeReason
from app.security.dependencies import RequestIdentity


_PREFIX = "TEST-DT-EP"
client = TestClient(app)


def _purge(db) -> None:
    db.execute(
        delete(DowntimeReason).where(
            DowntimeReason.reason_code.like(f"{_PREFIX}-%"),
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
        db.rollback()
        _purge(db)
        db.close()


def _seed(db, **fields) -> DowntimeReason:
    defaults = dict(
        tenant_id="default",
        reason_name="test reason",
        reason_group="OTHER",
        planned_flag=False,
        default_block_mode="BLOCK",
        requires_comment=False,
        requires_supervisor_review=False,
        active_flag=True,
        sort_order=0,
    )
    defaults.update(fields)
    row = DowntimeReason(**defaults)
    db.add(row)
    db.flush()
    return row


@pytest.fixture(autouse=True)
def override_authenticated_dependency():
    """Replace authenticated identity dependency with a header-driven identity
    so the endpoint can be exercised without wiring a full JWT."""
    route = cast(
        Any,
        next(
            r for r in app.routes
            if getattr(r, "path", "") == "/api/v1/downtime-reasons"
        ),
    )
    auth_dependency = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") == "require_authenticated_identity"
    )

    def _override(request: Request) -> RequestIdentity:
        tenant_id = (request.headers.get("X-Tenant-Id") or "default").strip() or "default"
        role_code = (request.headers.get("X-Role-Code") or "OPR").strip().upper()
        if request.headers.get("X-Force-Anon") == "1":
            raise HTTPException(status_code=401, detail="Authentication required")
        return RequestIdentity(
            user_id="test-user",
            username="test-user",
            email=None,
            tenant_id=tenant_id,
            role_code=role_code,
            is_authenticated=True,
            session_id="test-session",
        )

    app.dependency_overrides[auth_dependency] = _override
    try:
        yield
    finally:
        app.dependency_overrides.pop(auth_dependency, None)


def _codes(response_json: list[dict]) -> list[str]:
    return [item["reason_code"] for item in response_json]


# ─── 1. active reasons returned for tenant; inactive excluded; sort honored ─
def test_list_returns_active_sorted_excludes_inactive(db_session):
    db = db_session
    _seed(db, reason_code=f"{_PREFIX}-ZZ", reason_name="Z last", sort_order=90)
    _seed(db, reason_code=f"{_PREFIX}-AA", reason_name="A first", sort_order=10)
    _seed(
        db,
        reason_code=f"{_PREFIX}-INACTIVE",
        reason_name="should be hidden",
        sort_order=5,
        active_flag=False,
    )
    db.commit()

    response = client.get("/api/v1/downtime-reasons")
    assert response.status_code == 200
    body = response.json()

    returned_codes = _codes(body)
    assert f"{_PREFIX}-AA" in returned_codes
    assert f"{_PREFIX}-ZZ" in returned_codes
    assert f"{_PREFIX}-INACTIVE" not in returned_codes

    # Deterministic ordering: lower sort_order first, then reason_code.
    aa_idx = returned_codes.index(f"{_PREFIX}-AA")
    zz_idx = returned_codes.index(f"{_PREFIX}-ZZ")
    assert aa_idx < zz_idx


# ─── 2. response shape matches the FE contract ─────────────────────────────
def test_response_shape_matches_fe_contract(db_session):
    db = db_session
    _seed(
        db,
        reason_code=f"{_PREFIX}-SHAPE",
        reason_name="Shape check",
        reason_group="MATERIAL",
        planned_flag=True,
        requires_comment=True,
        requires_supervisor_review=True,
        sort_order=1,
    )
    db.commit()

    response = client.get("/api/v1/downtime-reasons")
    assert response.status_code == 200
    body = response.json()
    row = next(item for item in body if item["reason_code"] == f"{_PREFIX}-SHAPE")

    expected_keys = {
        "reason_code",
        "reason_name",
        "reason_group",
        "planned_flag",
        "requires_comment",
        "requires_supervisor_review",
    }
    assert set(row.keys()) == expected_keys
    assert row["reason_name"] == "Shape check"
    assert row["reason_group"] == "MATERIAL"
    assert row["planned_flag"] is True
    assert row["requires_comment"] is True
    assert row["requires_supervisor_review"] is True


# ─── 3. tenant isolation ────────────────────────────────────────────────────
def test_tenant_isolation_hides_other_tenants_rows(db_session):
    db = db_session
    _seed(
        db,
        tenant_id=f"{_PREFIX}-T1",
        reason_code=f"{_PREFIX}-T1-CODE",
        reason_name="tenant 1 row",
        sort_order=1,
    )
    _seed(
        db,
        tenant_id=f"{_PREFIX}-T2",
        reason_code=f"{_PREFIX}-T2-CODE",
        reason_name="tenant 2 row",
        sort_order=1,
    )
    db.commit()

    response_t1 = client.get(
        "/api/v1/downtime-reasons",
        headers={"X-Tenant-Id": f"{_PREFIX}-T1"},
    )
    assert response_t1.status_code == 200
    t1_codes = _codes(response_t1.json())
    assert f"{_PREFIX}-T1-CODE" in t1_codes
    assert f"{_PREFIX}-T2-CODE" not in t1_codes

    response_t2 = client.get(
        "/api/v1/downtime-reasons",
        headers={"X-Tenant-Id": f"{_PREFIX}-T2"},
    )
    assert response_t2.status_code == 200
    t2_codes = _codes(response_t2.json())
    assert f"{_PREFIX}-T2-CODE" in t2_codes
    assert f"{_PREFIX}-T1-CODE" not in t2_codes


# ─── 4. empty tenant catalog returns [] ──────────────────────────────────────
def test_empty_case_returns_empty_list(db_session):
    response = client.get(
        "/api/v1/downtime-reasons",
        headers={"X-Tenant-Id": f"{_PREFIX}-EMPTY"},
    )
    assert response.status_code == 200
    assert response.json() == []


# ─── 5. auth: authenticated access is enforced ──────────────────────────────
def test_anonymous_request_rejected():
    response = client.get(
        "/api/v1/downtime-reasons",
        headers={"X-Force-Anon": "1"},
    )
    assert response.status_code == 401
