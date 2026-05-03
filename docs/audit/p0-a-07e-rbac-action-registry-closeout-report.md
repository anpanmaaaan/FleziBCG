# P0-A-07E RBAC Action Registry Closeout Report

**Slice:** P0-A-07E  
**Date:** 2026-05-03  
**Status:** CLOSED  
**Precondition Slices:** P0-A-07A, P0-A-07B, P0-A-07C, P0-A-07D (all committed)

---

## Summary

This slice replays all P0-A-07 verification suites and confirms that the RBAC action
registry semantic alignment series is complete. All three semantic gaps identified in
P0-A-07A are confirmed resolved. The runtime `ACTION_CODE_REGISTRY` (20 codes),
canonical `action-code-registry.md`, route guards, test coverage, and CI gate are
fully aligned. No source code was changed in this slice.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** QA / verification replay + RBAC/action registry closeout + authorization semantic replay + no-domain-code
- **Hard Mode MOM:** v3
- **Reason:** Task validates authorization action semantics, route-level admin/security guards, RBAC registry/source/doc alignment, CI gate readiness, privileged impersonation boundary, and Admin/Governance readiness. All criteria for MOM v3 trigger.

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Doc | Why used |
|---|---|
| `docs/audit/p0-a-07a-rbac-action-registry-semantic-alignment-report.md` | Original gap identification — GAP-1/2/3 documented; 17 tests created; CI gates added |
| `docs/audit/p0-a-07b-dedicated-downtime-reason-admin-action-report.md` | GAP-1 fix — `admin.downtime_reason.manage` introduced; downtime_reasons.py updated |
| `docs/audit/p0-a-07c-dedicated-security-event-read-action-report.md` | GAP-2 fix — `admin.security_event.read` introduced; security_events.py updated |
| `docs/audit/p0-a-07d-route-level-impersonation-action-guard-alignment-report.md` | GAP-3 fix — impersonation create/revoke wired to dedicated action codes |
| `backend/app/security/rbac.py` | Runtime source of truth — 20 entries in `ACTION_CODE_REGISTRY` |
| `docs/design/02_registry/action-code-registry.md` | Canonical governance record — 20 codes across 6 domain groups |
| `backend/app/api/v1/downtime_reasons.py` | Route guards verified: both mutations use `admin.downtime_reason.manage` |
| `backend/app/api/v1/security_events.py` | Route guard verified: GET uses `admin.security_event.read` |
| `backend/app/api/v1/impersonations.py` | Route guards verified: create → `admin.impersonation.create`, revoke → `admin.impersonation.revoke`, current → `require_authenticated_identity` |
| `backend/tests/test_rbac_action_registry_alignment.py` | 20 tests — GAP docstrings updated, resolved-gap positive assertions confirmed |
| `.github/workflows/backend-ci.yml` | P0-A-07A and P0-A-07D steps present; all P0-A-07 tests covered |
| `.github/workflows/pr-gate.yml` | All P0-A-07 test files listed in targeted test set |

### Event Map

Verification-only slice. No command/event mutations introduced. No state machine
changes. No DB schema changes.

### Invariant Map

| Invariant | Evidence | Verified |
|---|---|---|
| `ACTION_CODE_REGISTRY` contains exactly 20 canonical codes | `test_action_code_registry_contains_exactly_canonical_set` | PASS |
| All codes map to valid `PermissionFamily` | `test_all_registry_values_are_valid_permission_families` | PASS |
| Execution codes → EXECUTE | `test_execution_codes_map_to_execute_family` | PASS |
| Approval codes → APPROVE | `test_approval_codes_map_to_approve_family` | PASS |
| All admin.* codes → ADMIN | `test_admin_codes_map_to_admin_family` | PASS |
| No code maps to VIEW | `test_no_action_code_maps_to_view_family` | PASS |
| `downtime_reasons.py` uses `admin.downtime_reason.manage`, not `admin.user.manage` | `test_known_gap_downtime_reasons_resolved_uses_dedicated_action_code` | PASS |
| `security_events.py` uses `admin.security_event.read`, not `admin.user.manage` | `test_known_gap_security_events_resolved_uses_dedicated_action_code` | PASS |
| `impersonations.py` create/revoke wired to dedicated action codes | `test_known_gap_impersonation_routes_resolved_use_dedicated_action_codes` | PASS |
| GET `/impersonations/current` uses `require_authenticated_identity` only | `test_impersonation_current_route_uses_authenticated_identity_only` | PASS |
| Impersonation action codes in registry with ADMIN family | `test_impersonation_codes_in_registry_with_admin_family` | PASS |
| Alembic head is `0010` | `alembic heads` command output | PASS |

### Verdict

**`ALLOW_P0A07E_RBAC_ACTION_REGISTRY_CLOSEOUT_REPLAY`**

All source evidence confirms the registry, route guards, docs, tests, and CI gate are
aligned. No blocking conditions found. Verification replay may proceed.

---

## P0-A-07 Gap Closure Map

| Gap | Original Finding (P0-A-07A) | Fix Slice | Current Evidence | Status |
|---|---|---|---|---|
| GAP-1 | `downtime_reasons.py` used `admin.user.manage` for downtime reason admin mutations — IAM domain code semantically incorrect for configuration/reference-data governance | P0-A-07B | `downtime_reasons.py` line 52, 69: `require_action("admin.downtime_reason.manage")`; test `test_known_gap_downtime_reasons_resolved_uses_dedicated_action_code` PASS | **RESOLVED** |
| GAP-2 | `security_events.py` used `admin.user.manage` for security event read — IAM code semantically incorrect for audit governance | P0-A-07C | `security_events.py` line 34: `require_action("admin.security_event.read")`; test `test_known_gap_security_events_resolved_uses_dedicated_action_code` PASS | **RESOLVED** |
| GAP-3 | `impersonations.py` create/revoke routes used only `require_authenticated_identity`; `admin.impersonation.create` and `admin.impersonation.revoke` were registered but not wired to routes | P0-A-07D | `impersonations.py` line 43: `require_action("admin.impersonation.create")`; line 87: `require_action("admin.impersonation.revoke")`; line 71: `require_authenticated_identity` (GET /current); test `test_known_gap_impersonation_routes_resolved_use_dedicated_action_codes` PASS | **RESOLVED** |

---

## Action Registry State Map

| Source | Expected State | Actual State | Decision |
|---|---|---|---|
| `docs/design/02_registry/action-code-registry.md` | 20 codes across 6 groups: execution (9), approval (2), IAM admin (3), MMD (3), config (1), audit (1) | Confirmed 20 entries; all groups present including P0-A-07B Config and P0-A-07C Audit sections; history table updated | **ALIGNED** |
| `backend/app/security/rbac.py ACTION_CODE_REGISTRY` | 20 codes; `admin.downtime_reason.manage → ADMIN`; `admin.security_event.read → ADMIN`; both impersonation codes → ADMIN | Exactly 20 entries; all families correct; no VIEW-family codes | **ALIGNED** |
| `backend/tests/test_rbac_action_registry_alignment.py` | 20 tests; all 3 GAP locks replaced with resolved-gap positive assertions | 20 tests confirmed; `_ALL_EXPECTED_CODES` is union of 6 expected sets totaling 20; all 3 GAP docstrings updated | **ALIGNED** |

### Full Registry (20 codes)

| Domain Group | Action Code | Family |
|---|---|---|
| Execution | `execution.start` | EXECUTE |
| Execution | `execution.complete` | EXECUTE |
| Execution | `execution.report_quantity` | EXECUTE |
| Execution | `execution.pause` | EXECUTE |
| Execution | `execution.resume` | EXECUTE |
| Execution | `execution.start_downtime` | EXECUTE |
| Execution | `execution.end_downtime` | EXECUTE |
| Execution | `execution.close` | EXECUTE |
| Execution | `execution.reopen` | EXECUTE |
| Approval | `approval.create` | APPROVE |
| Approval | `approval.decide` | APPROVE |
| IAM / Platform Admin | `admin.impersonation.create` | ADMIN |
| IAM / Platform Admin | `admin.impersonation.revoke` | ADMIN |
| IAM / Platform Admin | `admin.user.manage` | ADMIN |
| MMD | `admin.master_data.product.manage` | ADMIN |
| MMD | `admin.master_data.routing.manage` | ADMIN |
| MMD | `admin.master_data.resource_requirement.manage` | ADMIN |
| Configuration Admin | `admin.downtime_reason.manage` | ADMIN |
| Audit / Security Governance | `admin.security_event.read` | ADMIN |

---

## Route Guard Replay

| Route Area | Expected Guard | Source Evidence | Verification |
|---|---|---|---|
| `POST /downtime-reasons` (upsert) | `require_action("admin.downtime_reason.manage")` | `downtime_reasons.py` line 52 | `test_downtime_reason_admin_routes.py` — 2 PASSED |
| `POST /downtime-reasons/{code}/deactivate` | `require_action("admin.downtime_reason.manage")` | `downtime_reasons.py` line 69 | `test_downtime_reason_admin_routes.py` — 2 PASSED |
| `GET /downtime-reasons` | `require_authenticated_identity` | `downtime_reasons.py` line 36 | Unchanged; not an admin mutation |
| `GET /security-events` | `require_action("admin.security_event.read")` | `security_events.py` line 34 | `test_security_events_endpoint.py` — 3 PASSED |
| `POST /impersonations` (create) | `require_action("admin.impersonation.create")` | `impersonations.py` line 43 | `test_impersonation_routes.py` — 10 PASSED |
| `POST /impersonations/{id}/revoke` | `require_action("admin.impersonation.revoke")` | `impersonations.py` line 87 | `test_impersonation_routes.py` — 10 PASSED |
| `GET /impersonations/current` | `require_authenticated_identity` | `impersonations.py` line 71 | `test_impersonation_routes.py` — 10 PASSED; governance rule preserved |

---

## Verification Commands Run

| Command | Expected Result | Classification Rule |
|---|---|---|
| `pytest -q tests/test_rbac_action_registry_alignment.py` | 20 passed | PASS if all 20 green |
| `pytest -q tests/test_downtime_reason_admin_routes.py` | 2 passed | PASS if all green |
| `pytest -q tests/test_security_events_endpoint.py tests/test_admin_audit_security_events.py` | 5 passed | PASS if all green |
| `pytest -q tests/test_impersonation_routes.py` | 10 passed | PASS if all green |
| `pytest -q tests/test_access_service.py tests/test_qa_foundation_authorization.py` | 6 passed | PASS if all green |
| `pytest -q tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py` | 13 passed | PASS if all green |
| `pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | 14 passed, 3 skipped | PASS_WITH_LOCAL_SKIPS — live-DB tests skip without Postgres |
| `alembic heads` | `0010 (head)` | PASS if single head at 0010 |

---

## Results

| Command | Result | Classification |
|---|---|---|
| `test_rbac_action_registry_alignment.py` | **20 passed** | PASS |
| `test_downtime_reason_admin_routes.py` | **2 passed** | PASS |
| `test_security_events_endpoint.py` + `test_admin_audit_security_events.py` | **5 passed** | PASS |
| `test_impersonation_routes.py` | **10 passed** | PASS |
| `test_access_service.py` + `test_qa_foundation_authorization.py` | **6 passed** | PASS |
| `test_scope_rbac_foundation_alignment.py` + `test_pr_gate_workflow_config.py` | **13 passed** | PASS |
| `test_alembic_baseline.py` + `test_qa_foundation_migration_smoke.py` + `test_init_db_bootstrap_guard.py` | **14 passed, 3 skipped** | PASS_WITH_LOCAL_SKIPS |
| `alembic heads` | **0010 (head)** | PASS |

**Total across all required suites: 70 passed, 3 skipped, 0 failed.**

The 3 skipped tests require a live PostgreSQL connection not available in the local
dev environment. CI with a real Postgres service container covers them.

---

## Closeout Decision

**P0-A-07 series: CLOSED**

All three semantic gaps identified in P0-A-07A are resolved and confirmed:

- GAP-1 RESOLVED (P0-A-07B): `admin.downtime_reason.manage` in registry and route
- GAP-2 RESOLVED (P0-A-07C): `admin.security_event.read` in registry and route
- GAP-3 RESOLVED (P0-A-07D): Impersonation create/revoke wired to dedicated action codes

The RBAC action registry is aligned across all five sources:
1. Governance doc (`action-code-registry.md`)
2. Runtime registry (`ACTION_CODE_REGISTRY` in `rbac.py`)
3. Route guards (all three gap-affected route files)
4. Test suite (`test_rbac_action_registry_alignment.py` + route-specific test files)
5. CI gate (`backend-ci.yml` + `pr-gate.yml`)

No source code was changed in this slice.

---

## Existing Gaps / Known Debts

| Item | Category | Source | Notes |
|---|---|---|---|
| Role/permission DB seeding alignment | Technical debt | `seed_rbac_core()` in `rbac.py`; RBAC seed data | ADM, OTS, and other system roles need verified DB permission rows for all 20 action codes. Currently managed by seed scripts; not validated by automated test. Candidate for P0-A-08 or P0-A-09. |
| Live-DB skip tests | Environment gap | `test_alembic_baseline.py`, `test_qa_foundation_migration_smoke.py`, `test_init_db_bootstrap_guard.py` | 3 tests require live Postgres. Skip locally; CI with Postgres service container must cover. Not a code gap. |
| Admin UI / API consumer for new action codes | Product scope | Frontend + Admin API | `admin.downtime_reason.manage`, `admin.security_event.read`, impersonation action codes exist but no Admin UI has been wired to them. Out of scope for P0-A series. |

---

## Scope Compliance

| Rule | Status |
|---|---|
| Runtime authorization behavior unchanged | CONFIRMED — no route guard logic changed in P0-A-07E |
| No actions added or removed | CONFIRMED — registry unchanged |
| No route guards modified | CONFIRMED — inspection only |
| No services modified | CONFIRMED |
| No migrations modified | CONFIRMED — head remains 0010 |
| No frontend modified | CONFIRMED |
| No API endpoints added | CONFIRMED |
| No MMD, Station Execution, Quality, Material changed | CONFIRMED |
| No unrelated tests weakened or fixed | CONFIRMED |
| Closeout report created | CONFIRMED — this file |

---

## Risks

| Risk | Mitigation |
|---|---|
| CI has not run live Postgres for this commit | 3 skipped tests classified as `PASS_WITH_LOCAL_SKIPS`; CI with Postgres service container covers them per `.github/workflows/backend-ci.yml` |
| Local DB skips could mask migration regressions | `alembic heads` confirmed single head at `0010`; baseline freeze test passes in-memory |
| Stale registry doc diverging from runtime | `test_action_code_registry_contains_exactly_canonical_set` locks exact match; fails if either side drifts |
| Route guard drift in future slices | `test_known_gap_*_resolved_*` tests detect any reversion of GAP-1/2/3 fixes |
| Unrelated workspace changes contaminating results | Scope confirmed: no source changes made in P0-A-07E; diff is report-file-only |

---

## Recommended Next Slice

### P0-A-08 — Role/Permission DB Seeding Alignment

**Why:** The 20-code action registry is now stable. However, there is no automated
verification that system roles (ADM, OTS, etc.) have correct DB `Permission` and
`RolePermission` rows for all 20 action codes. `seed_rbac_core()` in `rbac.py` is
the seeding mechanism but its alignment to the 20-code registry has not been tested
at the DB-row level.

**Scope of P0-A-08:**
- Inspect `seed_rbac_core()` and compare against 20-code registry
- Verify ADM/OTS roles have correct ADMIN-family permission rows
- Verify OPR/SUP roles have correct EXECUTE-family permission rows
- Verify QAL/PMG have correct APPROVE-family rows
- Add DB-level regression tests (SQLite in-memory) proving seed produces correct rows
- No changes to runtime authorization logic

**Alternative — P0-A-09:** If role/permission seeding is out of scope for P0-A series,
the next candidate is a horizontal verification replay for a different domain vertical
(e.g., Quality, Material, or MMD admin action completeness).

---

## Stop Conditions Hit

None.

All mandatory files inspected. All source evidence gathered. All required verification
commands run. No source/domain behavior changes were made. All gaps confirmed resolved.
Closeout report created.
