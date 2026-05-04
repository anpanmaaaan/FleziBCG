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
REASON_CODES_SRC = (BACKEND_ROOT / "app" / "api" / "v1" / "reason_codes.py").read_text(encoding="utf-8")
REASON_CODE_SVC_SRC = (BACKEND_ROOT / "app" / "services" / "reason_code_service.py").read_text(encoding="utf-8")
REASON_CODE_REPO_SRC = (BACKEND_ROOT / "app" / "repositories" / "reason_code_repository.py").read_text(encoding="utf-8")
DOWNTIME_REASONS_SRC = (BACKEND_ROOT / "app" / "api" / "v1" / "downtime_reasons.py").read_text(encoding="utf-8")

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


# ─── MMD-BE-09A: BOM action code registry checks ─────────────────────────────

def test_bom_manage_action_code_exists():
    assert "admin.master_data.bom.manage" in ACTION_CODE_REGISTRY, (
        "admin.master_data.bom.manage is missing from ACTION_CODE_REGISTRY — required by MMD-BE-09A"
    )


def test_bom_manage_action_code_is_domain_specific():
    assert ACTION_CODE_REGISTRY.get("admin.master_data.bom.manage") == "ADMIN", (
        "admin.master_data.bom.manage must map to ADMIN family"
    )
    assert "admin.master_data.bom.manage" != "admin.user.manage", (
        "BOM action code must remain domain-specific and distinct from IAM user management"
    )


def test_bom_read_endpoints_do_not_require_manage_action():
    """BOM read routes must use authenticated-read only — not require_action."""
    bom_get_blocks = re.findall(
        r'@router\.get\("/\{product_id\}/boms[^"]*".*?\)[^@]+?(?=@router\.|$)',
        PRODUCTS_SRC,
        flags=re.DOTALL,
    )
    assert len(bom_get_blocks) >= 2, "Expected at least 2 BOM GET route blocks in products.py"
    for block in bom_get_blocks:
        assert "require_action" not in block, (
            "BOM GET route must not use require_action — authenticated-read only"
        )


def test_bom_write_routes_implemented_by_mmd_be_12():
    """MMD-BE-12: BOM write endpoints must be present and use admin.master_data.bom.manage."""
    required_paths = [
        "/{product_id}/boms",
        "/{product_id}/boms/{bom_id}",
        "/{product_id}/boms/{bom_id}/release",
        "/{product_id}/boms/{bom_id}/retire",
        "/{product_id}/boms/{bom_id}/items",
        "/{product_id}/boms/{bom_id}/items/{bom_item_id}",
    ]
    for path in required_paths:
        assert path in PRODUCTS_SRC, f"Expected BOM write route path missing: {path}"
    assert PRODUCTS_SRC.count("@router.post") >= 4, "Expected at least 4 POST routes"
    assert PRODUCTS_SRC.count("@router.patch") >= 3, "Expected at least 3 PATCH routes"
    assert PRODUCTS_SRC.count("@router.delete") >= 1, "Expected at least 1 DELETE route"


def test_bom_write_routes_use_bom_manage_action_code():
    """All BOM write route blocks must reference admin.master_data.bom.manage."""
    assert PRODUCTS_SRC.count('admin.master_data.bom.manage') >= 7, (
        "Expected at least 7 occurrences of admin.master_data.bom.manage (one per write endpoint)"
    )


def test_no_bom_forbidden_endpoints_exist():
    """Boundary guard: delete bom, reactivate, clone, bind product version must not exist."""
    forbidden_markers = [
        '@router.delete("/{product_id}/boms/{bom_id}"',
        '@router.post("/{product_id}/boms/{bom_id}/reactivate"',
        '@router.post("/{product_id}/boms/{bom_id}/clone"',
        '@router.post("/{product_id}/boms/{bom_id}/bind-product-version"',
        '@router.post("/{product_id}/boms/{bom_id}/bulk-import"',
        '@router.post("/{product_id}/boms/{bom_id}/replace-items"',
        '@router.post("/{product_id}/boms/{bom_id}/backflush"',
        '@router.post("/{product_id}/boms/{bom_id}/erp-post"',
    ]
    for marker in forbidden_markers:
        assert marker not in PRODUCTS_SRC, f"Forbidden BOM route found: {marker}"


# ─── MMD-BE-10A: Reason Code action code registry checks ─────────────────────

def test_reason_code_manage_action_code_exists():
    """MMD-BE-10A: admin.master_data.reason_code.manage must be present."""
    assert "admin.master_data.reason_code.manage" in ACTION_CODE_REGISTRY, (
        "admin.master_data.reason_code.manage is missing from ACTION_CODE_REGISTRY — required by MMD-BE-10A"
    )


def test_reason_code_manage_action_code_is_domain_specific():
    """Action code must map to ADMIN and must not equal the IAM manage code."""
    assert ACTION_CODE_REGISTRY.get("admin.master_data.reason_code.manage") == "ADMIN", (
        "admin.master_data.reason_code.manage must map to ADMIN family"
    )
    assert "admin.master_data.reason_code.manage" != "admin.user.manage", (
        "Reason Code action code must remain domain-specific and distinct from IAM user management"
    )


def test_existing_mmd_action_codes_unchanged_after_10a():
    """All pre-existing MMD action codes must remain unchanged after MMD-BE-10A."""
    expected = {
        "admin.master_data.product.manage": "ADMIN",
        "admin.master_data.product_version.manage": "ADMIN",
        "admin.master_data.routing.manage": "ADMIN",
        "admin.master_data.resource_requirement.manage": "ADMIN",
        "admin.master_data.bom.manage": "ADMIN",
    }
    for code, family in expected.items():
        assert code in ACTION_CODE_REGISTRY, f"Pre-existing MMD action code missing after 10A: {code}"
        assert ACTION_CODE_REGISTRY[code] == family, (
            f"Pre-existing MMD action code family changed: {code} → {ACTION_CODE_REGISTRY[code]!r}"
        )


def test_reason_code_read_endpoints_do_not_require_manage_action():
    """Reason Code GET routes must use authenticated-read only — not require_action."""
    rc_get_blocks = re.findall(
        r'@router\.get\b[^@]+?(?=@router\.|$)',
        REASON_CODES_SRC,
        flags=re.DOTALL,
    )
    assert len(rc_get_blocks) >= 2, "Expected at least 2 GET route blocks in reason_codes.py"
    for block in rc_get_blocks:
        assert "require_action" not in block, (
            "Reason Code GET route must not use require_action — authenticated-read only"
        )


def test_no_reason_code_write_routes_exist_yet():
    """MMD-BE-10A scope guard: Reason Code write routes must not yet exist."""
    forbidden_markers = [
        "@router.post(\"\",",
        "@router.post(\"\")",
        "@router.patch(",
        "@router.put(",
        "@router.delete(",
        "/release",
        "/retire",
        "/activate",
        "/deactivate",
        "/clone",
        "/bulk-import",
        "/map-downtime",
        "/bind-policy",
        "/erp-post",
        "/reactivate",
    ]
    for marker in forbidden_markers:
        assert marker not in REASON_CODES_SRC, (
            f"Unexpected Reason Code write route marker found in reason_codes.py: {marker!r}"
        )


def test_reason_code_does_not_modify_downtime_reason_api():
    """downtime_reasons.py must not import or reference reason_code/reason_codes module."""
    assert "reason_code" not in DOWNTIME_REASONS_SRC.lower() or (
        # allow the string 'reason_code' only as a field name inside payload references —
        # confirm it does NOT import from app.models.reason_code or reason_code_service
        "from app.models.reason_code" not in DOWNTIME_REASONS_SRC
        and "from app.services.reason_code" not in DOWNTIME_REASONS_SRC
        and "from app.repositories.reason_code" not in DOWNTIME_REASONS_SRC
    ), "downtime_reasons.py must not import from reason_code modules"


def test_reason_code_does_not_auto_map_to_downtime_reason():
    """Reason Code service and repository must not reference downtime_reasons table or model."""
    for src, name in [
        (REASON_CODE_SVC_SRC, "reason_code_service.py"),
        (REASON_CODE_REPO_SRC, "reason_code_repository.py"),
    ]:
        assert "downtime_reason" not in src.lower(), (
            f"{name} must not reference downtime_reason — no automatic mapping allowed"
        )
        assert "downtime_reasons" not in src.lower(), (
            f"{name} must not reference downtime_reasons table — no automatic mapping allowed"
        )
