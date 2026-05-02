# P0-A-06A-01 Report

## Summary
Implemented existing RBAC scope model alignment using Option A (constants + tests only).

- Existing `Scope` / `UserRoleAssignment` / `RoleScope` are treated as canonical foundation models.
- No duplicate `scope_nodes` / `scope_assignments` tables were introduced.
- No migration was added.
- Runtime RBAC/auth behavior was not changed.
- Added a dedicated foundation alignment test and wired it into backend CI + PR gate targeted test lists.

Verification commands were executed as requested. Multiple pre-existing failures were observed in unrelated baseline areas (documented below).

## Routing
- Selected brain: MOM Brain
- Selected mode: Backend foundation alignment / existing RBAC scope model alignment / schema governance / QA hardening
- Hard Mode MOM: v3 ON
- Reason: touches scope governance foundation, existing RBAC scope models, tenant-scoped authorization baseline, Alembic/CI foundation invariants

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| Existing scope model already present | `backend/app/models/rbac.py` | `Scope`, `UserRoleAssignment`, `RoleScope` exist |
| Prior 06A stop warned against duplicate tables | `docs/audit/p0-a-06a-scope-node-assignment-foundation-stop-report.md` | New `scope_nodes/scope_assignments` would duplicate architecture |
| Current baseline correction report | `docs/audit/p0-a-06a-00-alembic-head-baseline-correction-report.md` | Head was aligned to 0009 earlier |
| Access service already uses Scope/UserRoleAssignment | `backend/app/services/access_service.py` | Existing models are active runtime path |
| CI target files where new test must be included | `.github/workflows/backend-ci.yml`, `.github/workflows/pr-gate.yml` | Added new test entry |
| Requested canonical API contract path differs | `docs/design/00_platform/canonical-api-contract.md` missing; used `docs/design/05_application/canonical-api-contract.md` | Closest equivalent inspected |

### Event Map

| Command / Action | Required Event | Event Type | Decision |
|---|---|---|---|
| Add model constants | none | none_required | Non-runtime metadata only |
| Add alignment tests | none | none_required | Contract hardening only |
| Update CI targeted list | none | none_required | Workflow config only |

### Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required |
|---|---|---|---:|---|
| Existing Scope is canonical scope foundation | scope | ORM contract | No new | Yes |
| No duplicate scope tables/models | scope | test contract | No new | Yes |
| Existing RBAC runtime remains unchanged | authorization | scope-limited edits | No | Yes (regression) |
| Scope model is tenant-aware | tenant/scope | existing schema (`tenant_id`) | Already exists | Yes |
| User/role scope assignments remain compatible | scope/authorization | existing models retained | Already exists | Yes |
| No API/frontend behavior added | boundary | scope-limited edits | No | Yes |

### State Transition Map

Not applicable. No stateful workflow/command transition was changed.

### Test Matrix

| Test ID | Scenario | Type | Given | When | Then |
|---|---|---|---|---|---|
| SCOPE-01 | Existing scope models exist | regression | RBAC model module | import models | classes are present |
| SCOPE-02 | Canonical table names remain | regression | model metadata | inspect tablenames | expected names match |
| SCOPE-03 | Scope tenant/hierarchy fields present | regression | Scope table | inspect columns | tenant/scope/parent fields present |
| SCOPE-04 | UserRoleAssignment links role and scope | regression | assignment table | inspect columns | user/role/scope linkage present |
| SCOPE-05 | RoleScope compatibility model retained | regression | RoleScope table | inspect columns | role-scope columns present |
| SCOPE-06 | Scope constants exist | regression | model constants | assert values | hierarchy constants available |
| SCOPE-07 | Principal constants exist | regression | model constants | assert values | principal constants available |
| SCOPE-08 | Duplicate scope model/table names absent | regression | model module + metadata | assert absence | no `ScopeNode`/`ScopeAssignment`/duplicate tables |

### Verdict before coding

`ALLOW_P0A06A01_EXISTING_RBAC_SCOPE_ALIGNMENT`

## Selected Alignment Option
Option A — constants + tests only.

Why:
- Existing schema already provides scope node and assignment foundation.
- Runtime code already depends on these models.
- No mandatory additive fields were evidenced as blockers for this slice.

## Existing RBAC Scope Model Map

| Existing Model | Table | Current Fields | Foundation Equivalent | Decision |
|---|---|---|---|---|
| `Scope` | `scopes` | `id`, `tenant_id`, `scope_type`, `scope_value`, `parent_scope_id`, `created_at` | Canonical scope node | Keep unchanged |
| `UserRoleAssignment` | `user_role_assignments` | `id`, `user_id`, `role_id`, `scope_id`, `is_primary`, `is_active`, `valid_from`, `valid_to`, `created_at` | Canonical assignment/link | Keep unchanged |
| `RoleScope` | `role_scopes` | `id`, `user_role_id`, `scope_type`, `scope_value`, `created_at` | Existing compatibility scope-link model | Keep unchanged |

## Migration Decision
- Current Alembic head target expected by baseline tests: `0009`.
- Migration added in this slice: No.
- Reason: Option A selected; schema already sufficient for alignment objective.

## Backward Compatibility Decision
- Existing RBAC runtime behavior: unchanged.
- Existing tables retained: unchanged.
- No duplicate scope tables introduced.
- No API/frontend/admin/runtime authorization logic added.

## Files Inspected
- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `.github/copilot-instructions-hard-mode-mom-v2-addendum.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `docs/design/INDEX.md`
- `docs/design/AUTHORITATIVE_FILE_MAP.md`
- `docs/design/00_platform/product-business-truth-overview.md`
- `docs/design/00_platform/product-scope-and-phase-boundary.md`
- `docs/design/00_platform/system-overview-and-target-state.md`
- `docs/design/00_platform/domain-boundary-map.md`
- `docs/design/05_application/canonical-api-contract.md` (closest equivalent)
- `docs/design/00_platform/canonical-error-code-registry.md`
- `docs/design/00_platform/canonical-error-codes.md`
- `docs/governance/CODING_RULES.md`
- `docs/governance/ENGINEERING_DECISIONS.md`
- `docs/governance/SOURCE_STRUCTURE.md`
- `docs/audit/p0-a-06a-scope-node-assignment-foundation-stop-report.md`
- `docs/audit/p0-a-06a-00-alembic-head-baseline-correction-report.md`
- `docs/audit/p0-a-baseline-01-foundation-schema-baseline-freeze-report.md`
- `docs/audit/p0-a-ci-01-backend-ci-alembic-migration-gate-report.md`
- `docs/audit/p0-a-ci-01b-tenant-lifecycle-ci-gate-report.md`
- `docs/audit/p0-a-02a-tenant-lifecycle-anchor-report.md`
- `docs/audit/p0-a-02b-tenant-lifecycle-enforcement-report.md`
- `docs/audit/p0-a-02c-strict-tenant-existence-enforcement-report.md`
- `docs/audit/p0-a-02d-tenant-seed-bootstrap-dev-ci-report.md`
- `docs/audit/p0-a-05a-plant-hierarchy-orm-foundation-report.md`
- `backend/app/models/rbac.py`
- `backend/app/models/tenant.py`
- `backend/app/models/plant_hierarchy.py`
- `backend/app/models/user.py`
- `backend/app/security/rbac.py`
- `backend/app/security/dependencies.py`
- `backend/app/db/init_db.py`
- `backend/alembic/versions/`
- `backend/tests/test_alembic_baseline.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_qa_foundation_tenant_isolation.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

## Files Changed
| File | Change |
|---|---|
| `backend/app/models/rbac.py` | Added canonical scope/principal constants (non-runtime) |
| `backend/tests/test_scope_rbac_foundation_alignment.py` | New alignment contract tests (10 tests) |
| `.github/workflows/backend-ci.yml` | Added new test to targeted backend CI step |
| `.github/workflows/pr-gate.yml` | Added new test to targeted backend test list |
| `docs/audit/p0-a-06a-01-existing-rbac-scope-model-alignment-report.md` | New report |

## Migration Added
None.

## Tests Added / Updated
| Test | File | Purpose |
|---|---|---|
| `test_existing_scope_models_exist` | `backend/tests/test_scope_rbac_foundation_alignment.py` | Scope model presence contract |
| `test_existing_scope_table_names_are_canonical` | `backend/tests/test_scope_rbac_foundation_alignment.py` | Canonical table names lock |
| `test_scope_is_tenant_aware_and_hierarchical` | `backend/tests/test_scope_rbac_foundation_alignment.py` | Tenant + hierarchy fields lock |
| `test_scope_uniqueness_constraint_exists` | `backend/tests/test_scope_rbac_foundation_alignment.py` | Unique constraint lock |
| `test_user_role_assignment_links_role_and_scope` | `backend/tests/test_scope_rbac_foundation_alignment.py` | Assignment linkage lock |
| `test_role_scope_model_exists_as_compatibility_link` | `backend/tests/test_scope_rbac_foundation_alignment.py` | RoleScope compatibility lock |
| `test_scope_type_constants_exist` | `backend/tests/test_scope_rbac_foundation_alignment.py` | New constants lock |
| `test_principal_constants_exist` | `backend/tests/test_scope_rbac_foundation_alignment.py` | New principal constants lock |
| `test_no_duplicate_scope_model_names_exist` | `backend/tests/test_scope_rbac_foundation_alignment.py` | Duplicate model prevention |
| `test_no_duplicate_scope_table_names_registered` | `backend/tests/test_scope_rbac_foundation_alignment.py` | Duplicate table prevention |

## CI Gate Changes
| File | Change |
|---|---|
| `.github/workflows/backend-ci.yml` | Added `tests/test_scope_rbac_foundation_alignment.py` in `P0-A tests — CORS policy + PR gate workflow config` step |
| `.github/workflows/pr-gate.yml` | Added `tests/test_scope_rbac_foundation_alignment.py` in backend targeted list |

## Verification Commands Run
```bash
cd backend
python -m pytest -q tests/test_scope_rbac_foundation_alignment.py

python -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
python -m pytest -q tests/test_tenant_lifecycle_anchor.py tests/test_tenant_lifecycle_enforcement.py tests/test_tenant_seed_bootstrap.py
python -m pytest -q tests/test_plant_hierarchy_orm_foundation.py
python -m pytest -q tests/test_qa_foundation_authorization.py tests/test_qa_foundation_tenant_isolation.py

python -m pytest -q tests/test_pr_gate_workflow_config.py
```

Additional diagnostic command executed due observed failures:
```bash
python -m alembic heads
```

## Results
| Command | Result |
|---|---|
| `tests/test_scope_rbac_foundation_alignment.py` | 10 passed |
| `tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | 2 failed, 12 passed, 3 skipped (pre-existing Alembic duplicate head issue) |
| `tests/test_tenant_lifecycle_anchor.py tests/test_tenant_lifecycle_enforcement.py tests/test_tenant_seed_bootstrap.py` | 1 failed, 34 passed (pre-existing Alembic duplicate head issue) |
| `tests/test_plant_hierarchy_orm_foundation.py` | 4 failed, 16 passed (pre-existing Alembic duplicate head + cp932 decode issue) |
| `tests/test_qa_foundation_authorization.py tests/test_qa_foundation_tenant_isolation.py` | 4 passed |
| `tests/test_pr_gate_workflow_config.py` | 3 passed |
| `python -m alembic heads` | `0004` and `0009 (head)` with warning `Revision 0004 is present more than once` |

## Existing Gaps / Known Debts
| Gap | Evidence |
|---|---|
| Duplicate Alembic revision id `0004` in migration files | `backend/alembic/versions/0004_add_user_lifecycle_status.py` and `backend/alembic/versions/0004_reason_codes.py` |
| Alembic chain no longer single-head in current workspace | `python -m alembic heads` outputs `0004` and `0009` |
| Plant hierarchy migration AST tests read file using locale default and fail under cp932 due non-ASCII bytes | `UnicodeDecodeError` in `test_plant_hierarchy_orm_foundation.py` |
| Backend CI summary still contains stale informational text (`linear chain to 0007`) | `.github/workflows/backend-ci.yml` step summary line |

## Scope Compliance
- ✅ No `scope_nodes` table introduced
- ✅ No `scope_assignments` table introduced
- ✅ Existing `scopes`/`user_role_assignments`/`role_scopes` retained
- ✅ No runtime auth/RBAC behavior changes
- ✅ No API routes/frontend/admin UI changes
- ✅ No migration added
- ✅ No tenant lifecycle, plant hierarchy, MMD, execution, quality, material logic changes

## Risks
| Risk | Mitigation |
|---|---|
| Pre-existing duplicate revision causes migration/baseline regressions | Isolate as separate migration-governance repair slice |
| Baseline tests can mask Option A validity due unrelated migration graph fault | Alignment tests are isolated and passing |
| CI informational summary stale head text can mislead audits | Update summary string in dedicated CI hygiene slice |

## Recommended Next Slice
`P0-A-06A-01B` (or CI/migration hygiene slice):
1. Resolve duplicate revision id conflict (`0004_reason_codes.py` vs existing `0004_add_user_lifecycle_status.py`) and restore single linear head.
2. Normalize migration file encoding handling for locale-safe test reading (UTF-8 explicit reads in affected tests and/or migration file cleanup).
3. Re-run full foundation regression after migration graph repair.

## Stop Conditions Hit
Yes (during verification):
- Current Alembic head is not single/clear (`0004`, `0009`) due duplicate revision id.

This was detected after implementation and is pre-existing to this slice's intended scope. The slice itself remains non-runtime and migration-free.
