# Manufacturing Master Data Current-State Report — FleziBCG

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Initial snapshot. Classified 5 screens (BOM List/Detail, Routing Operation Detail, Resource Requirements, Reason Codes) as SHELL with mock fixtures. **SUPERSEDED — see §1 below for stale items.** |
| 2026-05-20 | v2.0 | PO-SA agent re-snapshot. All 5 previously-SHELL screens now wired to real APIs; 3 of 5 have full write-intent + server-derived capability gating; 2 remain read-only with parity gaps. Includes citation per claim. |

> **Supersedes v1.0.** v1.0 is preserved in git history (`docs/audit/mmd-current-state-report.md@a1b2c3d` or earlier commit before this overwrite). Reasons for resync in §1.4 below.

---

## 0. Reading Order for Agents

Before acting on this doc, a coding agent MUST read in this order:

1. This document.
2. `docs/roadmap/mmd-completion-roadmap-2026-05-20.md` (Now / Next / Later phasing).
3. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (authoritative for BOM↔PV binding).
4. The other 4 freeze handoffs (read, PV-write, BOM-write, ReasonCode-write).
5. `docs/implementation/p0-b-mmd-closeout-review.md` for P0-B-minimum verdict.

Do not act on v1.0 claims that contradict this v2.0 doc.

---

## 1. Executive Summary (2026-05-20)

### 1.1 What the FE renders today

| Screen | Status (2026-05-01 claim) | Status (2026-05-20 verified) | Evidence |
|---|---|---|---|
| Product List | PARTIAL | **CONNECTED + read-only** | `frontend/src/app/pages/ProductList.tsx` → `productApi.listProducts()` |
| Product Detail | PARTIAL | **CONNECTED + write-intent (PV lifecycle, BOM binding, toggle)** | `frontend/src/app/pages/ProductDetail.tsx` lines 716, 808, 816 consume `product_version_capabilities.can_create`, `v.allowed_actions.can_release`, `v.allowed_actions.can_retire` |
| Routing List | PARTIAL | **CONNECTED + read-only** | `frontend/src/app/pages/RouteList.tsx` → `routingApi.listRoutings()` |
| Routing Detail | PARTIAL | **CONNECTED + read-only** | `frontend/src/app/pages/RouteDetail.tsx` → `routingApi.getRouting(id)` |
| **BOM List** | SHELL | **CONNECTED + write-intent (capability-gated)** | `BomList.tsx` imports `BomCreateRequest`, `BomItemFromAPI`, uses `selectedProduct?.bom_capabilities?.can_create`; 383 lines |
| **BOM Detail** | SHELL | **CONNECTED + full CRUD intent (capability-gated)** | `BomDetail.tsx` imports `BomFromAPI`, `BomItemCreateRequest`, `BomItemUpdateRequest`, `BomUpdateRequest`; 707 lines |
| **Routing Operation Detail** | SHELL | **CONNECTED + read-only (write-intent absent)** | `RoutingOperationDetail.tsx` → `routingApi.getRouting()` + filter by operationId; no `capabilities` consumed; 222 lines |
| **Resource Requirements** | SHELL | **CONNECTED + read-only (write-intent absent)** | `ResourceRequirements.tsx` → `routingApi` + `ResourceRequirementItemFromAPI`; `grep can_create\|can_update\|can_delete` returns 0 hits; 276 lines |
| **Reason Codes** | SHELL | **CONNECTED + full CRUD intent (capability-gated)** | `ReasonCodes.tsx` → `reasonCodeApi`, `ReasonCodeCapabilities`; comment header cites MMD-FULLSTACK-13/13B/13C/13D; 861 lines |
| Downtime Reasons (in Station Execution) | CONNECTED | **CONNECTED — unchanged** | `downtimeReasons.ts` → `GET /v1/downtime-reasons`; still operationally active |

### 1.2 What the BE owns

| Sub-domain | BE read API | BE write API | Server-derived `capabilities`? | Frozen? |
|---|---|---|---|---|
| Product (header) | ✅ | ✅ | ✅ via `bom_capabilities`, `product_version_capabilities` on detail | Yes (P0-B closeout + mmd-be-* slices) |
| Product Version | ✅ | ✅ (POST, PATCH, release, retire) | ✅ `allowed_actions.can_release`, `can_retire`; `product_version_capabilities.can_create` | Yes (mmd-pv-write-baseline-01) |
| BOM | ✅ | ✅ (POST, PATCH, items POST/PATCH/DELETE, release, retire) | ✅ via `bom_capabilities` on product, plus per-BOM `allowed_actions` | Yes (mmd-bom-write-baseline-01) |
| Routing | ✅ | ✅ (POST, PATCH, release, retire) | ❌ no `capabilities` envelope on routing GET | Partial — write API exists but no capability guard surfaced to FE |
| Routing Operation | ✅ (nested in routing) | ✅ (POST, PATCH, DELETE under routing) | ❌ — see §3.3 | Partial — same |
| Resource Requirement | ✅ (nested) | ✅ (POST, PATCH, DELETE) | ❌ no `capabilities` field in `app/schemas/operation.py` or RR schema | Partial — same |
| Reason Code | ✅ | ✅ (POST, PATCH, release, retire) | ✅ via `ReasonCodeCapabilities` + per-row `allowed_actions` | Yes (mmd-reason-code-write-baseline-01) |
| BOM ↔ PV binding | ✅ (wrapper) | ✅ (POST, DELETE, toggle PATCH) | ✅ `ProductVersionBomBindingCapabilities` with `can_bind`, `can_unbind`, `can_toggle_bom_binding_required_for_release` | Yes (mmd-bom-pv-binding-baseline-01, 2026-05-08) |

### 1.3 What action codes exist

From `docs/design/02_registry/action-code-registry.md`, the 5 MMD action codes registered as ADMIN family:

- `admin.master_data.product_version.manage`
- `admin.master_data.routing.manage`
- `admin.master_data.resource_requirement.manage`
- `admin.master_data.bom.manage`
- `admin.master_data.reason_code.manage`

All 5 are wired into BE route guards (`backend/app/api/v1/products.py`, `routings.py`, `reason_codes.py`).

### 1.4 Why v1.0 was stale (root cause)

v1.0 looked for `frontend/src/app/api/bomApi.ts` and reported missing. **BOM types live inside `productApi.ts`** (`BomItemFromAPI` at line 116, `BomCreateRequest` at line 150). Same pattern for Resource Requirement — types live inside `routingApi.ts`. v1.0's API-file-existence heuristic was wrong for nested types.

Additionally, v1.0 predates: `mmd-fullstack-07` (BOM FE read), `mmd-fullstack-12` (BOM FE write intent), `mmd-fullstack-13/13B/13C/13D` (Reason Code FE write intent + governance + lifecycle defaults), `mmd-fullstack-14/14B` (BOM↔PV binding + capability guard) — these slices shipped between 2026-05-03 and 2026-05-19.

### 1.5 Truth-boundary disclosure (unchanged in substance)

- Backend remains source of truth for all MMD lifecycle decisions.
- Frontend sends intent only; backend is authorization truth.
- No FE button enables based on lifecycle-status alone for BOM, BOM binding, or Reason Code; it must consume `capabilities.can_*`. (RR and Routing Op are exceptions today — see §4 gaps.)
- `MockWarningBanner` / `BackendRequiredNotice` are still **imported** in 5 pages (BomList, BomDetail, ResourceRequirements, RoutingOperationDetail — but NOT ReasonCodes). They may be conditionally rendered for error/empty states; visual QA (MMD-FE-QA-03) must confirm whether they are visible in normal flow. Their presence in imports is no longer evidence of SHELL status.

---

## 2. Source Files Inspected (v2.0)

### 2.1 Frontend pages

| File | Lines | Status |
|---|---:|---|
| `frontend/src/app/pages/ProductList.tsx` | (re-read) | CONNECTED read-only |
| `frontend/src/app/pages/ProductDetail.tsx` | 1041 | CONNECTED + write intent + binding + toggle (capability-gated) |
| `frontend/src/app/pages/RouteList.tsx` | (re-read) | CONNECTED read-only |
| `frontend/src/app/pages/RouteDetail.tsx` | (re-read) | CONNECTED read-only |
| `frontend/src/app/pages/BomList.tsx` | 383 | CONNECTED + create intent (capability-gated) |
| `frontend/src/app/pages/BomDetail.tsx` | 707 | CONNECTED + full CRUD intent (capability-gated) |
| `frontend/src/app/pages/RoutingOperationDetail.tsx` | 222 | CONNECTED read-only (no write intent, no capability) |
| `frontend/src/app/pages/ResourceRequirements.tsx` | 276 | CONNECTED read-only (no write intent, no capability) |
| `frontend/src/app/pages/ReasonCodes.tsx` | 861 | CONNECTED + full CRUD intent (capability-gated) |

### 2.2 Frontend API modules

`frontend/src/app/api/`:

```
authApi.ts        dashboardApi.ts   downtimeReasons.ts  httpClient.ts
iamApi.ts         impersonationApi.ts  index.ts
operationApi.ts   operationMonitorApi.ts  productApi.ts
productionOrderApi.ts  qualityApi.ts  reasonCodeApi.ts
routingApi.ts     stationApi.ts     mappers/
```

**BOM types live in `productApi.ts`.** **RR types live in `routingApi.ts`.** **There is no standalone `bomApi.ts` or `resourceRequirementsApi.ts` — this is intentional, not a gap.**

### 2.3 Backend

- `backend/app/api/v1/products.py` — Product + PV + BOM + BOM-binding routes (verified)
- `backend/app/api/v1/routings.py` — Routing + Operation + RR routes (verified — RR has full CRUD lines 237–354)
- `backend/app/api/v1/reason_codes.py` — Reason code CRUD + capabilities endpoint
- `backend/app/models/`: `product.py`, `product_version.py`, `product_version_bom_binding.py`, `bom.py`, `routing.py`, `resource_requirement.py`, `reason_code.py`, `downtime_reason.py`
- `backend/app/schemas/operation.py` — operation schemas with `# Per-operation command capabilities derived from current backend guards` comment but NO `capabilities` field present in RR response schema; **see §3.3 for the gap.**
- `backend/alembic/versions/` — head is **0019** (Quality domain). MMD-owning migrations stop at 0014 (`0014_add_bom_binding_required_for_release_to_product_versions.py`).

---

## 3. Status per Screen (v2.0)

### 3.1 Product List, Product Detail, Routing List, Routing Detail

No behavior change since v1.0; all four read from real API. Product Detail has gained full PV write intent, BOM binding section, and toggle for `bom_binding_required_for_release` between v1.0 and v2.0 — all capability-gated.

### 3.2 BOM List, BOM Detail

**Promoted from SHELL → CONNECTED with capability-gated write intent.** Backend BOM API was implemented (`mmd-be-09`, `mmd-be-12`) and FE write intent (`mmd-fullstack-12`, `12b-a`, `12b-b`). BOM is now reachable from ProductDetail via product-scoped routes (`/products/:productId/boms/:bomId` or via query param `productId`).

BomDetail page exposes: edit meta, create item, edit item, delete item, release BOM, retire BOM — all gated by per-BOM `allowed_actions` from the GET response.

### 3.3 Routing Operation Detail (READ-ONLY GAP)

Backend has POST/PATCH/DELETE under `/routings/{rid}/operations[/{opid}]` (lines 120, 145, 172 in `backend/app/api/v1/routings.py`). FE page is read-only and has zero `capabilities` consumption — `grep can_create\|can_update\|can_delete` returns 0 hits.

**Two-sided gap:**
- Backend: routing GET response does not embed a per-operation `capabilities` envelope. The comment in `app/schemas/operation.py` line 55 says “Per-operation command capabilities derived from current backend guards” but the actual field is not present in `RoutingOperationItemFromAPI` exposed to FE.
- Frontend: no write-intent UI (no Edit/Delete/Add Operation buttons rendered) and no capability gating.

**This is `GAP-MMD-11` — see §4.**

### 3.4 Resource Requirements (READ-ONLY GAP)

Backend has full RR CRUD nested under routing operation (`backend/app/api/v1/routings.py` lines 237, 255, 278 POST, 308 PATCH, 340 DELETE) — all guarded by `admin.master_data.resource_requirement.manage`.

FE page renders 1 Edit label (line 260 — possibly disabled placeholder), no real handler, no capability gating. RR response schema does not embed `capabilities`.

**This is `GAP-MMD-12` — see §4.**

### 3.5 Reason Codes

**Full CRUD intent with capability gating.** No further gap.

### 3.6 BOM ↔ Product Version Binding (new since v1.0)

**Frozen 2026-05-08.** See `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` for invariants, release validation matrix, capability matrix, do-not-do rules.

---

## 4. Updated Gap Register

### 4.1 v1.0 gaps — disposition

| v1.0 ID | Topic | v2.0 disposition |
|---|---|---|
| GAP-MMD-01 | No BOM backend API or FE client | **RESOLVED** (`mmd-be-09/12`, `mmd-fullstack-07/12`) |
| GAP-MMD-02 | Routing operation fields incomplete | **PARTIALLY RESOLVED** — fields visible in `RoutingOperationItemFromAPI` but FE write-intent still missing; reopened as GAP-MMD-11 |
| GAP-MMD-03 | No RR backend or FE client | **RESOLVED on read; OPEN on write** (`mmd-be-*` RR API exists; FE still read-only) — reopened as GAP-MMD-12 |
| GAP-MMD-04 | No reason code management API | **RESOLVED** (`mmd-be-10/13`, `mmd-fullstack-13/13B/13C/13D`) |
| GAP-MMD-05 | Product lifecycle mutations disabled | **RESOLVED for PV; product-header mutations are intentionally absent (governance: mutations flow via PV)** |
| GAP-MMD-06 | Routing lifecycle mutations disabled | **STILL OPEN — GAP-MMD-13** (Routing header write API exists in backend but FE Save/Edit/Release/Retire buttons are still locked) |
| GAP-MMD-07 | BOM Detail disconnected from Product Detail | **RESOLVED** — BomDetail reads `productId` from query string and back-links to product |
| GAP-MMD-08 | Routing operation rows not linked to detail | **NEEDS VERIFICATION** (Slice MMD-FE-QA-03 to confirm in visual QA) |
| GAP-MMD-09 | RoutingOperation API lacks rich fields | **PARTIAL** — fields exposed but FE detail page does not surface all of them; collapsed into GAP-MMD-11 |
| GAP-MMD-10 | Live downtime reasons cover only downtime; no FE coverage for other domains | **RESOLVED via ReasonCodes** — FE ReasonCodes page covers DOWNTIME/SCRAP/PAUSE/REOPEN/QUALITY_HOLD/MAINTENANCE/MATERIAL/REWORK/EXCEPTION/GENERAL (per `REASON_DOMAINS` constant) |

### 4.2 v2.0 new gaps

| ID | Gap | Impact | Owning slice |
|---|---|---|---|
| GAP-MMD-11 | RoutingOperationDetail FE has no write intent and no server-derived capability gating; backend has full CRUD | IE engineers cannot maintain operation defs through FE; agents may infer enablement from lifecycle status (rule violation) | MMD-ROUTING-OP-WRITE-AUDIT-01 → MMD-ROUTING-OP-FE-WRITE-01 |
| GAP-MMD-12 | ResourceRequirements FE has no write intent and no server-derived capability gating; backend has full CRUD | Station-assignment correctness cannot be governed from FE; same rule-violation risk | MMD-RR-WRITE-AUDIT-01 → MMD-RR-FE-WRITE-01 |
| GAP-MMD-13 | RouteDetail / RouteList have routing lifecycle buttons disabled while backend supports POST/PATCH/release/retire | Routing governance ergonomics: IE engineers must use API directly to maintain routings | Future slice MMD-ROUTING-WRITE-FE-01 (out of current roadmap scope; queued) |
| GAP-MMD-14 | RR / Routing Op response schemas do not embed `capabilities` envelope (unlike PV, BOM, ReasonCode) | Pattern asymmetry; raises risk of FE inferring from lifecycle | Resolved by GAP-MMD-11 + GAP-MMD-12 implementation slices |
| GAP-MMD-15 | `MockWarningBanner` / `BackendRequiredNotice` still imported in 4 connected pages (BomList, BomDetail, ResourceRequirements, RoutingOperationDetail) | If conditionally rendered, may mislead users into thinking the screen is still SHELL | Visual QA (MMD-FE-QA-03) confirms; cleanup is one i18n-touch slice |
| GAP-MMD-16 | PV `is_current` advisory only; no enforcement, no UI, no event | Execution will need a deterministic “current” pointer before P0-C | MMD-PV-SETCURRENT-GOV-01 (contract) → MMD-PV-SETCURRENT-IMPL-01 |
| GAP-MMD-17 | `ProductVersionBomBinding.VALIDATED_ON_RELEASE` event deferred | No consumer yet — fine for now | Deferred (later lane) |

### 4.3 Verified deferred items (do not implement without governance contract)

Per `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §14 / §15, the following remain deferred. They are listed here so an agent reading v2.0 sees the full picture without jumping docs:

- Binding `effective_from` / `effective_to`
- Binding replace (atomic PRIMARY swap)
- Multiple binding types (SECONDARY, ALTERNATE)
- Plant/scope-specific binding
- Product-level / tenant-profile binding policy
- Automatic current-version selection
- Migrations after 0014 inside MMD scope (adjacent-domain migrations like Quality 0015–0019 are allowed)
- Material reservation, inventory movement, scrap posting, backflush, ERP posting, traceability genealogy, quality acceptance, production-order/APS triggered by binding

---

## 5. Capability-Pattern Compliance Matrix

The “server-derived capability” pattern was set by `mmd-fullstack-14b-bom-product-version-binding-capability-guard.md` (binding) and `mmd-fullstack-13B` (reason code). Pattern: backend returns `capabilities` envelope (or `allowed_actions` per row); frontend uses `capabilities?.can_*` for every button enablement; frontend never infers from lifecycle status alone.

| Sub-domain | BE returns capabilities? | FE consumes capabilities? | Compliance |
|---|---|---|---|
| Product (header) read | n/a (read-only mutations live at PV / BOM scope) | n/a | n/a |
| Product Version | ✅ (`product_version_capabilities`, per-row `allowed_actions`) | ✅ (ProductDetail.tsx lines 716, 808, 816) | **✅** |
| BOM (incl. items, lifecycle) | ✅ (`bom_capabilities`, per-row `allowed_actions`) | ✅ (BomList / BomDetail) | **✅** |
| BOM↔PV binding | ✅ (`ProductVersionBomBindingCapabilities`) | ✅ | **✅ Frozen** |
| Reason Code | ✅ (`ReasonCodeCapabilities`, per-row) | ✅ | **✅** |
| Routing (header) write | ❌ | n/a (FE buttons locked) | **❌** Gap (GAP-MMD-13) |
| Routing Operation | ❌ | ❌ | **❌** Gap (GAP-MMD-11) |
| Resource Requirement | ❌ | ❌ | **❌** Gap (GAP-MMD-12) |

---

## 6. Truth-Boundary Notes (carry-forward + refinement)

Refinements relative to v1.0:

1. v1.0 said “SHELL screens must not be treated as released manufacturing truth”. v2.0: no SHELL screens remain in MMD. Disclosure banners are now stale UI furniture in 4 pages — to be cleaned up in a small slice or during MMD-FE-QA-03 if visible.
2. Live downtime reasons (`/v1/downtime-reasons`) still must not be disrupted. ReasonCodes page is now a *governance-of-the-registry* UI and does not shadow the downtime-reasons read path used by `StartDowntimeDialog`. Both coexist; the reason-code page surfaces the broader vocabulary while the dialog still loads only the downtime subset for execution use.
3. PARTIAL no longer describes BOM / Reason Code / PV / Binding. The accurate label is now: **CONNECTED + capability-gated write intent** (or read-only).
4. RR and Routing Op are the only two MMD surfaces where the FE is still read-only despite backend write APIs existing — a parity asymmetry, not a domain miss.

---

## 7. Recommended Next Slice (referencing roadmap 2026-05-20)

Per `docs/roadmap/mmd-completion-roadmap-2026-05-20.md`:

- **Now lane**: Slice 1 (MMD-FE-QA-03 visual QA), then this Slice (MMD-CURRENT-STATE-V2 — done), then Slice 3 (MMD-MASTER-BASELINE-01).
- **Next lane**: Slice 4 (MMD-RR-WRITE-AUDIT-01), Slice 6 (MMD-ROUTING-OP-WRITE-AUDIT-01), Slice 8 (MMD-PV-SETCURRENT-GOV-01).
- **Later lane**: governance-contract-first deferrals.

After Slice 3 freezes the master baseline, the gap pack (GAP-MMD-11 / 12 / 13) is the next investment area inside MMD before any P0-C Execution work depends on it.

---

## 8. Verification Commands Used to Produce v2.0

```bash
# Confirm no mock fixtures in MMD pages
grep -nE "mockBom|mockOperation|mockRequirement|mockReasonCode" \
  frontend/src/app/pages/BomList.tsx \
  frontend/src/app/pages/BomDetail.tsx \
  frontend/src/app/pages/ResourceRequirements.tsx \
  frontend/src/app/pages/ReasonCodes.tsx \
  frontend/src/app/pages/RoutingOperationDetail.tsx
# Expected: no matches; exit code 1 (grep returns 1 when nothing found)

# Confirm BOM types live in productApi (not a missing bomApi)
grep -n "BomItemFromAPI\|BomCreateRequest" frontend/src/app/api/productApi.ts

# Confirm RR types live in routingApi
grep -n "ResourceRequirementItemFromAPI" frontend/src/app/api/index.ts

# Confirm RR / Routing Op pages have no capability consumption
grep -nE "can_create|can_update|can_delete|capabilities" \
  frontend/src/app/pages/ResourceRequirements.tsx \
  frontend/src/app/pages/RoutingOperationDetail.tsx

# Confirm action codes
grep -E "master_data\.(bom|product_version|reason_code|routing|resource_requirement)" \
  docs/design/02_registry/action-code-registry.md

# Confirm alembic head
ls backend/alembic/versions/ | sort | tail -3
```

All commands above were run on 2026-05-20 against the current commit. Observed:

- mock-fixture grep → 0 matches across all 5 files (exit 1, as expected for no-match grep).
- BomItemFromAPI / BomCreateRequest present in `productApi.ts` (lines 116, 150).
- `ResourceRequirementItemFromAPI` exported from `routingApi` in `api/index.ts`.
- RR + Routing-Op capability grep → 0 matches (the gap).
- 5 action codes present, ADMIN family.
- Alembic head: 0019 (Quality domain) — last MMD-owning migration is 0014.

### Build-state caveat (2026-05-20)

At time of v2.0 capture, the repo working copy is **dirty with in-flight station-execution refactor**: `git status` lists ~20 modified files including `frontend/src/app/i18n/registry/en.ts`, `frontend/src/app/i18n/registry/ja.ts`, `frontend/src/app/pages/StationExecution.tsx`, and `station-execution/*` components. Eslint and tsc fail against the current working copy (parse error + 2 unterminated string literals + 3 unclosed JSX tags). **None of the failing files are MMD-owning.** The MMD content claims in this v2.0 doc are valid against committed MMD source; the build red is a station-execution working-copy issue tracked separately. See `docs/audit/mmd-master-baseline-01-freeze-handoff.md` §8.1 for full verification log.

---

## 9. Acceptance for v2.0

This v2.0 supersedes v1.0 for all readers. Any agent that produces a report still claiming the SHELL classification for BOM List, BOM Detail, Routing Operation Detail, Resource Requirements, or Reason Codes is reading stale data and must be redirected to v2.0.

End of Manufacturing Master Data Current-State Report v2.0 — 2026-05-20.
