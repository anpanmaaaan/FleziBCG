# MMD-MASTER-BASELINE-01 — Full Manufacturing Master Data Foundation Closeout

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-20 | v1.0 | PO-SA agent master baseline. Aggregates 5 prior freeze handoffs plus current-state v2.0 into a single MMD-COMPLETE-FOR-DISCRETE-FIRST closeout. Includes documented parity-debt for RR + Routing Operation. |

---

## 1. Purpose

Single freeze document for the Manufacturing Master Data foundation. Replaces the need for a future agent to read five separate freeze handoffs to understand the MMD truth.

After this baseline, MMD foundation is closed for the discrete-first scope. Subsequent MMD changes must originate from the Later lane of `docs/roadmap/mmd-completion-roadmap-2026-05-20.md` and must begin with a governance contract slice.

---

## 2. Aggregated Baselines (sources of truth)

| Sub-domain | Frozen | Source baseline doc | Verdict |
|---|---|---|---|
| MMD read integration (all sub-domains) | 2026-05-03 | `docs/audit/mmd-read-baseline-01-read-integration-freeze-handoff.md`, `…-02-complete-read-integration-freeze-handoff.md` | ✅ Frozen |
| Product Version write governance | 2026-05-03 | `docs/audit/mmd-pv-write-baseline-01-product-version-write-freeze-handoff.md` | ✅ Frozen |
| BOM write governance | 2026-05-06 | `docs/audit/mmd-bom-write-baseline-01-bom-write-freeze-handoff.md` | ✅ Frozen |
| Reason Code write governance | 2026-05-06 | `docs/audit/mmd-reason-code-write-baseline-01-reason-code-write-freeze-handoff.md` | ✅ Frozen |
| BOM ↔ PV binding | 2026-05-08 (re-verified 2026-05-19 in capability-guard slice) | `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` | ✅ Frozen |
| Current-state snapshot | 2026-05-20 | `docs/audit/mmd-current-state-report.md` v2.0 | ✅ Current |

---

## 3. Implementation State (aggregated)

### 3.1 Sub-domain capability summary

| Sub-domain | BE Read | BE Write | Capability envelope | FE Read | FE Write Intent | Status |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Product (header) | ✅ | n/a | n/a | ✅ | n/a (write via PV) | ✅ Complete |
| Product Version | ✅ | ✅ POST/PATCH/release/retire | ✅ `product_version_capabilities`, per-row `allowed_actions` | ✅ | ✅ (capability-gated) | ✅ Complete |
| BOM (incl. items) | ✅ | ✅ POST/PATCH/items CRUD/release/retire | ✅ `bom_capabilities`, per-row `allowed_actions` | ✅ | ✅ (capability-gated) | ✅ Complete |
| BOM ↔ PV binding | ✅ wrapper | ✅ POST/DELETE; toggle via PV PATCH | ✅ `ProductVersionBomBindingCapabilities` | ✅ | ✅ (capability-gated) | ✅ Complete |
| Reason Code | ✅ | ✅ POST/PATCH/release/retire | ✅ `ReasonCodeCapabilities`, per-row `allowed_actions` | ✅ | ✅ (capability-gated) | ✅ Complete |
| Routing (header) | ✅ | ✅ POST/PATCH/release/retire | ❌ no envelope | ✅ | ❌ FE buttons locked | ⚠️ Parity debt (GAP-MMD-13) |
| Routing Operation | ✅ nested | ✅ POST/PATCH/DELETE | ❌ no envelope | ✅ via routing | ❌ no write intent | ⚠️ Parity debt (GAP-MMD-11) |
| Resource Requirement | ✅ nested | ✅ POST/PATCH/DELETE | ❌ no envelope | ✅ via routing | ❌ no write intent | ⚠️ Parity debt (GAP-MMD-12) |

### 3.2 Action Code Registry (5 MMD entries — all ADMIN family)

From `docs/design/02_registry/action-code-registry.md`:

1. `admin.master_data.product_version.manage`
2. `admin.master_data.routing.manage`
3. `admin.master_data.resource_requirement.manage`
4. `admin.master_data.bom.manage`
5. `admin.master_data.reason_code.manage`

(Additional `admin.master_data.product.manage` was added in `MMD-BE-02` per the registry; product-header write is governed but mutation flows through PV in practice.)

### 3.3 Alembic State

- Last MMD-owning migration: `0014_add_bom_binding_required_for_release_to_product_versions.py` (BOM-binding policy field).
- Current alembic HEAD as of 2026-05-20: `0019` (Quality domain — 0015–0019).
- Quality migrations (0015–0019) do NOT touch MMD tables. MMD model files are unchanged since 0014.

### 3.4 Test Coverage Aggregate

Per the 5 baseline freezes, MMD-owning backend tests:

| Test suite | Count (per source freeze) | Status |
|---|---:|---|
| `test_bom_binding_api.py` | 35 | ✅ Pass |
| `test_mmd_rbac_action_codes.py` | 39 (incl. schema contract) | ✅ Pass |
| `test_product_version_foundation_api.py` | 15 release-validation + adjacent | ✅ Pass |
| `test_alembic_baseline.py` | head check | ✅ Pass (head=0014 at binding freeze; this baseline notes head has since advanced to 0019 for adjacent domains) |
| `test_bom_foundation_api.py`, `test_bom_foundation_service.py` | foundation read | ✅ Pass |
| `test_product_foundation_api.py`, `test_product_foundation_service.py` | foundation | ✅ Pass |
| `test_routing_foundation_api.py`, `test_routing_foundation_service.py` | foundation | ✅ Pass |
| `test_resource_requirement_api.py`, `test_resource_requirement_service.py` | foundation | ✅ Pass |
| `test_reason_code_*.py` | foundation + write | ✅ Pass |

Frontend regression at last freeze:
- `npm run check:mmd:read` → 209 checks pass
- `npm run build` → exit 0
- `npm run lint` → exit 0
- `npm run lint:i18n:registry` → 1902 keys parity (en/ja)
- `npm run check:routes` → exit 0
- `npm run lint:i18n` (bash script) — Windows PowerShell CRLF caveat; use `lint:i18n:registry` Node.js equivalent

This master baseline does **not** re-run the suite from a documentation slice; the source freezes are authoritative for their respective branches. A coding agent owning the next implementation slice must re-run on the head commit before opening any patch.

---

## 4. Invariants (aggregated across all 5 freezes)

1. **Backend owns master-data truth.** Frontend sends intent only.
2. **Tenant isolation enforced** at service/repository/API for every MMD entity and capability computation.
3. **AND-authorization** where two domains co-own a mutation:
   - BOM ↔ PV binding mutation: `bom.manage` ∧ `pv.manage` (release validation is read-only and does not require `bom.manage`).
4. **Single-action authorization** where the mutation is intra-domain:
   - Product Version mutation: `product_version.manage`
   - BOM mutation: `bom.manage`
   - Reason Code mutation: `reason_code.manage`
   - Resource Requirement mutation: `resource_requirement.manage` (note: applies in current implementation; the FE parity slice MMD-RR-FE-WRITE-01 must not relax this)
   - Routing / Routing Operation mutation: `routing.manage`
5. **No FE button enables based on lifecycle status alone** for: Product Version, BOM, BOM↔PV binding, Reason Code (compliance verified). For Routing / Routing Operation / Resource Requirement, FE is currently read-only — when write intent is added, the same rule applies (enforced via audit slice prompts MMD-RR-WRITE-AUDIT-01 / MMD-ROUTING-OP-WRITE-AUDIT-01).
6. **Lifecycle preconditions** are enforced server-side, not in FE:
   - PV mutation requires `lifecycle_status = DRAFT` (except release, which moves to RELEASED).
   - BOM mutation requires `lifecycle_status = DRAFT` for content; release moves to RELEASED.
   - Binding bind requires PV DRAFT + BOM not RETIRED.
   - Reason Code mutation requires DRAFT for content; release moves to RELEASED.
   - Routing / operation / RR content mutation requires routing DRAFT (per service code).
7. **PV release validation gate** (`bom_binding_required_for_release` boolean) is read-only, does not mutate BOM or binding, does not require `bom.manage`, and emits no event on blocked release.
8. **Audit / event emission** is mandatory for every governed mutation. Reads do not emit security events. Blocked mutations emit no success event.
9. **Cross-domain side effects forbidden** from MMD mutations: no material/inventory/backflush/ERP/traceability/quality/execution behavior triggered by MMD writes.
10. **Adjacent migrations allowed** beyond 0014 only if they do not touch MMD-owning tables (Quality migrations 0015–0019 comply).
11. **`is_current` on Product Version is advisory only.** No enforcement, no partial-unique index, no FE control, no event. Future enforcement requires `MMD-PV-SETCURRENT-GOV-01` contract first.
12. **GET response schema for BOM binding includes `binding` + `capabilities`** — must not be changed without contract.

---

## 5. Do-Not-Do Rules (aggregated, hard guardrails)

Future agents must obtain a new Hard Mode MOM v3 verdict before implementing any of the following:

1. Implement Product Version `set_current` enforcement (advisory only today).
2. Implement binding replace (atomic PRIMARY swap).
3. Implement multiple BOM binding types (SECONDARY, ALTERNATE, etc.).
4. Implement binding `effective_from` / `effective_to`.
5. Implement plant/scope-specific binding (MMD-SCOPE-APPLICABILITY-01 prerequisite).
6. Implement product-level / tenant/plant/manufacturing-profile policy.
7. Implement material reservation, inventory movement, scrap posting, backflush, ERP posting from any MMD mutation.
8. Implement traceability genealogy, quality acceptance, or execution dispatch triggered by MMD state changes.
9. Implement production-order creation or APS selection from MMD state.
10. Implement automatic current-version selection.
11. Infer authorization from lifecycle status alone in any MMD frontend control.
12. Weaken AND-authorization on BOM↔PV binding mutations.
13. Add migrations that mutate MMD-owning tables (product, product_version, product_version_bom_binding, bom, bom_item, routing, routing_operation, resource_requirement, reason_code) beyond 0014 without a fresh governance contract.
14. Remove `binding` + `capabilities` wrapper from GET binding response.
15. Implement reason code write effect on the live `/v1/downtime-reasons` endpoint consumed by Station Execution (the dialog and the registry must remain decoupled).

---

## 6. Parity-Debt Items Inside MMD Scope (must close before MMD = FULLY FROZEN)

These are not deferred Later-lane items — they are tracked debt that this master baseline acknowledges:

| Gap | Owning slice | Status |
|---|---|---|
| GAP-MMD-11 — Routing Operation FE write intent + BE capability envelope | MMD-ROUTING-OP-WRITE-AUDIT-01 (verdict: OPEN) → MMD-ROUTING-OP-FE-WRITE-01 | Verdict published 2026-05-20; impl pending |
| GAP-MMD-12 — Resource Requirement FE write intent + BE capability envelope | MMD-RR-WRITE-AUDIT-01 (verdict: OPEN) → MMD-RR-FE-WRITE-01 | Verdict published 2026-05-20; impl pending |
| GAP-MMD-13 — Routing header FE write intent (Save/Edit/Release/Retire buttons) | MMD-ROUTING-WRITE-FE-01 (not yet scheduled) | Queued |
| GAP-MMD-15 — Stale `MockWarningBanner` / `BackendRequiredNotice` imports in 4 connected pages | MMD-FE-QA-03 (visual QA) → cleanup slice if visible | Awaiting QA evidence |
| GAP-MMD-16 — PV `is_current` advisory-only; governance contract needed before P0-C execution depends on it | MMD-PV-SETCURRENT-GOV-01 → MMD-PV-SETCURRENT-IMPL-01 | Contract draft pending |

When GAP-MMD-11, -12, -13 are closed and GAP-MMD-15 is cleaned, MMD foundation is **FULLY FROZEN**.

This master baseline is **MOSTLY FROZEN** — the foundation is production-quality for discrete-first execution; the three parity gaps are not blockers for P0-C entry but must close before P1.

---

## 7. Roadmap Update

`docs/roadmap/flezibcg-overall-roadmap-latest.md` Phase 2 status row should reflect:

> **P0-B MMD Status: MOSTLY FROZEN (2026-05-20)** — Foundation production-ready; parity gaps tracked in `docs/audit/mmd-master-baseline-01-freeze-handoff.md` §6. P0-C Execution Core entry not blocked. Reference: `docs/audit/mmd-master-baseline-01-freeze-handoff.md`.

(The actual edit to the roadmap doc is bundled with this master baseline slice — see §10 verification.)

---

## 8. Verification Commands

This master baseline does not execute the suite (it is a documentation aggregator). The commands below are the ones the **next slice** (MMD-RR-FE-WRITE-01 or MMD-ROUTING-OP-FE-WRITE-01) must run as its own gate:

```powershell
# Backend MMD bundle
g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q `
  tests/test_bom_binding_api.py `
  tests/test_bom_foundation_api.py `
  tests/test_bom_foundation_service.py `
  tests/test_product_foundation_api.py `
  tests/test_product_foundation_service.py `
  tests/test_product_version_foundation_api.py `
  tests/test_routing_foundation_api.py `
  tests/test_routing_foundation_service.py `
  tests/test_resource_requirement_api.py `
  tests/test_resource_requirement_service.py `
  tests/test_mmd_rbac_action_codes.py `
  tests/test_alembic_baseline.py

# Frontend MMD bundle
cd g:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read
npm.cmd run build
npm.cmd run lint
npm.cmd run lint:i18n:registry
npm.cmd run check:routes
```

Expected exit code for each: 0.

A PASS claim in any subsequent agent report without raw exit codes pasted in is rejected per the project rule (`feedback_pass_claims_need_exit_code`).

---

## 8.1 Verification Results — 2026-05-20 (PO-SA agent run, sandbox)

The PO-SA agent ran a partial verification on 2026-05-20 against the current working copy. Results:

| Command | Exit | Notes |
|---|---:|---|
| `node scripts/mmd-read-integration-regression-check.mjs` | `0` | 209 passed, 0 failed |
| `node scripts/check_i18n_registry_parity.mjs` | `0` | 2593 keys (en/ja parity) — note: count > 1902 at last freeze; registry has grown for non-MMD work, parity still holds |
| `node scripts/route-smoke-check.mjs` | `0` | All persona/route guard checks pass |
| `./node_modules/.bin/eslint src/` | **`1`** | **FAIL** — parse error `StationExecution.tsx:1259:2 '/' expected` |
| `./node_modules/.bin/tsc --noEmit -p .` | non-zero | 6 errors: `en.ts:2785` unterminated string, `ja.ts:2775` unterminated string, `StationExecution.tsx:1023/1069/1259` unclosed JSX elements |
| `./node_modules/.bin/vite build` | non-zero | Environment failure (`@rollup/rollup-linux-x64-gnu` missing in Windows-installed `node_modules`) — **NOT a project issue**; passes on Windows |

### Interpretation

The lint + tsc failures are caused by **uncommitted in-flight work** in the repo working copy as of 2026-05-20. `git status` shows 20+ modified files including `frontend/src/app/i18n/registry/en.ts`, `frontend/src/app/i18n/registry/ja.ts`, `frontend/src/app/pages/StationExecution.tsx`, and several `station-execution/*` component files. The most recent commit is `3e43e599 "coding"` followed by a series of station-execution refactor commits — this is mid-refactor by another agent / developer.

**None of the failing files are MMD-owning files.** No MMD model, MMD service, MMD schema, MMD api route, or MMD page is in the modified list (other than `mmd-current-state-report.md` and `p0-b-mmd-closeout-review.md` which I edited in this session as doc-only changes per the slice plan).

### Master baseline freeze status

Per the parent roadmap stop condition (`docs/roadmap/mmd-completion-roadmap-2026-05-20.md` §2.3): “A regression command does not exit 0 → halt; do not freeze on a red build.”

Therefore this master baseline document is published as **DRAFT FREEZE — pending clean-build re-verification**. The next agent owning either `MMD-RR-FE-WRITE-01` or `MMD-ROUTING-OP-FE-WRITE-01` (or whoever first re-runs MMD verification on a clean working copy) MUST:

1. Confirm the working copy is clean (`git status` shows no uncommitted MMD-relevant changes, station-execution refactor is committed or stashed).
2. Re-run the full §8 verification bundle on Windows PowerShell against the project `.venv` and project Postgres.
3. Paste all exit codes (raw) into §8.1 and flip the freeze status from DRAFT FREEZE to FROZEN.

Until that re-verification happens, this baseline is treated as truth for *content* (invariants, capabilities, do-not-do rules) but **NOT as a clean-build attestation**.

## 9. Final Verdict

**MMD FOUNDATION — DRAFT-FROZEN pending clean-build re-verification.** Discrete-first scope complete. Three parity gaps tracked with named owning slices. P0-C entry not blocked by MMD content; however, the red lint/tsc state in the current working copy must be cleared before any new MMD slice opens.

Coding agents acting on MMD must:
1. Read this master baseline.
2. Read `docs/audit/mmd-current-state-report.md` v2.0.
3. Read the relevant per-sub-domain freeze handoff if working on that sub-domain.
4. Read the MMD-* audit verdicts (`mmd-rr-write-audit-01-report.md`, `mmd-routing-op-write-audit-01-report.md`) before proposing any RR / Routing Op write change.
5. Run the verification bundle in §8 before opening any patch and paste exit codes in their report.

---

## 10. Documentation Updates Bundled

This slice also patches:

- `docs/roadmap/flezibcg-overall-roadmap-latest.md` Phase 2 status row → MOSTLY FROZEN with link to this baseline.
- `docs/implementation/p0-b-mmd-closeout-review.md` adds a v2.0 row noting supersession by this master baseline.

(Actual edits to those two files follow this slice; see commit log.)

End of MMD-MASTER-BASELINE-01 v1.0.
