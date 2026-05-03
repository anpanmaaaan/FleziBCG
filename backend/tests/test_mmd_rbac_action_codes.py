"""
MMD-BE-02: RBAC Action Code Regression Tests

Static checks that verify:
1. MMD-specific action codes exist in ACTION_CODE_REGISTRY with ADMIN family.
2. Product mutation endpoints do NOT use admin.user.manage.
3. Routing mutation endpoints do NOT use admin.user.manage.
4. Resource requirement mutation endpoints do NOT use admin.user.manage.
5. Each endpoint group uses its own MMD-specific action code.

These are deliberate source-level contract tests — not runtime integration tests.
A unit/integration test framework is not available in this project.
"""

import re
from pathlib import Path

from app.security.rbac import ACTION_CODE_REGISTRY

BACKEND_ROOT = Path(__file__).parent.parent
PRODUCTS_SRC = (BACKEND_ROOT / "app" / "api" / "v1" / "products.py").read_text(encoding="utf-8")
ROUTINGS_SRC = (BACKEND_ROOT / "app" / "api" / "v1" / "routings.py").read_text(encoding="utf-8")

# ─── Registry checks ──────────────────────────────────────────────────────────

def test_product_action_code_in_registry():
    assert "admin.master_data.product.manage" in ACTION_CODE_REGISTRY, (
        "admin.master_data.product.manage is missing from ACTION_CODE_REGISTRY"
    )


def test_product_action_code_is_admin_family():
    assert ACTION_CODE_REGISTRY.get("admin.master_data.product.manage") == "ADMIN", (
        "admin.master_data.product.manage must map to ADMIN family"
    )


def test_routing_action_code_in_registry():
    assert "admin.master_data.routing.manage" in ACTION_CODE_REGISTRY, (
        "admin.master_data.routing.manage is missing from ACTION_CODE_REGISTRY"
    )


def test_routing_action_code_is_admin_family():
    assert ACTION_CODE_REGISTRY.get("admin.master_data.routing.manage") == "ADMIN", (
        "admin.master_data.routing.manage must map to ADMIN family"
    )


def test_resource_requirement_action_code_in_registry():
    assert "admin.master_data.resource_requirement.manage" in ACTION_CODE_REGISTRY, (
        "admin.master_data.resource_requirement.manage is missing from ACTION_CODE_REGISTRY"
    )


def test_resource_requirement_action_code_is_admin_family():
    assert ACTION_CODE_REGISTRY.get("admin.master_data.resource_requirement.manage") == "ADMIN", (
        "admin.master_data.resource_requirement.manage must map to ADMIN family"
    )


def test_product_version_manage_action_code_exists():
    assert "admin.master_data.product_version.manage" in ACTION_CODE_REGISTRY, (
        "admin.master_data.product_version.manage is missing from ACTION_CODE_REGISTRY"
    )


def test_product_version_manage_action_code_is_domain_specific():
    assert ACTION_CODE_REGISTRY.get("admin.master_data.product_version.manage") == "ADMIN", (
        "admin.master_data.product_version.manage must map to ADMIN family"
    )
    assert "admin.master_data.product_version.manage" != "admin.user.manage", (
        "Product Version action code must remain domain-specific and distinct from IAM"
    )


def test_existing_mmd_action_codes_still_exist():
    expected_codes = {
        "admin.master_data.product.manage",
        "admin.master_data.routing.manage",
        "admin.master_data.resource_requirement.manage",
    }
    missing_codes = sorted(code for code in expected_codes if code not in ACTION_CODE_REGISTRY)
    assert missing_codes == [], f"Existing MMD action codes missing: {missing_codes}"


# ─── Placeholder code absence checks ─────────────────────────────────────────

def test_admin_user_manage_not_in_product_mutations():
    """Product endpoints must not use the IAM user-management placeholder code."""
    assert "admin.user.manage" not in PRODUCTS_SRC, (
        "products.py still references admin.user.manage — governance debt not resolved"
    )


def test_admin_user_manage_not_in_routing_mutations():
    """Routing and resource-requirement endpoints must not use the IAM placeholder code."""
    assert "admin.user.manage" not in ROUTINGS_SRC, (
        "routings.py still references admin.user.manage — governance debt not resolved"
    )


# ─── Correct code presence checks ────────────────────────────────────────────

def test_product_endpoints_use_product_action_code():
    """All 4 product mutation endpoints must use the product-specific action code."""
    count = PRODUCTS_SRC.count('"admin.master_data.product.manage"')
    assert count >= 4, (
        f"Expected ≥4 uses of admin.master_data.product.manage in products.py, found {count}"
    )


def test_routing_endpoints_use_routing_action_code():
    """All 7 routing mutation endpoints must use the routing-specific action code."""
    count = ROUTINGS_SRC.count('"admin.master_data.routing.manage"')
    assert count >= 7, (
        f"Expected ≥7 uses of admin.master_data.routing.manage in routings.py, found {count}"
    )


def test_resource_requirement_endpoints_use_rr_action_code():
    """All 3 resource-requirement mutation endpoints must use the RR-specific action code."""
    count = ROUTINGS_SRC.count('"admin.master_data.resource_requirement.manage"')
    assert count >= 3, (
        f"Expected ≥3 uses of admin.master_data.resource_requirement.manage in routings.py, found {count}"
    )


# ─── Read endpoint boundary check ────────────────────────────────────────────

def test_read_endpoints_do_not_require_mutation_action_code():
    """GET handlers must use require_authenticated_identity, not require_action."""
    # Extract all GET route function bodies (heuristic: look for require_action in GET handlers)
    # A GET handler signature starts with @router.get and should not contain require_action
    get_blocks = re.findall(
        r'@router\.get\b[^@]+?(?=@router\.|$)',
        PRODUCTS_SRC + ROUTINGS_SRC,
        flags=re.DOTALL,
    )
    for block in get_blocks:
        assert "require_action" not in block, (
            f"A GET handler unexpectedly uses require_action: {block[:200]!r}"
        )


def test_product_version_read_endpoints_do_not_require_manage_action():
    """Product Version read routes must remain authenticated-read only."""
    version_get_blocks = re.findall(
        r'@router\.get\("/\{product_id\}/versions(?:/\{version_id\})?".*?\)[^@]+?(?=@router\.|$)',
        PRODUCTS_SRC,
        flags=re.DOTALL,
    )
    assert len(version_get_blocks) == 2, "Expected 2 Product Version GET route blocks"
    for block in version_get_blocks:
        assert "require_action" not in block, "Product Version GET route must not require action code"


def test_product_version_write_routes_use_product_version_action_code():
    required_markers = [
        '@router.post("/{product_id}/versions"',
        '@router.patch("/{product_id}/versions/{version_id}"',
        '@router.post("/{product_id}/versions/{version_id}/release"',
        '@router.post("/{product_id}/versions/{version_id}/retire"',
    ]
    for marker in required_markers:
        assert marker in PRODUCTS_SRC, f"Missing Product Version write route marker: {marker}"

    count = PRODUCTS_SRC.count('"admin.master_data.product_version.manage"')
    assert count >= 4, (
        "Expected Product Version write routes to require admin.master_data.product_version.manage"
    )


def test_no_product_version_delete_reactivate_set_current_clone_binding_routes_exist():
    """Scope guard: keep deferred Product Version commands out of this slice."""
    forbidden_markers = [
        '@router.delete("/{product_id}/versions/{version_id}"',
        '@router.post("/{product_id}/versions/{version_id}/reactivate"',
        '@router.post("/{product_id}/versions/{version_id}/set-current"',
        '@router.post("/{product_id}/versions/{version_id}/clone"',
        '@router.post("/{product_id}/versions/{version_id}/bind-bom"',
        '@router.post("/{product_id}/versions/{version_id}/bind-routing"',
        '@router.post("/{product_id}/versions/{version_id}/bind-resource-requirement"',
    ]
    for marker in forbidden_markers:
        assert marker not in PRODUCTS_SRC, f"Unexpected deferred Product Version route marker found: {marker}"
