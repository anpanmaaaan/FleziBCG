from datetime import datetime, timedelta, timezone
from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.security_events as security_events_router_module
from app.models.security_event import SecurityEventLog
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _build_app(identity: RequestIdentity) -> FastAPI:
    app = FastAPI()
    app.include_router(security_events_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app


def _override_admin_dependency(app: FastAPI, identity: RequestIdentity) -> Any:
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == "/api/v1/security-events" and "GET" in (r.methods or set())
        ),
    )
    admin_dependency = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[admin_dependency] = lambda: identity


def _make_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SecurityEventLog.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _seed_event(
    db: Session,
    *,
    tenant_id: str,
    actor_user_id: str | None,
    event_type: str,
    resource_type: str | None,
    resource_id: str | None,
    created_at: datetime,
) -> None:
    db.add(
        SecurityEventLog(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            detail="seed",
            created_at=created_at,
        )
    )
    db.commit()


def _client_and_db() -> tuple[TestClient, Session]:
    identity = RequestIdentity(
        user_id="admin-user",
        username="admin-user",
        email=None,
        tenant_id="default",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="session-admin",
    )
    app = _build_app(identity)
    _override_admin_dependency(app, identity)

    db = _make_session()
    app.dependency_overrides[security_events_router_module.get_db] = lambda: db
    return TestClient(app), db


def test_security_event_list_returns_newest_first():
    client, db = _client_and_db()
    base = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)

    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="s-1",
        created_at=base,
    )
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-2",
        event_type="AUTH.LOGOUT",
        resource_type="session",
        resource_id="s-2",
        created_at=base + timedelta(minutes=1),
    )

    response = client.get("/api/v1/security-events")
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["event_type"] == "AUTH.LOGOUT"
    assert payload[1]["event_type"] == "AUTH.LOGIN"


def test_security_event_list_respects_default_limit():
    client, db = _client_and_db()
    now = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)

    for idx in range(120):
        _seed_event(
            db,
            tenant_id="default",
            actor_user_id="u",
            event_type=f"E{idx}",
            resource_type="session",
            resource_id=f"s-{idx}",
            created_at=now + timedelta(seconds=idx),
        )

    response = client.get("/api/v1/security-events")
    assert response.status_code == 200
    assert len(response.json()) == 100


def test_security_event_list_enforces_max_limit():
    client, db = _client_and_db()
    now = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)

    for idx in range(600):
        _seed_event(
            db,
            tenant_id="default",
            actor_user_id="u",
            event_type=f"E{idx}",
            resource_type="session",
            resource_id=f"s-{idx}",
            created_at=now + timedelta(seconds=idx),
        )

    response = client.get("/api/v1/security-events?limit=9999")
    assert response.status_code == 200
    assert len(response.json()) == 500


def test_filter_by_event_type():
    client, db = _client_and_db()
    now = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="s-1",
        created_at=now,
    )
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGOUT",
        resource_type="session",
        resource_id="s-2",
        created_at=now + timedelta(minutes=1),
    )

    response = client.get("/api/v1/security-events?event_type=auth.login")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["event_type"] == "AUTH.LOGIN"


def test_filter_by_actor_user_id():
    client, db = _client_and_db()
    now = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="actor-a",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="s-1",
        created_at=now,
    )
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="actor-b",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="s-2",
        created_at=now + timedelta(minutes=1),
    )

    response = client.get("/api/v1/security-events?actor_user_id=actor-b")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["actor_user_id"] == "actor-b"


def test_filter_by_resource_type():
    client, db = _client_and_db()
    now = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="s-1",
        created_at=now,
    )
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-2",
        event_type="IAM.USER_ACTIVATE",
        resource_type="user",
        resource_id="u-2",
        created_at=now + timedelta(minutes=1),
    )

    response = client.get("/api/v1/security-events?resource_type=user")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["resource_type"] == "user"


def test_filter_by_resource_id():
    client, db = _client_and_db()
    now = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="target-id",
        created_at=now,
    )
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGOUT",
        resource_type="session",
        resource_id="other-id",
        created_at=now + timedelta(minutes=1),
    )

    response = client.get("/api/v1/security-events?resource_id=target-id")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["resource_id"] == "target-id"


def test_filter_by_time_range_if_supported():
    client, db = _client_and_db()
    base = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="s-1",
        created_at=base,
    )
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="u-1",
        event_type="AUTH.LOGOUT",
        resource_type="session",
        resource_id="s-2",
        created_at=base + timedelta(hours=2),
    )

    response = client.get(
        "/api/v1/security-events?created_from=2026-05-01T09:00:00Z&created_to=2026-05-01T11:00:00Z"
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["event_type"] == "AUTH.LOGOUT"


def test_combined_filters():
    client, db = _client_and_db()
    base = datetime(2026, 5, 1, 8, 0, 0, tzinfo=timezone.utc)
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="actor-a",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="target",
        created_at=base,
    )
    _seed_event(
        db,
        tenant_id="default",
        actor_user_id="actor-a",
        event_type="AUTH.LOGIN",
        resource_type="session",
        resource_id="other",
        created_at=base + timedelta(minutes=1),
    )

    response = client.get(
        "/api/v1/security-events?event_type=AUTH.LOGIN&actor_user_id=actor-a&resource_type=session&resource_id=target"
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["resource_id"] == "target"


def test_filter_no_results_returns_empty_list():
    client, db = _client_and_db()
    response = client.get("/api/v1/security-events?event_type=DOES.NOT.EXIST")
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_filter_values_handled_by_current_error_convention():
    client, db = _client_and_db()
    response = client.get("/api/v1/security-events?limit=abc")
    assert response.status_code == 422
