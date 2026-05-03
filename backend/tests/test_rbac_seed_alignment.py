"""P0-A-08: RBAC Seed Alignment Tests

Tests that seed_rbac_core() produces the correct Permission and RolePermission
rows for all action codes in ACTION_CODE_REGISTRY, aligned with the
SYSTEM_ROLE_FAMILIES role/family model.

These tests run against an in-memory SQLite database — no live Postgres needed.
User-assignment seeding (_load_default_users) is isolated by patching so that
tests focus purely on Permission/RolePermission contract.

Source-of-truth precedence:
  1. backend/app/security/rbac.py ACTION_CODE_REGISTRY — runtime action registry
  2. backend/app/security/rbac.py SYSTEM_ROLE_FAMILIES — role/family model
  3. docs/design/02_registry/action-code-registry.md — governance record

P0-A-07B: admin.downtime_reason.manage added, verified here.
P0-A-07C: admin.security_event.read added, verified here.
P0-A-07D: admin.impersonation.create / admin.impersonation.revoke wired, verified here.
"""

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

import app.security.rbac as rbac_module
from app.models.rbac import (
    Permission,
    Role,
    RolePermission,
    RoleScope,
    Scope,
    UserRole,
    UserRoleAssignment,
)
from app.security.rbac import (
    ACTION_CODE_REGISTRY,
    SYSTEM_ROLE_FAMILIES,
    seed_rbac_core,
)

# ---------------------------------------------------------------------------
# Derived constants — computed from source, never hardcoded
# ---------------------------------------------------------------------------

_ADMIN_FAMILY_ACTION_CODES = frozenset(
    code for code, family in ACTION_CODE_REGISTRY.items() if family == "ADMIN"
)
_EXECUTE_FAMILY_ACTION_CODES = frozenset(
    code for code, family in ACTION_CODE_REGISTRY.items() if family == "EXECUTE"
)
_APPROVE_FAMILY_ACTION_CODES = frozenset(
    code for code, family in ACTION_CODE_REGISTRY.items() if family == "APPROVE"
)

# Expected action-level RolePermission count per role:
# For each role, count action codes whose family is in that role's allowed families.
_EXPECTED_ACTION_ROLE_PERMISSION_COUNT: dict[str, int] = {
    role_code: sum(
        1
        for _code, fam in ACTION_CODE_REGISTRY.items()
        if fam in families
    )
    for role_code, families in SYSTEM_ROLE_FAMILIES.items()
}

# Expected family-level RolePermission count per role:
_EXPECTED_FAMILY_ROLE_PERMISSION_COUNT: dict[str, int] = {
    role_code: len(families)
    for role_code, families in SYSTEM_ROLE_FAMILIES.items()
}


# ---------------------------------------------------------------------------
# DB fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def seeded_db(monkeypatch) -> Session:
    """In-memory SQLite DB with RBAC tables created and seed_rbac_core() run.

    _load_default_users is patched to [] to isolate Permission/RolePermission
    seeding from user-assignment seeding. This keeps the fixture minimal and
    avoids importing unrelated models (User, etc.).
    """
    # Isolate user-assignment path
    monkeypatch.setattr(rbac_module, "_load_default_users", lambda: [])

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Role.__table__.create(bind=engine)
    Permission.__table__.create(bind=engine)
    RolePermission.__table__.create(bind=engine)
    Scope.__table__.create(bind=engine)
    UserRole.__table__.create(bind=engine)
    RoleScope.__table__.create(bind=engine)
    UserRoleAssignment.__table__.create(bind=engine)

    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = session_factory()
    seed_rbac_core(db)
    db.commit()
    return db


# ---------------------------------------------------------------------------
# Permission rows: all action codes present
# ---------------------------------------------------------------------------


def test_seed_creates_permission_row_for_every_action_code(seeded_db: Session) -> None:
    """Every action code in ACTION_CODE_REGISTRY must have a Permission row."""
    for action_code in ACTION_CODE_REGISTRY:
        row = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert row is not None, (
            f"Permission row missing for action code '{action_code}'. "
            f"seed_rbac_core() must create a Permission row for every "
            f"ACTION_CODE_REGISTRY entry."
        )


def test_seed_permission_family_matches_registry(seeded_db: Session) -> None:
    """Every Permission row's family must match ACTION_CODE_REGISTRY[action_code]."""
    for action_code, expected_family in ACTION_CODE_REGISTRY.items():
        row = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert row is not None, f"Permission row missing for '{action_code}'"
        assert row.family == expected_family, (
            f"Permission '{action_code}' has family '{row.family}', "
            f"expected '{expected_family}' per ACTION_CODE_REGISTRY."
        )


def test_seed_permission_action_code_field_set(seeded_db: Session) -> None:
    """action_code field on Permission row must equal the code, not None."""
    for action_code in ACTION_CODE_REGISTRY:
        row = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert row is not None, f"Permission row missing for '{action_code}'"
        assert row.action_code == action_code, (
            f"Permission '{action_code}' has action_code='{row.action_code}', "
            f"expected the action code string itself."
        )


def test_seed_creates_exactly_one_permission_per_action_code(seeded_db: Session) -> None:
    """Each action code must have exactly one Permission row — no duplicates."""
    for action_code in ACTION_CODE_REGISTRY:
        count = seeded_db.scalar(
            select(func.count()).select_from(Permission).where(Permission.code == action_code)
        )
        assert count == 1, (
            f"Expected 1 Permission row for '{action_code}', got {count}. "
            f"Possible duplicate from non-idempotent seed."
        )


# ---------------------------------------------------------------------------
# P0-A-07B/07C/07D: specific action codes from resolved GAPs
# ---------------------------------------------------------------------------


def test_seed_p0a07b_downtime_reason_manage_permission_exists(seeded_db: Session) -> None:
    """GAP-1 (P0-A-07B): admin.downtime_reason.manage must have a Permission row
    with ADMIN family. This code was added in P0-A-07B."""
    row = seeded_db.scalar(
        select(Permission).where(Permission.code == "admin.downtime_reason.manage")
    )
    assert row is not None, "Permission row missing for admin.downtime_reason.manage"
    assert row.family == "ADMIN"
    assert row.action_code == "admin.downtime_reason.manage"


def test_seed_p0a07c_security_event_read_permission_exists(seeded_db: Session) -> None:
    """GAP-2 (P0-A-07C): admin.security_event.read must have a Permission row
    with ADMIN family. This code was added in P0-A-07C."""
    row = seeded_db.scalar(
        select(Permission).where(Permission.code == "admin.security_event.read")
    )
    assert row is not None, "Permission row missing for admin.security_event.read"
    assert row.family == "ADMIN"
    assert row.action_code == "admin.security_event.read"


def test_seed_p0a07d_impersonation_create_permission_exists(seeded_db: Session) -> None:
    """GAP-3 (P0-A-07D): admin.impersonation.create must have a Permission row
    with ADMIN family."""
    row = seeded_db.scalar(
        select(Permission).where(Permission.code == "admin.impersonation.create")
    )
    assert row is not None, "Permission row missing for admin.impersonation.create"
    assert row.family == "ADMIN"
    assert row.action_code == "admin.impersonation.create"


def test_seed_p0a07d_impersonation_revoke_permission_exists(seeded_db: Session) -> None:
    """GAP-3 (P0-A-07D): admin.impersonation.revoke must have a Permission row
    with ADMIN family."""
    row = seeded_db.scalar(
        select(Permission).where(Permission.code == "admin.impersonation.revoke")
    )
    assert row is not None, "Permission row missing for admin.impersonation.revoke"
    assert row.family == "ADMIN"
    assert row.action_code == "admin.impersonation.revoke"


# ---------------------------------------------------------------------------
# System roles
# ---------------------------------------------------------------------------


def test_seed_creates_all_system_roles(seeded_db: Session) -> None:
    """All role codes in SYSTEM_ROLE_FAMILIES must have a Role row after seed."""
    for role_code in SYSTEM_ROLE_FAMILIES:
        row = seeded_db.scalar(select(Role).where(Role.code == role_code))
        assert row is not None, (
            f"Role row missing for '{role_code}'. "
            f"seed_rbac_core() must create all system roles."
        )
        assert row.is_system is True, f"Role '{role_code}' must be marked is_system=True"
        assert row.is_active is True, f"Role '{role_code}' must be marked is_active=True"


# ---------------------------------------------------------------------------
# RolePermission rows: action-level alignment
# ---------------------------------------------------------------------------


def test_seed_adm_role_gets_all_admin_family_action_permissions(seeded_db: Session) -> None:
    """ADM role must have RolePermission rows for all ADMIN-family action codes."""
    adm_role = seeded_db.scalar(select(Role).where(Role.code == "ADM"))
    assert adm_role is not None

    for action_code in _ADMIN_FAMILY_ACTION_CODES:
        permission = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert permission is not None, f"Permission missing for '{action_code}'"
        link = seeded_db.scalar(
            select(RolePermission).where(
                RolePermission.role_id == adm_role.id,
                RolePermission.permission_id == permission.id,
            )
        )
        assert link is not None, (
            f"ADM role missing RolePermission for action code '{action_code}'"
        )


def test_seed_ots_role_gets_all_admin_family_action_permissions(seeded_db: Session) -> None:
    """OTS role must have RolePermission rows for all ADMIN-family action codes."""
    ots_role = seeded_db.scalar(select(Role).where(Role.code == "OTS"))
    assert ots_role is not None

    for action_code in _ADMIN_FAMILY_ACTION_CODES:
        permission = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert permission is not None, f"Permission missing for '{action_code}'"
        link = seeded_db.scalar(
            select(RolePermission).where(
                RolePermission.role_id == ots_role.id,
                RolePermission.permission_id == permission.id,
            )
        )
        assert link is not None, (
            f"OTS role missing RolePermission for action code '{action_code}'"
        )


def test_seed_opr_role_gets_all_execute_family_action_permissions(seeded_db: Session) -> None:
    """OPR role must have RolePermission rows for all EXECUTE-family action codes."""
    opr_role = seeded_db.scalar(select(Role).where(Role.code == "OPR"))
    assert opr_role is not None

    for action_code in _EXECUTE_FAMILY_ACTION_CODES:
        permission = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert permission is not None, f"Permission missing for '{action_code}'"
        link = seeded_db.scalar(
            select(RolePermission).where(
                RolePermission.role_id == opr_role.id,
                RolePermission.permission_id == permission.id,
            )
        )
        assert link is not None, (
            f"OPR role missing RolePermission for action code '{action_code}'"
        )


def test_seed_qal_role_gets_all_approve_family_action_permissions(seeded_db: Session) -> None:
    """QAL role must have RolePermission rows for all APPROVE-family action codes."""
    qal_role = seeded_db.scalar(select(Role).where(Role.code == "QAL"))
    assert qal_role is not None

    for action_code in _APPROVE_FAMILY_ACTION_CODES:
        permission = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert permission is not None, f"Permission missing for '{action_code}'"
        link = seeded_db.scalar(
            select(RolePermission).where(
                RolePermission.role_id == qal_role.id,
                RolePermission.permission_id == permission.id,
            )
        )
        assert link is not None, (
            f"QAL role missing RolePermission for action code '{action_code}'"
        )


def test_seed_pmg_role_gets_all_approve_family_action_permissions(seeded_db: Session) -> None:
    """PMG role must have RolePermission rows for all APPROVE-family action codes."""
    pmg_role = seeded_db.scalar(select(Role).where(Role.code == "PMG"))
    assert pmg_role is not None

    for action_code in _APPROVE_FAMILY_ACTION_CODES:
        permission = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert permission is not None, f"Permission missing for '{action_code}'"
        link = seeded_db.scalar(
            select(RolePermission).where(
                RolePermission.role_id == pmg_role.id,
                RolePermission.permission_id == permission.id,
            )
        )
        assert link is not None, (
            f"PMG role missing RolePermission for action code '{action_code}'"
        )


def test_seed_view_only_roles_get_no_action_level_role_permissions(seeded_db: Session) -> None:
    """Roles with only VIEW family must have 0 action-level RolePermission rows.

    VIEW has no action codes in ACTION_CODE_REGISTRY (governance rule). Roles
    that only have VIEW (QCI, EXE, PLN, INV) must not receive action-code
    RolePermission rows.
    """
    view_only_roles = [
        code for code, families in SYSTEM_ROLE_FAMILIES.items()
        if families == {"VIEW"}
    ]
    # Verify our test logic: these should be QCI, EXE, PLN, INV
    assert len(view_only_roles) > 0, "Expected at least one VIEW-only role in SYSTEM_ROLE_FAMILIES"

    for role_code in view_only_roles:
        role = seeded_db.scalar(select(Role).where(Role.code == role_code))
        assert role is not None

        action_permission_links = seeded_db.scalars(
            select(RolePermission)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id == role.id,
                Permission.action_code.is_not(None),
            )
        ).all()
        assert len(action_permission_links) == 0, (
            f"VIEW-only role '{role_code}' has unexpected action-level "
            f"RolePermission rows: "
            f"{[r.permission_id for r in action_permission_links]}"
        )


def test_seed_opr_role_has_no_admin_action_permissions(seeded_db: Session) -> None:
    """OPR must never have ADMIN-family action permissions.

    Governance invariant: ADM/OTS intentionally lack EXECUTE. Symmetrically,
    OPR must never gain ADMIN-family actions via seed.
    """
    opr_role = seeded_db.scalar(select(Role).where(Role.code == "OPR"))
    assert opr_role is not None

    for action_code in _ADMIN_FAMILY_ACTION_CODES:
        permission = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert permission is not None
        link = seeded_db.scalar(
            select(RolePermission).where(
                RolePermission.role_id == opr_role.id,
                RolePermission.permission_id == permission.id,
            )
        )
        assert link is None, (
            f"OPR role incorrectly has RolePermission for ADMIN action '{action_code}'. "
            f"OPR must not be granted ADMIN-family actions."
        )


def test_seed_adm_role_has_no_execute_action_permissions(seeded_db: Session) -> None:
    """ADM must never have EXECUTE-family action permissions.

    Governance invariant: ADM/OTS must impersonate an OPR to perform execution
    actions. ADM must not be directly granted EXECUTE actions.
    """
    adm_role = seeded_db.scalar(select(Role).where(Role.code == "ADM"))
    assert adm_role is not None

    for action_code in _EXECUTE_FAMILY_ACTION_CODES:
        permission = seeded_db.scalar(
            select(Permission).where(Permission.code == action_code)
        )
        assert permission is not None
        link = seeded_db.scalar(
            select(RolePermission).where(
                RolePermission.role_id == adm_role.id,
                RolePermission.permission_id == permission.id,
            )
        )
        assert link is None, (
            f"ADM role incorrectly has RolePermission for EXECUTE action '{action_code}'. "
            f"ADM must not be directly granted EXECUTE-family actions."
        )


# ---------------------------------------------------------------------------
# Idempotency: no duplicate rows on repeated seed
# ---------------------------------------------------------------------------


def test_seed_idempotent_no_duplicate_permission_rows(monkeypatch) -> None:
    """Running seed_rbac_core() twice must not produce duplicate Permission rows."""
    monkeypatch.setattr(rbac_module, "_load_default_users", lambda: [])

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Role.__table__.create(bind=engine)
    Permission.__table__.create(bind=engine)
    RolePermission.__table__.create(bind=engine)
    Scope.__table__.create(bind=engine)
    UserRole.__table__.create(bind=engine)
    RoleScope.__table__.create(bind=engine)
    UserRoleAssignment.__table__.create(bind=engine)

    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    db = session_factory()
    seed_rbac_core(db)
    db.commit()
    db.close()

    db = session_factory()
    seed_rbac_core(db)
    db.commit()

    for action_code in ACTION_CODE_REGISTRY:
        count = db.scalar(
            select(func.count()).select_from(Permission).where(Permission.code == action_code)
        )
        assert count == 1, (
            f"Duplicate Permission rows after double seed for '{action_code}': count={count}"
        )

    db.close()


def test_seed_idempotent_no_duplicate_role_permission_rows(monkeypatch) -> None:
    """Running seed_rbac_core() twice must not produce duplicate RolePermission rows."""
    monkeypatch.setattr(rbac_module, "_load_default_users", lambda: [])

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Role.__table__.create(bind=engine)
    Permission.__table__.create(bind=engine)
    RolePermission.__table__.create(bind=engine)
    Scope.__table__.create(bind=engine)
    UserRole.__table__.create(bind=engine)
    RoleScope.__table__.create(bind=engine)
    UserRoleAssignment.__table__.create(bind=engine)

    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    db = session_factory()
    seed_rbac_core(db)
    db.commit()
    count_after_first = db.scalar(select(func.count()).select_from(RolePermission))
    db.close()

    db = session_factory()
    seed_rbac_core(db)
    db.commit()
    count_after_second = db.scalar(select(func.count()).select_from(RolePermission))
    db.close()

    assert count_after_first == count_after_second, (
        f"RolePermission row count changed from {count_after_first} to "
        f"{count_after_second} on second seed run — seed is not idempotent."
    )


def test_seed_idempotent_no_duplicate_role_rows(monkeypatch) -> None:
    """Running seed_rbac_core() twice must not produce duplicate Role rows."""
    monkeypatch.setattr(rbac_module, "_load_default_users", lambda: [])

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Role.__table__.create(bind=engine)
    Permission.__table__.create(bind=engine)
    RolePermission.__table__.create(bind=engine)
    Scope.__table__.create(bind=engine)
    UserRole.__table__.create(bind=engine)
    RoleScope.__table__.create(bind=engine)
    UserRoleAssignment.__table__.create(bind=engine)

    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    db = session_factory()
    seed_rbac_core(db)
    db.commit()
    db.close()

    db = session_factory()
    seed_rbac_core(db)
    db.commit()

    for role_code in SYSTEM_ROLE_FAMILIES:
        count = db.scalar(
            select(func.count()).select_from(Role).where(Role.code == role_code)
        )
        assert count == 1, (
            f"Duplicate Role rows after double seed for '{role_code}': count={count}"
        )

    db.close()
