# MMD-BE-10A — Reason Code Action Code Registry Patch

**Audit Report · Hard Mode MOM v3 Verified**
**Version:** 1.0
**Date:** 2026-05-04
**Task ID:** MMD-BE-10A
**Auditor:** AI Brain MOM v3 Auto-Execution
**Status:** COMPLETE

---

## §1 Task Summary

MMD-BE-10A registers `admin.master_data.reason_code.manage` in the RBAC action
code registry to satisfy the authorization governance prerequisite defined by
MMD-BE-10. No Reason Code write API is added in this slice. The action code is
registered as a forward-declared authorization contract so that future write route
implementation (MMD-BE-13) can reference a stable, well-reviewed code that was
approved independently of any runtime change.

---

## §2 Scope

**In scope:**
- `backend/app/security/rbac.py` — one line added to `ACTION_CODE_REGISTRY`
- `backend/tests/test_mmd_rbac_action_codes.py` — 7 new tests added (section MMD-BE-10A)
- `docs/design/02_registry/action-code-registry.md` — one row added to MMD table

**Out of scope:**
- Reason Code write API endpoints (deferred to MMD-BE-13)
- Reason Code write request schemas (`CreateRequest`, `UpdateRequest`)
- Any DB migration or model change
- Frontend write-path enablement
- `downtime_reasons` API or model (separate domain, unchanged)

---

## §3 Hard Mode MOM v3 Evidence

### 3.1 Design Evidence Extract

| Source | Relevant Fact |
|--------|---------------|
| `docs/design/02_domain/product_definition/reason-code-write-governance-contract.md` §13 | Backend Implementation Readiness Gate: `admin.master_data.reason_code.manage` absent; must be registered by MMD-BE-10A before write routes can be built |
| `docs/audit/mmd-be-10-reason-code-write-governance-contract.md` §6 | Authorization/Action-Code Decisions: code absent; MMD-BE-10A must add it |
| `docs/design/02_registry/action-code-registry.md` §MMD table | Governance rule #4: new action code requires (a) `rbac.py` entry, (b) registry doc entry, (c) regression test |
| `backend/app/api/v1/reason_codes.py` | Only `GET /reason-codes` and `GET /reason-codes/{id}`; both use `require_authenticated_identity`; no write routes |
| `backend/app/security/rbac.py` L57–63 (pre-patch) | `admin.master_data.bom.manage` at end of MMD block; `admin.downtime_reason.manage` starts config section |

### 3.2 Event Map

| Change | Expected Side Effects | Forbidden Side Effects |
|--------|-----------------------|------------------------|
| Add `admin.master_data.reason_code.manage` to `ACTION_CODE_REGISTRY` dict | None — static Python dict, no runtime event | No endpoint grants new capabilities; no DB change; no FE change; no operational event |

### 3.3 Invariant Map

| Invariant | Enforcement |
|-----------|-------------|
| Reason Code write API remains absent | No write routes added; existing `tests/test_reason_code_foundation_api.py` 405 tests unchanged |
| Read endpoints use `require_authenticated_identity` | Source unchanged; new test `test_reason_code_read_endpoints_do_not_require_manage_action` verifies |
| New action code maps to `ADMIN` family | Asserted by `test_reason_code_manage_action_code_is_domain_specific` |
| New code is distinct from `admin.user.manage` | Asserted by `test_reason_code_manage_action_code_is_domain_specific` |
| Existing 5 MMD action codes unchanged | Asserted by `test_existing_mmd_action_codes_unchanged_after_10a` |
| `downtime_reason` domain unaffected | Asserted by `test_reason_code_does_not_modify_downtime_reason_api` and `test_reason_code_does_not_auto_map_to_downtime_reason` |

### 3.4 State Transition Map

`ACTION_CODE_REGISTRY` is a static Python dict — not a stateful entity. No state
transitions exist. The change is purely additive (one new key–value pair).

### 3.5 Authorization Contract Map

| Route | Required Code | Before Patch | After Patch |
|-------|--------------|--------------|-------------|
| Future `POST /v1/reason-codes` | `admin.master_data.reason_code.manage` | Code absent in registry | Code present; ready for use by write route |
| Future `PATCH /v1/reason-codes/{id}` | `admin.master_data.reason_code.manage` | Code absent | Code present |
| `GET /v1/reason-codes` | `require_authenticated_identity` | Unchanged | Unchanged |
| `GET /v1/reason-codes/{id}` | `require_authenticated_identity` | Unchanged | Unchanged |

### 3.6 Registry Patch Map

| File | Change |
|------|--------|
| `backend/app/security/rbac.py` | Added `"admin.master_data.reason_code.manage": "ADMIN",` after `admin.master_data.bom.manage` entry |
| `docs/design/02_registry/action-code-registry.md` | Added row to MMD table: `\| admin.master_data.reason_code.manage \| ADMIN \| Create, update, release, or retire a Reason Code definition (when write APIs are enabled by MMD-BE-13) \|` |

### 3.7 Test Matrix

| Test | File | Result |
|------|------|--------|
| `test_reason_code_manage_action_code_exists` | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| `test_reason_code_manage_action_code_is_domain_specific` | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| `test_existing_mmd_action_codes_unchanged_after_10a` | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| `test_reason_code_read_endpoints_do_not_require_manage_action` | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| `test_no_reason_code_write_routes_exist_yet` | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| `test_reason_code_does_not_modify_downtime_reason_api` | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| `test_reason_code_does_not_auto_map_to_downtime_reason` | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| All pre-existing MMD RBAC tests (24 total) | `test_mmd_rbac_action_codes.py` | ✅ PASS |
| **Total** | | **31 passed, 0 failed** |

### 3.8 Verdict

**SAFE TO PROCEED — all stop conditions clear:**
- `admin.master_data.reason_code.manage` was confirmed absent before patching
- No write routes exist in `reason_codes.py`
- No write schemas in `reason_code.py`
- All existing MMD action codes remain unchanged
- Downtime reason domain unaffected
- Frontend MMD read regression: 134/134 pass

---

## §4 Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `backend/app/security/rbac.py` | Modified | Added `admin.master_data.reason_code.manage` → ADMIN to `ACTION_CODE_REGISTRY` |
| `backend/tests/test_mmd_rbac_action_codes.py` | Modified | Added 7 new tests in section MMD-BE-10A |
| `docs/design/02_registry/action-code-registry.md` | Modified | Added Reason Code row to MMD table |

---

## §5 Verification Results

### Backend Tests
```
tests/test_mmd_rbac_action_codes.py — 31 passed, 0 failed, 1 warning (DB not reachable — expected)
```
All 7 new MMD-BE-10A tests pass. All 24 pre-existing tests pass.

### Frontend MMD Read Regression
```
npm run check:mmd:read — 134 passed, 0 failed
```
No read-path regressions introduced.

---

## §6 Governance Compliance

| Rule | Status |
|------|--------|
| Action code naming: `admin.master_data.<entity>.manage` | ✅ Correct |
| Action code family: `ADMIN` | ✅ Correct |
| Entry in `rbac.py` | ✅ Added |
| Entry in `action-code-registry.md` | ✅ Added |
| Regression test | ✅ Added (7 tests) |
| No write API added in this slice | ✅ Confirmed |
| No frontend change | ✅ Confirmed |
| No DB migration | ✅ Confirmed |
| No auto-commit | ✅ Confirmed |

---

## §7 Definition of Done

| Criterion | Status |
|-----------|--------|
| `admin.master_data.reason_code.manage` in `ACTION_CODE_REGISTRY` | ✅ |
| Action code maps to `ADMIN` family | ✅ |
| Registry doc (`action-code-registry.md`) updated | ✅ |
| Existing MMD action codes unchanged | ✅ |
| No Reason Code write API added | ✅ |
| Reason Code read API unchanged | ✅ |
| Tests prove action code exists | ✅ |
| Tests prove Reason Code write routes still absent | ✅ |
| Backend static tests pass: 31/31 | ✅ |
| Frontend MMD read regression passes: 134/134 | ✅ |
| Audit report created | ✅ |
| No auto-commit performed | ✅ |

---

## §8 Outstanding Work

MMD-BE-10A is complete. The next authorization-dependent slice is:

- **MMD-BE-13** — Reason Code Write API (POST create, PATCH update, lifecycle commands)
  - MUST reference `admin.master_data.reason_code.manage` registered here
  - MUST NOT re-register or rename this action code
  - Triggers full Hard Mode MOM v3 (stateful lifecycle, write API, schemas)

No other outstanding work from this slice.
