"""Service layer tests for Reason Code functionality (MMD-BE-07, MMD-BE-13)."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.models.reason_code import ReasonCode
from app.models.security_event import SecurityEventLog
from app.schemas.reason_code import ReasonCodeCreateRequest, ReasonCodeUpdateRequest
from app.services.reason_code_service import (
    create_reason_code,
    get_reason_code,
    list_reason_codes,
    release_reason_code,
    retire_reason_code,
    update_reason_code,
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
    SecurityEventLog.__table__.create(bind=engine)
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
        _populate_test_codes(db)
        
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


# 笏笏笏 MMD-BE-13: Create Reason Code (service) 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏

class TestCreateReasonCode:

    def test_create_reason_code_sets_draft_default(self, db: Session):
        item = create_reason_code(
            db,
            tenant_id="tenant-A",
            actor_user_id="user-admin",
            payload=ReasonCodeCreateRequest(
                reason_domain="DOWNTIME",
                reason_category="Planned",
                reason_code="DT-SVC-01",
                reason_name="Service Test Code",
            ),
        )
        assert item.lifecycle_status == "DRAFT"
        assert item.tenant_id == "tenant-A"
        assert item.reason_code == "DT-SVC-01"
        assert item.reason_domain == "DOWNTIME"

    def test_create_reason_code_enforces_unique_code_per_domain(self, db: Session):
        payload = ReasonCodeCreateRequest(
            reason_domain="DOWNTIME",
            reason_category="Planned",
            reason_code="DT-SVC-DUP",
            reason_name="Duplicate",
        )
        create_reason_code(db, tenant_id="tenant-A", actor_user_id="admin", payload=payload)
        with pytest.raises(ValueError, match="Duplicate"):
            create_reason_code(db, tenant_id="tenant-A", actor_user_id="admin", payload=payload)

    def test_create_reason_code_same_code_different_domain_is_allowed(self, db: Session):
        for domain in ["DOWNTIME", "SCRAP"]:
            create_reason_code(
                db,
                tenant_id="tenant-A",
                actor_user_id="admin",
                payload=ReasonCodeCreateRequest(
                    reason_domain=domain,
                    reason_category="Cat",
                    reason_code="SHARED-CODE-01",
                    reason_name="Shared Code",
                ),
            )


# 笏笏笏 MMD-BE-13: Update Reason Code (service) 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏

class TestUpdateReasonCode:

    def test_update_reason_code_only_draft(self, db: Session):
        _populate_test_codes(db)
        with pytest.raises(ValueError, match="cannot be updated"):
            update_reason_code(
                db,
                tenant_id="tenant-A",
                actor_user_id="admin",
                reason_code_id="RC-001",  # RELEASED
                payload=ReasonCodeUpdateRequest(reason_name="New Name"),
            )

    def test_update_draft_updates_mutable_fields(self, db: Session):
        _populate_test_codes(db)
        item = update_reason_code(
            db,
            tenant_id="tenant-A",
            actor_user_id="admin",
            reason_code_id="RC-004",  # DRAFT
            payload=ReasonCodeUpdateRequest(reason_name="Updated Draft Name", sort_order=99),
        )
        assert item.reason_name == "Updated Draft Name"
        assert item.sort_order == 99

    def test_update_reason_code_rejects_immutable_reason_code(self, db: Session):
        """reason_code field cannot be in UpdateRequest (extra=forbid)."""
        with pytest.raises(Exception):
            ReasonCodeUpdateRequest(reason_code="CHANGED")  # type: ignore[call-arg]

    def test_update_reason_code_rejects_immutable_reason_domain(self, db: Session):
        """reason_domain field cannot be in UpdateRequest (extra=forbid)."""
        with pytest.raises(Exception):
            ReasonCodeUpdateRequest(reason_domain="SCRAP")  # type: ignore[call-arg]

    def test_update_reason_code_rejects_immutable_reason_category(self, db: Session):
        """reason_category field cannot be in UpdateRequest (extra=forbid)."""
        with pytest.raises(Exception):
            ReasonCodeUpdateRequest(reason_category="Utilities")  # type: ignore[call-arg]


# 笏笏笏 MMD-BE-13: Release Reason Code (service) 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏

class TestReleaseReasonCode:

    def test_release_only_draft(self, db: Session):
        _populate_test_codes(db)
        item = release_reason_code(
            db, tenant_id="tenant-A", actor_user_id="admin", reason_code_id="RC-004"
        )
        assert item.lifecycle_status == "RELEASED"

    def test_release_rejects_released(self, db: Session):
        _populate_test_codes(db)
        with pytest.raises(ValueError, match="Only DRAFT"):
            release_reason_code(
                db, tenant_id="tenant-A", actor_user_id="admin", reason_code_id="RC-001"
            )

    def test_release_rejects_retired(self, db: Session):
        item = create_reason_code(
            db,
            tenant_id="tenant-A",
            actor_user_id="admin",
            payload=ReasonCodeCreateRequest(
                reason_domain="DOWNTIME",
                reason_category="Cat",
                reason_code="DT-RETIRE-PRE",
                reason_name="Pre-retire",
            ),
        )
        retire_reason_code(
            db, tenant_id="tenant-A", actor_user_id="admin", reason_code_id=item.reason_code_id
        )
        with pytest.raises(ValueError, match="RETIRED"):
            release_reason_code(
                db, tenant_id="tenant-A", actor_user_id="admin", reason_code_id=item.reason_code_id
            )


# 笏笏笏 MMD-BE-13: Retire Reason Code (service) 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏

class TestRetireReasonCode:

    def test_retire_draft_or_released(self, db: Session):
        _populate_test_codes(db)
        for rc_id in ["RC-001", "RC-004"]:  # RELEASED, DRAFT
            item = retire_reason_code(
                db, tenant_id="tenant-A", actor_user_id="admin", reason_code_id=rc_id
            )
            assert item.lifecycle_status == "RETIRED"

    def test_retire_rejects_already_retired(self, db: Session):
        item = create_reason_code(
            db,
            tenant_id="tenant-A",
            actor_user_id="admin",
            payload=ReasonCodeCreateRequest(
                reason_domain="DOWNTIME",
                reason_category="Cat",
                reason_code="DT-RETW-01",
                reason_name="Pre-retire 2",
            ),
        )
        retire_reason_code(
            db, tenant_id="tenant-A", actor_user_id="admin", reason_code_id=item.reason_code_id
        )
        with pytest.raises(ValueError, match="already RETIRED"):
            retire_reason_code(
                db, tenant_id="tenant-A", actor_user_id="admin", reason_code_id=item.reason_code_id
            )


# 笏笏笏 MMD-BE-13: Boundary guards (service) 笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏笏

def test_no_downtime_reason_mapping_field_or_behavior():
    """reason_code_service.py must not reference downtime_reason anywhere."""
    import app.services.reason_code_service as svc_mod
    SRC = open(svc_mod.__file__, encoding="utf-8").read()
    assert "downtime_reason" not in SRC.lower()


def test_no_execution_material_quality_erp_side_effects():
    """reason_code_service.py must not reference execution, quality, ERP, or material move symbols."""
    import app.services.reason_code_service as svc_mod
    SRC = open(svc_mod.__file__, encoding="utf-8").read()
    forbidden_terms = [
        "operation_event",
        "quality_hold",
        "erp_post",
        "backflush",
        "material_move",
        "start_downtime",
        "end_downtime",
        "quality_accept",
        "inventory_move",
    ]
    for term in forbidden_terms:
        assert term not in SRC.lower(), f"reason_code_service must not reference: {term!r}"


def test_reason_code_event_names_are_canonical_and_non_operational():
    """Only canonical ReasonCode.* security events are allowed in reason_code_service."""
    import app.services.reason_code_service as svc_mod

    src = open(svc_mod.__file__, encoding="utf-8").read()
    allowed = {
        'event_type="ReasonCode.CREATED"',
        'event_type="ReasonCode.UPDATED"',
        'event_type="ReasonCode.RELEASED"',
        'event_type="ReasonCode.RETIRED"',
    }
    for marker in allowed:
        assert marker in src, f"Missing canonical ReasonCode event marker: {marker}"

    assert 'event_type="REASONCODE.' not in src, "Legacy REASONCODE.* event naming is forbidden"
