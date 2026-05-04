# P0-A-12C Report

## Routing

- Selected brain: MOM Brain
- Selected mode: Strict + QA + Architecture
- Hard Mode MOM: v3 ON
- Reason: This slice audits approval governance schema foundation, Alembic migration safety, PR-gate coverage, and working-tree isolation for a DB-backed approval contract change.

## Summary

The current working tree no longer contains the original uncommitted approval model/schema/migration/workflow changes from the earlier BACKEND-QA-BASELINE-03 blocker report. Those approval-governed-resource-identity sources are now present as clean tracked files in the repo and were validated in place.

Current uncommitted state is limited to:

- one approval test-file lint cleanup applied in this slice;
- unrelated frontend/docs/output artifacts.

The approval governed resource identity slice is valid as an additive schema foundation:

- model and response schema expose nullable governed resource identity fields;
- Alembic revision `0011` cleanly extends `0010` with additive nullable columns;
- approval runtime still uses current `action_type` behavior and does not prematurely adopt generic governed-action matching;
- PR gate and backend CI both include the governed-resource-identity schema test.

BACKEND-QA-BASELINE-03 is **not fully unblocked yet** because `ruff check .` still fails on unrelated committed BOM/script lint debt, and this slice leaves one uncommitted backend test file plus unrelated docs/frontend artifacts in the tree.

## Working Tree Classification

### Current dirty files

| File | Classification | Decision |
|---|---|---|
| `backend/tests/test_approval_governed_resource_identity_schema.py` | Approval governed resource identity | Keep in this slice; import-only lint cleanup applied |
| `frontend/tsconfig.json` | Frontend unrelated changes | Exclude from approval slice |
| `CLAUDE.md` | Unknown / human-owned repo note | Exclude from approval slice |
| `backend/bom_baseline_pytest_output.txt` | Audit/output artifact | Exclude from approval slice |
| `backend/bom_foundation_api_output_utf8.txt` | Audit/output artifact | Exclude from approval slice |
| `docs/audit/mmd-bom-write-baseline-01-bom-write-freeze-handoff.md` | Audit/doc artifact, BOM unrelated | Exclude from approval slice |
| `docs/audit/p0-a-13b-governed-action-type-registry-contract-report.md` | Approval-adjacent audit/doc artifact | Exclude from this slice unless intentionally grouped with docs-only P0-A-13B |
| `docs/design/01_foundation/governed-action-type-registry-contract.md` | Approval-adjacent design doc | Exclude from this slice unless intentionally grouped with docs-only P0-A-13B |

### Earlier blocker-set files from the prior BACKEND-QA-BASELINE-03 stop report

These files are **not currently dirty**, but source inspection shows they belong to the approval-governed-resource-identity contract family rather than to BACKEND-QA-BASELINE-03 mechanical formatting:

| File | Classification | Current State |
|---|---|---|
| `backend/app/models/approval.py` | Approval governed resource identity | Clean tracked source |
| `backend/app/schemas/approval.py` | Approval governed resource identity | Clean tracked source |
| `backend/alembic/versions/0011_add_governed_resource_identity_to_approvals.py` | Approval governed resource identity | Clean tracked source |
| `backend/tests/test_approval_governed_resource_identity_schema.py` | Approval governed resource identity | Dirty only because of this slice's lint cleanup |
| `backend/tests/test_approval_security_events.py` | CI/PR gate follow-up for approval | Clean tracked source |
| `backend/tests/test_approval_service_current_behavior.py` | Approval regression lock | Clean tracked source |
| `backend/tests/test_pr_gate_workflow_config.py` | CI/PR gate follow-up | Clean tracked source |
| `.github/workflows/backend-ci.yml` | CI/PR gate follow-up | Clean tracked source |
| `.github/workflows/pr-gate.yml` | CI/PR gate follow-up | Clean tracked source |
| `backend/app/api/v1/products.py` | Product/BOM/Product Version unrelated changes | Clean tracked source; unrelated to approval |
| `backend/app/schemas/product.py` | Product/BOM/Product Version unrelated changes | Clean tracked source; unrelated to approval |
| `backend/app/schemas/bom.py` | Product/BOM/Product Version unrelated changes | Clean tracked source; unrelated to approval |
| `backend/app/services/product_service.py` | Product/BOM/Product Version unrelated changes | Clean tracked source; unrelated to approval |
| `backend/scripts/audit_broken_ops.py` | Backend utility/script WIP | Clean tracked source; unrelated to approval |
| `docs/audit/tech-debt-testenv-02-backend-test-db-connectivity.md` | Audit/doc artifact | Clean tracked source |

## Design Evidence Extract

### Source docs read

| Doc | Why used |
|---|---|
| `docs/design/00_platform/product-business-truth-overview.md` | Backend/auth/governance truth boundary |
| `docs/design/01_foundation/approval-service-generic-extension-contract.md` | Defines schema-foundation-only boundary for governed resource identity |
| `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | Defines governed resource identity and governed action type as future generic approval contract truth |
| `docs/design/01_foundation/approval-and-separation-of-duties-model.md` | Locks SoD invariant |
| `docs/design/02_registry/action-code-registry.md` | Confirms approval API uses `approval.create` / `approval.decide`, separate from governed transition identity |
| `docs/audit/p0-a-12a-approval-security-event-test-gate-report.md` | Confirms approval security-event test inclusion was previously required in CI/PR gate |

### Commands / actions found

| Command / Action | Domain | Source doc | Evidence |
|---|---|---|---|
| `approval.create` | Approval API authz | `docs/design/02_registry/action-code-registry.md` | Approval API authorization remains approval-domain RBAC |
| `approval.decide` | Approval API authz | `docs/design/02_registry/action-code-registry.md` | Approval decision remains approval-domain RBAC |
| governed resource identity foundation | Approval future contract | `docs/design/01_foundation/approval-service-generic-extension-contract.md` | Future generic adoption requires explicit governed resource fields |
| governed action identity separate from RBAC | Governance contract | `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | Governed transition truth is distinct from permission truth |

### Events found

| Event | Trigger | Source doc | Evidence |
|---|---|---|---|
| `APPROVAL.REQUESTED` | approval request creation | `docs/design/01_foundation/governed-action-approval-applicability-contract.md` §10 | Expected canonical approval event taxonomy |
| `APPROVAL.APPROVED` | approval decision approved | same | Expected canonical approval event taxonomy |
| `APPROVAL.REJECTED` | approval decision rejected | same | Expected canonical approval event taxonomy |
| `APPROVAL.CANCELLED` | cancellation only if implemented | same | Not implemented today |

### States found

| State | Entity | Source doc | Evidence |
|---|---|---|---|
| `PENDING` | `ApprovalRequest` | `docs/design/01_foundation/approval-service-generic-extension-contract.md` | Current approval lifecycle remains narrow |
| `APPROVED` | `ApprovalRequest` | same | Terminal current state |
| `REJECTED` | `ApprovalRequest` | same | Terminal current state |
| `CANCELLED` | `ApprovalRequest` schema-only debt | same | Not an implemented lifecycle path |

### Invariants found

| Invariant | Type | Source doc | Evidence |
|---|---|---|---|
| requester must not equal decider, including under impersonation | authorization / auditability | `docs/design/01_foundation/approval-and-separation-of-duties-model.md` | SoD remains non-negotiable |
| governed resource identity must be explicit for future generic adoption | auditability / tenant / scope | `docs/design/01_foundation/approval-service-generic-extension-contract.md` | `subject_type` / `subject_ref` are insufficient long-term |
| governed action type is distinct from RBAC action code | authorization | `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | approval is layered governance, not RBAC replacement |
| frontend must not own permission truth | authorization | `docs/design/00_platform/product-business-truth-overview.md` | backend remains source of truth |

### Explicit exclusions

| Exclusion | Source doc | Reason |
|---|---|---|
| generic approval runtime adoption | `docs/design/01_foundation/approval-service-generic-extension-contract.md` | This slice does not authorize runtime expansion |
| scope-aware approval rule matching | `docs/design/01_foundation/governed-action-approval-applicability-contract.md` | Contract future state only |
| product/BOM behavior changes | product/business truth + current source inspection | Unrelated domain slice |

## Invariant Map

| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| Existing approval rows without governed fields remain valid | auditability | nullable columns + compatibility tests | No | Yes | `approval-service-generic-extension-contract.md` |
| Governed identity fields remain optional in this slice | authorization boundary | model/schema/migration | No | Yes | same |
| Current runtime still keys behavior off current `action_type` allowlist | authorization | service layer | No | Yes | same |
| RBAC action codes remain `approval.create` / `approval.decide` | authorization | API/security layer | No | Yes | `action-code-registry.md` |
| SoD requester != decider remains unchanged | auditability | service layer | No | Yes | `approval-and-separation-of-duties-model.md` |
| Approval security events remain `REQUESTED/APPROVED/REJECTED` only | auditability | service layer tests | No | Yes | `governed-action-approval-applicability-contract.md` |

## Migration Impact Map

| Concern | Finding | Result |
|---|---|---|
| Revision chain | `0011` declares `down_revision = "0010"`; `0010_reason_codes.py` exists with `revision = "0010"` | Valid linear link |
| Upgrade present | `upgrade()` adds six columns to `approval_requests` | Present |
| Downgrade present | `downgrade()` drops those six columns in reverse order | Present |
| Backward compatibility | All new columns are nullable with no destructive rewrite or backfill requirement | Safe for existing rows |
| Default / nullability safety | No non-null column added; no server-side backfill demanded | Safe |
| Destructive operations | No table drop, rename, rewrite, or data delete | None |
| Tenant isolation risk | `tenant_id` column remains unchanged; new `governed_resource_tenant_id` is additive only | No regression detected |
| Scope/audit risk | `governed_resource_scope_ref` is additive only; no rule-matching logic changes | No runtime regression detected |
| Reversibility | Downgrade exists and is additive reversal only | Reversible |

## Approval Governed Resource Identity Contract Decision

Decision: **ACCEPT as schema foundation only; do not treat as generic approval runtime adoption.**

Accepted contract scope:

1. `ApprovalRequest` stores optional governed resource identity fields.
2. `ApprovalRequestResponse` exposes those fields.
3. Alembic migration adds nullable columns only.
4. Approval runtime still creates/decides using current `action_type`, `subject_type`, and `subject_ref`.
5. Approval SecurityEventLog taxonomy remains unchanged in this slice.
6. CI/PR gate should include `test_approval_governed_resource_identity_schema.py`, and it does.

Rejected interpretations:

1. This slice does **not** implement registry-controlled governed action runtime.
2. This slice does **not** add scope-aware approval rule matching.
3. This slice does **not** change tenant/scope/audit semantics.
4. This slice does **not** justify product/BOM changes.

## Changes Made

Only one code change was made in this slice:

- removed unused imports from `backend/tests/test_approval_governed_resource_identity_schema.py` so the approval-specific test file is lint-clean without changing behavior.

No model, schema, service, migration, workflow, or product/BOM source changes were made by this slice.

## Files Changed

Accepted into this slice:

- `backend/tests/test_approval_governed_resource_identity_schema.py`
- `docs/audit/p0-a-12c-approval-governed-resource-identity-isolation.md`

Explicitly excluded from this slice:

- `frontend/tsconfig.json`
- `CLAUDE.md`
- `backend/bom_baseline_pytest_output.txt`
- `backend/bom_foundation_api_output_utf8.txt`
- `docs/audit/mmd-bom-write-baseline-01-bom-write-freeze-handoff.md`
- `docs/audit/p0-a-13b-governed-action-type-registry-contract-report.md`
- `docs/design/01_foundation/governed-action-type-registry-contract.md`

## Verification Results

Commands run successfully:

```powershell
Push-Location "g:/Work/FleziBCG/backend"
$env:PYTHONPATH='.'
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q \
  tests/test_approval_governed_resource_identity_schema.py \
  tests/test_approval_security_events.py \
  tests/test_approval_service_current_behavior.py \
  tests/test_pr_gate_workflow_config.py
Pop-Location
```

Result: `38 passed, 1 warning`

```powershell
Push-Location "g:/Work/FleziBCG/backend"
$env:PYTHONPATH='.'
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q \
  tests/test_alembic_baseline.py \
  tests/test_qa_foundation_migration_smoke.py
Pop-Location
```

Result: `9 passed, 3 skipped, 1 warning`

```bash
wsl bash -c "cd /mnt/g/Work/FleziBCG/backend && PYTHONPATH=.venv/lib/python3.12/site-packages:. python3 -m ruff check tests/test_approval_governed_resource_identity_schema.py"
```

Result: `All checks passed!`

Additional evidence:

- `backend/tests/test_approval_governed_resource_identity_schema.py`, `backend/tests/test_approval_security_events.py`, and `backend/tests/test_approval_service_current_behavior.py` confirm current approval runtime behavior is unchanged.
- `.github/workflows/backend-ci.yml` includes both `tests/test_approval_security_events.py` and `tests/test_approval_governed_resource_identity_schema.py`.
- `.github/workflows/pr-gate.yml` includes both tests in the explicit backend test list.

Verification limits / failures outside this slice:

1. `ruff check .` for the whole backend still fails because of unrelated files:
   - `backend/scripts/audit_broken_ops.py`
   - `backend/tests/test_bom_allowed_actions_12b_a.py`
   - `backend/tests/test_bom_capability_guard_12b_a.py`
2. `scripts/verify_backend.py --testenv-only` was not fully runnable in the current Windows venv because that environment does not currently have `ruff` installed even though `backend/requirements.txt` expects it.
3. Full backend suite was runnable from backend cwd, but it has one unrelated failure:
   - `tests/test_user_lifecycle_status.py::test_user_status_migration_does_not_touch_unrelated_tables`
   - failure cause: Windows `cp932` decode error reading `0004_add_user_lifecycle_status.py`

## Scope Compliance

- No ruff format applied: **Confirmed**
- No frontend changed: **Confirmed by this slice**; existing `frontend/tsconfig.json` remains excluded and untouched
- No product/BOM behavior changed unless justified: **Confirmed**
- No auth/tenant/scope semantics weakened: **Confirmed**
- No unrelated domain refactor: **Confirmed**

## BACKEND-QA-BASELINE-03 Readiness

BACKEND-QA-BASELINE-03 is **not yet ready**.

Remaining blockers:

1. Current tree still has uncommitted files outside a mechanical formatting slice.
2. Global `ruff check .` is red due to unrelated BOM/script lint debt.
3. Full backend suite is not fully green on Windows due an unrelated encoding-sensitive migration test.

What is now unblocked:

- The approval-governed-resource-identity schema foundation is isolated conceptually and validated.
- It no longer needs to be treated as an unknown backend blocker for BACKEND-QA-BASELINE-03.

## Recommended Next Slice

1. Commit or stash the approval-test lint cleanup and the P0-A-12C audit report.
2. Separate unrelated dirty docs/frontend/output artifacts from backend work.
3. Run a dedicated unrelated-cleanup slice for the remaining backend Ruff failures in BOM/script files.
4. Fix the Windows encoding issue in `tests/test_user_lifecycle_status.py` or the referenced migration file before using Windows full-suite results as a release gate.
5. Re-run BACKEND-QA-BASELINE-03 only after the working tree is clean and global backend lint is green.

## Suggested Commit Commands

Approval isolation slice only:

```bash
git add backend/tests/test_approval_governed_resource_identity_schema.py docs/audit/p0-a-12c-approval-governed-resource-identity-isolation.md
git commit -m "test(approval): isolate governed resource identity schema slice"
```

Approval-adjacent docs-only slice, if intended:

```bash
git add docs/audit/p0-a-13b-governed-action-type-registry-contract-report.md docs/design/01_foundation/governed-action-type-registry-contract.md
git commit -m "docs(approval): add governed action type registry contract"
```

Do not include these in the approval isolation commit:

```bash
git restore --staged frontend/tsconfig.json CLAUDE.md backend/bom_baseline_pytest_output.txt backend/bom_foundation_api_output_utf8.txt docs/audit/mmd-bom-write-baseline-01-bom-write-freeze-handoff.md
```