"""
Verify PLN (Planner) and INV (Inventory) roles exist and are execution-denied.

CHECKS
------
RI-1   PLN role exists in SYSTEM_ROLE_FAMILIES with VIEW only
RI-2   INV role exists in SYSTEM_ROLE_FAMILIES with VIEW only
RI-3   PLN cannot execute (has_permission EXECUTE → False)
RI-4   INV cannot execute (has_permission EXECUTE → False)
RI-5   PLN cannot start operation (has_action execution.start → False)
RI-6   INV cannot start operation (has_action execution.start → False)
RI-7   PLN cannot report quantity (has_action execution.report_quantity → False)
RI-8   INV cannot report quantity (has_action execution.report_quantity → False)
RI-9   PLN cannot complete operation (has_action execution.complete → False)
RI-10  INV cannot complete operation (has_action execution.complete → False)
RI-11  PLN can view (has_permission VIEW → True)
RI-12  INV can view (has_permission VIEW → True)
RI-13  OPR still has EXECUTE (regression check)
RI-14  SUP still has EXECUTE (regression check)
RI-15  PLN role alias resolves correctly
RI-16  INV role alias resolves correctly
RI-17  PLN demo user seeded
RI-18  INV demo user seeded
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from sqlalchemy import select

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.user import User
from app.security.rbac import (
    SYSTEM_ROLE_FAMILIES,
    IdentityLike,
    has_action,
    has_permission,
    normalize_role_code,
)

TENANT_ID = "default"


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _make_identity(user_id: str, acting_role_code: str | None = None) -> IdentityLike:
    return IdentityLike(
        user_id=user_id,
        tenant_id=TENANT_ID,
        is_authenticated=True,
        acting_role_code=acting_role_code,
    )


def check_ri1_pln_exists() -> Check:
    families = SYSTEM_ROLE_FAMILIES.get("PLN")
    ok = families is not None and families == {"VIEW"}
    return Check(
        name="RI-1 PLN role exists with VIEW only",
        passed=ok,
        detail=f"PLN families={families}",
    )


def check_ri2_inv_exists() -> Check:
    families = SYSTEM_ROLE_FAMILIES.get("INV")
    ok = families is not None and families == {"VIEW"}
    return Check(
        name="RI-2 INV role exists with VIEW only",
        passed=ok,
        detail=f"INV families={families}",
    )


def check_ri3_pln_no_execute(db) -> Check:
    identity = _make_identity("pln-001", acting_role_code="PLN")
    result = has_permission(db, identity, "EXECUTE")
    return Check(
        name="RI-3 PLN cannot execute",
        passed=not result,
        detail=f"has_permission EXECUTE={result}",
    )


def check_ri4_inv_no_execute(db) -> Check:
    identity = _make_identity("inv-001", acting_role_code="INV")
    result = has_permission(db, identity, "EXECUTE")
    return Check(
        name="RI-4 INV cannot execute",
        passed=not result,
        detail=f"has_permission EXECUTE={result}",
    )


def check_ri5_pln_no_start(db) -> Check:
    identity = _make_identity("pln-001", acting_role_code="PLN")
    result = has_action(db, identity, "execution.start")
    return Check(
        name="RI-5 PLN cannot start operation",
        passed=not result,
        detail=f"has_action execution.start={result}",
    )


def check_ri6_inv_no_start(db) -> Check:
    identity = _make_identity("inv-001", acting_role_code="INV")
    result = has_action(db, identity, "execution.start")
    return Check(
        name="RI-6 INV cannot start operation",
        passed=not result,
        detail=f"has_action execution.start={result}",
    )


def check_ri7_pln_no_report(db) -> Check:
    identity = _make_identity("pln-001", acting_role_code="PLN")
    result = has_action(db, identity, "execution.report_quantity")
    return Check(
        name="RI-7 PLN cannot report quantity",
        passed=not result,
        detail=f"has_action execution.report_quantity={result}",
    )


def check_ri8_inv_no_report(db) -> Check:
    identity = _make_identity("inv-001", acting_role_code="INV")
    result = has_action(db, identity, "execution.report_quantity")
    return Check(
        name="RI-8 INV cannot report quantity",
        passed=not result,
        detail=f"has_action execution.report_quantity={result}",
    )


def check_ri9_pln_no_complete(db) -> Check:
    identity = _make_identity("pln-001", acting_role_code="PLN")
    result = has_action(db, identity, "execution.complete")
    return Check(
        name="RI-9 PLN cannot complete operation",
        passed=not result,
        detail=f"has_action execution.complete={result}",
    )


def check_ri10_inv_no_complete(db) -> Check:
    identity = _make_identity("inv-001", acting_role_code="INV")
    result = has_action(db, identity, "execution.complete")
    return Check(
        name="RI-10 INV cannot complete operation",
        passed=not result,
        detail=f"has_action execution.complete={result}",
    )


def check_ri11_pln_can_view(db) -> Check:
    identity = _make_identity("pln-001", acting_role_code="PLN")
    result = has_permission(db, identity, "VIEW")
    return Check(
        name="RI-11 PLN can view",
        passed=result,
        detail=f"has_permission VIEW={result}",
    )


def check_ri12_inv_can_view(db) -> Check:
    identity = _make_identity("inv-001", acting_role_code="INV")
    result = has_permission(db, identity, "VIEW")
    return Check(
        name="RI-12 INV can view",
        passed=result,
        detail=f"has_permission VIEW={result}",
    )


def check_ri13_opr_still_execute(db) -> Check:
    identity = _make_identity("opr-001", acting_role_code="OPR")
    result = has_permission(db, identity, "EXECUTE")
    return Check(
        name="RI-13 OPR still has EXECUTE (regression)",
        passed=result,
        detail=f"has_permission EXECUTE={result}",
    )


def check_ri14_sup_still_execute(db) -> Check:
    identity = _make_identity("sup-001", acting_role_code="SUP")
    result = has_permission(db, identity, "EXECUTE")
    return Check(
        name="RI-14 SUP still has EXECUTE (regression)",
        passed=result,
        detail=f"has_permission EXECUTE={result}",
    )


def check_ri15_pln_alias() -> Check:
    result = normalize_role_code("PLANNER")
    return Check(
        name="RI-15 PLN alias resolves",
        passed=result == "PLN",
        detail=f"normalize_role_code('PLANNER')={result}",
    )


def check_ri16_inv_alias() -> Check:
    result = normalize_role_code("INVENTORY")
    return Check(
        name="RI-16 INV alias resolves",
        passed=result == "INV",
        detail=f"normalize_role_code('INVENTORY')={result}",
    )


def check_ri17_pln_demo_user(db) -> Check:
    user = db.scalar(select(User).where(User.user_id == "pln-001"))
    return Check(
        name="RI-17 PLN demo user seeded",
        passed=user is not None,
        detail=f"user={'found' if user else 'missing'}",
    )


def check_ri18_inv_demo_user(db) -> Check:
    user = db.scalar(select(User).where(User.user_id == "inv-001"))
    return Check(
        name="RI-18 INV demo user seeded",
        passed=user is not None,
        detail=f"user={'found' if user else 'missing'}",
    )


def main() -> None:
    init_db()
    db = SessionLocal()

    checks: list[Check] = []

    # Static checks (no DB needed)
    checks.append(check_ri1_pln_exists())
    checks.append(check_ri2_inv_exists())
    checks.append(check_ri15_pln_alias())
    checks.append(check_ri16_inv_alias())

    # DB-backed checks
    checks.append(check_ri3_pln_no_execute(db))
    checks.append(check_ri4_inv_no_execute(db))
    checks.append(check_ri5_pln_no_start(db))
    checks.append(check_ri6_inv_no_start(db))
    checks.append(check_ri7_pln_no_report(db))
    checks.append(check_ri8_inv_no_report(db))
    checks.append(check_ri9_pln_no_complete(db))
    checks.append(check_ri10_inv_no_complete(db))
    checks.append(check_ri11_pln_can_view(db))
    checks.append(check_ri12_inv_can_view(db))
    checks.append(check_ri13_opr_still_execute(db))
    checks.append(check_ri14_sup_still_execute(db))
    checks.append(check_ri17_pln_demo_user(db))
    checks.append(check_ri18_inv_demo_user(db))

    db.close()

    print("\n" + "=" * 60)
    print("PLN / INV Role Verification")
    print("=" * 60)

    passed = 0
    failed = 0
    for c in checks:
        status = "PASS" if c.passed else "FAIL"
        icon = "✅" if c.passed else "❌"
        print(f"  {icon} [{status}] {c.name}")
        if not c.passed:
            print(f"         Detail: {c.detail}")
            failed += 1
        else:
            passed += 1

    print(f"\nTotal: {passed} passed, {failed} failed out of {len(checks)}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    print("\nAll checks PASSED ✅")


if __name__ == "__main__":
    main()
