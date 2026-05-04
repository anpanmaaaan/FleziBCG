"""P0-A-15A: ApprovalRule scope applicability schema foundation tests.

These tests verify that ApprovalRule model has the new nullable scope
applicability fields added in migration 0012, and that backward compatibility
with existing tenant_id + action_type rules is fully maintained.

No scope-aware runtime matching is implemented in this slice.
No governed action type enforcement is implemented.
No API changes are tested here.
"""
from datetime import datetime, timezone

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.models.approval import ApprovalRule
from app.db.base import Base


def _make_session():
    """Create an in-memory SQLite session for isolated schema tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session_ = sessionmaker(bind=engine)
    return Session_(), engine


# ---------------------------------------------------------------------------
# Field existence tests
# ---------------------------------------------------------------------------

def test_approval_rule_has_governed_action_type_field() -> None:
    """P0-A-15A: ApprovalRule has nullable governed_action_type field."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="QC_HOLD",
        approver_role_code="QC_MANAGER",
        tenant_id="tenant1",
        governed_action_type="quality.work_order.qc_hold",
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(tenant_id="tenant1").first()
    assert fetched is not None
    assert fetched.governed_action_type == "quality.work_order.qc_hold"
    session.close()


def test_approval_rule_has_governed_resource_type_field() -> None:
    """P0-A-15A: ApprovalRule has nullable governed_resource_type field."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="SCRAP",
        approver_role_code="PLANT_MANAGER",
        tenant_id="tenant1",
        governed_resource_type="WORK_ORDER",
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(governed_resource_type="WORK_ORDER").first()
    assert fetched is not None
    assert fetched.governed_resource_type == "WORK_ORDER"
    session.close()


def test_approval_rule_has_scope_ref_field() -> None:
    """P0-A-15A: ApprovalRule has nullable scope_ref field."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="REWORK",
        approver_role_code="LINE_SUPERVISOR",
        tenant_id="tenant1",
        scope_ref="plant/01/area/02/line/03",
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(scope_ref="plant/01/area/02/line/03").first()
    assert fetched is not None
    assert fetched.scope_ref == "plant/01/area/02/line/03"
    session.close()


def test_approval_rule_has_scope_type_field() -> None:
    """P0-A-15A: ApprovalRule has nullable scope_type field."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="WO_SPLIT",
        approver_role_code="PLANT_MANAGER",
        tenant_id="tenant1",
        scope_type="plant",
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(scope_type="plant").first()
    assert fetched is not None
    assert fetched.scope_type == "plant"
    session.close()


def test_approval_rule_has_priority_field() -> None:
    """P0-A-15A: ApprovalRule has nullable integer priority field."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="QC_RELEASE",
        approver_role_code="QC_MANAGER",
        tenant_id="tenant1",
        priority=10,
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(priority=10).first()
    assert fetched is not None
    assert fetched.priority == 10
    session.close()


def test_approval_rule_has_effective_from_field() -> None:
    """P0-A-15A: ApprovalRule has nullable effective_from datetime field."""
    session, engine = _make_session()
    dt = datetime(2026, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
    rule = ApprovalRule(
        action_type="QC_HOLD",
        approver_role_code="QC_MANAGER",
        tenant_id="tenant2",
        effective_from=dt,
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(tenant_id="tenant2").first()
    assert fetched is not None
    assert fetched.effective_from is not None
    session.close()


def test_approval_rule_has_effective_to_field() -> None:
    """P0-A-15A: ApprovalRule has nullable effective_to datetime field."""
    session, engine = _make_session()
    dt = datetime(2027, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    rule = ApprovalRule(
        action_type="SCRAP",
        approver_role_code="PLANT_MANAGER",
        tenant_id="tenant3",
        effective_to=dt,
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(tenant_id="tenant3").first()
    assert fetched is not None
    assert fetched.effective_to is not None
    session.close()


# ---------------------------------------------------------------------------
# Nullability / backward compatibility tests
# ---------------------------------------------------------------------------

def test_approval_rule_scope_fields_are_all_nullable() -> None:
    """P0-A-15A: All new scope applicability fields default to None."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="QC_HOLD",
        approver_role_code="QC_MANAGER",
        tenant_id="tenant-legacy",
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(tenant_id="tenant-legacy").first()
    assert fetched is not None
    assert fetched.governed_action_type is None
    assert fetched.governed_resource_type is None
    assert fetched.scope_ref is None
    assert fetched.scope_type is None
    assert fetched.priority is None
    assert fetched.effective_from is None
    assert fetched.effective_to is None
    session.close()


def test_existing_approval_rule_fields_remain_unchanged() -> None:
    """P0-A-15A: Existing fields (action_type, approver_role_code, tenant_id, is_active) are present."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="REWORK",
        approver_role_code="QUALITY_LEAD",
        tenant_id="acme",
        is_active=True,
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(tenant_id="acme").first()
    assert fetched is not None
    assert fetched.action_type == "REWORK"
    assert fetched.approver_role_code == "QUALITY_LEAD"
    assert fetched.tenant_id == "acme"
    assert fetched.is_active is True
    session.close()


def test_wildcard_tenant_rule_valid_at_schema_level() -> None:
    """P0-A-15A: Wildcard '*' tenant rule remains valid with new nullable scope fields."""
    session, engine = _make_session()
    rule = ApprovalRule(
        action_type="QC_HOLD",
        approver_role_code="QC_MANAGER",
        tenant_id="*",
    )
    session.add(rule)
    session.commit()
    fetched = session.query(ApprovalRule).filter_by(tenant_id="*").first()
    assert fetched is not None
    assert fetched.tenant_id == "*"
    assert fetched.scope_ref is None
    assert fetched.governed_action_type is None
    session.close()


def test_approval_rule_scope_columns_exist_in_db_schema() -> None:
    """P0-A-15A: Migration adds scope applicability columns to approval_rules table."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("approval_rules")}
    expected_new = {
        "governed_action_type",
        "governed_resource_type",
        "scope_ref",
        "scope_type",
        "priority",
        "effective_from",
        "effective_to",
    }
    for col in expected_new:
        assert col in columns, f"Expected column '{col}' in approval_rules but not found"


def test_no_scope_aware_matching_implemented() -> None:
    """P0-A-15A: Confirm that approval_repository does not perform scope-aware matching.

    This is a source-level contract test: inspect that get_rules_for_action
    only filters by action_type and tenant_id, not scope fields.
    """
    import inspect as pyinspect
    from app.repositories import approval_repository
    source = pyinspect.getsource(approval_repository.get_rules_for_action)
    # scope_ref, governed_action_type, governed_resource_type must NOT appear in matching logic
    assert "scope_ref" not in source, "scope_ref MUST NOT be in get_rules_for_action in P0-A-15A"
    assert "governed_action_type" not in source, \
        "governed_action_type MUST NOT be used in runtime matching in P0-A-15A"
    # Legacy matching dimensions must still be present
    assert "action_type" in source
    assert "tenant_id" in source
