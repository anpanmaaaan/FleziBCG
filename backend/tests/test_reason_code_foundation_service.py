"""Service layer tests for Reason Code functionality."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.models.reason_code import ReasonCode
from app.services.reason_code_service import (
    get_reason_code,
    list_reason_codes,
)


@pytest.fixture
def db() -> Session:
    """Create in-memory SQLite test database."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ReasonCode.__table__.create(bind=engine)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_local()


def _populate_test_codes(db: Session) -> list[ReasonCode]:
    """Create and persist sample reason codes for testing."""
    codes = [
        ReasonCode(
            reason_code_id="RC-001",
            tenant_id="tenant-A",
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
            tenant_id="tenant-A",
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
            tenant_id="tenant-A",
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
            tenant_id="tenant-A",
            reason_domain="DOWNTIME",
            reason_category="Utilities",
            reason_code="DT-UTIL-01",
            reason_name="Utilities Issue",
            description="Power or utilities failure",
            lifecycle_status="DRAFT",
            requires_comment=True,
            is_active=False,
            sort_order=25,
        ),
    ]
    for code in codes:
        db.add(code)
    db.commit()
    return codes


class TestListReasonCodes:
    """Test list_reason_codes service function."""

    def test_list_reason_codes_returns_released_active_by_default(self, db: Session):
        """Default filter returns RELEASED + is_active=true codes."""
        _populate_test_codes(db)
        
        result = list_reason_codes(db, tenant_id="tenant-A")
        
        assert len(result) == 3
        ids = {item.reason_code_id for item in result}
        assert ids == {"RC-001", "RC-002", "RC-003"}

    def test_list_reason_codes_filters_by_domain(self, db: Session):
        """Filter by reason_domain narrows results."""
        _populate_test_codes(db)
        
        result = list_reason_codes(db, tenant_id="tenant-A", reason_domain="DOWNTIME")
        
        assert len(result) == 2
        ids = {item.reason_code_id for item in result}
        assert ids == {"RC-001", "RC-002"}

    def test_list_reason_codes_filters_by_category(self, db: Session):
        """Filter by reason_category narrows results."""
        _populate_test_codes(db)
        
        result = list_reason_codes(
            db, tenant_id="tenant-A", reason_category="Dimensional Defect"
        )
        
        assert len(result) == 1
        assert result[0].reason_code_id == "RC-003"

    def test_list_reason_codes_filters_by_lifecycle_status(self, db: Session):
        """Filter by lifecycle_status overrides default."""
        _populate_test_codes(db)
        
        result = list_reason_codes(
            db, tenant_id="tenant-A", lifecycle_status="DRAFT"
        )
        
        # RC-004 is DRAFT + inactive
        # With lifecycle_status="DRAFT", default include_inactive=False still filters to is_active
        assert len(result) == 0

    def test_list_reason_codes_filters_by_lifecycle_status_with_inactive(self, db: Session):
        """Filter by lifecycle_status with include_inactive includes all codes."""
        _populate_test_codes(db)
        
        result = list_reason_codes(
            db, tenant_id="tenant-A", lifecycle_status="DRAFT", include_inactive=True
        )
        
        # RC-004 is DRAFT + inactive
        assert len(result) == 1
        assert result[0].reason_code_id == "RC-004"

    def test_list_reason_codes_can_include_inactive(self, db: Session):
        """include_inactive flag allows filtering to all codes of default lifecycle_status."""
        _populate_test_codes(db)
        
        # With include_inactive=True but default lifecycle_status=RELEASED,
        # we get all RELEASED codes (active and inactive)
        # RC-004 is DRAFT, so it's excluded
        result = list_reason_codes(
            db, tenant_id="tenant-A", include_inactive=True
        )
        
        assert len(result) == 3
        ids = {item.reason_code_id for item in result}
        assert ids == {"RC-001", "RC-002", "RC-003"}

    def test_list_reason_codes_tenant_scoped(self, db: Session):
        """Results are scoped by tenant_id."""
        codes = _populate_test_codes(db)
        
        # Add codes for a different tenant
        other_codes = [
            ReasonCode(
                reason_code_id="RC-OTHER-001",
                tenant_id="tenant-B",
                reason_domain="DOWNTIME",
                reason_category="Test",
                reason_code="DT-OTHER-01",
                reason_name="Other Tenant Code",
                lifecycle_status="RELEASED",
                requires_comment=False,
                is_active=True,
                sort_order=0,
            ),
        ]
        for code in other_codes:
            db.add(code)
        db.commit()
        
        # Query for tenant-A should not include tenant-B codes
        result_a = list_reason_codes(db, tenant_id="tenant-A")
        assert len(result_a) == 3
        assert all(item.tenant_id == "tenant-A" for item in result_a)
        
        # Query for tenant-B should not include tenant-A codes
        result_b = list_reason_codes(db, tenant_id="tenant-B")
        assert len(result_b) == 1
        assert result_b[0].reason_code_id == "RC-OTHER-001"

    def test_list_reason_codes_ordered_by_domain_category_sort_order(
        self, db: Session
    ):
        """Results are ordered by (reason_domain, reason_category, sort_order)."""
        _populate_test_codes(db)
        
        result = list_reason_codes(
            db, tenant_id="tenant-A", include_inactive=True
        )
        
        # With include_inactive=True but default lifecycle_status=RELEASED,
        # we get 3 codes (RC-004 is DRAFT, excluded)
        assert len(result) == 3
        # DOWNTIME codes come first, then SCRAP
        domains = [item.reason_domain for item in result]
        assert domains == ["DOWNTIME", "DOWNTIME", "SCRAP"]


class TestGetReasonCode:
    """Test get_reason_code service function."""

    def test_get_reason_code_returns_matching_code(self, db: Session):
        """get_reason_code returns matching code by id."""
        _populate_test_codes(db)
        
        result = get_reason_code(db, tenant_id="tenant-A", reason_code_id="RC-001")
        
        assert result is not None
        assert result.reason_code_id == "RC-001"
        assert result.reason_code == "DT-MAINT-01"
        assert result.reason_domain == "DOWNTIME"

    def test_get_reason_code_returns_none_for_missing_code(self, db: Session):
        """get_reason_code returns None for nonexistent code."""
        _populate_test_codes(db)
        
        result = get_reason_code(db, tenant_id="tenant-A", reason_code_id="MISSING")
        
        assert result is None

    def test_get_reason_code_returns_none_for_wrong_tenant(self, db: Session):
        """get_reason_code respects tenant_id scope."""
        _populate_test_codes(db)
        
        result = get_reason_code(db, tenant_id="wrong-tenant", reason_code_id="RC-001")
        
        assert result is None

    def test_reason_code_status_values_are_stable(self, db: Session):
        """Lifecycle status values are stable (DRAFT, RELEASED, RETIRED)."""
        _populate_test_codes(db)
        
        result = list_reason_codes(
            db, tenant_id="tenant-A", include_inactive=True
        )
        
        statuses = {item.lifecycle_status for item in result}
        assert statuses.issubset({"DRAFT", "RELEASED", "RETIRED"})
