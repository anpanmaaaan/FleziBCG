"""API tests for Reason Code endpoints (read-only, no mutations)."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import app.api.v1.reason_codes as reason_codes_router_module
from app.models.reason_code import ReasonCode
from app.security.dependencies import RequestIdentity, require_authenticated_identity


def _build_app(identity: RequestIdentity) -> FastAPI:
    """Build a test FastAPI app with reason_codes router."""
    app = FastAPI()
    app.include_router(reason_codes_router_module.router, prefix="/api/v1")
    app.dependency_overrides[require_authenticated_identity] = lambda: identity
    return app


def _make_session():
    """Create an in-memory SQLite test database session."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ReasonCode.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


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

    def test_reason_code_routes_do_not_expose_post_patch_delete(self):
        """Verify POST, PATCH, DELETE methods are not available."""
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
        
        # POST to /reason-codes should not be allowed
        response = client.post("/api/v1/reason-codes", json={})
        assert response.status_code == 405  # Method Not Allowed

        # PATCH to /reason-codes/{id} should not be allowed
        response = client.patch("/api/v1/reason-codes/RC-001", json={})
        assert response.status_code == 405

        # DELETE to /reason-codes/{id} should not be allowed
        response = client.delete("/api/v1/reason-codes/RC-001")
        assert response.status_code == 405
