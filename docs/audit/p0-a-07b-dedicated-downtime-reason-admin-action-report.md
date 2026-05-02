# P0-A-07B Audit Report: Dedicated Downtime Reason Admin Action Code

**Slice:** P0-A-07B  
**Date:** 2026-05-02  
**Status:** COMPLETE  
**Precondition Slice:** P0-A-07A (committed)

---

## Objective

Resolve GAP-1 identified in P0-A-07A: `downtime_reasons.py` was using
`admin.user.manage` (IAM domain action code) to guard downtime reason admin
mutation routes. This is a semantic mismatch — downtime reason administration is
configuration/reference-data governance, not IAM user lifecycle management.

---

## Changes Made

### 1. `backend/app/security/rbac.py`

Added `admin.downtime_reason.manage` to `ACTION_CODE_REGISTRY`:

```python
# Configuration administration action codes — govern platform-administered
# reference/config data (not manufacturing master data, not IAM).
"admin.downtime_reason.manage": "ADMIN",
```

Total action codes: **19** (was 18).

### 2. `backend/app/api/v1/downtime_reasons.py`

Replaced `require_action("admin.user.manage")` with
`require_action("admin.downtime_reason.manage")` on both admin mutation routes:

| Route | Before | After |
|---|---|---|
| `POST /downtime-reasons` | `admin.user.manage` | `admin.downtime_reason.manage` |
| `POST /downtime-reasons/{code}/deactivate` | `admin.user.manage` | `admin.downtime_reason.manage` |
| `GET /downtime-reasons` | `require_authenticated_identity` | `require_authenticated_identity` (unchanged) |

### 3. `docs/design/02_registry/action-code-registry.md`

Added new "Configuration Administration" section with entry:

| Action Code | Family | Description |
|---|---|---|
| `admin.downtime_reason.manage` | ADMIN | Create, update, or deactivate a Downtime Reason reference entry |

Added history entry for P0-A-07B.

### 4. `backend/tests/test_rbac_action_registry_alignment.py`

- Updated module docstring: GAP-1 marked as RESOLVED in P0-A-07B.
- Added `_EXPECTED_ADMIN_CONFIG_CODES = frozenset({"admin.downtime_reason.manage"})`.
- Added `_EXPECTED_ADMIN_CONFIG_CODES` to `_ALL_EXPECTED_CODES` union.
- Added `test_all_canonical_admin_config_codes_in_registry` — positive registry completeness test.
- Updated `test_admin_codes_map_to_admin_family` — includes config codes in admin family check.
- Replaced `test_known_gap_downtime_reasons_uses_admin_user_manage` (GAP-1 lock) with
  `test_known_gap_downtime_reasons_resolved_uses_dedicated_action_code` (resolved-gap positive assertion).

Total tests in file: **18** (was 17).

---

## Compatibility

**Policy A — Strict semantic cutover** applied:

- System is pre-production.
- `test_downtime_reason_admin_routes.py` uses `_override_admin_dependency` which dynamically
  finds the non-`get_db` dependency on each route — survives action code rename without any
  structural change.
- No existing production DB grants using `admin.user.manage` for downtime reason operations.

---

## Verification Results

| Command | Result |
|---|---|
| `pytest -q tests/test_rbac_action_registry_alignment.py` | **18 passed** |
| `pytest -q tests/test_downtime_reason_admin_routes.py tests/test_access_service.py tests/test_qa_foundation_authorization.py` | **8 passed** |
| `pytest -q tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | **27 passed, 3 skipped** |

All pre-existing tests pass. No regressions.

---

## GAP Status (Post P0-A-07B)

| GAP | Description | Status |
|---|---|---|
| GAP-1 | `downtime_reasons.py` used `admin.user.manage` for downtime admin mutations | **RESOLVED** |
| GAP-2 | `security_events.py` uses `admin.user.manage` for admin-restricted read | Open — deferred |
| GAP-3 | `impersonations.py` uses `require_authenticated_identity` instead of `require_action` | Open — deferred |

---

## Registry Summary (Post P0-A-07B)

| Domain | Count | Codes |
|---|---|---|
| Execution | 9 | `execution.{start,complete,report_quantity,pause,resume,start_downtime,end_downtime,close,reopen}` |
| Approval | 2 | `approval.{create,decide}` |
| IAM / Platform Admin | 3 | `admin.{impersonation.create,impersonation.revoke,user.manage}` |
| MMD | 3 | `admin.master_data.{product,routing,resource_requirement}.manage` |
| Configuration Admin | 1 | `admin.downtime_reason.manage` |
| **Total** | **19** | |

---

## Invariants Confirmed

1. `admin.downtime_reason.manage` is in `ACTION_CODE_REGISTRY` with `ADMIN` family.
2. `downtime_reasons.py` uses `admin.downtime_reason.manage` for both admin mutation routes.
3. `downtime_reasons.py` does not use `admin.user.manage` for downtime reason operations.
4. `admin.user.manage` remains correct in IAM-domain routes (`users.py`, etc.).
5. Runtime registry and governance doc are in sync (19 codes each, all documented).
6. GAP-2 and GAP-3 state is unchanged and still locked by their respective test cases.
