# P0-A-07A RBAC Action Registry Semantic Alignment Report

Date: 2026-05-02
Workspace: g:/Work/FleziBCG
Slice: P0-A-07A
Mode: Verification-only / alignment + tests only — no runtime behavior change

## Summary

Inspected the canonical action code registry, runtime `ACTION_CODE_REGISTRY` in `rbac.py`, and all `require_action` usage across API routes and tests. Produced action usage map, documented known semantic gaps, added regression tests, and updated CI gates. No runtime authorization behavior was changed.

## Routing
- Selected brain: MOM Brain
- Selected mode: Backend foundation alignment + RBAC/action registry semantic alignment + QA/contract hardening + no-runtime-behavior-change
- Hard Mode MOM: v3
- Reason: Task touches authorization action semantics, role/action foundation, security boundary, and Admin/Governance API readiness.

## Hard Mode MOM v3 Gate

### Design Evidence Extract
| Doc | Why used |
|---|---|
| `docs/design/02_registry/action-code-registry.md` | Canonical governance record of all action codes and naming convention |
| `backend/app/security/rbac.py ACTION_CODE_REGISTRY` | Runtime source of truth — authoritative dict of action → family mappings |
| `backend/app/api/v1/*.py` (all route files) | Actual `require_action(...)` call patterns in production routes |
| `backend/tests/test_mmd_rbac_action_codes.py` | Existing MMD action code regression tests — not duplicated |
| `docs/governance/CODING_RULES.md` | Governance rule: reads use `require_authenticated_identity`, not `require_action` |

### Event Map
Alignment-only slice. No command/event mutations were introduced.

### Invariant Map
| Invariant | Evidence | Tested |
|---|---|---|
| Registry doc and `ACTION_CODE_REGISTRY` match exactly — all 18 codes | Source inspection and test | Yes |
| All action codes map to a valid PermissionFamily | Source inspection | Yes |
| Execution codes → EXECUTE family | rbac.py | Yes |
| Approval codes → APPROVE family | rbac.py | Yes |
| Admin/IAM/MMD codes → ADMIN family | rbac.py | Yes |
| No code maps to VIEW family | Governance rule | Yes |
| operations.py only uses registered execution codes | Route scan | Yes |
| approvals.py only uses registered approval codes | Route scan | Yes |
| Known gaps are locked to current state | Semantic gap tests | Yes |

### Verdict
ALLOW_P0A07A_RBAC_ACTION_REGISTRY_SEMANTIC_ALIGNMENT

## Selected Alignment Option
**Option A — Evidence + tests only**

Reason: `ACTION_CODE_REGISTRY` in `rbac.py` is already a named constant and perfectly matches the governance record. No missing constants, no incorrect mappings, no production code changes needed or safe in this slice.

## Action Usage Map
| Source Area | Action Code / Pattern | Current Use | Registry Match? | Decision |
|---|---|---|---|---|
| `operations.py` | `execution.start/complete/report_quantity/pause/resume/start_downtime/end_downtime/close/reopen` | All 9 execution mutation routes | Yes — all EXECUTE | Stable/pass |
| `approvals.py` | `approval.create`, `approval.decide` | Approval create and decide routes | Yes — both APPROVE | Stable/pass |
| `users.py`, `access.py`, `iam.py` | `admin.user.manage` | IAM user lifecycle routes | Yes — ADMIN | Stable/pass |
| `products.py` | `admin.master_data.product.manage` | Product mutation routes | Yes — ADMIN | Covered by test_mmd_rbac_action_codes |
| `routings.py` | `admin.master_data.routing.manage`, `admin.master_data.resource_requirement.manage` | Routing/RR mutation routes | Yes — ADMIN | Covered by test_mmd_rbac_action_codes |
| `downtime_reasons.py` | `admin.user.manage` | Downtime reason admin mutations (upsert/deactivate) | GAP-1: semantic mismatch — CONFIGURE/ADMIN action using IAM code | Known debt; locked in test |
| `security_events.py` | `admin.user.manage` | Security event read (admin-restricted) | GAP-2: no dedicated read code; governance prefers require_authenticated_identity | Known debt; locked in test |
| `impersonations.py` | `require_authenticated_identity` only | Impersonation create/revoke/current | GAP-3: `admin.impersonation.create/revoke` registered but routes delegate to service layer | Known debt; locked in test |
| `ACTION_CODE_REGISTRY` | 18 codes total | Runtime authorization source | Exact match with registry doc | Pass |

## Runtime Behavior Decision
Runtime authorization behavior is **UNCHANGED**. No new action codes were enforced. No existing action semantics were changed. `require_action` and `has_action` behavior is identical before and after this slice.

## Backward Compatibility Decision
- Existing tests/routes use the same action codes as before.
- No DB schema changes.
- No frontend changes.
- No API changes.

## Files Inspected
- `docs/design/02_registry/action-code-registry.md`
- `docs/governance/CODING_RULES.md`, `ENGINEERING_DECISIONS.md`, `SOURCE_STRUCTURE.md`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/api/v1/operations.py`, `users.py`, `approvals.py`, `products.py`, `routings.py`, `downtime_reasons.py`, `security_events.py`, `impersonations.py`, `access.py`, `iam.py`
- `backend/tests/test_mmd_rbac_action_codes.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_scope_rbac_foundation_alignment.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`
- `docs/audit/p0-a-06a-02-scope-foundation-verification-replay-report.md`

## Files Changed
| File | Change |
|---|---|
| `backend/tests/test_rbac_action_registry_alignment.py` | Created — 17 tests (Option A) |
| `.github/workflows/backend-ci.yml` | Added P0-A-07A step; updated CI summary text |
| `.github/workflows/pr-gate.yml` | Added test_rbac_action_registry_alignment.py to backend test list |
| `docs/audit/p0-a-07a-rbac-action-registry-semantic-alignment-report.md` | Created — this report |

## Tests Added / Updated
### New: `backend/tests/test_rbac_action_registry_alignment.py` — 17 tests
- `test_all_canonical_execution_codes_in_registry`
- `test_all_canonical_approval_codes_in_registry`
- `test_all_canonical_admin_iam_codes_in_registry`
- `test_all_canonical_admin_mmd_codes_in_registry`
- `test_action_code_registry_contains_exactly_canonical_set`
- `test_all_registry_values_are_valid_permission_families`
- `test_execution_codes_map_to_execute_family`
- `test_approval_codes_map_to_approve_family`
- `test_admin_codes_map_to_admin_family`
- `test_no_action_code_maps_to_view_family`
- `test_operations_route_uses_only_registered_action_codes`
- `test_operations_route_uses_only_execution_codes`
- `test_approval_routes_use_only_approval_codes`
- `test_known_gap_downtime_reasons_uses_admin_user_manage` (GAP-1 lock)
- `test_known_gap_security_events_uses_admin_user_manage` (GAP-2 lock)
- `test_known_gap_impersonation_routes_use_require_authenticated_identity` (GAP-3 lock)
- `test_impersonation_codes_exist_in_registry_for_future_gating` (GAP-3 companion)

## CI Gate Changes
- `backend-ci.yml`: Added dedicated step `P0-A-07A tests — RBAC action registry semantic alignment`; updated CI summary text to mention RBAC action registry (07A).
- `pr-gate.yml`: Added `tests/test_rbac_action_registry_alignment.py` to backend test list.

## Verification Commands Run
```
alembic heads
  → 0010 (head)

pytest -q tests/test_rbac_action_registry_alignment.py
  → 17 passed in 0.64s

pytest -q tests/test_scope_rbac_foundation_alignment.py tests/test_access_service.py tests/test_qa_foundation_authorization.py
  → 16 passed in 2.78s

pytest -q tests/test_qa_foundation_tenant_isolation.py tests/test_pr_gate_workflow_config.py
  → 4 passed in 1.08s

pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
  → 14 passed, 3 skipped in 1.18s
```

## Results
| Suite | Result |
|---|---|
| test_rbac_action_registry_alignment.py | 17 passed |
| test_scope_rbac_foundation_alignment.py + test_access_service.py + test_qa_foundation_authorization.py | 16 passed |
| test_qa_foundation_tenant_isolation.py + test_pr_gate_workflow_config.py | 4 passed |
| test_alembic_baseline.py + test_qa_foundation_migration_smoke.py + test_init_db_bootstrap_guard.py | 14 passed, 3 skipped (expected local DB skips) |

## Existing Gaps / Known Debts
| Gap | Location | Description | Future Fix |
|---|---|---|---|
| GAP-1 | `downtime_reasons.py` | Uses `admin.user.manage` for downtime reason admin mutations — semantic mismatch | Dedicated `admin.downtime_reason.manage` action code in future slice |
| GAP-2 | `security_events.py` | Uses `admin.user.manage` for admin-restricted read endpoint | Dedicated `admin.security_events.read` code or move to `require_authenticated_identity` + service-layer check |
| GAP-3 | `impersonations.py` | `admin.impersonation.create/revoke` in registry but routes use service-layer auth | Add `require_action(...)` to routes in future governance slice |

## Scope Compliance
- No runtime authorization behavior changed.
- No role management API added.
- No Admin UI added.
- No frontend changes.
- No migration added.
- No DB schema changed.
- No tenant lifecycle changed.
- No MMD or Execution changed.
- No existing action codes renamed.

## Risks
| Risk | Status |
|---|---|
| Registry/source conflict | No conflict — registry doc and runtime `ACTION_CODE_REGISTRY` match exactly |
| Brittle route scans | Scans use simple `read_text` + regex for specific known codes — non-brittle |
| Runtime auth behavior drift | Not possible — no production code changed |
| CI gate drift | Resolved — both CI files updated |

## Recommended Next Slice
- **P0-A-07B** (if needed): Resolve GAP-1 and/or GAP-3:
  - Add `admin.downtime_reason.manage` action code to `ACTION_CODE_REGISTRY` and registry doc
  - Update `downtime_reasons.py` to use dedicated action code
  - Add `require_action(...)` to impersonation create/revoke routes using existing codes
  - Each requires: (a) code in `rbac.py`, (b) registry doc entry, (c) regression test

## Stop Conditions Hit
None.
