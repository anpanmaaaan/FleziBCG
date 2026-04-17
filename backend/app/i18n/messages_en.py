"""EN message catalog — canonical error / API messages."""

EN_MESSAGES: dict[str, str] = {
    # ── auth ──
    "auth.invalid_credentials": "Invalid username or password",
    "auth.token_expired": "Token has expired",
    "auth.token_invalid": "Invalid or malformed token",
    "auth.required": "Authentication required",
    "auth.session_missing": "Session is missing",
    "auth.session_invalid": "Session is invalid or revoked",
    "auth.logout_success": "Logged out successfully",
    "auth.logout_all_success": "All sessions logged out",

    # ── rbac ──
    "rbac.permission_denied": "Permission denied",
    "rbac.role_not_found": "Role not found",
    "rbac.insufficient_permissions": "Insufficient permissions for this action",

    # ── operations ──
    "operation.not_found": "Operation not found",
    "operation.already_started": "Operation is already started",
    "operation.already_completed": "Operation is already completed",
    "operation.cannot_complete": "Operation cannot be completed in its current state",
    "operation.cannot_abort": "Operation cannot be aborted in its current state",
    "operation.clock_on_required": "Clock-on is required before reporting quantities",
    "operation.invalid_quantity": "Reported quantity is invalid",
    "operation.start_conflict": "Operation start conflicts with current state",

    # ── station ──
    "station.not_found": "Workstation not found",
    "station.already_claimed": "Workstation is already claimed by another operator",
    "station.not_claimed": "Workstation is not claimed",
    "station.claim_not_owned": "You do not own this workstation claim",

    # ── work orders ──
    "work_order.not_found": "Work order not found",

    # ── production orders ──
    "production_order.not_found": "Production order not found",

    # ── approval ──
    "approval.not_found": "Approval request not found",
    "approval.already_decided": "Approval has already been decided",
    "approval.self_approval": "Cannot approve your own request",
    "approval.permission_denied": "Not authorized to decide on this approval",

    # ── impersonation ──
    "impersonation.not_allowed": "Impersonation is not allowed for your role",
    "impersonation.target_admin": "Cannot impersonate an admin role",
    "impersonation.already_active": "An impersonation session is already active",
    "impersonation.not_found": "Impersonation session not found",
    "impersonation.expired": "Impersonation session has expired",

    # ── tenant ──
    "tenant.missing": "Tenant ID is required",
    "tenant.invalid": "Invalid tenant ID",

    # ── validation ──
    "validation.required_field": "Required field is missing",
    "validation.invalid_format": "Invalid input format",
}
