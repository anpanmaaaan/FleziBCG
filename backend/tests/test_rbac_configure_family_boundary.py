"""P0-A-09: IEP CONFIGURE family boundary lock tests.

This suite locks the current intentional posture:
- IEP has CONFIGURE capability at role-family level.
- ACTION_CODE_REGISTRY currently has zero CONFIGURE-family action codes.
- No API route currently requires a CONFIGURE-family action code.
- seed_rbac_core() still seeds family-level CONFIGURE permission and links it
  to IEP at tenant wildcard scope.

Do not add CONFIGURE action codes without authoritative design and governance
approval for concrete IEP/configuration mutations.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.security.rbac as rbac_module
from app.models.rbac import Permission, Role, RolePermission, RoleScope, Scope, UserRole, UserRoleAssignment
from app.security.rbac import ACTION_CODE_REGISTRY, SYSTEM_ROLE_FAMILIES, seed_rbac_core

BACKEND_ROOT = Path(__file__).parent.parent


def test_iep_role_includes_configure_family() -> None:
    assert "IEP" in SYSTEM_ROLE_FAMILIES
    assert "CONFIGURE" in SYSTEM_ROLE_FAMILIES["IEP"]


def test_action_registry_has_zero_configure_family_action_codes() -> None:
    configure_codes = {
        code for code, family in ACTION_CODE_REGISTRY.items() if family == "CONFIGURE"
    }
    assert configure_codes == set(), (
        "Unexpected CONFIGURE action codes found. P0-A-09 boundary assumes zero "
        "CONFIGURE action codes until a dedicated IEP/configuration governance slice."
    )


def test_api_routes_do_not_require_configure_action_codes() -> None:
    import re

    api_v1_dir = BACKEND_ROOT / "app" / "api" / "v1"
    used_codes: list[str] = []
    for file_path in sorted(api_v1_dir.glob("*.py")):
        src = file_path.read_text(encoding="utf-8")
        used_codes.extend(re.findall(r'require_action\("([^"]+)"\)', src))

    configure_used = [c for c in used_codes if c in ACTION_CODE_REGISTRY and ACTION_CODE_REGISTRY[c] == "CONFIGURE"]
    assert not configure_used, (
        f"API routes currently use CONFIGURE action codes: {configure_used}. "
        "P0-A-09 boundary assumes no CONFIGURE action guard is active yet."
    )


@pytest.fixture()
def seeded_db(monkeypatch) -> Session:
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


def test_seed_creates_configure_family_permission_row(seeded_db: Session) -> None:
    row = seeded_db.scalar(select(Permission).where(Permission.code == "CONFIGURE"))
    assert row is not None
    assert row.family == "CONFIGURE"
    assert row.action_code is None


def test_seed_links_iep_to_configure_family_permission(seeded_db: Session) -> None:
    iep_role = seeded_db.scalar(select(Role).where(Role.code == "IEP"))
    assert iep_role is not None

    configure_perm = seeded_db.scalar(select(Permission).where(Permission.code == "CONFIGURE"))
    assert configure_perm is not None

    link = seeded_db.scalar(
        select(RolePermission).where(
            RolePermission.role_id == iep_role.id,
            RolePermission.permission_id == configure_perm.id,
            RolePermission.scope_type == "tenant",
            RolePermission.scope_value == "*",
        )
    )
    assert link is not None, (
        "IEP must keep CONFIGURE family-level RolePermission link while CONFIGURE "
        "action codes are not yet introduced."
    )


def test_seed_creates_no_configure_action_permissions(seeded_db: Session) -> None:
    configure_action_rows = seeded_db.scalars(
        select(Permission).where(
            Permission.family == "CONFIGURE",
            Permission.action_code.is_not(None),
        )
    ).all()
    assert configure_action_rows == [], (
        "Expected zero action-level CONFIGURE permissions for current registry posture."
    )
