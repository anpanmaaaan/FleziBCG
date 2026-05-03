"""P0-A-13: Governed resource identity schema foundation tests.

These tests verify that ApprovalRequest model has the new nullable
governed resource identity fields and that backward compatibility
with subject_type/subject_ref is maintained.

No generic approval runtime behavior is implemented in this slice.
No scope-aware rule matching is implemented.
No governed action type enforcement is implemented.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.approval import ApprovalRequest, ApprovalRule, ApprovalDecision, ApprovalAuditLog
from app.models.impersonation import ImpersonationSession
from app.db.base import Base


def _make_session():
    """Create an in-memory SQLite session for isolated tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session_ = sessionmaker(bind=engine)
    return Session_()


def test_approval_request_has_governed_resource_type_field() -> None:
    """P0-A-13: ApprovalRequest model has governed_resource_type nullable field."""
    session = _make_session()
    
    # Create a request with governed_resource_type set
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        requester_role_code="QC_INSPECTOR",
        subject_type="OPERATION",
        subject_ref="OP-123",
        governed_resource_type="OPERATION",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    # Verify field was persisted
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_resource_type == "OPERATION"
    
    session.close()


def test_approval_request_has_governed_resource_id_field() -> None:
    """P0-A-13: ApprovalRequest model has governed_resource_id nullable field."""
    session = _make_session()
    
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        requester_role_code="QC_INSPECTOR",
        governed_resource_id="12345",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_resource_id == "12345"
    
    session.close()


def test_approval_request_has_governed_resource_display_ref_field() -> None:
    """P0-A-13: ApprovalRequest model has governed_resource_display_ref nullable field."""
    session = _make_session()
    
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        governed_resource_display_ref="OP-123-Display",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_resource_display_ref == "OP-123-Display"
    
    session.close()


def test_approval_request_has_governed_resource_tenant_id_field() -> None:
    """P0-A-13: ApprovalRequest model has governed_resource_tenant_id nullable field."""
    session = _make_session()
    
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        governed_resource_tenant_id="tenant1",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_resource_tenant_id == "tenant1"
    
    session.close()


def test_approval_request_has_governed_resource_scope_ref_field() -> None:
    """P0-A-13: ApprovalRequest model has governed_resource_scope_ref nullable field."""
    session = _make_session()
    
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        governed_resource_scope_ref="plant:PLANT1/area:AREA1/line:LINE1",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_resource_scope_ref == "plant:PLANT1/area:AREA1/line:LINE1"
    
    session.close()


def test_approval_request_has_governed_action_type_field() -> None:
    """P0-A-13: ApprovalRequest model has governed_action_type nullable field."""
    session = _make_session()
    
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        governed_action_type="QC_HOLD",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_action_type == "QC_HOLD"
    
    session.close()


def test_governed_resource_fields_are_nullable() -> None:
    """P0-A-13: All governed resource identity fields are nullable."""
    session = _make_session()
    
    # Create a request WITHOUT governed resource fields
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_resource_type is None
    assert retrieved.governed_resource_id is None
    assert retrieved.governed_resource_display_ref is None
    assert retrieved.governed_resource_tenant_id is None
    assert retrieved.governed_resource_scope_ref is None
    assert retrieved.governed_action_type is None
    
    session.close()


def test_subject_type_and_subject_ref_remain_supported() -> None:
    """P0-A-13: Backward compatibility: subject_type and subject_ref remain functional."""
    session = _make_session()
    
    # Create a request with BOTH old and new fields
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        subject_type="OPERATION",  # Old field
        subject_ref="OP-123",  # Old field
        governed_resource_type="OPERATION",  # New field
        governed_resource_id="12345",  # New field
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    # Both old and new fields work
    assert retrieved.subject_type == "OPERATION"
    assert retrieved.subject_ref == "OP-123"
    assert retrieved.governed_resource_type == "OPERATION"
    assert retrieved.governed_resource_id == "12345"
    
    session.close()


def test_existing_approval_without_governed_fields_still_loads() -> None:
    """P0-A-13: Existing requests (without governed fields) load correctly."""
    session = _make_session()
    
    # Simulate old row format (before migration)
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="SCRAP",
        requester_id="user2",
        subject_type="MATERIAL",
        subject_ref="MAT-456",
        reason="Material scrap request",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.action_type == "SCRAP"
    assert retrieved.subject_type == "MATERIAL"
    # New fields should be None (NULL in DB)
    assert retrieved.governed_resource_type is None
    
    session.close()


def test_all_governed_fields_can_be_set_together() -> None:
    """P0-A-13: All governed resource fields can be populated together."""
    session = _make_session()
    
    req = ApprovalRequest(
        tenant_id="tenant1",
        action_type="QC_HOLD",
        requester_id="user1",
        requester_role_code="QC_INSPECTOR",
        governed_resource_type="OPERATION",
        governed_resource_id="op-789",
        governed_resource_display_ref="OP-789-PRD-123",
        governed_resource_tenant_id="tenant1",
        governed_resource_scope_ref="plant:PLANT1/area:AREA1/line:LINE1",
        governed_action_type="QC_HOLD",
        reason="Quality hold",
    )
    session.add(req)
    session.commit()
    
    retrieved = session.query(ApprovalRequest).filter_by(id=req.id).one()
    assert retrieved.governed_resource_type == "OPERATION"
    assert retrieved.governed_resource_id == "op-789"
    assert retrieved.governed_resource_display_ref == "OP-789-PRD-123"
    assert retrieved.governed_resource_tenant_id == "tenant1"
    assert retrieved.governed_resource_scope_ref == "plant:PLANT1/area:AREA1/line:LINE1"
    assert retrieved.governed_action_type == "QC_HOLD"
    
    session.close()
