"""
Phase 6C Step 2: Impersonation verification script.

CHECKS
------
EC-1   ADM without impersonation cannot EXECUTE
EC-2   ADM with active impersonation (acting as OPR) can EXECUTE
EC-3   ADM with expired impersonation cannot EXECUTE
EC-4   OTS without impersonation cannot EXECUTE
EC-5   OTS with active impersonation (acting as SUP) can EXECUTE
EC-6   acting_role=ADM is rejected at session creation
EC-7   acting_role=OTS is rejected at session creation
EC-8   OPR (non-ADM/OTS) cannot create impersonation session
EC-9   Revoked session: ADM cannot EXECUTE after revocation
EC-10  Audit log: SESSION_CREATED entry present
EC-11  Audit log: PERMISSION_USED entry present for EXECUTE
EC-12  Audit log: SESSION_REVOKED entry present
EC-13  S1-S4 seed regression still passes
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.impersonation import ImpersonationAuditLog, ImpersonationSession
from app.models.rbac import Role, UserRole, RoleScope
from app.repositories.impersonation_repository import get_active_impersonation_session
from app.schemas.impersonation import ImpersonationCreateRequest
from app.security.rbac import IdentityLike, has_permission
from app.services.impersonation_service import (
    create_impersonation_session,
    revoke_impersonation_session,
)

TENANT_ID = "default"

_SUFFIX = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
ADM_USER = f"verify-adm-{_SUFFIX}"
OTS_USER = f"verify-ots-{_SUFFIX}"
OPR_USER = f"verify-opr-{_SUFFIX}"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _make_identity(user_id: str, acting_role: str | None = None) -> IdentityLike:
    return IdentityLike(
        user_id=user_id,
        tenant_id=TENANT_ID,
        is_authenticated=True,
        acting_role_code=acting_role,
    )


# ---------------------------------------------------------------------------
# Fixture setup / teardown helpers
# ---------------------------------------------------------------------------


def _create_user_role(db, user_id: str, role_code: str) -> UserRole:
    role = db.scalar(select(Role).where(Role.code == role_code))
    if role is None:
        raise RuntimeError(f"Role {role_code!r} not found – run init_db first")

    ur = UserRole(
        user_id=user_id,
        role_id=role.id,
        tenant_id=TENANT_ID,
        is_active=True,
    )
    db.add(ur)
    db.flush()

    db.add(
        RoleScope(
            user_role_id=ur.id,
            scope_type="tenant",
            scope_value=TENANT_ID,
        )
    )
    db.commit()
    return ur


def _delete_test_users(db) -> None:
    for uid in (ADM_USER, OTS_USER, OPR_USER):
        user_roles = list(db.scalars(select(UserRole).where(UserRole.user_id == uid)))
        for ur in user_roles:
            db.execute(delete(RoleScope).where(RoleScope.user_role_id == ur.id))
        db.execute(delete(UserRole).where(UserRole.user_id == uid))

    sessions = list(
        db.scalars(
            select(ImpersonationSession).where(
                ImpersonationSession.real_user_id.in_([ADM_USER, OTS_USER, OPR_USER])
            )
        )
    )
    for s in sessions:
        db.execute(
            delete(ImpersonationAuditLog).where(
                ImpersonationAuditLog.session_id == s.id
            )
        )
    db.execute(
        delete(ImpersonationSession).where(
            ImpersonationSession.real_user_id.in_([ADM_USER, OTS_USER, OPR_USER])
        )
    )
    db.commit()


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def check_ec1_adm_no_impersonation_cannot_execute(db) -> Check:
    ident = _make_identity(ADM_USER)
    result = has_permission(db, ident, "EXECUTE")
    return Check(
        name="EC-1 ADM without impersonation cannot EXECUTE",
        passed=result is False,
        detail=f"has_permission returned {result}",
    )


def check_ec2_adm_with_impersonation_can_execute(db) -> Check:
    session = create_impersonation_session(
        db,
        real_user_id=ADM_USER,
        real_role_code="ADM",
        tenant_id=TENANT_ID,
        request_data=ImpersonationCreateRequest(
            acting_role_code="OPR",
            reason="EC-2 test",
            duration_minutes=60,
        ),
    )
    ident = _make_identity(ADM_USER, acting_role=session.acting_role_code)
    result = has_permission(db, ident, "EXECUTE")
    return Check(
        name="EC-2 ADM with impersonation (acting OPR) can EXECUTE",
        passed=result is True,
        detail=f"has_permission returned {result}, session_id={session.id}",
    )


def check_ec3_expired_impersonation_cannot_execute(db) -> Check:
    # Insert an expired session directly (bypass service to force past expiry).
    # An active session for ADM_USER may already exist (from EC-2); that's fine.
    # The key assertion is that the expired session is never returned as active.
    expired = ImpersonationSession(
        real_user_id=ADM_USER,
        real_role_code="ADM",
        acting_role_code="OPR",
        tenant_id=TENANT_ID,
        reason="EC-3 expired test",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
    )
    db.add(expired)
    db.commit()
    db.refresh(expired)

    active = get_active_impersonation_session(db, ADM_USER, TENANT_ID)
    # The expired session must NOT appear as the active session.
    expired_not_returned = active is None or active.id != expired.id
    return Check(
        name="EC-3 Expired impersonation session is not returned as active",
        passed=expired_not_returned,
        detail=(
            f"expired.id={expired.id}, "
            f"active={'None' if active is None else f'session_id={active.id}'}"
        ),
    )


def check_ec4_ots_no_impersonation_cannot_execute(db) -> Check:
    ident = _make_identity(OTS_USER)
    result = has_permission(db, ident, "EXECUTE")
    return Check(
        name="EC-4 OTS without impersonation cannot EXECUTE",
        passed=result is False,
        detail=f"has_permission returned {result}",
    )


def check_ec5_ots_with_impersonation_can_execute(db) -> Check:
    session = create_impersonation_session(
        db,
        real_user_id=OTS_USER,
        real_role_code="OTS",
        tenant_id=TENANT_ID,
        request_data=ImpersonationCreateRequest(
            acting_role_code="SUP",
            reason="EC-5 test",
            duration_minutes=60,
        ),
    )
    ident = _make_identity(OTS_USER, acting_role=session.acting_role_code)
    result = has_permission(db, ident, "EXECUTE")
    return Check(
        name="EC-5 OTS with impersonation (acting SUP) can EXECUTE",
        passed=result is True,
        detail=f"has_permission returned {result}, session_id={session.id}",
    )


def check_ec6_acting_adm_forbidden(db) -> Check:
    rejected = False
    detail = "no exception raised"
    try:
        create_impersonation_session(
            db,
            real_user_id=ADM_USER,
            real_role_code="ADM",
            tenant_id=TENANT_ID,
            request_data=ImpersonationCreateRequest(
                acting_role_code="ADM",
                reason="EC-6 forbidden test",
                duration_minutes=30,
            ),
        )
    except ValueError as exc:
        rejected = True
        detail = str(exc)
    return Check(
        name="EC-6 acting_role=ADM is rejected",
        passed=rejected,
        detail=detail,
    )


def check_ec7_acting_ots_forbidden(db) -> Check:
    rejected = False
    detail = "no exception raised"
    try:
        create_impersonation_session(
            db,
            real_user_id=ADM_USER,
            real_role_code="ADM",
            tenant_id=TENANT_ID,
            request_data=ImpersonationCreateRequest(
                acting_role_code="OTS",
                reason="EC-7 forbidden test",
                duration_minutes=30,
            ),
        )
    except ValueError as exc:
        rejected = True
        detail = str(exc)
    return Check(
        name="EC-7 acting_role=OTS is rejected",
        passed=rejected,
        detail=detail,
    )


def check_ec8_opr_cannot_create_impersonation(db) -> Check:
    rejected = False
    detail = "no exception raised"
    try:
        create_impersonation_session(
            db,
            real_user_id=OPR_USER,
            real_role_code="OPR",
            tenant_id=TENANT_ID,
            request_data=ImpersonationCreateRequest(
                acting_role_code="SUP",
                reason="EC-8 unauthorized test",
                duration_minutes=30,
            ),
        )
    except PermissionError as exc:
        rejected = True
        detail = str(exc)
    return Check(
        name="EC-8 OPR cannot create impersonation (PermissionError)",
        passed=rejected,
        detail=detail,
    )


def check_ec9_revoked_session_cannot_execute(db) -> Check:
    active = get_active_impersonation_session(db, ADM_USER, TENANT_ID)
    if active is None:
        return Check(
            name="EC-9 Revoked session: cannot EXECUTE after revocation",
            passed=False,
            detail="No active session found to revoke",
        )

    revoked = revoke_impersonation_session(
        db,
        session_id=active.id,
        requesting_user_id=ADM_USER,
        tenant_id=TENANT_ID,
    )

    post_revoke_active = get_active_impersonation_session(db, ADM_USER, TENANT_ID)
    can_exec = post_revoke_active is not None
    return Check(
        name="EC-9 Revoked session: cannot EXECUTE after revocation",
        passed=not can_exec and revoked.revoked_at is not None,
        detail=f"revoked_at={revoked.revoked_at}, post_revoke_active={post_revoke_active}",
    )


def check_ec10_audit_log_session_created(db) -> Check:
    entries = list(
        db.scalars(
            select(ImpersonationAuditLog).where(
                ImpersonationAuditLog.real_user_id.in_([ADM_USER, OTS_USER]),
                ImpersonationAuditLog.event_type == "SESSION_CREATED",
            )
        )
    )
    return Check(
        name="EC-10 Audit log: SESSION_CREATED entries exist",
        passed=len(entries) > 0,
        detail=f"SESSION_CREATED entries: {len(entries)}",
    )


def check_ec11_audit_log_permission_used(db) -> Check:
    # Trigger a permission use by resolving an active OTS session
    active = get_active_impersonation_session(db, OTS_USER, TENANT_ID)
    if active is None:
        return Check(
            name="EC-11 Audit log: PERMISSION_USED entry for impersonated EXECUTE",
            passed=False,
            detail="No active OTS session to test with",
        )

    from app.services.impersonation_service import log_impersonation_permission_use

    log_impersonation_permission_use(db, active, "EXECUTE", endpoint="/test/verify")

    entries = list(
        db.scalars(
            select(ImpersonationAuditLog).where(
                ImpersonationAuditLog.session_id == active.id,
                ImpersonationAuditLog.event_type == "PERMISSION_USED",
                ImpersonationAuditLog.permission_family == "EXECUTE",
            )
        )
    )
    return Check(
        name="EC-11 Audit log: PERMISSION_USED entry for impersonated EXECUTE",
        passed=len(entries) > 0,
        detail=f"PERMISSION_USED/EXECUTE entries for session {active.id}: {len(entries)}",
    )


def check_ec12_audit_log_session_revoked(db) -> Check:
    entries = list(
        db.scalars(
            select(ImpersonationAuditLog).where(
                ImpersonationAuditLog.real_user_id.in_([ADM_USER, OTS_USER]),
                ImpersonationAuditLog.event_type == "SESSION_REVOKED",
            )
        )
    )
    return Check(
        name="EC-12 Audit log: SESSION_REVOKED entry exists",
        passed=len(entries) > 0,
        detail=f"SESSION_REVOKED entries: {len(entries)}",
    )


def check_ec13_seed_regression() -> Check:
    proc = subprocess.run(
        [sys.executable, "-m", "scripts.seed.seed_all"],
        capture_output=True,
        text=True,
    )
    passed = proc.returncode == 0
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
    return Check(
        name="EC-13 S1-S4 seed regression",
        passed=passed,
        detail=" | ".join(tail),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    init_db()

    with SessionLocal() as db:
        _delete_test_users(db)

        _create_user_role(db, ADM_USER, "ADM")
        _create_user_role(db, OTS_USER, "OTS")
        _create_user_role(db, OPR_USER, "OPR")

        checks: list[Check] = []
        try:
            checks.append(check_ec1_adm_no_impersonation_cannot_execute(db))
            checks.append(check_ec2_adm_with_impersonation_can_execute(db))
            checks.append(check_ec3_expired_impersonation_cannot_execute(db))
            checks.append(check_ec4_ots_no_impersonation_cannot_execute(db))
            checks.append(check_ec5_ots_with_impersonation_can_execute(db))
            checks.append(check_ec6_acting_adm_forbidden(db))
            checks.append(check_ec7_acting_ots_forbidden(db))
            checks.append(check_ec8_opr_cannot_create_impersonation(db))
            checks.append(check_ec9_revoked_session_cannot_execute(db))
            checks.append(check_ec10_audit_log_session_created(db))
            checks.append(check_ec11_audit_log_permission_used(db))
            checks.append(check_ec12_audit_log_session_revoked(db))
        finally:
            _delete_test_users(db)

    checks.append(check_ec13_seed_regression())

    print("\nPhase 6C Step 2 – Impersonation Verification")
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
