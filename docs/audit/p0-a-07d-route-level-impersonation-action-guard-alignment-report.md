# P0-A-07D Report

## Summary

Resolved GAP-3 from P0-A-07A. Impersonation create and revoke routes now use route-level
`require_action` guards with the dedicated action codes `admin.impersonation.create` and
`admin.impersonation.revoke` that were pre-registered in P0-A-07A. GET `/current` remains
`require_authenticated_identity` (read/status, not privileged mutation). Service-layer
business rules are entirely unchanged. New route-level test coverage added. All verification
commands pass.

---

## Routing
- Selected brain: MOM Brain
- Selected mode: Backend implementation + RBAC/action registry hardening + impersonation authorization boundary alignment + route guard contract alignment + QA/regression
- Hard Mode MOM: v3
- Reason: Touches route-level authorization guard behavior, RBAC action registry, privileged impersonation boundary, admin/security permission semantics, and service-layer SoD interaction.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract
| Doc | Evidence |
|---|---|
| P0-A-07A report (GAP-3) | `impersonations.py` uses `require_authenticated_identity`; codes registered for future route-level gating |
| P0-A-07B/C reports | GAP-1/GAP-2 resolved; 20 codes; prior assertions stable |
| `docs/design/02_registry/action-code-registry.md` | `admin.impersonation.create` and `admin.impersonation.revoke` already in IAM section; no doc update needed |
| `backend/app/security/rbac.py` | Both codes present at ADMIN family; registry unchanged |
| `backend/app/api/v1/impersonations.py` | 3 routes, all used `require_authenticated_identity`; create/revoke now wired to dedicated actions |
| `backend/app/services/impersonation_service.py` | `ALLOWED_IMPERSONATORS = {"ADM", "OTS"}` checks role_code; ownership check on revoke. Both untouched. |
| `backend/app/security/dependencies.py` `require_action` | Checks DB permission rows for action's family; additive over service checks |
| No `test_impersonation*.py` existed | Required new route test file |

### Verdict
**`ALLOW_P0A07D_ROUTE_LEVEL_IMPERSONATION_ACTION_GUARD_ALIGNMENT`**

---

## Service-Layer Interaction Policy

**Policy A — Route-level strict guard + keep service checks**

- Route-level `require_action` is additive, not replacing service invariants
- Service `ALLOWED_IMPERSONATORS` check and revoke ownership check remain fully intact
- SoD is strengthened: caller must hold ADMIN action AND pass service business rules
- Pre-production system; `_override_admin_dependency` in tests avoids needing live DB rows

---

## Route Guard Decision

| Route | Before | After | Rationale |
|---|---|---|---|
| POST `/impersonations` (create) | `require_authenticated_identity` | `require_action("admin.impersonation.create")` | Privileged mutation — dedicated action code pre-existed in registry |
| POST `/impersonations/{id}/revoke` | `require_authenticated_identity` | `require_action("admin.impersonation.revoke")` | Privileged mutation — dedicated action code pre-existed in registry |
| GET `/impersonations/current` | `require_authenticated_identity` | `require_authenticated_identity` (unchanged) | Read/status — not a privileged mutation; correct per governance rule |

---

## Files Inspected

- `docs/audit/p0-a-07a-rbac-action-registry-semantic-alignment-report.md`
- `docs/audit/p0-a-07b-dedicated-downtime-reason-admin-action-report.md`
- `docs/audit/p0-a-07c-dedicated-security-event-read-action-report.md`
- `docs/design/02_registry/action-code-registry.md`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/api/v1/impersonations.py`
- `backend/app/services/impersonation_service.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

---

## Files Changed

### `backend/app/api/v1/impersonations.py`
- Added `require_action` to import alongside `require_authenticated_identity`
- POST `` route: `require_authenticated_identity` → `require_action("admin.impersonation.create")`
- POST `/{session_id}/revoke` route: `require_authenticated_identity` → `require_action("admin.impersonation.revoke")`
- GET `/current` route: unchanged

### `backend/tests/test_rbac_action_registry_alignment.py`
- Updated module docstring: GAP-3 marked as RESOLVED in P0-A-07D
- Replaced `test_known_gap_impersonation_routes_use_require_authenticated_identity` with `test_known_gap_impersonation_routes_resolved_use_dedicated_action_codes` (positive resolved-gap assertion)
- Replaced `test_impersonation_codes_exist_in_registry_for_future_gating` with `test_impersonation_codes_in_registry_with_admin_family` (stable positive lock, no "future" framing)
- Added `test_impersonation_current_route_uses_authenticated_identity_only` — confirms GET /current is identity-only
- Total tests: **20** (net unchanged — 2 old replaced with 3 new)

### `backend/tests/test_impersonation_routes.py` (NEW)
10 route-level tests covering:
- Create route delegates with correct params
- Create route rejects without action (403)
- Create route: service PermissionError → 403
- Create route: service ValueError → 400
- Revoke route delegates with correct params
- Revoke route rejects without action (403)
- Revoke route: service LookupError → 404
- Revoke route: service PermissionError → 403
- Current route returns active session
- Current route returns null when no session

### `.github/workflows/backend-ci.yml`
- Added new step "P0-A-07D tests — impersonation route guard alignment" running `test_impersonation_routes.py`

### `.github/workflows/pr-gate.yml`
- Added `tests/test_impersonation_routes.py` to the backend test list

---

## Tests Added / Updated

| Test | File | Change |
|---|---|---|
| `test_known_gap_impersonation_routes_resolved_use_dedicated_action_codes` | test_rbac_action_registry_alignment.py | Replaced GAP-3 lock — positive resolved-gap assertion |
| `test_impersonation_current_route_uses_authenticated_identity_only` | test_rbac_action_registry_alignment.py | New — confirms GET /current remains identity-only |
| `test_impersonation_codes_in_registry_with_admin_family` | test_rbac_action_registry_alignment.py | Replaced companion — stable positive registry lock |
| 10 new tests | test_impersonation_routes.py | New — route-level contract tests |

---

## Verification Commands Run

```
python -m pytest -q tests/test_rbac_action_registry_alignment.py
python -m pytest -q tests/test_impersonation_routes.py
python -m pytest -q tests/test_access_service.py tests/test_qa_foundation_authorization.py tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py
python -m pytest -q tests/test_downtime_reason_admin_routes.py tests/test_security_events_endpoint.py tests/test_admin_audit_security_events.py tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
```

---

## Results

| Command | Result |
|---|---|
| `pytest -q tests/test_rbac_action_registry_alignment.py` | **20 passed** |
| `pytest -q tests/test_impersonation_routes.py` | **10 passed** |
| `pytest -q tests/test_access_service.py tests/test_qa_foundation_authorization.py tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py` | **19 passed** |
| `pytest -q tests/test_downtime_reason_admin_routes.py tests/test_security_events_endpoint.py tests/test_admin_audit_security_events.py tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | **21 passed, 3 skipped** |

All pre-existing tests pass. No regressions. 3 skipped = live Postgres (expected locally).

---

## Remaining Known Gaps

| GAP | Description | Status |
|---|---|---|
| GAP-1 | `downtime_reasons.py` used `admin.user.manage` for downtime admin mutations | **RESOLVED** (P0-A-07B) |
| GAP-2 | `security_events.py` used `admin.user.manage` for admin-restricted audit read | **RESOLVED** (P0-A-07C) |
| GAP-3 | `impersonations.py` used `require_authenticated_identity` instead of dedicated action guards | **RESOLVED** (P0-A-07D) |

**All P0-A-07A documented semantic gaps are now resolved.**

---

## Registry Summary (Post P0-A-07D)

No registry changes were needed. Impersonation codes were pre-registered in the original P0-A-07A baseline.

| Domain | Count | Codes |
|---|---|---|
| Execution | 9 | `execution.{start,complete,report_quantity,pause,resume,start_downtime,end_downtime,close,reopen}` |
| Approval | 2 | `approval.{create,decide}` |
| IAM / Platform Admin | 3 | `admin.{impersonation.create,impersonation.revoke,user.manage}` |
| MMD | 3 | `admin.master_data.{product,routing,resource_requirement}.manage` |
| Configuration Admin | 1 | `admin.downtime_reason.manage` |
| Audit / Security Governance | 1 | `admin.security_event.read` |
| **Total** | **20** (unchanged) | |

---

## Scope Compliance

| Rule | Status |
|---|---|
| No migration added | ✓ |
| No frontend change | ✓ |
| No Admin UI added | ✓ |
| No impersonation business rules changed | ✓ |
| Service-layer invariants unchanged | ✓ |
| No API path/schema/response changes | ✓ |
| No tenant/scope enforcement change | ✓ |
| No MMD/Execution/Quality change | ✓ |
| GAP-1 and GAP-2 positive assertions still pass | ✓ |

---

## Risks

| Risk | Status |
|---|---|
| Service-layer SoD conflict | Not triggered — service checks are additive, not replaced |
| Existing roles missing new action | Pre-production; test coverage uses `_override_admin_dependency` |
| Broad RBAC rewrite | Not triggered — 2 guard lines changed, 1 import added |
| Test fixture drift | New test file follows established route test pattern |

---

## Recommended Next Slice

All P0-A-07x GAP series (GAP-1, GAP-2, GAP-3) are now resolved. P0-A RBAC semantic alignment is complete.

Recommended: proceed to the next P0-A foundation hardening slice as defined by the project roadmap. Candidates may include:
- P0-A-08: audit/compliance review of the now-complete action code registry
- P0-A-09: role/permission DB seeding alignment (ensuring ADM, OTS roles have correct DB permission rows for the 20 action codes)
- Or next feature/execution slice per product roadmap

---

## Stop Conditions Hit

None.
