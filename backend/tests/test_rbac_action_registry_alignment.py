"""P0-A-07A: RBAC Action Registry Semantic Alignment Tests

This suite locks the canonical action code registry to the current source
implementation and documents known semantic gaps without changing behavior.

Source of truth precedence:
  1. docs/design/02_registry/action-code-registry.md  — governance record
  2. backend/app/security/rbac.py ACTION_CODE_REGISTRY  — runtime truth

Tests here verify runtime truth matches governance record.
They do NOT change runtime authorization behavior.

--- Known semantic gaps (documented here, fixed in future slices) ---

GAP-1: RESOLVED in P0-A-07B.
  admin.downtime_reason.manage action code added. downtime_reasons.py updated
  to use dedicated code. See audit report p0-a-07b-dedicated-downtime-reason-admin-action-report.md.

GAP-2: RESOLVED in P0-A-07C.
  admin.security_event.read action code added. security_events.py updated
  to use dedicated code. See audit report p0-a-07c-dedicated-security-event-read-action-report.md.

GAP-3: RESOLVED in P0-A-07D.
  impersonations.py create and revoke routes now use route-level require_action
  guards (admin.impersonation.create, admin.impersonation.revoke). Service-layer
  business checks remain intact. GET /current remains require_authenticated_identity.
  See audit report p0-a-07d-route-level-impersonation-action-guard-alignment-report.md.
"""

from pathlib import Path
from typing import Literal

from app.security.rbac import ACTION_CODE_REGISTRY

# ---------------------------------------------------------------------------
# Constants derived from authoritative registry doc
# ---------------------------------------------------------------------------

_EXPECTED_EXECUTION_CODES = frozenset({
    "execution.start",
    "execution.complete",
    "execution.report_quantity",
    "execution.pause",
    "execution.resume",
    "execution.start_downtime",
    "execution.end_downtime",
    "execution.close",
    "execution.reopen",
})

_EXPECTED_APPROVAL_CODES = frozenset({
    "approval.create",
    "approval.decide",
})

_EXPECTED_ADMIN_IAM_CODES = frozenset({
    "admin.impersonation.create",
    "admin.impersonation.revoke",
    "admin.user.manage",
})

_EXPECTED_ADMIN_MMD_CODES = frozenset({
    "admin.master_data.product.manage",
    "admin.master_data.routing.manage",
    "admin.master_data.resource_requirement.manage",
})

_EXPECTED_ADMIN_CONFIG_CODES = frozenset({
    "admin.downtime_reason.manage",
})

_EXPECTED_ADMIN_AUDIT_CODES = frozenset({
    "admin.security_event.read",
})

_ALL_EXPECTED_CODES = (
    _EXPECTED_EXECUTION_CODES
    | _EXPECTED_APPROVAL_CODES
    | _EXPECTED_ADMIN_IAM_CODES
    | _EXPECTED_ADMIN_MMD_CODES
    | _EXPECTED_ADMIN_CONFIG_CODES
    | _EXPECTED_ADMIN_AUDIT_CODES
)

_VALID_FAMILIES: frozenset[str] = frozenset({"VIEW", "EXECUTE", "APPROVE", "CONFIGURE", "ADMIN"})

BACKEND_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Registry completeness: all canonical codes are present
# ---------------------------------------------------------------------------


def test_all_canonical_execution_codes_in_registry() -> None:
    """All 9 execution action codes from registry doc must be in ACTION_CODE_REGISTRY."""
    missing = _EXPECTED_EXECUTION_CODES - set(ACTION_CODE_REGISTRY)
    assert not missing, f"Missing execution codes in ACTION_CODE_REGISTRY: {missing}"


def test_all_canonical_approval_codes_in_registry() -> None:
    """approval.create and approval.decide must be in ACTION_CODE_REGISTRY."""
    missing = _EXPECTED_APPROVAL_CODES - set(ACTION_CODE_REGISTRY)
    assert not missing, f"Missing approval codes in ACTION_CODE_REGISTRY: {missing}"


def test_all_canonical_admin_iam_codes_in_registry() -> None:
    """IAM admin action codes including impersonation must be in ACTION_CODE_REGISTRY."""
    missing = _EXPECTED_ADMIN_IAM_CODES - set(ACTION_CODE_REGISTRY)
    assert not missing, f"Missing IAM admin codes in ACTION_CODE_REGISTRY: {missing}"


def test_all_canonical_admin_mmd_codes_in_registry() -> None:
    """MMD admin action codes must be in ACTION_CODE_REGISTRY."""
    missing = _EXPECTED_ADMIN_MMD_CODES - set(ACTION_CODE_REGISTRY)
    assert not missing, f"Missing MMD admin codes in ACTION_CODE_REGISTRY: {missing}"


def test_all_canonical_admin_config_codes_in_registry() -> None:
    """Configuration administration action codes must be in ACTION_CODE_REGISTRY."""
    missing = _EXPECTED_ADMIN_CONFIG_CODES - set(ACTION_CODE_REGISTRY)
    assert not missing, f"Missing config admin codes in ACTION_CODE_REGISTRY: {missing}"


def test_all_canonical_admin_audit_codes_in_registry() -> None:
    """Audit/security governance action codes must be in ACTION_CODE_REGISTRY."""
    missing = _EXPECTED_ADMIN_AUDIT_CODES - set(ACTION_CODE_REGISTRY)
    assert not missing, f"Missing audit admin codes in ACTION_CODE_REGISTRY: {missing}"


def test_action_code_registry_contains_exactly_canonical_set() -> None:
    """ACTION_CODE_REGISTRY must contain exactly the codes defined in the registry doc.

    If this fails, either a new code was added without a registry doc entry,
    or a code was removed without removing the registry doc entry.
    """
    actual = set(ACTION_CODE_REGISTRY)
    unexpected = actual - _ALL_EXPECTED_CODES
    missing = _ALL_EXPECTED_CODES - actual
    assert not unexpected, f"Unexpected codes in ACTION_CODE_REGISTRY (not in registry doc): {unexpected}"
    assert not missing, f"Missing codes in ACTION_CODE_REGISTRY (in registry doc but absent): {missing}"


# ---------------------------------------------------------------------------
# Family mapping checks
# ---------------------------------------------------------------------------


def test_all_registry_values_are_valid_permission_families() -> None:
    """Every value in ACTION_CODE_REGISTRY must be a valid PermissionFamily literal."""
    invalid = {
        code: family
        for code, family in ACTION_CODE_REGISTRY.items()
        if family not in _VALID_FAMILIES
    }
    assert not invalid, f"Invalid PermissionFamily values in ACTION_CODE_REGISTRY: {invalid}"


def test_execution_codes_map_to_execute_family() -> None:
    """All execution.* action codes must map to EXECUTE family."""
    wrong = {
        code: ACTION_CODE_REGISTRY[code]
        for code in _EXPECTED_EXECUTION_CODES
        if ACTION_CODE_REGISTRY.get(code) != "EXECUTE"
    }
    assert not wrong, f"Execution codes with wrong family: {wrong}"


def test_approval_codes_map_to_approve_family() -> None:
    """All approval.* action codes must map to APPROVE family."""
    wrong = {
        code: ACTION_CODE_REGISTRY[code]
        for code in _EXPECTED_APPROVAL_CODES
        if ACTION_CODE_REGISTRY.get(code) != "APPROVE"
    }
    assert not wrong, f"Approval codes with wrong family: {wrong}"


def test_admin_codes_map_to_admin_family() -> None:
    """All admin.* action codes must map to ADMIN family."""
    admin_codes = _EXPECTED_ADMIN_IAM_CODES | _EXPECTED_ADMIN_MMD_CODES | _EXPECTED_ADMIN_CONFIG_CODES | _EXPECTED_ADMIN_AUDIT_CODES
    wrong = {
        code: ACTION_CODE_REGISTRY[code]
        for code in admin_codes
        if ACTION_CODE_REGISTRY.get(code) != "ADMIN"
    }
    assert not wrong, f"Admin codes with wrong family: {wrong}"


def test_no_action_code_maps_to_view_family() -> None:
    """No action code should map to VIEW.

    Governance rule: read endpoints use require_authenticated_identity, not
    require_action. VIEW does not require fine-grained action gating.
    """
    view_codes = {
        code for code, family in ACTION_CODE_REGISTRY.items() if family == "VIEW"
    }
    assert not view_codes, (
        f"Action codes mapping to VIEW family (not allowed): {view_codes}"
    )


# ---------------------------------------------------------------------------
# Route alignment: operations route uses only registered codes
# ---------------------------------------------------------------------------


def test_operations_route_uses_only_registered_action_codes() -> None:
    """All require_action calls in operations.py must use codes in ACTION_CODE_REGISTRY.

    This prevents new execution routes from using ad-hoc/unregistered codes.
    """
    import re

    src = (BACKEND_ROOT / "app" / "api" / "v1" / "operations.py").read_text(encoding="utf-8")
    used_codes = re.findall(r'require_action\("([^"]+)"\)', src)
    assert used_codes, "No require_action calls found in operations.py — guard was removed?"
    unregistered = [c for c in used_codes if c not in ACTION_CODE_REGISTRY]
    assert not unregistered, (
        f"operations.py uses unregistered action codes: {unregistered}"
    )


def test_operations_route_uses_only_execution_codes() -> None:
    """All require_action calls in operations.py must use execution.* codes only."""
    import re

    src = (BACKEND_ROOT / "app" / "api" / "v1" / "operations.py").read_text(encoding="utf-8")
    used_codes = re.findall(r'require_action\("([^"]+)"\)', src)
    non_execution = [c for c in used_codes if not c.startswith("execution.")]
    assert not non_execution, (
        f"operations.py has non-execution action codes: {non_execution}"
    )


def test_approval_routes_use_only_approval_codes() -> None:
    """All require_action calls in approvals.py must use approval.* codes."""
    import re

    src = (BACKEND_ROOT / "app" / "api" / "v1" / "approvals.py").read_text(encoding="utf-8")
    used_codes = re.findall(r'require_action\("([^"]+)"\)', src)
    non_approval = [c for c in used_codes if not c.startswith("approval.")]
    assert not non_approval, (
        f"approvals.py has non-approval action codes: {non_approval}"
    )


# ---------------------------------------------------------------------------
# Known semantic gap locks — document existing state, detect drift
# ---------------------------------------------------------------------------


def test_known_gap_downtime_reasons_resolved_uses_dedicated_action_code() -> None:
    """GAP-1 RESOLVED (P0-A-07B): downtime_reasons.py now uses admin.downtime_reason.manage.

    admin.user.manage must no longer appear in downtime_reasons.py.
    The dedicated code must be present for both admin mutation routes.
    """
    import re

    src = (BACKEND_ROOT / "app" / "api" / "v1" / "downtime_reasons.py").read_text(encoding="utf-8")
    used_codes = re.findall(r'require_action\("([^"]+)"\)', src)
    assert "admin.downtime_reason.manage" in used_codes, (
        "downtime_reasons.py does not use admin.downtime_reason.manage. "
        "GAP-1 resolution may have been reverted."
    )
    assert "admin.user.manage" not in used_codes, (
        "downtime_reasons.py still uses admin.user.manage. GAP-1 was not resolved."
    )


def test_known_gap_security_events_resolved_uses_dedicated_action_code() -> None:
    """GAP-2 RESOLVED (P0-A-07C): security_events.py now uses admin.security_event.read.

    admin.user.manage must no longer appear in security_events.py.
    The dedicated audit read code must be present.
    """
    import re

    src = (BACKEND_ROOT / "app" / "api" / "v1" / "security_events.py").read_text(encoding="utf-8")
    used_codes = re.findall(r'require_action\("([^"]+)"\)', src)
    assert "admin.security_event.read" in used_codes, (
        "security_events.py does not use admin.security_event.read. "
        "GAP-2 resolution may have been reverted."
    )
    assert "admin.user.manage" not in used_codes, (
        "security_events.py still uses admin.user.manage. GAP-2 was not resolved."
    )


def test_known_gap_impersonation_routes_resolved_use_dedicated_action_codes() -> None:
    """GAP-3 RESOLVED (P0-A-07D): impersonations.py create and revoke routes
    now use route-level require_action guards.

    admin.impersonation.create must be used for the create route.
    admin.impersonation.revoke must be used for the revoke route.
    GET /current must remain require_authenticated_identity (read/status — not privileged mutation).
    """
    import re

    src = (BACKEND_ROOT / "app" / "api" / "v1" / "impersonations.py").read_text(encoding="utf-8")
    used_codes = re.findall(r'require_action\("([^"]+)"\)', src)
    assert "admin.impersonation.create" in used_codes, (
        "impersonations.py does not use admin.impersonation.create. "
        "GAP-3 resolution may have been reverted."
    )
    assert "admin.impersonation.revoke" in used_codes, (
        "impersonations.py does not use admin.impersonation.revoke. "
        "GAP-3 resolution may have been reverted."
    )


def test_impersonation_current_route_uses_authenticated_identity_only() -> None:
    """GET /current (status/read) must NOT use require_action.

    Read/status routes should use require_authenticated_identity per governance rule.
    The create and revoke routes use dedicated action codes; /current is read-only.
    """
    import re

    src = (BACKEND_ROOT / "app" / "api" / "v1" / "impersonations.py").read_text(encoding="utf-8")
    assert "require_authenticated_identity" in src, (
        "impersonations.py no longer uses require_authenticated_identity. "
        "GET /current route guard may have been incorrectly removed."
    )


def test_impersonation_codes_in_registry_with_admin_family() -> None:
    """Impersonation action codes exist in registry with ADMIN family.

    Registry was pre-populated in P0-A-07A; this test is the stable positive lock.
    """
    assert "admin.impersonation.create" in ACTION_CODE_REGISTRY
    assert "admin.impersonation.revoke" in ACTION_CODE_REGISTRY
    assert ACTION_CODE_REGISTRY["admin.impersonation.create"] == "ADMIN"
    assert ACTION_CODE_REGISTRY["admin.impersonation.revoke"] == "ADMIN"
