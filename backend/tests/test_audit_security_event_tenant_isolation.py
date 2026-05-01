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


def _seed(db: Session, *, tenant_id: str, event_type: str, actor_user_id: str, resource_type: str, resource_id: str):
    db.add(
        SecurityEventLog(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            detail="seed",
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()


def test_security_event_list_does_not_leak_cross_tenant_events():
    identity = RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id="tenant_a",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-a",
    )
    app = _build_app(identity)
    _override_admin_dependency(app, identity)
    db = _make_session()
    app.dependency_overrides[security_events_router_module.get_db] = lambda: db

    _seed(
        db,
        tenant_id="tenant_a",
        event_type="AUTH.LOGIN",
        actor_user_id="a-user",
        resource_type="session",
        resource_id="shared-id",
    )
    _seed(
        db,
        tenant_id="tenant_b",
        event_type="AUTH.LOGIN",
        actor_user_id="b-user",
        resource_type="session",
        resource_id="shared-id",
    )

    client = TestClient(app)
    response = client.get("/api/v1/security-events")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["tenant_id"] == "tenant_a"
    assert body[0]["actor_user_id"] == "a-user"


def test_security_event_filters_do_not_bypass_tenant_isolation():
    identity = RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id="tenant_a",
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-a",
    )
    app = _build_app(identity)
    _override_admin_dependency(app, identity)
    db = _make_session()
    app.dependency_overrides[security_events_router_module.get_db] = lambda: db

    _seed(
        db,
        tenant_id="tenant_b",
        event_type="SENSITIVE.EVENT",
        actor_user_id="b-only",
        resource_type="session",
        resource_id="b-only-resource",
    )

    client = TestClient(app)
    response = client.get(
        "/api/v1/security-events?event_type=SENSITIVE.EVENT&actor_user_id=b-only&resource_type=session&resource_id=b-only-resource"
    )

    assert response.status_code == 200
    assert response.json() == []
