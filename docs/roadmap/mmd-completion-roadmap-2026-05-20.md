# MMD Completion Roadmap — Audit + Slice Plan

| Date | Version | Change |
|---|---:|---|
| 2026-05-20 | v1.0 | PO-SA agent audit of Manufacturing Master Data and full slice roadmap to closeout. Baseline: G:\Work\FleziBCG. |

> Authoritative read order used: (1) `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (May 19), (2) `docs/audit/mmd-current-state-report.md` (May 1 — partially stale), (3) `docs/implementation/p0-b-mmd-closeout-review.md` (Apr 29), (4) `docs/roadmap/flezibcg-overall-roadmap-latest.md`, (5) `docs/design/02_domain/product_definition/*.md`, (6) live source under `backend/app/` and `frontend/src/app/`.

---

## Part 1 — Review Verdict

### 1.1 Verdict

**MMD foundation is substantially complete and frozen for the discrete-first scope. Remaining work to “hoàn thiện” is bounded and predictable** — it splits into (a) closeout hygiene (visual QA, master baseline doc, doc-freshness patch), (b) gap fills (capability guard parity for the two least-mature surfaces — Resource Requirement and Routing Operation Detail), and (c) deferred-but-needed-before-P1-execution items (set_current enforcement, binding effective-dating, plant/scope applicability). Hard scope expansions (multi-binding-types, replace, ERP/backflush) **must remain deferred**.

### 1.2 What is accepted (evidence in repo)

| Sub-domain | Status | Primary evidence |
|---|---|---|
| Product (header) read/write | ✅ Production-ready | `backend/app/api/v1/products.py`; P0-B closeout §“API Surface Status” |
| Product Version (PV) read/write/lifecycle | ✅ Frozen | `mmd-pv-write-baseline-01-product-version-write-freeze-handoff.md`; `mmd-be-08`, `mmd-be-11` |
| BOM foundation read | ✅ Frozen | `mmd-read-baseline-01/02-*-freeze-handoff.md`; `mmd-be-04/05` |
| BOM write governance + API | ✅ Frozen | `mmd-bom-write-baseline-01-*-freeze-handoff.md`; `mmd-be-09/12`; FE inside `productApi.ts` (`BomCreateRequest`, `BomItemFromAPI`) |
| Reason Code read/write + lifecycle | ✅ Frozen | `mmd-reason-code-write-baseline-01-*-freeze-handoff.md`; `mmd-be-10/13`; `frontend/src/app/api/reasonCodeApi.ts` |
| Routing + Routing Operation (header + sequence) | ✅ Production-ready | P0-B closeout `0015_routings.sql`; `routingApi.ts` returns nested operations |
| Resource Requirement read | ✅ Connected | P0-B closeout “Resource Requirement API (nested under routing operation)”; `ResourceRequirementItemFromAPI` exported in `api/index.ts` |
| BOM ↔ PV binding (entity + API + release validation + capability guard) | ✅ **Frozen 2026-05-08** | `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (74 BE tests, 209 FE checks, alembic head 0014) |
| Frontend uses server-derived capabilities (no lifecycle-only inference) | ✅ Enforced | `ProductDetail.tsx` (lines 103–105 cited in freeze doc), regression Section P |
| Tenant isolation, audit/event emission, action-code registry | ✅ Enforced | `test_mmd_rbac_action_codes.py`, `record_security_event()` |

### 1.3 What needs correction (doc-truth drift)

| Item | Issue | Action |
|---|---|---|
| `docs/audit/mmd-current-state-report.md` (May 1) | Lists BOM List/Detail, RoutingOperationDetail, ResourceRequirements, ReasonCodes as **SHELL** — but `grep "mockBom\|mockOperation\|mockRequirement\|mockReasonCode" frontend/src/app/pages/*` returns **0 occurrences** in all five pages as of 2026-05-20. The doc is stale. | Re-snapshot as `mmd-current-state-report.md v2.0` after MMD-MASTER-BASELINE-01. |
| BomList.tsx still imports `MockWarningBanner` and `BackendRequiredNotice` | Likely cosmetic; needs visual QA to confirm whether shell-mode UX is still being shown despite real API wiring | Verified in MMD-FE-QA-03 (visual QA slice below). |
| `docs/audit/mmd-current-state-report.md` recommends “MMD-BE-01 (BOM read model)” as the highest-value next step | Already done — BOM read/write/binding all shipped | Mark superseded in next snapshot. |

### 1.4 What is rejected or deferred (do not implement now)

Per `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §15 “Do-Not-Do Rules”, the following **stay deferred** and any future agent must produce a new Hard Mode MOM v3 governance contract before touching them:

1. PV `set_current` enforcement (advisory-only today)
2. Binding replace (atomic PRIMARY swap)
3. Multiple BOM binding types (SECONDARY, ALTERNATE)
4. Binding `effective_from` / `effective_to`
5. Plant/scope-specific binding (MMD-SCOPE-APPLICABILITY-01)
6. Product-level / tenant-profile binding policy
7. Material reservation, inventory movement, scrap posting, backflush — these belong to Phase 8 (P1-C), **not MMD**
8. ERP posting from binding mutations
9. Traceability genealogy / quality acceptance triggered by binding state
10. Automatic current-version selection
11. Migrations after 0014 in the binding scope

### 1.5 Evidence still needed (before some later slices can be safely planned)

- **MMD-FE-QA-03 visual evidence** — no browser screenshots exist yet for binding section, toggle, release-readiness states (explicit recommendation in freeze doc §16).
- **End-to-end smoke** of PV release path with `bom_binding_required_for_release = true` against a seeded BOM in RELEASED state — only unit/integration coverage today.
- **Cross-tenant negative read test pack** for the binding endpoint — covered for product/routing/RR (P0-B closeout) but the freeze doc does not call it out separately for binding; verify before MASTER-BASELINE.
- **Resource Requirement FE write-intent + capability guard** — code inspection shows RR page uses `routingApi` reads; whether write-intent is page-level or absent needs confirming in MMD-RR-WRITE-AUDIT-01 (slice below).
- **Routing Operation Detail FE write-intent** — same as above; today the page is read-only against `routingApi.getRouting()`.

---

## Part 2 — Full Slice Roadmap (Now / Next / Later)

### 2.1 Phasing principle

MMD “hoàn thiện” here means: **production-ready for discrete-first execution use, frozen as P0-B-COMPLETE, before P0-C Execution Core expansion forces any further MMD refactor**. We do **not** in this roadmap expand MMD into batch/process/ISA-88 (P2-A), backflush (P1-C), or ERP master sync (P1-A). Those are correctly outside MMD’s scope per overall roadmap.

Three lanes:

| Lane | Purpose |
|---|---|
| **Now** (this iteration) | Closeout hygiene — visual QA, doc resync, master baseline. Zero new behavior. |
| **Next** (1–2 iterations) | Gap fills inside MMD: parity for RR + Routing Op Detail, set_current governance, binding visual finalization, current-state report v2. |
| **Later** (governance-contract-first) | Scope-applicability, effective dating, binding replace, secondary/alternate types — none of these proceed without a new policy contract. |

### 2.2 Dependency graph

```
MMD-FE-QA-03 (visual QA, binding)
        │
        ├── MMD-CURRENT-STATE-V2 (doc resync) ──► MMD-MASTER-BASELINE-01 (closeout freeze)
        │
        ├── MMD-RR-WRITE-AUDIT-01 ──► MMD-RR-FE-WRITE-01 (if gap exists)
        │
        └── MMD-ROUTING-OP-WRITE-AUDIT-01 ──► MMD-ROUTING-OP-FE-WRITE-01 (if gap exists)

(NEXT, after MASTER-BASELINE only — each requires its own governance contract first)
MMD-PV-SETCURRENT-GOV-01 ──► MMD-PV-SETCURRENT-IMPL-01
MMD-BINDING-EFFECTIVE-DATING-GOV-01 ──► (impl deferred until consumer demand)
MMD-SCOPE-APPLICABILITY-01-GOV ──► (impl deferred)
```

### 2.3 Stop conditions across the roadmap

Halt and re-plan if any of these become true:

- A slice tries to add cross-domain side effects (material/inventory/backflush/ERP/traceability/quality/execution) from a binding or master-data mutation.
- Frontend introduces lifecycle-status-based gating in place of `capabilities.can_*`.
- Any AND-authorization rule (`bom.manage` ∧ `pv.manage`) is relaxed to OR or to single-action.
- Migration > 0014 is created without a fresh governance contract.
- Any slice tries to combine two of the deferred items (e.g., set_current + effective dating in one go).
- A slice attempts to remove the `binding` + `capabilities` wrapper from the GET response (breaks 209 FE regression checks).

---

## Part 3 — Slice Specs (Now lane)

### Slice 1 — MMD-FE-QA-03 — BOM ↔ PV Binding Runtime Visual QA

#### Intent
Capture browser-rendered evidence (screenshots + console + network capture) for the BOM↔PV binding section, the `bom_binding_required_for_release` toggle, and all six release-readiness states. Catch rendering, i18n, capability-button regressions that unit tests do not see.

#### Baseline Sources
- `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §8 (UI), §9.3 (capability matrix), §16 (explicit recommendation)
- `frontend/src/app/pages/ProductDetail.tsx`
- `docs/audit/mmd-fe-qa-02-runtime-visual-evidence-pack.md` (template for prior visual evidence pack)

#### In Scope
- Seed a tenant with: 1 product, 1 DRAFT PV, 1 DRAFT BOM, 1 RELEASED BOM, 1 RETIRED BOM.
- Capture screenshots for: (a) no-binding + flag=false, (b) no-binding + flag=true → `BLOCKED_NO_BINDING`, (c) bound to DRAFT BOM + flag=true → `BLOCKED_DRAFT_BOM`, (d) bound to RETIRED BOM + flag=true → `BLOCKED_RETIRED_BOM`, (e) bound to RELEASED BOM + flag=true → `READY`, (f) post-release state.
- Capture i18n: en + ja for at least 2 states.
- Capture capability-driven button enable/disable for personas: ADM (both perms), IEP (only pv.manage), OPR (no perms).
- Store evidence under `docs/audit/mmd-fe-qa-03-screenshots/` (one folder, indexed `case-XX-{state}.png`).

#### Explicitly Out of Scope
- Any source code changes (this is QA evidence only).
- Cypress/Playwright automation rewrites (existing e2e suite is fine; only manual capture this slice).
- Mobile/tablet viewport audit (deferred to Station UI workstream).
- Performance/load testing.

#### Files / Areas to Inspect
- `frontend/src/app/pages/ProductDetail.tsx` (binding section, capability gating)
- `frontend/src/app/api/productApi.ts` (`ProductVersionBomBindingResponse`)
- `frontend/src/app/i18n/registry/en.ts`, `ja.ts` — confirm all readiness state labels present
- `backend/tests/test_bom_binding_api.py` — to mirror states in the seed fixture

#### Implementation Rules
- Use a fresh DB schema (alembic upgrade to 0014). Do not piggyback on a working environment with mixed state.
- Capture network panel for each binding mutation (POST/DELETE) and PV release (POST .../release).
- For BLOCKED states, capture both UI text and the HTTP 400 response detail.
- One screenshot = one state; do not combine.

#### Tests Required
None new. This slice runs the existing test/regression gates as a sanity check, **not as PASS evidence for the slice itself**:

- `pytest -q tests/test_bom_binding_api.py tests/test_product_version_foundation_api.py` (exit 0)
- `npm run check:mmd:read` (exit 0, 209 checks)
- `npm run build && npm run lint && npm run lint:i18n:registry && npm run check:routes` (all exit 0)

#### Verification Commands
```powershell
# Backend regression baseline (must still pass before evidence capture)
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_bom_binding_api.py tests/test_product_version_foundation_api.py tests/test_mmd_rbac_action_codes.py
# FE regression baseline
cd g:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read
npm.cmd run build
npm.cmd run lint
npm.cmd run lint:i18n:registry
npm.cmd run check:routes
```

#### Documentation Updates
- Add `docs/audit/mmd-fe-qa-03-runtime-visual-evidence-pack.md` (the report).
- Add screenshots under `docs/audit/mmd-fe-qa-03-screenshots/`.
- Do **not** modify the freeze doc; reference it.

#### Definition of Done
- ≥ 12 screenshots covering 6 readiness states × 2 personas (ADM, IEP) on at least one locale; ≥ 2 screenshots on `ja` for any 2 states.
- Each screenshot indexed with: timestamp (UTC), persona, locale, PV state, BOM state, binding state, flag value, expected readiness, observed readiness — table in the report.
- Zero discrepancies between expected and observed; if any discrepancy is found, slice halts and opens a defect ticket.
- All four regression commands above exit 0 (paste exit codes into the report).

#### Stop Conditions
- A discrepancy with the freeze contract is found → halt; do not patch FE in this slice; raise defect.
- `npm run lint:i18n:registry` reports drift (mid-slice, someone modified registry) → halt; do not capture more evidence until registry is restored.
- Test/regression command exits non-zero on the same commit being captured → halt; slice cannot ship.

---

### Slice 2 — MMD-CURRENT-STATE-V2 — Refresh `mmd-current-state-report.md`

#### Intent
Bring the May-1 current-state report up to truth as of MMD-FE-QA-03 close. The May-1 doc misclassifies 5 screens as SHELL — every coding agent reading the doc first gets a false picture and may waste a slice trying to “build BOM read”.

#### Baseline Sources
- Current source state on the same commit as MMD-FE-QA-03 completion.
- `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (authoritative for binding).
- All `mmd-*-baseline-01-*-freeze-handoff.md` documents (5 freezes).
- `p0-b-mmd-closeout-review.md`.

#### In Scope
- Re-inspect 9 MMD screens for current data source (real API vs mock).
- Re-inspect API client layer (productApi/routingApi/reasonCodeApi) and explicitly state where BOM and RR live (they are nested inside productApi / routingApi, not standalone — the May-1 doc wrongly looked for `bomApi.ts`).
- Re-inspect the disabled-mutation buttons table: many are now enabled behind `capabilities.can_*`.
- Refresh GAP-MMD-01..10 — most are now resolved.
- Add new GAP-MMD-11..N for RR FE write parity, Routing Op Detail FE write parity, set_current governance, scope-applicability deferral.

#### Explicitly Out of Scope
- Any source change.
- Any new governance contract.

#### Files / Areas to Inspect
- All 9 MMD pages under `frontend/src/app/pages/` referenced by the May-1 report.
- `frontend/src/app/api/index.ts` and all api modules.
- `backend/app/api/v1/products.py`, `routings.py`, `reason_codes.py` (or equivalent).
- `docs/design/02_domain/product_definition/*.md` for current contract status lines.

#### Implementation Rules
- Treat the May-1 doc as **history**: do not delete; replace with v2.0 and link history.
- Every claim must cite a file path. No “I believe …”.
- For any field not present in `RoutingOperationItemFromAPI` per the May-1 doc (`setup_time`, `work_center`, `required_skill`, `required_skill_level`, `qc_checkpoint_count`), re-check today — note status truthfully.

#### Tests Required
None — documentation slice.

#### Verification Commands
```bash
# Spot-check: confirm no remaining mock fixtures in MMD pages
grep -nE "mockBom|mockOperation|mockRequirement|mockReasonCode" frontend/src/app/pages/*.tsx
# Confirm api index still exports the named clients
grep -E "bomApi|reasonCodeApi|routingApi|productApi" frontend/src/app/api/index.ts
```

#### Documentation Updates
- Overwrite `docs/audit/mmd-current-state-report.md` with v2.0; carry the v1.0 History row.
- Add a “Supersedes” banner pointing to v1.0.

#### Definition of Done
- v2.0 published with file-path evidence for every section that changed.
- All previously open GAP-MMD-01..10 explicitly marked Resolved / Superseded / Still-Open.
- Reviewer can find at least 3 stale claims in v1.0 marked corrected in v2.0.

#### Stop Conditions
- A claim cannot be verified by a `grep` or file read → mark as Evidence-Needed, not as Resolved.
- The slice grows beyond rewriting the current-state doc → halt; create a separate doc-cleanup slice.

---

### Slice 3 — MMD-MASTER-BASELINE-01 — Full MMD Foundation Closeout

#### Intent
Single freeze document that aggregates all 5 prior freeze handoffs (read-baseline, pv-write-baseline, bom-write-baseline, reason-code-write-baseline, bom-pv-binding-baseline) into one MMD-COMPLETE-FOR-DISCRETE-FIRST baseline, plus the refreshed current-state. After this slice, MMD is closed unless a Hard Mode MOM v3 verdict re-opens scope.

#### Baseline Sources
- The five existing freeze handoffs (see §1.2).
- `mmd-current-state-report.md` v2.0 from Slice 2.
- `mmd-fe-qa-03-runtime-visual-evidence-pack.md` from Slice 1.

#### In Scope
- Aggregate invariants, capability matrices, do-not-do rules, regression coverage totals, alembic head, action-code registry entries.
- One “Final Freeze Verdict” section signed by PO-SA agent.
- Update `docs/roadmap/flezibcg-overall-roadmap-latest.md` §“Phase 2 — P0-B” to state P0-B-MMD = FROZEN with link to this baseline.

#### Explicitly Out of Scope
- Anything that adds new behavior.
- Anything that re-opens a deferred item.

#### Files / Areas to Inspect
- All freeze handoff docs.
- `docs/design/02_registry/action-code-registry.md` — confirm 5 MMD action codes are present and ADMIN-family.
- Alembic head — **as of 2026-05-20 the head is 0019** (Quality domain added 0015–0019). The MMD master baseline must (a) state the head observed at freeze time, (b) confirm no migration after the binding freeze touches MMD models (`product_versions`, `product_version_bom_bindings`, `boms`, `bom_items`, `routings`, `routing_operations`, `resource_requirements`, `reason_codes`), (c) leave Quality migrations untouched.

#### Implementation Rules
- Quote, do not rewrite, the invariants from each freeze doc.
- Where two freeze docs disagree, **do not silently pick one** — surface the conflict and open a follow-up ticket.

#### Tests Required
Re-run the full MMD regression bundle on the commit that this baseline freezes:

- Backend: `pytest -q tests/test_bom_binding_api.py tests/test_bom_foundation_api.py tests/test_bom_foundation_service.py tests/test_product_foundation_api.py tests/test_product_foundation_service.py tests/test_product_version_foundation_api.py tests/test_routing_foundation_api.py tests/test_routing_foundation_service.py tests/test_resource_requirement_api.py tests/test_resource_requirement_service.py tests/test_reason_code_*.py tests/test_mmd_rbac_action_codes.py tests/test_alembic_baseline.py`
- Frontend: `check:mmd:read`, `build`, `lint`, `lint:i18n:registry`, `check:routes`

All must exit 0. Paste exit codes into the doc.

#### Verification Commands
See Tests Required.

#### Documentation Updates
- New doc: `docs/audit/mmd-master-baseline-01-freeze-handoff.md`.
- Patch: `docs/roadmap/flezibcg-overall-roadmap-latest.md` Phase 2 status row.
- Patch: `docs/implementation/p0-b-mmd-closeout-review.md` to add a “v2.0 — superseded by MMD-MASTER-BASELINE-01” row.

#### Definition of Done
- Single doc that lets a new agent reproduce MMD truth without reading 5 separate freezes.
- Roadmap reflects MMD frozen status.
- All listed test/lint exit codes pasted with timestamps.

#### Stop Conditions
- A regression command does not exit 0 → halt; do not freeze on a red build.
- Roadmap edit creates a merge conflict in `flezibcg-overall-roadmap-latest.md` → halt; bring back to PO-SA review.

---

## Part 4 — Slice Specs (Next lane)

### Slice 4 — MMD-RR-WRITE-AUDIT-01 — Resource Requirement FE Write Parity Audit

#### Intent
Backend has full RR write API (POST/PATCH/DELETE nested under routing operation per P0-B closeout). FE today renders RR list against `routingApi.ts` and `ResourceRequirementItemFromAPI`. Audit whether FE exposes write-intent buttons gated by `capabilities.can_*`, parity with BOM-binding pattern, and whether server-derived capability is returned on the RR GET response.

#### Baseline Sources
- `docs/implementation/p0-b-mmd-closeout-review.md` §“P0-B Resource Requirement API”
- `frontend/src/app/pages/ResourceRequirements.tsx`
- `frontend/src/app/api/routingApi.ts` (RR types)
- The pattern set by `mmd-fullstack-14b-bom-product-version-binding-capability-guard.md`

#### In Scope
- Document: does the RR GET endpoint return a `capabilities` envelope? If not, this is GAP-MMD-RR-1.
- Document: does the FE infer button enablement from lifecycle status or from `capabilities`? If lifecycle-only, this is GAP-MMD-RR-2 (violates §15 rule 12 of binding freeze doc, applied by analogy).
- Decide: do we lift RR FE to the same server-derived capability pattern, or accept current state as “read-only is sufficient for P0-B”?

#### Explicitly Out of Scope
- Any source code change.
- Any new backend endpoint.
- Cross-tenant negative tests (assumed covered by P0-B closeout).

#### Files / Areas to Inspect
- `backend/app/api/v1/routings.py` RR nested routes (POST/PATCH/DELETE)
- `backend/app/services/resource_requirement_service.py`
- `frontend/src/app/pages/ResourceRequirements.tsx`
- `frontend/src/app/api/routingApi.ts`
- `backend/tests/test_resource_requirement_api.py` — what scenarios are covered

#### Implementation Rules
- This is an audit slice; do **not** edit code.
- Produce a verdict: ACCEPT current state, or open Slice 5 (MMD-RR-FE-WRITE-01).

#### Tests Required
None new.

#### Verification Commands
```bash
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_resource_requirement_api.py tests/test_resource_requirement_service.py
```

#### Documentation Updates
- `docs/audit/mmd-rr-write-audit-01-report.md`

#### Definition of Done
- One of two verdicts published:
  - **ACCEPT** — RR FE stays read-only for now; add to deferred list with rationale.
  - **OPEN** — proceed to MMD-RR-FE-WRITE-01 with explicit slice prompt.

#### Stop Conditions
- The audit discovers FE writes RR by lifecycle-status inference (not capability-based) → halt; that becomes a defect, not part of this audit slice.

---

### Slice 5 (conditional) — MMD-RR-FE-WRITE-01 — Resource Requirement FE Write Intent + Capability Guard

#### Intent
If Slice 4 verdict is OPEN: lift RR FE to the same pattern as BOM binding (server-derived `capabilities.can_create/can_update/can_delete`, intent-only FE).

#### Baseline Sources
- Slice 4 audit verdict.
- `mmd-fullstack-14b-bom-product-version-binding-capability-guard.md` (pattern reference).

#### In Scope
- Extend RR GET response to embed `capabilities`.
- Extend FE to render intent buttons gated by `capabilities.can_*`.
- Extend i18n registry for new labels (en + ja parity).
- Extend regression script (`check:mmd:read`) with new Section for RR capability consumption.

#### Explicitly Out of Scope
- New backend behavior — the RR write endpoints already exist.
- Plant/scope-specific RR (deferred to MMD-SCOPE-APPLICABILITY-01).
- Effective-dating for RR (out of scope; not in any contract).

#### Files / Areas to Inspect
- `backend/app/schemas/routing.py` or wherever `ResourceRequirementResponse` lives.
- `backend/app/services/resource_requirement_service.py`
- `frontend/src/app/pages/ResourceRequirements.tsx`
- `frontend/scripts/mmd-read-integration-regression-check.mjs`

#### Implementation Rules
- AND-semantics if RR mutation requires both `routing.manage` and any other action — confirm from existing service code, do not invent.
- FE must not infer from lifecycle status.

#### Tests Required
- New BE tests: `can_create`, `can_update`, `can_delete` capability computation for each combination of (PV/routing lifecycle × persona perms).
- FE regression Section (e.g., Section Q): assert RR buttons are gated by capability fields, not by `routing.lifecycle_status`.

#### Verification Commands
```powershell
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_resource_requirement_api.py
cd g:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read
npm.cmd run build
npm.cmd run lint
npm.cmd run lint:i18n:registry
```

#### Documentation Updates
- `docs/audit/mmd-rr-fe-write-01-report.md`
- Patch `mmd-current-state-report.md` v2.0 GAP table (resolve GAP-MMD-RR-*).

#### Definition of Done
- All tests pass; FE regression count increases.
- Cap matrix table mirrors the BOM-binding capability matrix style.

#### Stop Conditions
- Slice cannot keep BE response wire-format backward compatible → halt; this becomes a contract slice first.
- The RR service requires touching execution/material to compute capability → halt; capability must be computable from MMD-only context.

---

### Slice 6 — MMD-ROUTING-OP-WRITE-AUDIT-01 — Routing Operation Detail FE Write Parity Audit

Same shape as Slice 4 but for `RoutingOperationDetail.tsx`. Backend exposes `POST /routings/{id}/operations`, `PATCH /routings/{id}/operations/{opId}`, `DELETE …` per P0-B closeout. FE today reads operation via `routingApi.getRouting(routeId)` and filters; verify whether write-intent is exposed and capability-gated.

(All sections mirror Slice 4 with substitution: RR → Routing Operation, ResourceRequirements.tsx → RoutingOperationDetail.tsx.)

#### Stop Conditions specific to this slice
- Audit reveals RoutingOperationDetail still consumes mock fixtures (it should not, per the May-20 grep) → halt; the May-1 doc was right and the grep was wrong; investigate before continuing.

---

### Slice 7 (conditional) — MMD-ROUTING-OP-FE-WRITE-01 — Routing Operation FE Write Intent + Capability Guard

Same shape as Slice 5 but for Routing Operation Detail. Conditional on Slice 6 verdict.

---

### Slice 8 — MMD-PV-SETCURRENT-GOV-01 — Governance Contract for PV `set_current`

#### Intent
Today `ProductVersion.is_current` is advisory only — there is no partial-unique enforcement, no UI control, and no event. P0-C Execution will need a deterministic way to pick “which version is the production target for a product right now”. Without governance, agents will be tempted to add ad-hoc `set_current` endpoints. This slice writes the contract, **not** the implementation.

#### Baseline Sources
- `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §14, §15 rules 1 & 11.
- `docs/design/02_domain/product_definition/product-version-foundation-contract.md`
- `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md`

#### In Scope
- Contract:
  - Authorization: `product_version.manage` only? Or also `product.manage`? (Recommendation: only `product_version.manage`; PV header is the entity.)
  - Lifecycle precondition: PV must be RELEASED to be set current.
  - Cardinality invariant: at most one CURRENT PV per (tenant, product). Partial-unique index proposal.
  - Mutation event: `PRODUCT_VERSION.SET_CURRENT` (new action code? or re-use `pv.manage`?).
  - Backward compatibility: existing `is_current = true` rows must remain valid; migration must enforce uniqueness without dropping data.
  - Read-only invariants for downstream: Execution / APS may read `is_current`, must not infer “release”.
- Capability matrix: `can_set_current`, `can_unset_current` (or only set?).
- Boundary guardrails: set_current does NOT touch BOM binding, execution, material, ERP.

#### Explicitly Out of Scope
- Any implementation. Migration script is **proposed** in the contract but not applied.
- Any FE work.
- Automatic current-version selection on RELEASE (separate future contract).

#### Files / Areas to Inspect
- `backend/app/models/product_version.py` — confirm `is_current` exists; check current default.
- `backend/alembic/versions/` — find when `is_current` was added.
- `docs/design/02_registry/product-event-registry.md`
- `docs/design/02_registry/action-code-registry.md`

#### Implementation Rules
- Contract must satisfy Hard Mode MOM v3 invariants (backend truth, AND-auth where applicable, tenant isolation, audit/event).
- Boundary section must explicitly list the 10 do-not-do rules from binding freeze §15 and confirm each remains protected.

#### Tests Required
None — contract slice.

#### Verification Commands
None — contract slice.

#### Documentation Updates
- `docs/design/02_domain/product_definition/product-version-set-current-governance-contract.md`
- Patch: `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` to add the set_current row.

#### Definition of Done
- Contract reviewed by PO-SA agent.
- All sections of the Standard Decision Format completed (Verdict, Reasoning, Scope, Architecture Impact, Risks, Next Agent Prompt, DoD).
- Risk register lists the migration concurrency risk and the “partial-unique on multi-tenant table” pattern note.

#### Stop Conditions
- Discovery that `is_current` is already consumed by execution/APS — halt; this becomes a wider cross-domain contract.
- Multi-plant scope-aware “current” requirements surface — halt; merge into MMD-SCOPE-APPLICABILITY-01 instead.

---

### Slice 9 (after Slice 8) — MMD-PV-SETCURRENT-IMPL-01

Implementation of the contract from Slice 8. Standard pattern: model + service + API + capability guard + tests + migration. Out of scope here until the contract is signed.

---

## Part 5 — Later lane (governance-contract-first, no implementation in this roadmap)

Each item below requires its own governance contract slice **before** any implementation slice is opened. They are listed so future agents do not “sneak” them into other slices.

| ID | Topic | Reason it stays Later |
|---|---|---|
| MMD-BINDING-EFFECTIVE-DATING-GOV-01 | `effective_from` / `effective_to` for binding | Adds time-bounded applicability; needs end-of-effectivity semantics, overlap rules, release-gate interaction. |
| MMD-BINDING-REPLACE-GOV-01 | Atomic PRIMARY swap | Needs rollback model, event sequence, authorization re-check semantics. |
| MMD-BINDING-MULTITYPE-GOV-01 | SECONDARY / ALTERNATE binding types | Needs selection-policy contract: who picks at execution time? |
| MMD-SCOPE-APPLICABILITY-01 | Plant/scope-specific binding + master data applicability | Requires plant hierarchy applicability layer + tenant/plant/manufacturing-profile policy contract. |
| MMD-PROFILE-POLICY-01 | Tenant/plant/manufacturing-profile policy for binding | Needs manufacturing-mode profile to be wired first (`DESIGN-MFGMODE-01`). |
| MMD-BINDING-VALIDATED-EVENT-01 | Emit `ProductVersionBomBinding.VALIDATED_ON_RELEASE` | Currently no consumer; emit only when a consumer is defined to avoid orphan events. |
| MMD-ISA88-FOUNDATION | Recipe / phase model | Belongs to P2-A, not MMD. |
| MMD-ERP-MASTER-SYNC | ERP-driven product/BOM sync | Belongs to P1-A integration, not MMD. |

---

## Part 6 — Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Stale current-state doc misleads next coding agent into rebuilding done work | HIGH (already happening) | MEDIUM (lost cycles) | Slice 2 fixes immediately. |
| Visual QA discovers i18n gap for `ja` on a release-readiness label | MEDIUM | LOW | Slice 1 has both locales in scope; fix in the same slice if cosmetic. |
| `lint:i18n` PowerShell/CRLF caveat trips a future Windows-only agent | MEDIUM | LOW | Already documented in freeze doc §13; carry forward in master baseline. |
| RR or Routing Op Detail FE still infers from lifecycle status | MEDIUM | MEDIUM (privilege bypass class) | Slice 4 / Slice 6 audits will surface; remediation via Slice 5 / Slice 7. |
| `is_current` consumed by execution/APS before contract is signed | LOW | HIGH | Slice 8 must inspect execution code first; halt if consumer found. |
| Partial-unique index migration races against multi-tenant writes | LOW | HIGH | Contract slice must specify safe migration order (lock → backfill → constraint). |
| Scope creep: an agent bundles set_current + effective-dating + replace in one go | MEDIUM | HIGH | Per-slice DoD + Stop Conditions enforced; PO-SA review gate. |
| Backend RR write tests cover happy path but not capability-matrix corners | UNKNOWN | MEDIUM | Slice 4 audit confirms; if gap, add tests in Slice 5. |

---

## Part 7 — Opinion vs Evidence Marker

This table marks every non-trivial claim in this roadmap as **E (evidence)** or **O (opinion)**.

| # | Claim | E / O | Source / Reasoning |
|---|---|---|---|
| 1 | BOM↔PV binding is frozen 2026-05-08 | E | `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` History row, §1 |
| 2 | 5 SHELL pages from May-1 doc no longer use mock fixtures as of 2026-05-20 | E | `grep mockBom\|mockOperation\|mockRequirement\|mockReasonCode frontend/src/app/pages/{Bom*,Reason*,Resource*,RoutingOp*}.tsx` returned 0 |
| 3 | BOM types live inside `productApi.ts`, not a standalone `bomApi.ts` | E | `head frontend/src/app/pages/BomList.tsx` shows `import type { BomCreateRequest, BomItemFromAPI } from "@/app/api/productApi"` |
| 4 | RR types live inside `routingApi.ts` | E | `frontend/src/app/api/index.ts` exports `ResourceRequirementItemFromAPI` from `./routingApi` |
| 5 | Alembic head at **binding-freeze time** was 0014; **current head as of 2026-05-20 is 0019** (Quality domain added 0015–0019 after the binding freeze) | E | Binding freeze §6 for 0014; live listing `ls backend/alembic/versions/` for 0019. Note: binding-freeze §15 rule 13 ("no migrations after 0014") was scoped to *the binding baseline*, not to the whole project — Quality migrations 0015–0019 are an adjacent domain and do not violate that rule. |
| 6 | P0-B MMD minimum is implemented and test-verified | E | `p0-b-mmd-closeout-review.md` Executive Summary, 141 pytest passed |
| 7 | The May-1 current-state report is stale | E | Cross-check with claims #2, #3, #4 above |
| 8 | MMD-FE-QA-03 is the explicit next-recommended slice | E | `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §16 |
| 9 | `set_current` is advisory-only today | E | `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §14 row 2, §15 rule 1 |
| 10 | Recommendation to require **only** `product_version.manage` for set_current (not also `product.manage`) | O | My PO-SA opinion: PV is the entity being mutated; AND-auth here would be overkill. Confirm in Slice 8 contract review. |
| 11 | Recommendation that MMD does not expand into batch/process/ISA-88/ERP/backflush before P1 | E | `flezibcg-overall-roadmap-latest.md` Phase 8 (Backflush in P1-C), Phase 11 (ISA-88 in P2-A), §“Explicit exclusions” for P0-B |
| 12 | Recommendation that Slice 4 / Slice 6 be **audits before implementation** | O | My PO-SA opinion: audit risk is lower than direct implementation slice when the gap class is parity-with-binding-pattern; this matches the “PASS claims require exit codes” feedback rule — audit-then-decide avoids probe-then-PASS shortcut. |
| 13 | Partial-unique index for `is_current` is the recommended pattern | O | My opinion based on PostgreSQL partial-unique-index practice; needs DB lead review in Slice 8. |
| 14 | Risk of stale current-state doc misleading agents is HIGH likelihood | O | Inferred from project-instruction priority list rule 6 (“Source audit reports and latest agent reports” are precedence input). |

---

## Appendix A — Coding-Agent Prompt Stubs (ready to issue)

These are **prompt skeletons**. Each one must be hand-finalized with the live commit SHA and the freeze doc commit SHA before being given to a coding agent.

### A.1 Prompt for MMD-FE-QA-03

> You are implementing **MMD-FE-QA-03 — BOM↔PV Binding Runtime Visual QA**.
>
> **Read first (block on completion of each):**
> 1. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md`
> 2. `docs/audit/mmd-fe-qa-02-runtime-visual-evidence-pack.md` (pattern)
> 3. `docs/ai-skills/qa-e2e-layer/SKILL.md`
> 4. `docs/ai-skills/design-md-ui-governor/SKILL.md`
>
> Confirm in your first reply that you have read each of the four documents by name. Do not modify source code. Capture evidence per the slice spec. Run the four verification commands and paste raw exit codes (PASS claims without exit codes will be rejected per project rule). On any expected-vs-observed discrepancy, halt and raise a defect — do not patch FE in this slice.

### A.2 Prompt for MMD-CURRENT-STATE-V2

> Documentation-only slice. You must NOT modify source. Re-snapshot `docs/audit/mmd-current-state-report.md` against the current commit; every claim cites a file path. Do not delete v1.0 content — supersede it. Run the verification grep commands listed in the slice spec and paste raw output.

### A.3 Prompt for MMD-RR-WRITE-AUDIT-01

> Audit slice. Do NOT modify source. Read `p0-b-mmd-closeout-review.md`, the binding capability-guard report, and the live `ResourceRequirements.tsx` + `routingApi.ts`. Produce a verdict: ACCEPT current state OR OPEN Slice 5. Report must cite specific file lines where capability fields are (or are not) consumed.

---

## Appendix B — Definition of “MMD Hoàn Thiện”

Per this roadmap, MMD is considered **hoàn thiện cho discrete-first** when **all** of the following are true:

1. MMD-MASTER-BASELINE-01 has been published and references all 5 prior freezes plus the current-state v2.
2. All MMD screens render real data; zero mock fixtures (verified by grep).
3. All MMD write surfaces gate intent buttons by server-derived `capabilities.can_*` (no lifecycle-only gating).
4. Alembic head observed at master-baseline-freeze time is documented; no migration **after** that head touches MMD-owned tables without a fresh MMD governance contract (adjacent-domain migrations like Quality 0015–0019 are allowed).
5. Backend regression bundle (all `test_*mmd*`, `test_bom_*`, `test_product_*`, `test_routing_*`, `test_resource_requirement_*`, `test_reason_code_*`, `test_alembic_baseline.py`) exits 0.
6. FE regression bundle (`check:mmd:read`, `build`, `lint`, `lint:i18n:registry`, `check:routes`) exits 0.
7. Visual QA evidence pack exists for the binding section and at least one persona × locale matrix.
8. No deferred item has been silently implemented; each remains in the Later lane until its governance contract is opened.

When 1–8 hold, MMD is closed for P0. Subsequent work must come from the Later lane and must begin with a governance contract slice.

---

*End of MMD Completion Roadmap v1.0 — 2026-05-20.*
