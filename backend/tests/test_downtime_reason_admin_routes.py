from __future__ import annotations

from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

import app.api.v1.downtime_reasons as downtime_reason_router_module
from app.models.downtime_reason import DowntimeReason
from app.models.security_event import SecurityEventLog
from app.schemas.downtime_reason import (
    DowntimeReasonAdminItem,
    DowntimeReasonUpsertRequest,
)
from app.security.dependencies import RequestIdentity, require_authenticated_identity
from app.services.downtime_reason_service import (
    deactivate_downtime_reason,
    upsert_downtime_reason,
)


_PREFIX = "TEST-DT-ADMIN"


def _build_app() -> tuple[FastAPI, RequestIdentity]:
    app = FastAPI()
    app.include_router(downtime_reason_router_module.router, prefix="/api/v1")
    identity = RequestIdentity(
        user_id="admin-user",
        username="admin-user",
        email=None,
        tenant_id="default",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="session-admin",
    )
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app, identity


def _override_admin_dependency(app: FastAPI, path: str, identity: RequestIdentity) -> None:
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == path and "POST" in (r.methods or set())
        ),
    )
    admin_dependency = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[admin_dependency] = lambda: identity


def _make_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    DowntimeReason.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def test_admin_routes_exist_and_delegate_to_service(monkeypatch):
    app, identity = _build_app()
    _override_admin_dependency(app, "/api/v1/downtime-reasons", identity)
    _override_admin_dependency(app, "/api/v1/downtime-reasons/{reason_code}/deactivate", identity)

    fake_db = object()
    app.dependency_overrides[downtime_reason_router_module.get_db] = lambda: fake_db

    monkeypatch.setattr(
        downtime_reason_router_module,
        "upsert_downtime_reason_service",
        lambda db, tenant_id, actor_user_id, payload: DowntimeReasonAdminItem(
            reason_code=payload.reason_code,
            reason_name=payload.reason_name,
            reason_group=payload.reason_group,
            planned_flag=payload.planned_flag,
            default_block_mode=payload.default_block_mode,
            requires_comment=payload.requires_comment,
            requires_supervisor_review=payload.requires_supervisor_review,
            active_flag=True,
            sort_order=payload.sort_order,
        ),
    )
    monkeypatch.setattr(
        downtime_reason_router_module,
        "deactivate_downtime_reason_service",
        lambda db, tenant_id, actor_user_id, reason_code: DowntimeReasonAdminItem(
            reason_code=reason_code,
            reason_name="Stopped",
            reason_group="OTHER",
            planned_flag=False,
            default_block_mode="BLOCK",
            requires_comment=False,
            requires_supervisor_review=False,
            active_flag=False,
            sort_order=0,
        ),
    )

    client = TestClient(app)
    upsert = client.post(
        "/api/v1/downtime-reasons",
        json={
            "reason_code": f"{_PREFIX}-UPSERT",
            "reason_name": "Setup stop",
            "reason_group": "CHANGEOVER",
            "planned_flag": True,
            "default_block_mode": "BLOCK",
            "requires_comment": False,
            "requires_supervisor_review": True,
            "sort_order": 40,
        },
    )
    assert upsert.status_code == 200
    assert upsert.json()["reason_code"] == f"{_PREFIX}-UPSERT"

    deactivate = client.post(f"/api/v1/downtime-reasons/{_PREFIX}-UPSERT/deactivate")
    assert deactivate.status_code == 200
    assert deactivate.json()["active_flag"] is False


def test_service_upsert_and_deactivate_record_security_events():
    db = _make_session()
    payload = DowntimeReasonUpsertRequest(
        reason_code=f"{_PREFIX}-UPSERT",
        reason_name="Setup stop",
        reason_group="CHANGEOVER",
        planned_flag=True,
        default_block_mode="BLOCK",
        requires_comment=False,
        requires_supervisor_review=True,
        sort_order=40,
    )

    created = upsert_downtime_reason(
        db,
        tenant_id="default",
        actor_user_id="admin-user",
        payload=payload,
    )
    assert created.active_flag is True

    updated = upsert_downtime_reason(
        db,
        tenant_id="default",
        actor_user_id="admin-user",
        payload=payload.model_copy(
            update={
                "reason_name": "Setup stop updated",
                "planned_flag": False,
                "default_block_mode": "WARN",
                "requires_comment": True,
                "requires_supervisor_review": False,
                "sort_order": 5,
            }
        ),
    )
    assert updated.reason_name == "Setup stop updated"
    assert updated.default_block_mode == "WARN"

    deactivated = deactivate_downtime_reason(
        db,
        tenant_id="default",
        actor_user_id="admin-user",
        reason_code=f"{_PREFIX}-UPSERT",
    )
    assert deactivated is not None
    assert deactivated.active_flag is False

    row = db.scalar(
        select(DowntimeReason).where(
            DowntimeReason.reason_code == f"{_PREFIX}-UPSERT",
            DowntimeReason.tenant_id == "default",
        )
    )
    assert row is not None
    assert row.active_flag is False
    assert row.reason_name == "Setup stop updated"

    events = list(
        db.scalars(
            select(SecurityEventLog)
            .where(SecurityEventLog.resource_id == f"{_PREFIX}-UPSERT")
            .order_by(SecurityEventLog.id)
        )
    )
    assert [event.event_type for event in events] == [
        "MASTER.DOWNTIME_REASON_UPSERT",
        "MASTER.DOWNTIME_REASON_UPSERT",
        "MASTER.DOWNTIME_REASON_DEACTIVATE",
    ]
