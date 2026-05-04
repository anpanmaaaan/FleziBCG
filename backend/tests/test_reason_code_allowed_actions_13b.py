"""Reason Code Allowed Actions tests (MMD-FULLSTACK-13B capability guard)."""

from __future__ import annotations

import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.v1.reason_codes as reason_codes_router_module
from app.models.reason_code import ReasonCode
from app.models.security_event import SecurityEventLog
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _make_identity(tenant_id: str = "tenant_a") -> RequestIdentity:
    return RequestIdentity(
        user_id="admin-a",
        username="admin-a",
        email=None,
        tenant_id=tenant_id,
        role_code="ADMIN",
        is_authenticated=True,
        session_id="s-admin",
    )


def _make_session_local():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ReasonCode.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    return sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )


def _build_app(
    identity: RequestIdentity, session_local, has_manage: bool = False
) -> FastAPI:
    from app.api.v1.reason_codes import get_db

    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[get_db] = lambda: session_local()
    # Patch has_action at module level so SQLite test db doesn't need permission rows.
    reason_codes_router_module.has_action = lambda db, ident, action_code, *a, **kw: (
        has_manage
    )
    return app


def _mk_reason_code(
    db,
    *,
    tenant_id: str,
    reason_code: str,
    lifecycle_status: str = "DRAFT",
) -> ReasonCode:
    row = ReasonCode(
        reason_code_id=uuid.uuid4().hex,
        tenant_id=tenant_id,
        reason_domain="DOWNTIME",
        reason_category="Test",
        reason_code=reason_code,
        reason_name=f"Test {reason_code}",
        lifecycle_status=lifecycle_status,
        requires_comment=False,
        is_active=True,
        sort_order=0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ─── Response includes allowed_actions ────────────────────────────────────────


def test_list_reason_codes_includes_allowed_actions():
    """GET /reason-codes includes allowed_actions in each item (MMD-FULLSTACK-13B)."""
    identity = _make_identity()
    session_local = _make_session_local()
    db = session_local()
    _mk_reason_code(
        db, tenant_id="tenant_a", reason_code="RC-001", lifecycle_status="DRAFT"
    )
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get("/api/v1/reason-codes")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert "allowed_actions" in items[0], "Missing allowed_actions in list response"
    aa = items[0]["allowed_actions"]
    assert "can_update" in aa
    assert "can_release" in aa
    assert "can_retire" in aa
    assert "can_create_sibling" in aa


def test_get_reason_code_includes_allowed_actions():
    """GET /reason-codes/{id} includes allowed_actions (MMD-FULLSTACK-13B)."""
    identity = _make_identity()
    session_local = _make_session_local()
    db = session_local()
    row = _mk_reason_code(
        db, tenant_id="tenant_a", reason_code="RC-002", lifecycle_status="DRAFT"
    )
    rc_id = row.reason_code_id
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get(f"/api/v1/reason-codes/{rc_id}")
    assert response.status_code == 200
    detail = response.json()
    assert "allowed_actions" in detail, "Missing allowed_actions in detail response"
    assert "can_update" in detail["allowed_actions"]
    assert "can_release" in detail["allowed_actions"]
    assert "can_retire" in detail["allowed_actions"]
    assert "can_create_sibling" in detail["allowed_actions"]


# ─── No manage permission → all false ─────────────────────────────────────────


def test_reason_code_allowed_actions_all_false_without_manage():
    """Non-manage user gets all write capabilities false (MMD-FULLSTACK-13B)."""
    identity = _make_identity()
    session_local = _make_session_local()
    db = session_local()
    _mk_reason_code(
        db, tenant_id="tenant_a", reason_code="RC-003", lifecycle_status="DRAFT"
    )
    db.close()

    app = _build_app(identity, session_local, has_manage=False)
    client = TestClient(app)

    response = client.get("/api/v1/reason-codes")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    aa = items[0]["allowed_actions"]
    assert aa["can_update"] is False
    assert aa["can_release"] is False
    assert aa["can_retire"] is False
    assert aa["can_create_sibling"] is False


# ─── Manage permission + lifecycle matrix ────────────────────────────────────


def test_draft_reason_code_allowed_actions_all_true_with_manage():
    """DRAFT + manage: can_update, can_release, can_retire, can_create_sibling all true."""
    identity = _make_identity()
    session_local = _make_session_local()
    db = session_local()
    _mk_reason_code(
        db, tenant_id="tenant_a", reason_code="RC-D01", lifecycle_status="DRAFT"
    )
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get("/api/v1/reason-codes")
    assert response.status_code == 200
    aa = response.json()[0]["allowed_actions"]
    assert aa["can_update"] is True
    assert aa["can_release"] is True
    assert aa["can_retire"] is True
    assert aa["can_create_sibling"] is True


def test_released_reason_code_allowed_actions_retire_and_sibling_with_manage():
    """RELEASED + manage: can_retire and can_create_sibling only."""
    identity = _make_identity()
    session_local = _make_session_local()
    db = session_local()
    _mk_reason_code(
        db, tenant_id="tenant_a", reason_code="RC-R01", lifecycle_status="RELEASED"
    )
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get("/api/v1/reason-codes")
    assert response.status_code == 200
    aa = response.json()[0]["allowed_actions"]
    assert aa["can_update"] is False
    assert aa["can_release"] is False
    assert aa["can_retire"] is True
    assert aa["can_create_sibling"] is True


def test_retired_reason_code_allowed_actions_sibling_only_with_manage():
    """RETIRED + manage: can_create_sibling only; all write mutations false."""
    identity = _make_identity()
    session_local = _make_session_local()
    db = session_local()
    _mk_reason_code(
        db, tenant_id="tenant_a", reason_code="RC-RT1", lifecycle_status="RETIRED"
    )
    db.close()

    app = _build_app(identity, session_local, has_manage=True)
    client = TestClient(app)

    response = client.get("/api/v1/reason-codes")
    assert response.status_code == 200
    aa = response.json()[0]["allowed_actions"]
    assert aa["can_update"] is False
    assert aa["can_release"] is False
    assert aa["can_retire"] is False
    assert aa["can_create_sibling"] is True


# ─── Read remains accessible without manage permission ────────────────────────


def test_read_reason_codes_does_not_require_manage_permission():
    """Read endpoints return 200 regardless of manage permission (auth only)."""
    identity = _make_identity()
    session_local = _make_session_local()
    db = session_local()
    _mk_reason_code(
        db, tenant_id="tenant_a", reason_code="RC-ANY", lifecycle_status="RELEASED"
    )
    db.close()

    # Non-manage user
    app = _build_app(identity, session_local, has_manage=False)
    client = TestClient(app)

    response = client.get("/api/v1/reason-codes")
    assert response.status_code == 200, "Read must not require manage permission"
    items = response.json()
    # Data still returned; allowed_actions all false
    assert len(items) == 1
    assert items[0]["reason_code"] == "RC-ANY"
    assert items[0]["allowed_actions"]["can_update"] is False
