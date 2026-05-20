# MMD-FULLSTACK-15 — Resource Requirement FE Write Intent + Capability Guard

## Slice Name

**MMD-FULLSTACK-15 — Resource Requirement FE Write Intent + Server-Derived Capability Guard**

Alternate ID (for traceability with the audit chain): `MMD-RR-FE-WRITE-01`.

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-20 | v0.1 | PO-SA agent slice spec. Origin: `mmd-rr-write-audit-01-report.md` verdict OPEN. |

---

## 1. Intent

Lift Resource Requirement (RR) — the only MMD sub-domain that still ships full backend CRUD without an FE write-intent surface — to the same server-derived capability-guard pattern set by:

- BOM↔PV binding (`mmd-fullstack-14b-bom-product-version-binding-capability-guard.md`)
- Reason Code (`mmd-fullstack-13b-reason-code-server-derived-capability-guard.md`)
- BOM (`mmd-fullstack-12b-bom-server-derived-capability-guard.md`)

After this slice, RR write-intent will be available in the FE, gated by server-derived `capabilities` and per-row `allowed_actions`, with no lifecycle-status inference from the frontend.

This is a paired-slice with MMD-FULLSTACK-16 (Routing Operation FE Write Intent — Slice 7 in the completion roadmap). MMD-FULLSTACK-15 ships first as the simpler of the two.

---

## 2. Baseline Sources (MUST READ — block before any code edit)

The implementing agent MUST read each of the following BEFORE making any source change. The agent MUST acknowledge each by name in its first reply (per `feedback_coding_agent_skill_reading`).

1. `docs/audit/mmd-rr-write-audit-01-report.md` (this slice's parent audit — verdict, gap, recommended fix)
2. `docs/audit/mmd-master-baseline-01-freeze-handoff.md` (master MMD baseline — invariants, do-not-do rules)
3. `docs/audit/mmd-current-state-report.md` v2.0 (current state)
4. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (gold-standard pattern reference)
5. `docs/audit/mmd-fullstack-14b-bom-product-version-binding-capability-guard.md` (FE-side capability-guard pattern)
6. `docs/audit/mmd-fullstack-13b-reason-code-server-derived-capability-guard.md` (alt capability-guard reference)
7. `docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md` (the RR domain contract — status `IMPLEMENTED_AND_CANONICAL_FOR_P0_B`)
8. `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
9. `docs/ai-skills/autonomous-implementation-agent/SKILL.md`
10. `docs/ai-skills/design-md-ui-governor/SKILL.md` (FE governance)

The agent's first reply must include an acknowledgement block of the form:

```
ACK — read the following baseline sources:
- mmd-rr-write-audit-01-report.md
- mmd-master-baseline-01-freeze-handoff.md
- mmd-current-state-report.md (v2.0)
- mmd-bom-pv-binding-baseline-01-freeze-handoff.md
- mmd-fullstack-14b-bom-product-version-binding-capability-guard.md
- mmd-fullstack-13b-reason-code-server-derived-capability-guard.md
- resource-requirement-mapping-contract.md
- hard-mode-mom-v3 SKILL.md
- autonomous-implementation-agent SKILL.md
- design-md-ui-governor SKILL.md
```

If any of the above is unreadable or missing, the agent halts and reports — does not proceed.

---

## 3. Pre-flight: Working Copy Sanity

Before making any source change, the agent runs:

```powershell
git status
```

If the working copy is not clean (uncommitted changes outside this slice's plan), the agent **HALTS** and reports. Specifically: as of 2026-05-20 the branch `feature/station-execution-flow-v2` contains ~20 modified files from an unrelated station-execution refactor that cause `eslint` and `tsc` to fail. **This slice must NOT start until that refactor is committed, stashed, or reverted by its owner.**

Verify both `eslint src/` and `tsc --noEmit -p .` exit `0` on the working copy BEFORE the first code edit. Paste exit codes in the slice report under §“Pre-flight”.

---

## 4. In Scope

### 4.1 Backend changes

In `backend/app/schemas/resource_requirement.py`:

- Add `ResourceRequirementCapabilities` model (Pydantic), shape:
  ```python
  class ResourceRequirementCapabilities(BaseModel):
      can_create: bool
      reason: str | None
  ```
- Add `ResourceRequirementAllowedActions` model:
  ```python
  class ResourceRequirementAllowedActions(BaseModel):
      can_update: bool
      can_delete: bool
  ```
- Extend the existing RR item response model to include `allowed_actions: ResourceRequirementAllowedActions`.
- Add a new list-response wrapper:
  ```python
  class ResourceRequirementListResponse(BaseModel):
      items: list[ResourceRequirementItem]
      capabilities: ResourceRequirementCapabilities
  ```

In `backend/app/services/resource_requirement_service.py`:

- Add a pure function `_compute_rr_capabilities(routing_lifecycle: str, caller_has_action: bool) -> ResourceRequirementCapabilities`.
- Add a pure function `_compute_rr_allowed_actions(routing_lifecycle: str, caller_has_action: bool) -> ResourceRequirementAllowedActions`.
- `can_create`: `routing.lifecycle_status == "DRAFT" AND caller_has_action`. Else reason is one of:
  - `"routing_not_draft"` — when routing is RELEASED or RETIRED.
  - `"missing_action_code"` — when caller lacks `admin.master_data.resource_requirement.manage`.
- `can_update` and `can_delete`: same condition as `can_create`. (RR mutation requires routing DRAFT and the action code.)
- Compute capabilities once per request; do not re-derive per item.

In `backend/app/api/v1/routings.py`:

- Modify the GET-list endpoint at `/routings/{routing_id}/operations/{operation_id}/resource-requirements` to return `ResourceRequirementListResponse` (`{ items, capabilities }`) instead of the bare list.
- Modify the GET-one and POST/PATCH responses to include `allowed_actions` per item.
- DELETE response unchanged (204 No Content).
- Authorization unchanged: single-action `admin.master_data.resource_requirement.manage` for mutation; `require_authenticated_identity` for read. **Do NOT introduce AND-semantics with `routing.manage`** — RR mutation is intra-RR-domain (see audit §4 reasoning).

### 4.2 Frontend changes

In `frontend/src/app/api/routingApi.ts`:

- Add types `ResourceRequirementCapabilities`, `ResourceRequirementAllowedActions`, `ResourceRequirementListResponse`.
- Update `ResourceRequirementItemFromAPI` to include `allowed_actions`.
- Update RR list-fetch function to return the wrapper.

In `frontend/src/app/pages/ResourceRequirements.tsx`:

- Consume `capabilities.can_create` for the page-level "Assign Resource" button (replace current locked placeholder).
- Consume `allowed_actions.can_update` and `allowed_actions.can_delete` per row for Edit / Delete row buttons.
- Add minimal create form (modal or inline) and edit form. Pattern: mirror `BomList.tsx` / `BomDetail.tsx` write-intent UX.
- POST/PATCH/DELETE error mapping: 400 / 403 / 404 / 409 / 422 → localized messages.
- Remove `MockWarningBanner` and `BackendRequiredNotice` imports — RR is no longer SHELL.
- No lifecycle-status inference. Button enablement consumes only `capabilities.*` / `allowed_actions.*`.

In `frontend/src/app/i18n/registry/en.ts` and `ja.ts`:

- Add keys (en + ja parity):
  - `resourceRequirements.button.create`
  - `resourceRequirements.button.edit`
  - `resourceRequirements.button.delete`
  - `resourceRequirements.form.resource_type`
  - `resourceRequirements.form.capability`
  - `resourceRequirements.form.quantity_required`
  - `resourceRequirements.form.notes`
  - `resourceRequirements.error.unauthorized`
  - `resourceRequirements.error.manageForbidden`
  - `resourceRequirements.error.notFound`
  - `resourceRequirements.error.conflict`
  - `resourceRequirements.error.validation`
  - `resourceRequirements.error.routing_not_draft`
  - `resourceRequirements.empty.no_requirements`

In `frontend/scripts/mmd-read-integration-regression-check.mjs`:

- Add a new Section (next available letter — likely **Section Q**) with checks:
  - `rr_response_includes_capabilities_field` — schema check on `routingApi.ts`.
  - `rr_response_includes_allowed_actions_per_item` — schema check.
  - `rr_page_consumes_can_create` — text search for `capabilities?.can_create` in `ResourceRequirements.tsx`.
  - `rr_page_consumes_can_update` — same.
  - `rr_page_consumes_can_delete` — same.
  - `rr_page_no_lifecycle_only_gate` — assert no expression of form `routing.lifecycle_status === "DRAFT"` controls button disabled state.
  - `rr_page_no_mock_banner_imports` — assert `MockWarningBanner` and `BackendRequiredNotice` are NOT imported in `ResourceRequirements.tsx`.

---

## 5. Explicitly Out of Scope

- **No new backend behavior** beyond capability surfacing. The existing POST/PATCH/DELETE business logic must not change.
- **No new action codes.** Use existing `admin.master_data.resource_requirement.manage`.
- **No AND-semantics** with `routing.manage`. RR is intra-domain.
- **No plant/scope-specific RR applicability.** Deferred to `MMD-SCOPE-APPLICABILITY-01`.
- **No effective-dating for RR.** Not in any contract.
- **No cross-domain side effects.** RR mutation must not touch execution, material, ERP, traceability, quality, work order, APS.
- **No migration changes.** RR table exists since migration 0016; capability is computed in service, not stored.
- **No changes to Routing Operation FE.** That is the sibling slice MMD-FULLSTACK-16; do not bundle.
- **No changes to Routing-header FE write buttons.** That is GAP-MMD-13, deferred to MMD-ROUTING-WRITE-FE-01.
- **No changes to `mmd-current-state-report.md` v2.0 GAPs section** in this slice's diff — wait until verification passes, then close GAP-MMD-12 and GAP-MMD-14 in the final report step.

---

## 6. Files / Areas to Inspect

Before editing, read in order:

| File | Why |
|---|---|
| `backend/app/schemas/resource_requirement.py` | Existing RR Pydantic models; understand `ResourceRequirementItem` shape |
| `backend/app/services/resource_requirement_service.py` | Existing CRUD + helpers |
| `backend/app/api/v1/routings.py` lines 237–360 | RR routes; understand the existing response shape and how to extend |
| `backend/tests/test_resource_requirement_api.py` | Existing API test coverage |
| `backend/tests/test_resource_requirement_service.py` | Existing service test coverage |
| `backend/tests/test_mmd_rbac_action_codes.py` | Source-level action-code contract tests |
| `frontend/src/app/api/routingApi.ts` | Where RR FE types live |
| `frontend/src/app/pages/ResourceRequirements.tsx` (276 lines) | Page to extend with write intent |
| `frontend/src/app/pages/BomList.tsx` (383 lines) | Pattern reference: page-level capability + create modal |
| `frontend/src/app/pages/BomDetail.tsx` (707 lines) | Pattern reference: per-row allowed_actions + edit modal |
| `frontend/src/app/pages/ReasonCodes.tsx` (861 lines) | Pattern reference: list + capability + create/edit/retire |
| `frontend/src/app/pages/ProductDetail.tsx` lines 716, 808, 816 | Pattern reference: per-row allowed_actions consumption |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | Add Section Q here |

---

## 7. Implementation Rules

1. **Backend truth, frontend intent.** FE never decides authorization; backend computes capability and returns it. FE renders button enable state ONLY from `capabilities.*` / `allowed_actions.*`.
2. **Pure capability function.** `_compute_rr_capabilities` and `_compute_rr_allowed_actions` MUST be pure functions taking `(routing_lifecycle, caller_has_action)`. No DB access inside them. They are called from the API layer after DB load.
3. **No lifecycle-status inference** anywhere in the FE. Adding any expression like `routing.lifecycle_status === "DRAFT"` to gate a button is a violation and fails Section Q check `rr_page_no_lifecycle_only_gate`.
4. **No new audit/event types.** Existing service emits events for create/update/delete; do not duplicate.
5. **Backward compat — soft.** Existing API consumers (if any) of the bare list response will break when the list endpoint becomes `{ items, capabilities }`. Mitigation: this is an internal API; FE is the sole known consumer; update FE in the same slice. If a non-FE consumer is discovered during implementation, HALT and bring back to PO-SA review.
6. **Tenant isolation preserved.** Capability computation never crosses tenant boundary. Existing tenant filters in service code must be retained.
7. **Error mapping.** 400 → validation; 403 → action-forbidden; 404 → routing or operation not found; 409 → duplicate / cardinality conflict; 422 → lifecycle precondition (e.g., routing not DRAFT). Server returns problem-detail-style `detail` string; FE shows localized message.
8. **i18n parity.** en.ts and ja.ts MUST have identical key sets after this slice. `lint:i18n:registry` check must remain green.
9. **No source code formatting drift.** Do not run global formatter; only edit lines necessary for the slice.
10. **Sandbox limits.** If the implementing agent runs in a non-Windows sandbox without project `.venv` / Postgres, it may still write code and update tests, but verification (§9) MUST be run on a Windows machine with the project `.venv` AND raw exit codes pasted in the report — per `feedback_pass_claims_need_exit_code`.

---

## 8. Tests Required

### 8.1 Backend (Python — pytest)

Extend `backend/tests/test_resource_requirement_api.py` with a capability-matrix test pack. Minimum cases:

| Test name | Routing lifecycle | Caller perm | Expected `can_create` | Expected `allowed_actions.can_*` |
|---|---|---|:---:|:---:|
| `test_rr_caps_draft_routing_with_perm` | DRAFT | has `resource_requirement.manage` | true | true |
| `test_rr_caps_draft_routing_no_perm` | DRAFT | no perm | false (`missing_action_code`) | false |
| `test_rr_caps_released_routing_with_perm` | RELEASED | has perm | false (`routing_not_draft`) | false |
| `test_rr_caps_retired_routing_with_perm` | RETIRED | has perm | false (`routing_not_draft`) | false |
| `test_rr_caps_released_routing_no_perm` | RELEASED | no perm | false | false |
| `test_rr_list_response_includes_capabilities` | n/a | n/a | shape check on wrapper | n/a |
| `test_rr_item_response_includes_allowed_actions` | n/a | n/a | shape check per item | n/a |
| `test_rr_create_forbidden_when_can_create_false` | RELEASED | has perm | n/a | POST returns 422 (existing) — confirm error code + add allowed_actions in error path is irrelevant |

Existing tests in `test_resource_requirement_api.py` and `test_resource_requirement_service.py` MUST continue to pass without modification (other than adapting if the bare-list response shape was asserted directly).

In `backend/tests/test_mmd_rbac_action_codes.py`: confirm `admin.master_data.resource_requirement.manage` is still tested as schema contract. Add one assertion: RR response schema includes the new `allowed_actions` / `capabilities` shape.

### 8.2 Frontend (regression — Node.js)

Extend `frontend/scripts/mmd-read-integration-regression-check.mjs` with Section Q (named `RR-CAPABILITY` or similar). Checks listed in §4.2 above.

Existing 209 checks in Sections A–P MUST continue to pass.

### 8.3 No E2E / Playwright in this slice

Playwright e2e is out of scope. UX behavior is covered by the regression script + visual QA (deferred to a follow-up MMD-FE-QA-04 if required).

---

## 9. Verification Commands

Run on Windows PowerShell from `g:\Work\FleziBCG`:

```powershell
# Backend bundle
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q `
  tests/test_resource_requirement_api.py `
  tests/test_resource_requirement_service.py `
  tests/test_mmd_rbac_action_codes.py `
  tests/test_routing_foundation_api.py `
  tests/test_routing_foundation_service.py `
  tests/test_alembic_baseline.py

# Frontend bundle
cd g:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read
npm.cmd run build
npm.cmd run lint
npm.cmd run lint:i18n:registry
npm.cmd run check:routes
```

### 9.1 PASS-claim rule (per `feedback_pass_claims_need_exit_code`)

The slice report MUST include raw exit codes pasted from the actual terminal run. PASS claims without exit codes will be rejected. The agent must NOT chain commands and report a combined PASS; each command’s exit code is recorded separately.

Acceptable format in the report:

```
$ g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_resource_requirement_api.py
... output ...
EXIT=0

$ npm.cmd run check:mmd:read
... output ...
EXIT=0
```

### 9.2 Expected results

All commands MUST exit 0.

Note on Windows-only caveat: `npm run lint:i18n` (bash script) may fail on PowerShell due to CRLF; use `npm run lint:i18n:registry` (Node.js) which is the canonical equivalent on Windows.

---

## 10. Documentation Updates

Within this slice:

1. Write `docs/audit/mmd-fullstack-15-resource-requirement-fe-write-intent-report.md` — the implementation report. Sections: ACK block, Pre-flight (git status + lint + tsc exit codes), Source changes summary (file list with LOC), Test additions summary, Verification exit codes (raw paste), Notes / deviations, Closeout verdict.
2. Patch `docs/audit/mmd-current-state-report.md` v2.0 §4.2 to mark GAP-MMD-12 and GAP-MMD-14 as RESOLVED with the new slice ID.
3. Patch `docs/audit/mmd-master-baseline-01-freeze-handoff.md` §6 row for GAP-MMD-12 to RESOLVED.
4. Do NOT patch the design contract `resource-requirement-mapping-contract.md` (status remains `IMPLEMENTED_AND_CANONICAL_FOR_P0_B`; this slice only adds capability surfacing, not domain semantics).
5. Do NOT touch any non-MMD doc.

---

## 11. Definition of Done

- ✅ ACK block in first reply lists 10 baseline sources by name.
- ✅ Pre-flight `git status` shows clean WC (or only this slice's files); `eslint` and `tsc` both exit 0 BEFORE the first code edit.
- ✅ Backend: schemas extended, service computes capabilities purely, API returns wrapper + per-item allowed_actions.
- ✅ Frontend: page consumes server-derived capability/allowed_actions; no lifecycle-status inference; mock banner imports removed.
- ✅ Backend tests: 7 new capability-matrix tests + 2 shape tests, all passing.
- ✅ Frontend regression: Section Q added (≥ 7 new checks), all passing; total count > 209.
- ✅ i18n: en + ja parity maintained; ≥ 14 new keys added.
- ✅ All §9 verification commands exit 0 with raw exit codes pasted in the implementation report.
- ✅ §10 documentation updates landed.
- ✅ GAP-MMD-12 and GAP-MMD-14 marked RESOLVED in current-state v2.0 and master baseline §6.
- ✅ Closeout verdict in slice report: COMPLETE.

---

## 12. Stop Conditions

The agent HALTS and reports back to PO-SA (does not improvise) when ANY of these are true:

1. Working copy is dirty with non-slice files at start of work.
2. `eslint` or `tsc` is red BEFORE the first code edit (carry-over from station-execution refactor).
3. RR capability computation would require touching execution, material, ERP, traceability, quality, work order, or APS code/imports → halt; capability must be MMD-only.
4. Backward-compat: another consumer (not the FE page) of the bare RR list response is discovered → halt; PO-SA decides whether to dual-publish or migrate consumer.
5. Routing service refuses to expose `lifecycle_status` to RR service via the existing repository pattern → halt; do not add cross-domain imports.
6. Any test in `test_resource_requirement_api.py` or `test_resource_requirement_service.py` requires modification beyond adapting to the new response wrapper → halt; this likely means the agent is changing business logic.
7. Adding new action code(s) seems necessary → halt; this slice does not introduce action codes.
8. AND-semantic with `routing.manage` seems necessary → halt; the audit verdict explicitly rules this out.
9. Migration > 0019 seems necessary → halt; RR capability is computed, not stored.
10. Any verification command exits non-zero AND the cause is in code this slice changed → fix and re-run; if the cause is unrelated (e.g., station-execution refactor red) → halt and surface.
11. The agent finds itself doing a "broad refactor" (e.g., renaming many files, moving folders) → halt; this is a single-purpose slice.
12. Total LOC change exceeds 800 lines across all files → halt; the slice is too large to be one safe boundary.

---

## 13. Final Report Format

The slice report (`docs/audit/mmd-fullstack-15-resource-requirement-fe-write-intent-report.md`) MUST contain:

```markdown
# MMD-FULLSTACK-15 — Implementation Report

## ACK
(list of 10 baseline sources read, by name)

## Pre-flight
- git status: <clean | listed file>
- eslint src/: EXIT=<code>
- tsc --noEmit: EXIT=<code>

## Source Changes
| File | LOC delta | Purpose |
|---|---:|---|
... (one row per modified file)

## Test Additions
| Test | Status |
|---|---|
... (each new test listed)

## Verification — Raw Exit Codes
$ <command>
... output ...
EXIT=<code>
(repeat for each command in §9)

## Notes / Deviations
(any judgment calls or deviations from this spec)

## Closeout Verdict
COMPLETE | INCOMPLETE | HALTED
(reason if not COMPLETE)
```

---

## 14. Coding-Agent Prompt (paste directly to the agent)

> Implement **MMD-FULLSTACK-15 — Resource Requirement FE Write Intent + Server-Derived Capability Guard**.
>
> **Slice spec**: `docs/audit/mmd-fullstack-15-resource-requirement-fe-write-intent.md` (this file).
>
> **Read first (block on completion, ack each by name in your first reply per the `ACK` template in §2):**
> 1. `docs/audit/mmd-rr-write-audit-01-report.md`
> 2. `docs/audit/mmd-master-baseline-01-freeze-handoff.md`
> 3. `docs/audit/mmd-current-state-report.md` v2.0
> 4. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md`
> 5. `docs/audit/mmd-fullstack-14b-bom-product-version-binding-capability-guard.md`
> 6. `docs/audit/mmd-fullstack-13b-reason-code-server-derived-capability-guard.md`
> 7. `docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md`
> 8. `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
> 9. `docs/ai-skills/autonomous-implementation-agent/SKILL.md`
> 10. `docs/ai-skills/design-md-ui-governor/SKILL.md`
>
> **Then**:
> - Pre-flight (§3): confirm working copy clean and lint/tsc green BEFORE first edit.
> - Implement scope per §4.
> - Respect rules per §7 and stop conditions per §12.
> - Run verification per §9; paste raw exit codes per `feedback_pass_claims_need_exit_code`.
> - Write implementation report per §13.
> - Patch docs per §10 (mark GAP-MMD-12 and GAP-MMD-14 RESOLVED).
>
> **Do NOT**:
> - Add new action codes.
> - Introduce AND-semantics with `routing.manage`.
> - Touch execution / material / ERP / traceability / quality / work-order / APS.
> - Bundle MMD-FULLSTACK-16 (Routing Op FE Write) into the same PR.
> - Make any change in the FE that infers from lifecycle status without going through `capabilities.*` or `allowed_actions.*`.
> - Add a migration; RR capability is computed, not stored.
>
> Verdict on completion: COMPLETE iff all §11 DoD items hold and all §9 commands exit 0.

End of MMD-FULLSTACK-15 slice spec v0.1.
