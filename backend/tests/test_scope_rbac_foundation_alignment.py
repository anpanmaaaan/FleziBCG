"""P0-A-06A-01 alignment tests for existing RBAC scope foundation.

This suite locks the canonical foundation to existing RBAC models:
- Scope -> scopes
- UserRoleAssignment -> user_role_assignments
- RoleScope -> role_scopes

It also prevents accidental introduction of duplicate scope model names.
"""

from app.models import rbac as rbac_models
from app.models.rbac import RoleScope, Scope, UserRoleAssignment


def test_existing_scope_models_exist() -> None:
    assert Scope is not None
    assert UserRoleAssignment is not None
    assert RoleScope is not None


def test_existing_scope_table_names_are_canonical() -> None:
    assert Scope.__tablename__ == "scopes"
    assert UserRoleAssignment.__tablename__ == "user_role_assignments"
    assert RoleScope.__tablename__ == "role_scopes"


def test_scope_is_tenant_aware_and_hierarchical() -> None:
    columns = Scope.__table__.c
    assert "tenant_id" in columns
    assert "scope_type" in columns
    assert "scope_value" in columns
    assert "parent_scope_id" in columns


def test_scope_uniqueness_constraint_exists() -> None:
    unique_names = {
        c.name for c in Scope.__table__.constraints if getattr(c, "name", None)  # type: ignore[attr-defined]
    }
    assert "uq_scope_tenant_type_value" in unique_names


def test_user_role_assignment_links_role_and_scope() -> None:
    columns = UserRoleAssignment.__table__.c
    assert "user_id" in columns
    assert "role_id" in columns
    assert "scope_id" in columns


def test_role_scope_model_exists_as_compatibility_link() -> None:
    columns = RoleScope.__table__.c
    assert "user_role_id" in columns
    assert "scope_type" in columns
    assert "scope_value" in columns


def test_scope_type_constants_exist() -> None:
    assert rbac_models.SCOPE_TYPE_TENANT == "tenant"
    assert rbac_models.SCOPE_TYPE_PLANT == "plant"
    assert rbac_models.SCOPE_TYPE_AREA == "area"
    assert rbac_models.SCOPE_TYPE_LINE == "line"
    assert rbac_models.SCOPE_TYPE_STATION == "station"
    assert rbac_models.SCOPE_TYPE_EQUIPMENT == "equipment"
    assert rbac_models.SUPPORTED_SCOPE_TYPES == (
        "tenant",
        "plant",
        "area",
        "line",
        "station",
        "equipment",
    )


def test_principal_constants_exist() -> None:
    assert rbac_models.PRINCIPAL_TYPE_USER == "user"
    assert rbac_models.PRINCIPAL_TYPE_ROLE == "role"


def test_no_duplicate_scope_model_names_exist() -> None:
    assert not hasattr(rbac_models, "ScopeNode")
    assert not hasattr(rbac_models, "ScopeAssignment")


def test_no_duplicate_scope_table_names_registered() -> None:
    table_names = set(rbac_models.Base.metadata.tables.keys())
    assert "scopes" in table_names
    assert "user_role_assignments" in table_names
    assert "role_scopes" in table_names
    assert "scope_nodes" not in table_names
    assert "scope_assignments" not in table_names
