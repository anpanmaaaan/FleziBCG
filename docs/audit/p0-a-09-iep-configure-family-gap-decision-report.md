# P0-A-09 IEP CONFIGURE Family Gap Decision Report

**Slice:** P0-A-09  
**Date:** 2026-05-03  
**Status:** COMPLETE  
**Decision Type:** Governance boundary lock (no runtime behavior change)

---

## Summary

P0-A-09 classifies the remaining IEP/CONFIGURE family gap as an intentional,
reserved-family posture and locks it with tests.

- `SYSTEM_ROLE_FAMILIES` keeps `IEP -> {VIEW, CONFIGURE}`.
- `ACTION_CODE_REGISTRY` currently has zero `CONFIGURE`-family action codes.
- No current API route uses a `CONFIGURE` action guard.
- `seed_rbac_core()` remains aligned: it seeds family-level `CONFIGURE` permission
  and links it to `IEP` without any action-level CONFIGURE permissions.

Selected **Option A (decision/report + boundary tests)**. No production RBAC runtime,
route guard, schema, or API behavior changes were made.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Backend foundation decision + RBAC/action registry governance + CONFIGURE-family gap analysis + QA/contract hardening + no-runtime-behavior-change
- **Hard Mode MOM:** v3
- **Reason:** Task touches RBAC permission family semantics, IEP role/action boundary, system role permission seeding, authorization registry governance, and future admin/governance readiness.

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Source | Evidence |
|---|---|
| `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md` | Identified debt: IEP has CONFIGURE family but no CONFIGURE action codes. Recommended follow-up slice. |
| `backend/app/security/rbac.py` | `PermissionFamily` includes `CONFIGURE`; `SYSTEM_ROLE_FAMILIES["IEP"] = {"VIEW", "CONFIGURE"}`; `ACTION_CODE_REGISTRY` has 21 codes with families EXECUTE/APPROVE/ADMIN only. |
| `docs/design/02_registry/action-code-registry.md` | Defines CONFIGURE family conceptually, but registry list contains no CONFIGURE action entries. |
| `backend/app/api/v1/*.py` guard scan | Route guards use execution.*, approval.*, and admin.* action codes only; no CONFIGURE code usage. |
| `docs/design/00_platform/authorization-model-overview.md` | IEP exists as role-level actor, but no concrete IEP CONFIGURE action naming authority provided. |
| `docs/design/01_foundation/role-model-and-scope-resolution.md` | IEP listed in role model; no concrete action-code-level contract for IEP configure mutations. |

### Current CONFIGURE Family Source Map

| Source Area | Evidence | Decision |
|---|---|---|
| `PermissionFamily` in `rbac.py` | `Literal["VIEW", "EXECUTE", "APPROVE", "CONFIGURE", "ADMIN"]` | CONFIGURE remains valid as family concept |
| `SYSTEM_ROLE_FAMILIES` in `rbac.py` | `IEP: {"VIEW", "CONFIGURE"}` | Keep unchanged |
| `ACTION_CODE_REGISTRY` in `rbac.py` | No code mapped to `CONFIGURE` | No action added in this slice |
| Seed logic `seed_rbac_core()` | Seeds family-level permission rows for all families including CONFIGURE; action-level rows only for registry entries | Aligned and unchanged |
| API routes in `backend/app/api/v1/` | No CONFIGURE action guard present | No route change required |

### IEP / CONFIGURE Usage Map

| Source / Route / Doc | Mentions IEP/CONFIGURE? | Current Action? | Decision |
|---|---|---|---|
| `backend/app/security/rbac.py` | Yes | IEP role family includes CONFIGURE; no CONFIGURE action codes | Keep as reserved-family posture |
| `backend/app/api/v1/*.py` | Yes (`require_action` usage) | None in CONFIGURE family | Do not invent guard |
| `backend/app/services/*.py` | No relevant concrete IEP CONFIGURE command/action naming found | None | No runtime change |
| `docs/design/00_platform/authorization-model-overview.md` | Yes (IEP role mention) | No concrete IEP action name | Insufficient authority for Option B |
| `docs/design/01_foundation/role-model-and-scope-resolution.md` | Yes (IEP role mention) | No concrete action name | Insufficient authority for Option B |
| `docs/design/02_registry/action-code-registry.md` | Yes (CONFIGURE family definition) | No CONFIGURE action entries | Supports Option A lock |

### Action Boundary Decision

A CONFIGURE action code is **not required now** and must **not** be invented in this slice.

- No current route/service requires a concrete IEP CONFIGURE action.
- No authoritative doc defines exact action naming (`iep.configure.*`, `admin.iep.*`, etc.).
- Zero CONFIGURE action codes is acceptable temporarily as reserved-family posture.

Before future IEP/configure implementation, a dedicated design/contract slice must define:
1. exact action code name,
2. target route/service command scope,
3. SoD/audit requirements,
4. registry + runtime + tests rollout.

### Implementation Option Decision

**Selected Option A — Decision/report + boundary lock tests**

- Production code changes needed: **No**
- Runtime behavior changes needed: **No**
- Files changed: boundary tests + CI lists + report only

### Runtime Behavior Decision

- `has_action` semantics: unchanged
- Route guards: unchanged
- `seed_rbac_core()` behavior: unchanged
- `ACTION_CODE_REGISTRY`: unchanged

### Backward Compatibility Decision

- Existing role taxonomy preserved
- Existing action names preserved
- No schema/migration changes
- No API/frontend/Admin UI changes

### Invariant Map

| Invariant | Evidence | Test Needed |
|---|---|---|
| No CONFIGURE action code is invented without authority | No authoritative naming/route contract found | Yes |
| IEP CONFIGURE posture is documented as reserved family | `SYSTEM_ROLE_FAMILIES` + decision report | Yes |
| Seed remains aligned | Existing P0-A-08 seed tests + new boundary tests | Yes |
| Runtime auth behavior unchanged | No changes in evaluator/guards/registry | Yes (regression) |
| No route guard changes unless justified | No route changes in this slice | Yes (route regression) |
| No migration/frontend/Admin UI added | Scope policy | Yes (migration sanity + diff review) |

### Test Matrix

| Test Area | Test Case | Expected Result | File |
|---|---|---|---|
| CONFIGURE boundary | IEP includes CONFIGURE family | PASS | `backend/tests/test_rbac_configure_family_boundary.py` |
| CONFIGURE boundary | Registry has zero CONFIGURE-family action codes | PASS | `backend/tests/test_rbac_configure_family_boundary.py` |
| CONFIGURE boundary | API routes do not require CONFIGURE action code | PASS | `backend/tests/test_rbac_configure_family_boundary.py` |
| Seed boundary | Seed creates family-level CONFIGURE permission row | PASS | `backend/tests/test_rbac_configure_family_boundary.py` |
| Seed boundary | Seed links IEP to CONFIGURE family permission | PASS | `backend/tests/test_rbac_configure_family_boundary.py` |
| Seed boundary | No action-level CONFIGURE permission rows created | PASS | `backend/tests/test_rbac_configure_family_boundary.py` |
| Seed/action regression | P0-A-08 seed alignment suite | PASS | `backend/tests/test_rbac_seed_alignment.py` |
| Registry regression | Action registry alignment suite | PASS | `backend/tests/test_rbac_action_registry_alignment.py` |

### Risk / Stop Condition Map

| Risk | Mitigation |
|---|---|
| Inventing scope too early | Option A selected; no new action code introduced |
| Role family/action mismatch drift | Boundary tests lock zero CONFIGURE-action posture |
| Seed drift | Existing seed alignment tests + new CONFIGURE boundary tests |
| Brittle scans | Route scan constrained to `backend/app/api/v1/*.py` and `require_action("...")` pattern only |
| Over-granting roles | No new actions; no role-family change; existing SoD regressions remain green |

### Verdict Before Coding

**`ALLOW_P0A09_IEP_CONFIGURE_ACTION_BOUNDARY_LOCK`**

---

## Selected Option

**Option A — Decision/report only + boundary lock tests**

---

## CONFIGURE Family Decision

Current posture is explicitly accepted and locked:

- `CONFIGURE` is a valid role-family capability (IEP).
- Action-code-level CONFIGURE remains intentionally empty until a future,
  authoritative IEP/configuration command contract exists.

No new action code added in P0-A-09.

---

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `.github/copilot-instructions-hard-mode-mom-v2-addendum.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `docs/design/INDEX.md`
- `docs/design/AUTHORITATIVE_FILE_MAP.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/00_platform/authorization-model-overview.md`
- `docs/design/01_foundation/role-model-and-scope-resolution.md`
- `docs/design/02_registry/action-code-registry.md`
- `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md`
- `docs/audit/p0-a-08-role-permission-db-seeding-alignment-report.md`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/services/access_service.py`
- `backend/app/models/rbac.py`
- `backend/app/api/v1/*.py`
- `backend/tests/test_rbac_seed_alignment.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `backend/tests/test_access_service.py`
- `backend/tests/test_scope_rbac_foundation_alignment.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_rbac_configure_family_boundary.py` | Created new boundary lock suite (6 tests) |
| `.github/workflows/backend-ci.yml` | Added P0-A-09 boundary test step and summary text |
| `.github/workflows/pr-gate.yml` | Added new boundary test to targeted backend test list |
| `docs/audit/p0-a-09-iep-configure-family-gap-decision-report.md` | Created report |

---

## Tests Added / Updated

### New

`backend/tests/test_rbac_configure_family_boundary.py`:

1. `test_iep_role_includes_configure_family`
2. `test_action_registry_has_zero_configure_family_action_codes`
3. `test_api_routes_do_not_require_configure_action_codes`
4. `test_seed_creates_configure_family_permission_row`
5. `test_seed_links_iep_to_configure_family_permission`
6. `test_seed_creates_no_configure_action_permissions`

### Updated

No existing test logic changed in this slice.

---

## Verification Commands Run

```powershell
cd backend
python -m pytest -q tests/test_rbac_configure_family_boundary.py
python -m pytest -q tests/test_rbac_seed_alignment.py
python -m pytest -q tests/test_rbac_action_registry_alignment.py
python -m pytest -q tests/test_access_service.py tests/test_qa_foundation_authorization.py
python -m pytest -q tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py
python -m pytest -q tests/test_downtime_reason_admin_routes.py
python -m pytest -q tests/test_security_events_endpoint.py tests/test_admin_audit_security_events.py
python -m pytest -q tests/test_impersonation_routes.py
python -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
python -m alembic heads
```

---

## Results

| Command | Result | Classification |
|---|---|---|
| `test_rbac_configure_family_boundary.py` | 6 passed | PASS |
| `test_rbac_seed_alignment.py` | 20 passed | PASS |
| `test_rbac_action_registry_alignment.py` | 20 passed | PASS |
| `test_access_service.py` + `test_qa_foundation_authorization.py` | 6 passed | PASS |
| `test_scope_rbac_foundation_alignment.py` + `test_pr_gate_workflow_config.py` | 13 passed | PASS |
| `test_downtime_reason_admin_routes.py` | 2 passed | PASS |
| `test_security_events_endpoint.py` + `test_admin_audit_security_events.py` | 5 passed | PASS |
| `test_impersonation_routes.py` | 10 passed | PASS |
| migration sanity trio | 14 passed, 3 skipped | PASS_WITH_LOCAL_SKIPS |
| `alembic heads` | 0010 (head) | PASS |

**Total:** 96 passed, 3 skipped, 0 failed.

Local skips are expected live-Postgres checks; CI should cover with containerized Postgres.

---

## Existing Gaps / Known Debts

1. IEP CONFIGURE action code naming remains deferred; must be defined by a dedicated
   future design contract before implementation.
2. No current IEP/configuration mutation route exists that requires CONFIGURE action guard.
3. Live Postgres-dependent migration checks still skip locally when DB is unavailable.

---

## Scope Compliance

- No new action code introduced without authority
- No RBAC runtime evaluator changes
- No route guard changes
- No schema/migration changes
- No frontend/Admin UI/API additions
- No tenant/scope lifecycle behavior changes
- No MMD/execution/quality/material contract expansion

---

## Risks

- Future contributors may add IEP/configure behavior without action-code governance gate
  if boundary tests are ignored.
- CONFIGURE family may remain under-specified until a dedicated IEP slice defines concrete commands.

Mitigation: P0-A-09 boundary tests and this decision report establish explicit stop/go criteria.

---

## Recommended Next Slice

**P0-A-10 — IEP Configuration Contract Definition (Design-first, no implementation by default)**

Produce authoritative contract for any future IEP/configuration commands:
- explicit domain scope and command list,
- exact action code naming,
- route/service boundaries,
- SoD/audit requirements,
- rollout and regression plan.

Only after that contract exists should Option-B style action code introduction be considered.

---

## Stop Conditions Hit

None.
