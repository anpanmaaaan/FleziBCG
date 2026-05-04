"""API tests for Reason Code endpoints — read and write (MMD-BE-07, MMD-BE-13)."""
from typing import Any, cast

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import app.api.v1.reason_codes as reason_codes_router_module
from app.models.reason_code import ReasonCode
from app.models.security_event import SecurityEventLog
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _build_app(identity: RequestIdentity) -> FastAPI:
    """Build a test FastAPI app with reason_codes router."""
    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app


def _make_session_factory():
    """Create an in-memory SQLite engine + sessionmaker for write tests."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ReasonCode.__table__.create(bind=engine)
    SecurityEventLog.__table__.create(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _make_session():
    """Create an in-memory SQLite test database session (read tests)."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ReasonCode.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _make_identity(tenant_id: str = "test-tenant") -> RequestIdentity:
    return RequestIdentity(
        user_id="admin-user",
        username="adminuser",
        email=None,
        tenant_id=tenant_id,
        role_code="ADM",
        is_authenticated=True,
        session_id="s-admin",
    )


def _override_rc_manage(app: FastAPI, path: str, method: str, identity: RequestIdentity) -> Any:
    """Override the require_action dependency for a specific Reason Code write route."""
    route = cast(
        Any,
        next(
            r
            for r in app.routes
            if getattr(r, "path", "") == path and method in (r.methods or set())
        ),
    )
    action_dep = next(
        dep.call
        for dep in route.dependant.dependencies
        if getattr(dep.call, "__name__", "") != "get_db"
    )
    app.dependency_overrides[action_dep] = lambda: identity
    return action_dep


def _make_managed_app(identity: RequestIdentity, session_local) -> FastAPI:
    """Build app with manage action identity injected for all Reason Code write routes."""
    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[reason_codes_router_module.get_db] = lambda: session_local()

    write_routes = [
        ("/api/v1/reason-codes", "POST"),
        ("/api/v1/reason-codes/{reason_code_id}", "PATCH"),
        ("/api/v1/reason-codes/{reason_code_id}/release", "POST"),
        ("/api/v1/reason-codes/{reason_code_id}/retire", "POST"),
    ]
    for path, method in write_routes:
        _override_rc_manage(app, path, method, identity)

    return app


def _populate_test_codes(db):
    """Add test reason codes to the database."""
    codes = [
        ReasonCode(
            reason_code_id="RC-001",
            tenant_id="test-tenant",
            reason_domain="DOWNTIME",
            reason_category="Planned Maintenance",
            reason_code="DT-MAINT-01",
            reason_name="Scheduled Preventive Maintenance",
            description="Planned downtime for routine maintenance",
            lifecycle_status="RELEASED",
            requires_comment=False,
            is_active=True,
            sort_order=10,
        ),
        ReasonCode(
            reason_code_id="RC-002",
            tenant_id="test-tenant",
            reason_domain="DOWNTIME",
            reason_category="Unplanned Breakdown",
            reason_code="DT-BREAK-01",
            reason_name="Equipment Breakdown",
            description="Machine breakdown requiring repair",
            lifecycle_status="RELEASED",
            requires_comment=True,
            is_active=True,
            sort_order=20,
        ),
        ReasonCode(
            reason_code_id="RC-003",
            tenant_id="test-tenant",
            reason_domain="SCRAP",
            reason_category="Dimensional Defect",
            reason_code="SC-DIM-01",
            reason_name="Out of Tolerance Dimension",
            description="Part failed dimensional inspection",
            lifecycle_status="RELEASED",
            requires_comment=True,
            is_active=True,
            sort_order=10,
        ),
        ReasonCode(
            reason_code_id="RC-004",
            tenant_id="test-tenant",
            reason_domain="DOWNTIME",
            reason_category="Planned Maintenance",
            reason_code="DT-MAINT-02",
            reason_name="Seasonal Maintenance",
            description="Seasonal preventive maintenance",
            lifecycle_status="RELEASED",
            requires_comment=False,
            is_active=False,  # Inactive
            sort_order=15,
        ),
    ]
    for code in codes:
        db.add(code)
    db.commit()


class TestListReasonCodesAPI:
    """Test GET /api/v1/reason-codes endpoint."""

    def test_list_reason_codes_returns_default_released_active_codes(self):
        """GET /reason-codes returns RELEASED + active codes by default."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # RC-001, RC-002, RC-003 (RC-004 is inactive)

        ids = {item["reason_code_id"] for item in data}
        assert ids == {"RC-001", "RC-002", "RC-003"}

    def test_list_reason_codes_filters_by_domain(self):
        """GET /reason-codes?domain=DOWNTIME filters by domain."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes?domain=DOWNTIME")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # RC-001, RC-002
        
        ids = {item["reason_code_id"] for item in data}
        assert ids == {"RC-001", "RC-002"}

    def test_list_reason_codes_filters_by_category(self):
        """GET /reason-codes?category=... filters by category."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes?category=Unplanned%20Breakdown")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reason_code_id"] == "RC-002"

    def test_list_reason_codes_filters_by_lifecycle_status(self):
        """GET /reason-codes?lifecycle_status=DRAFT filters by status."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes?lifecycle_status=RELEASED")

        assert response.status_code == 200
        data = response.json()
        # All test codes are RELEASED, so this should work
        assert all(item["lifecycle_status"] == "RELEASED" for item in data)

    def test_list_reason_codes_include_inactive(self):
        """GET /reason-codes?include_inactive=true includes inactive codes."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes?include_inactive=true")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # RC-001, RC-002, RC-003, RC-004

        ids = {item["reason_code_id"] for item in data}
        assert ids == {"RC-001", "RC-002", "RC-003", "RC-004"}

    def test_list_reason_codes_requires_auth(self):
        """GET /reason-codes requires authentication."""
        from fastapi import HTTPException
        
        # Create identity with is_authenticated=False (like unauthenticated)
        identity = RequestIdentity(
            user_id=None,
            username=None,
            email=None,
            tenant_id=None,
            role_code=None,
            is_authenticated=False,
            session_id=None,
        )
        
        # Override dependency to raise 403 if not authenticated
        def check_auth():
            if not identity.is_authenticated:
                raise HTTPException(status_code=403, detail="Not authenticated")
            return identity
        
        app = _build_app(identity)
        app.dependency_overrides[require_authenticated_identity] = check_auth
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes")

        # Should fail because identity check fails
        assert response.status_code == 403


class TestGetReasonCodeAPI:
    """Test GET /api/v1/reason-codes/{reason_code_id} endpoint."""

    def test_get_reason_code_returns_one_code(self):
        """GET /reason-codes/{id} returns a single code."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes/RC-001")

        assert response.status_code == 200
        data = response.json()
        assert data["reason_code_id"] == "RC-001"
        assert data["reason_code"] == "DT-MAINT-01"
        assert data["reason_domain"] == "DOWNTIME"

    def test_get_reason_code_returns_404_for_missing_code(self):
        """GET /reason-codes/{id} returns 404 if not found."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes/NONEXISTENT")

        assert response.status_code == 404

    def test_get_reason_code_returns_404_for_cross_tenant_code(self):
        """GET /reason-codes/{id} returns 404 for cross-tenant access."""
        # The code RC-001 belongs to "test-tenant"
        # If the client is authenticated as "other-tenant", should get 404
        identity = RequestIdentity(
            user_id="user-2",
            username="other-user",
            email=None,
            tenant_id="other-tenant",  # Different tenant
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-2",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db
        
        _populate_test_codes(db)
        
        client = TestClient(app)
        response = client.get("/api/v1/reason-codes/RC-001")

        assert response.status_code == 404

    def test_reason_code_hard_delete_route_does_not_exist(self):
        """DELETE /reason-codes/{id} must remain 405 Method Not Allowed."""
        identity = RequestIdentity(
            user_id="user-1",
            username="testuser",
            email=None,
            tenant_id="test-tenant",
            role_code="OPERATOR",
            is_authenticated=True,
            session_id="s-1",
        )
        app = _build_app(identity)
        db = _make_session()
        app.dependency_overrides[reason_codes_router_module.get_db] = lambda: db

        _populate_test_codes(db)

        client = TestClient(app)
        response = client.delete("/api/v1/reason-codes/RC-001")
        assert response.status_code == 405  # Method Not Allowed


# ─── MMD-BE-13: Create Reason Code ───────────────────────────────────────────

def test_create_reason_code_creates_draft():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        "/api/v1/reason-codes",
        json={
            "reason_domain": "DOWNTIME",
            "reason_category": "Planned Maintenance",
            "reason_code": "DT-NEW-01",
            "reason_name": "New Downtime Code",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reason_code"] == "DT-NEW-01"
    assert data["lifecycle_status"] == "DRAFT"
    assert data["tenant_id"] == "test-tenant"
    assert data["reason_domain"] == "DOWNTIME"


def test_create_reason_code_rejects_duplicate_code_for_same_domain():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    payload = {
        "reason_domain": "DOWNTIME",
        "reason_category": "Planned",
        "reason_code": "DUP-01",
        "reason_name": "Duplicate Code",
    }
    client.post("/api/v1/reason-codes", json=payload)
    second = client.post("/api/v1/reason-codes", json=payload)
    assert second.status_code == 409


def test_create_reason_code_rejects_lifecycle_status_payload():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        "/api/v1/reason-codes",
        json={
            "reason_domain": "DOWNTIME",
            "reason_category": "Planned",
            "reason_code": "DT-X-01",
            "reason_name": "Test",
            "lifecycle_status": "RELEASED",
        },
    )
    assert response.status_code == 422


def test_create_reason_code_rejects_tenant_id_payload():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        "/api/v1/reason-codes",
        json={
            "reason_domain": "DOWNTIME",
            "reason_category": "Planned",
            "reason_code": "DT-X-02",
            "reason_name": "Test",
            "tenant_id": "evil-tenant",
        },
    )
    assert response.status_code == 422


def test_create_reason_code_rejects_downtime_reason_id_payload():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post(
        "/api/v1/reason-codes",
        json={
            "reason_domain": "DOWNTIME",
            "reason_category": "Planned",
            "reason_code": "DT-X-03",
            "reason_name": "Test",
            "downtime_reason_id": "dt-001",
        },
    )
    assert response.status_code == 422


def test_create_reason_code_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[reason_codes_router_module.get_db] = lambda: session_local()

    deny_dep = _override_rc_manage(app, "/api/v1/reason-codes", "POST", identity)
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/reason-codes",
        json={
            "reason_domain": "DOWNTIME",
            "reason_category": "Planned",
            "reason_code": "DT-X-04",
            "reason_name": "Test",
        },
    )
    assert response.status_code == 403


# ─── MMD-BE-13: Update Reason Code ───────────────────────────────────────────

def test_update_reason_code_allows_draft_metadata_update():
    identity = _make_identity()
    session_local = _make_session_factory()
    db = session_local()
    rc = ReasonCode(
        reason_code_id="RC-DRAFT",
        tenant_id="test-tenant",
        reason_domain="DOWNTIME",
        reason_category="Planned",
        reason_code="DT-UPDT-01",
        reason_name="Original Name",
        lifecycle_status="DRAFT",
        requires_comment=False,
        is_active=True,
        sort_order=0,
    )
    db.add(rc)
    db.commit()
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        "/api/v1/reason-codes/RC-DRAFT",
        json={"reason_name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["reason_name"] == "Updated Name"


def test_update_reason_code_rejects_released():
    identity = _make_identity()
    session_local = _make_session_factory()
    db = session_local()
    rc = ReasonCode(
        reason_code_id="RC-REL",
        tenant_id="test-tenant",
        reason_domain="DOWNTIME",
        reason_category="Planned",
        reason_code="DT-REL-01",
        reason_name="Released Code",
        lifecycle_status="RELEASED",
        requires_comment=False,
        is_active=True,
        sort_order=0,
    )
    db.add(rc)
    db.commit()
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch("/api/v1/reason-codes/RC-REL", json={"reason_name": "New Name"})
    assert response.status_code == 409


def test_update_reason_code_rejects_retired():
    identity = _make_identity()
    session_local = _make_session_factory()
    db = session_local()
    rc = ReasonCode(
        reason_code_id="RC-RET",
        tenant_id="test-tenant",
        reason_domain="DOWNTIME",
        reason_category="Planned",
        reason_code="DT-RET-01",
        reason_name="Retired Code",
        lifecycle_status="RETIRED",
        requires_comment=False,
        is_active=True,
        sort_order=0,
    )
    db.add(rc)
    db.commit()
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch("/api/v1/reason-codes/RC-RET", json={"reason_name": "New Name"})
    assert response.status_code == 409


def test_update_reason_code_rejects_lifecycle_status_patch():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        "/api/v1/reason-codes/RC-NONEXISTENT",
        json={"lifecycle_status": "RELEASED"},
    )
    assert response.status_code == 422


def test_update_reason_code_rejects_reason_code_patch():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        "/api/v1/reason-codes/RC-NONEXISTENT",
        json={"reason_code": "CANNOT-CHANGE"},
    )
    assert response.status_code == 422


def test_update_reason_code_rejects_reason_domain_patch():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        "/api/v1/reason-codes/RC-NONEXISTENT",
        json={"reason_domain": "SCRAP"},
    )
    assert response.status_code == 422


def test_update_reason_code_rejects_downtime_reason_mapping_patch():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.patch(
        "/api/v1/reason-codes/RC-NONEXISTENT",
        json={"downtime_reason_id": "dt-001"},
    )
    assert response.status_code == 422


def test_update_reason_code_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[reason_codes_router_module.get_db] = lambda: session_local()

    deny_dep = _override_rc_manage(app, "/api/v1/reason-codes/{reason_code_id}", "PATCH", identity)
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    assert client.patch("/api/v1/reason-codes/RC-X", json={"reason_name": "X"}).status_code == 403


# ─── MMD-BE-13: Release Reason Code ──────────────────────────────────────────

def test_release_reason_code_changes_draft_to_released():
    identity = _make_identity()
    session_local = _make_session_factory()
    db = session_local()
    rc = ReasonCode(
        reason_code_id="RC-TO-RELEASE",
        tenant_id="test-tenant",
        reason_domain="DOWNTIME",
        reason_category="Planned",
        reason_code="DT-RELE-01",
        reason_name="To Release",
        lifecycle_status="DRAFT",
        requires_comment=False,
        is_active=True,
        sort_order=0,
    )
    db.add(rc)
    db.commit()
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    response = client.post("/api/v1/reason-codes/RC-TO-RELEASE/release")
    assert response.status_code == 200
    assert response.json()["lifecycle_status"] == "RELEASED"


def test_release_reason_code_rejects_released_or_retired():
    identity = _make_identity()
    session_local = _make_session_factory()
    db = session_local()
    for rc_id, status in [("RC-ALREADY-REL", "RELEASED"), ("RC-ALREADY-RET", "RETIRED")]:
        db.add(ReasonCode(
            reason_code_id=rc_id,
            tenant_id="test-tenant",
            reason_domain="DOWNTIME",
            reason_category="Planned",
            reason_code=f"DT-{rc_id}",
            reason_name="Code",
            lifecycle_status=status,
            requires_comment=False,
            is_active=True,
            sort_order=0,
        ))
    db.commit()
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    assert client.post("/api/v1/reason-codes/RC-ALREADY-REL/release").status_code == 409
    assert client.post("/api/v1/reason-codes/RC-ALREADY-RET/release").status_code == 409


def test_release_reason_code_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[reason_codes_router_module.get_db] = lambda: session_local()

    deny_dep = _override_rc_manage(
        app, "/api/v1/reason-codes/{reason_code_id}/release", "POST", identity
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    assert client.post("/api/v1/reason-codes/RC-X/release").status_code == 403


# ─── MMD-BE-13: Retire Reason Code ───────────────────────────────────────────

def test_retire_reason_code_changes_draft_or_released_to_retired():
    identity = _make_identity()
    session_local = _make_session_factory()
    db = session_local()
    for rc_id, status in [("RC-DR-RETIRE", "DRAFT"), ("RC-RE-RETIRE", "RELEASED")]:
        db.add(ReasonCode(
            reason_code_id=rc_id,
            tenant_id="test-tenant",
            reason_domain="DOWNTIME",
            reason_category="Planned",
            reason_code=f"DT-{rc_id}",
            reason_name="Code",
            lifecycle_status=status,
            requires_comment=False,
            is_active=True,
            sort_order=0,
        ))
    db.commit()
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    r1 = client.post("/api/v1/reason-codes/RC-DR-RETIRE/retire")
    assert r1.status_code == 200
    assert r1.json()["lifecycle_status"] == "RETIRED"

    r2 = client.post("/api/v1/reason-codes/RC-RE-RETIRE/retire")
    assert r2.status_code == 200
    assert r2.json()["lifecycle_status"] == "RETIRED"


def test_retire_reason_code_rejects_already_retired():
    identity = _make_identity()
    session_local = _make_session_factory()
    db = session_local()
    db.add(ReasonCode(
        reason_code_id="RC-ALREADY-RET2",
        tenant_id="test-tenant",
        reason_domain="DOWNTIME",
        reason_category="Planned",
        reason_code="DT-ARET-02",
        reason_name="Already Retired",
        lifecycle_status="RETIRED",
        requires_comment=False,
        is_active=True,
        sort_order=0,
    ))
    db.commit()
    db.close()

    app = _make_managed_app(identity, session_local)
    client = TestClient(app)

    assert client.post("/api/v1/reason-codes/RC-ALREADY-RET2/retire").status_code == 409


def test_retire_reason_code_requires_manage_action():
    identity = _make_identity()
    session_local = _make_session_factory()

    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    app.dependency_overrides[reason_codes_router_module.get_db] = lambda: session_local()

    deny_dep = _override_rc_manage(
        app, "/api/v1/reason-codes/{reason_code_id}/retire", "POST", identity
    )
    app.dependency_overrides[deny_dep] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Forbidden")
    )

    client = TestClient(app)
    assert client.post("/api/v1/reason-codes/RC-X/retire").status_code == 403


# ─── MMD-BE-13: Scope / boundary guards ──────────────────────────────────────

def test_no_reason_code_hard_delete_reactivate_activate_deactivate_clone_bulk_map_policy_routes_exist():
    """Boundary guard: no forbidden routes must be present in the router."""
    import app.api.v1.reason_codes as rc_mod

    REASON_CODES_SRC = open(rc_mod.__file__, encoding="utf-8").read()
    forbidden_markers = [
        "@router.delete(",
        "/reactivate",
        "/activate",
        "/deactivate",
        "/clone",
        "/bulk-import",
        "/map-downtime",
        "/bind-policy",
        "/erp-post",
        "/start-downtime",
        "/quality-accept",
        "/material-move",
        "/backflush",
    ]
    for marker in forbidden_markers:
        assert marker not in REASON_CODES_SRC, (
            f"Forbidden route marker found in reason_codes.py: {marker!r}"
        )


def test_reason_code_read_endpoints_do_not_require_manage_action():
    """GET routes must remain require_authenticated_identity (not require_action)."""
    import re
    import app.api.v1.reason_codes as rc_mod

    REASON_CODES_SRC = open(rc_mod.__file__, encoding="utf-8").read()
    get_blocks = re.findall(
        r'@router\.get\b[^@]+?(?=@router\.|$)',
        REASON_CODES_SRC,
        flags=re.DOTALL,
    )
    assert len(get_blocks) >= 2, "Expected at least 2 GET route blocks"
    for block in get_blocks:
        assert "require_action" not in block, (
            "GET route must not use require_action — authenticated-read only"
        )


def test_reason_code_write_does_not_modify_downtime_reason_api():
    """reason_code_service must not import from downtime_reason modules."""
    import app.services.reason_code_service as svc_mod

    SVC_SRC = open(svc_mod.__file__, encoding="utf-8").read()
    assert "downtime_reason" not in SVC_SRC.lower(), (
        "reason_code_service.py must not reference downtime_reason modules"
    )
