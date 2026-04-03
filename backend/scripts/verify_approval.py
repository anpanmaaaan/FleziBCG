"""
Phase 6C Step 3: Approval Engine verification script.

CHECKS
------
AP-1  Correct approver (QAL) can approve a QC_HOLD request
AP-2  Requester cannot approve their own request
AP-3  Wrong role (OPR) cannot decide a QC_HOLD request
AP-4  ADM impersonating QAL cannot approve their own request
AP-5  OTS impersonating QAL can approve another user's request
AP-6  Already-decided request cannot be re-decided
AP-7  Unknown action_type is rejected at request creation
AP-8  PMG can approve SCRAP (multi-role rule)
AP-9  QAL cannot approve WO_SPLIT (PMG only)
AP-10 Audit log: REQUEST_CREATED entries exist
AP-11 Audit log: DECISION_MADE entries exist
AP-12 S1-S4 seed regression still passes
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.approval import ApprovalAuditLog, ApprovalDecision, ApprovalRequest
from app.models.impersonation import ImpersonationAuditLog, ImpersonationSession
from app.models.rbac import Role, RoleScope, UserRole
from app.repositories.approval_repository import get_audit_logs_for_request
from app.schemas.approval import ApprovalCreateRequest, ApprovalDecideRequest
from app.schemas.impersonation import ImpersonationCreateRequest
from app.security.rbac import IdentityLike, has_permission
from app.services.approval_service import (
    create_approval_request,
    decide_approval_request,
)
from app.services.impersonation_service import create_impersonation_session

TENANT_ID = "default"

_SUFFIX = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
ADM_USER = f"verify-ap-adm-{_SUFFIX}"
OTS_USER = f"verify-ap-ots-{_SUFFIX}"
OPR_USER = f"verify-ap-opr-{_SUFFIX}"
QAL_USER = f"verify-ap-qal-{_SUFFIX}"
PMG_USER = f"verify-ap-pmg-{_SUFFIX}"

_ALL_USERS = (ADM_USER, OTS_USER, OPR_USER, QAL_USER, PMG_USER)


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


# ---------------------------------------------------------------------------
# Shared state across checks (populated in check functions)
# ---------------------------------------------------------------------------
_ap1_request_id: int | None = None  # used by AP-6 (re-decide)
_ap_audit_request_ids: list[int] = []  # collected for AP-10/AP-11


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _create_user_role(db, user_id: str, role_code: str) -> UserRole:
    role = db.scalar(select(Role).where(Role.code == role_code))
    if role is None:
        raise RuntimeError(f"Role {role_code!r} not found — run init_db first")
    ur = UserRole(user_id=user_id, role_id=role.id, tenant_id=TENANT_ID, is_active=True)
    db.add(ur)
    db.flush()
    db.add(RoleScope(user_role_id=ur.id, scope_type="tenant", scope_value=TENANT_ID))
    db.commit()
    return ur


def _delete_test_data(db) -> None:
    # Delete approval requests for test users first (cascades to decisions and audit_logs).
    test_requests = list(
        db.scalars(
            select(ApprovalRequest).where(
                ApprovalRequest.requester_id.in_(_ALL_USERS)
            )
        )
    )
    for req in test_requests:
        db.execute(delete(ApprovalAuditLog).where(ApprovalAuditLog.request_id == req.id))
        db.execute(delete(ApprovalDecision).where(ApprovalDecision.request_id == req.id))
    db.execute(
        delete(ApprovalRequest).where(ApprovalRequest.requester_id.in_(_ALL_USERS))
    )

    # Delete impersonation sessions for test users (cascades to impersonation_audit_logs).
    sessions = list(
        db.scalars(
            select(ImpersonationSession).where(
                ImpersonationSession.real_user_id.in_(_ALL_USERS)
            )
        )
    )
    for s in sessions:
        db.execute(delete(ImpersonationAuditLog).where(ImpersonationAuditLog.session_id == s.id))
    db.execute(
        delete(ImpersonationSession).where(
            ImpersonationSession.real_user_id.in_(_ALL_USERS)
        )
    )

    # Delete user roles and scopes.
    for uid in _ALL_USERS:
        user_roles = list(db.scalars(select(UserRole).where(UserRole.user_id == uid)))
        for ur in user_roles:
            db.execute(delete(RoleScope).where(RoleScope.user_role_id == ur.id))
        db.execute(delete(UserRole).where(UserRole.user_id == uid))

    db.commit()


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_ap1_correct_approver_can_approve(db) -> Check:
    global _ap1_request_id
    req = create_approval_request(
        db,
        requester_id=OPR_USER,
        requester_role_code="OPR",
        tenant_id=TENANT_ID,
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            reason="AP-1 test: normal QC hold request",
        ),
    )
    _ap1_request_id = req.id
    _ap_audit_request_ids.append(req.id)

    decision = decide_approval_request(
        db,
        request_id=req.id,
        decider_user_id=QAL_USER,
        decider_role_code="QAL",
        tenant_id=TENANT_ID,
        decide_data=ApprovalDecideRequest(decision="APPROVED", comment="AP-1 approve"),
    )
    return Check(
        name="AP-1 Correct approver (QAL) can approve a QC_HOLD request",
        passed=decision.decision == "APPROVED" and decision.decider_id == QAL_USER,
        detail=f"decision={decision.decision} decider={decision.decider_id}",
    )


def check_ap2_requester_cannot_approve_own(db) -> Check:
    req = create_approval_request(
        db,
        requester_id=OPR_USER,
        requester_role_code="OPR",
        tenant_id=TENANT_ID,
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            reason="AP-2 test: self-approval attempt",
        ),
    )
    _ap_audit_request_ids.append(req.id)

    rejected = False
    detail = "no exception raised"
    try:
        decide_approval_request(
            db,
            request_id=req.id,
            decider_user_id=OPR_USER,  # same as requester
            decider_role_code="OPR",
            tenant_id=TENANT_ID,
            decide_data=ApprovalDecideRequest(decision="APPROVED"),
        )
    except ValueError as exc:
        rejected = True
        detail = str(exc)
    return Check(
        name="AP-2 Requester cannot approve their own request",
        passed=rejected,
        detail=detail,
    )


def check_ap3_wrong_role_cannot_decide(db) -> Check:
    req = create_approval_request(
        db,
        requester_id=QAL_USER,
        requester_role_code="QAL",
        tenant_id=TENANT_ID,
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            reason="AP-3 test: wrong role attempt",
        ),
    )
    _ap_audit_request_ids.append(req.id)

    # Also confirm OPR has no APPROVE RBAC permission.
    opr_ident = IdentityLike(user_id=OPR_USER, tenant_id=TENANT_ID, is_authenticated=True)
    opr_has_approve = has_permission(db, opr_ident, "APPROVE")

    rejected = False
    detail = "no exception raised"
    try:
        decide_approval_request(
            db,
            request_id=req.id,
            decider_user_id=OPR_USER,
            decider_role_code="OPR",
            tenant_id=TENANT_ID,
            decide_data=ApprovalDecideRequest(decision="APPROVED"),
        )
    except PermissionError as exc:
        rejected = True
        detail = f"opr_has_approve={opr_has_approve} | {exc}"
    return Check(
        name="AP-3 Wrong role (OPR) cannot decide a QC_HOLD request",
        passed=rejected and not opr_has_approve,
        detail=detail,
    )


def check_ap4_impersonation_self_approval_blocked(db) -> Check:
    # ADM_USER creates a request.
    req = create_approval_request(
        db,
        requester_id=ADM_USER,
        requester_role_code="ADM",
        tenant_id=TENANT_ID,
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            reason="AP-4 test: impersonation self-approval",
        ),
    )
    _ap_audit_request_ids.append(req.id)

    # ADM_USER impersonates QAL — acting_role="QAL" — but remains real user ADM_USER.
    imp_session = create_impersonation_session(
        db,
        real_user_id=ADM_USER,
        real_role_code="ADM",
        tenant_id=TENANT_ID,
        request_data=ImpersonationCreateRequest(
            acting_role_code="QAL",
            reason="AP-4 impersonation test",
            duration_minutes=60,
        ),
    )

    rejected = False
    detail = "no exception raised"
    try:
        # Even though acting_role_code="QAL", decider_user_id==requester_id → blocked.
        decide_approval_request(
            db,
            request_id=req.id,
            decider_user_id=ADM_USER,       # real user_id — same as requester
            decider_role_code="QAL",        # acting role via impersonation
            tenant_id=TENANT_ID,
            decide_data=ApprovalDecideRequest(decision="APPROVED"),
            impersonation_session_id=imp_session.id,
        )
    except ValueError as exc:
        rejected = True
        detail = f"session_id={imp_session.id} | {exc}"
    return Check(
        name="AP-4 ADM impersonating QAL cannot approve their own request",
        passed=rejected,
        detail=detail,
    )


def check_ap5_impersonation_different_user_can_decide(db) -> Check:
    # OPR_USER creates a QC_HOLD request.
    req = create_approval_request(
        db,
        requester_id=OPR_USER,
        requester_role_code="OPR",
        tenant_id=TENANT_ID,
        request_data=ApprovalCreateRequest(
            action_type="QC_HOLD",
            reason="AP-5 test: OTS impersonating QAL approves OPR request",
        ),
    )
    _ap_audit_request_ids.append(req.id)

    # OTS_USER impersonates QAL.
    imp_session = create_impersonation_session(
        db,
        real_user_id=OTS_USER,
        real_role_code="OTS",
        tenant_id=TENANT_ID,
        request_data=ImpersonationCreateRequest(
            acting_role_code="QAL",
            reason="AP-5 impersonation test",
            duration_minutes=60,
        ),
    )

    decision = decide_approval_request(
        db,
        request_id=req.id,
        decider_user_id=OTS_USER,           # real user — different from OPR_USER ✓
        decider_role_code="QAL",            # acting role via impersonation
        tenant_id=TENANT_ID,
        decide_data=ApprovalDecideRequest(
            decision="APPROVED", comment="AP-5 impersonated approve"
        ),
        impersonation_session_id=imp_session.id,
    )
    return Check(
        name="AP-5 OTS impersonating QAL can approve another user's request",
        passed=(
            decision.decision == "APPROVED"
            and decision.decider_id == OTS_USER
            and decision.impersonation_session_id == imp_session.id
        ),
        detail=(
            f"decision={decision.decision} decider={decision.decider_id} "
            f"session={decision.impersonation_session_id}"
        ),
    )


def check_ap6_cannot_redecide_already_decided(db) -> Check:
    if _ap1_request_id is None:
        return Check(
            name="AP-6 Already-decided request cannot be re-decided",
            passed=False,
            detail="AP-1 did not run or failed to capture request_id",
        )
    rejected = False
    detail = "no exception raised"
    try:
        decide_approval_request(
            db,
            request_id=_ap1_request_id,
            decider_user_id=QAL_USER,
            decider_role_code="QAL",
            tenant_id=TENANT_ID,
            decide_data=ApprovalDecideRequest(decision="REJECTED"),
        )
    except ValueError as exc:
        rejected = True
        detail = str(exc)
    return Check(
        name="AP-6 Already-decided request cannot be re-decided",
        passed=rejected,
        detail=detail,
    )


def check_ap7_unknown_action_type_rejected(db) -> Check:
    rejected = False
    detail = "no exception raised"
    try:
        create_approval_request(
            db,
            requester_id=OPR_USER,
            requester_role_code="OPR",
            tenant_id=TENANT_ID,
            request_data=ApprovalCreateRequest(
                action_type="INVALID_THING",
                reason="AP-7 invalid action type test",
            ),
        )
    except ValueError as exc:
        rejected = True
        detail = str(exc)
    return Check(
        name="AP-7 Unknown action_type is rejected at request creation",
        passed=rejected,
        detail=detail,
    )


def check_ap8_pmg_can_approve_scrap(db) -> Check:
    req = create_approval_request(
        db,
        requester_id=OPR_USER,
        requester_role_code="OPR",
        tenant_id=TENANT_ID,
        request_data=ApprovalCreateRequest(
            action_type="SCRAP",
            reason="AP-8 test: PMG approves SCRAP",
        ),
    )
    _ap_audit_request_ids.append(req.id)

    decision = decide_approval_request(
        db,
        request_id=req.id,
        decider_user_id=PMG_USER,
        decider_role_code="PMG",
        tenant_id=TENANT_ID,
        decide_data=ApprovalDecideRequest(decision="APPROVED"),
    )
    return Check(
        name="AP-8 PMG can approve SCRAP (multi-role rule)",
        passed=decision.decision == "APPROVED" and decision.decider_id == PMG_USER,
        detail=f"decision={decision.decision} decider={decision.decider_id}",
    )


def check_ap9_qal_cannot_approve_wo_split(db) -> Check:
    req = create_approval_request(
        db,
        requester_id=OPR_USER,
        requester_role_code="OPR",
        tenant_id=TENANT_ID,
        request_data=ApprovalCreateRequest(
            action_type="WO_SPLIT",
            reason="AP-9 test: QAL tries WO_SPLIT (PMG only)",
        ),
    )
    _ap_audit_request_ids.append(req.id)

    rejected = False
    detail = "no exception raised"
    try:
        decide_approval_request(
            db,
            request_id=req.id,
            decider_user_id=QAL_USER,
            decider_role_code="QAL",
            tenant_id=TENANT_ID,
            decide_data=ApprovalDecideRequest(decision="APPROVED"),
        )
    except PermissionError as exc:
        rejected = True
        detail = str(exc)
    return Check(
        name="AP-9 QAL cannot approve WO_SPLIT (PMG only)",
        passed=rejected,
        detail=detail,
    )


def check_ap10_audit_request_created(db) -> Check:
    if not _ap_audit_request_ids:
        return Check(
            name="AP-10 Audit log: REQUEST_CREATED entries exist",
            passed=False,
            detail="No request IDs collected",
        )
    entries = list(
        db.scalars(
            select(ApprovalAuditLog).where(
                ApprovalAuditLog.request_id.in_(_ap_audit_request_ids),
                ApprovalAuditLog.event_type == "REQUEST_CREATED",
            )
        )
    )
    return Check(
        name="AP-10 Audit log: REQUEST_CREATED entries exist",
        passed=len(entries) > 0,
        detail=f"REQUEST_CREATED entries: {len(entries)}",
    )


def check_ap11_audit_decision_made(db) -> Check:
    if not _ap_audit_request_ids:
        return Check(
            name="AP-11 Audit log: DECISION_MADE entries exist",
            passed=False,
            detail="No request IDs collected",
        )
    entries = list(
        db.scalars(
            select(ApprovalAuditLog).where(
                ApprovalAuditLog.request_id.in_(_ap_audit_request_ids),
                ApprovalAuditLog.event_type == "DECISION_MADE",
            )
        )
    )
    return Check(
        name="AP-11 Audit log: DECISION_MADE entries exist",
        passed=len(entries) > 0,
        detail=f"DECISION_MADE entries: {len(entries)}",
    )


def check_ap12_seed_regression() -> Check:
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.seed.seed_all"],
        capture_output=True,
        text=True,
    )
    passed = proc.returncode == 0
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
    return Check(
        name="AP-12 S1-S4 seed regression",
        passed=passed,
        detail=" | ".join(tail),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    init_db()

    with SessionLocal() as db:
        _delete_test_data(db)

        _create_user_role(db, ADM_USER, "ADM")
        _create_user_role(db, OTS_USER, "OTS")
        _create_user_role(db, OPR_USER, "OPR")
        _create_user_role(db, QAL_USER, "QAL")
        _create_user_role(db, PMG_USER, "PMG")

        checks: list[Check] = []
        try:
            checks.append(check_ap1_correct_approver_can_approve(db))
            checks.append(check_ap2_requester_cannot_approve_own(db))
            checks.append(check_ap3_wrong_role_cannot_decide(db))
            checks.append(check_ap4_impersonation_self_approval_blocked(db))
            checks.append(check_ap5_impersonation_different_user_can_decide(db))
            checks.append(check_ap6_cannot_redecide_already_decided(db))
            checks.append(check_ap7_unknown_action_type_rejected(db))
            checks.append(check_ap8_pmg_can_approve_scrap(db))
            checks.append(check_ap9_qal_cannot_approve_wo_split(db))
            checks.append(check_ap10_audit_request_created(db))
            checks.append(check_ap11_audit_decision_made(db))
        finally:
            _delete_test_data(db)

    checks.append(check_ap12_seed_regression())

    print("\nPhase 6C Step 3 – Approval Engine Verification")
    print("=" * 60)
    for check in checks:
        state = "PASS" if check.passed else "FAIL"
        print(f"[{state}] {check.name}")
        print(f"       {check.detail}")

    failed = [c for c in checks if not c.passed]
    print()
    if failed:
        print(f"FAILED: {len(failed)}/{len(checks)} checks")
        raise SystemExit(1)

    print(f"All {len(checks)} checks passed.")


if __name__ == "__main__":
    main()
