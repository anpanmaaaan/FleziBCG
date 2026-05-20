# MMD-ROUTING-OP-WRITE-AUDIT-01 — Routing Operation Detail FE Write Parity Audit

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-20 | v1.0 | PO-SA agent audit. No source code modified. |

---

## 1. Scope

Audit whether the Routing Operation sub-domain of MMD has frontend write-intent + server-derived capability gating parity with the BOM, Reason Code, and BOM↔PV binding pattern.

---

## 2. Baseline Sources Read

| Document | Status |
|---|---|
| `docs/implementation/p0-b-mmd-closeout-review.md` | ✅ Read — confirms POST/PATCH/DELETE for routing operations are implemented |
| `docs/design/02_domain/product_definition/routing-foundation-contract.md` | ✅ Inspected |
| `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` | ✅ Read — pattern reference |
| `backend/app/api/v1/routings.py` | ✅ Inspected — lines 120, 145, 172 for operation routes |
| `backend/app/schemas/operation.py` | ✅ Inspected — capability comment present but no envelope field |
| `frontend/src/app/pages/RoutingOperationDetail.tsx` | ✅ Inspected — 222 lines |
| `frontend/src/app/api/routingApi.ts` | ✅ Inspected |

---

## 3. Findings

### 3.1 Backend Routing Operation API (present)

From `backend/app/api/v1/routings.py`:

| Method | Path | Auth (action) | Line |
|---|---|---|---|
| POST | `/routings/{routing_id}/operations` | `admin.master_data.routing.manage` (inferred from action code registry; confirm in slice) | 120 |
| PATCH | `/routings/{routing_id}/operations/{operation_id}` | same | 145 |
| DELETE | `/routings/{routing_id}/operations/{operation_id}` | same | 172 |

Operations are returned nested inside the routing GET response (`routingApi.getRouting()` returns `RoutingItemFromAPI` with `operations: RoutingOperationItemFromAPI[]`).

### 3.2 Backend Routing Operation response schema (gap)

`backend/app/schemas/operation.py` line 55 contains: `# Per-operation command capabilities derived from current backend guards`. The comment indicates an intent but the field is **not present** in the operation response schema exposed to the FE.

Grep on `backend/app/schemas/*.py` for `RoutingOperationCapabilities` or similar returns no matches. Conclusion: **routing operation responses do not embed `capabilities` or per-operation `allowed_actions`** — the same gap class as RR (GAP-MMD-14).

### 3.3 Frontend RoutingOperationDetail page (gap)

`frontend/src/app/pages/RoutingOperationDetail.tsx` (222 lines):

- Imports: `HttpError, routingApi, RoutingItemFromAPI` plus UI components — no write API client, no capability type import.
- The page calls `routingApi.getRouting(routeId)` then filters by `operationId` to find the operation inside the nested `operations[]` array.
- The grep `can_create|can_update|can_delete|capabilities|allowed_actions` returns **0 hits**.
- The page has no Edit / Delete / Add buttons rendered — `Lock` icon is imported, suggesting any future write action is shown as disabled.

**FE is read-only. No capability consumption. Same gap class as RR.**

### 3.4 Linked-from question (v1.0 GAP-MMD-08 follow-up)

v1.0 GAP-MMD-08 said RouteDetail did not link operation rows to RoutingOperationDetail. The audit did **not** re-verify in this slice (would require reading `RouteDetail.tsx`). Conservative carry-forward: assume the gap is open until MMD-FE-QA-03 visual QA confirms — added as a check item to the visual QA preparation pack.

### 3.5 Rich-fields question (v1.0 GAP-MMD-09 follow-up)

v1.0 listed `setup_time`, `run_time_per_unit`, `work_center`, `required_skill`, `required_skill_level`, `qc_checkpoint_count` as missing from `RoutingOperationItemFromAPI`. Audit confirms the page only displays `operation_code`, `operation_name`, `sequence_no`, `standard_cycle_time`, `required_resource_type` (per the read-only render code). The page does not attempt to render the v1.0-listed missing fields, so either:

- the fields are still missing from BE (consistent with no migration adding them since 0014), or
- they exist on BE but FE has not been updated to render them.

This is a **second sub-gap** under GAP-MMD-11: rich-field surfacing. Resolution belongs to MMD-ROUTING-OP-FE-WRITE-01 (because the write intent will need these fields editable anyway).

---

## 4. Verdict

**OPEN — proceed to MMD-ROUTING-OP-FE-WRITE-01 (Slice 7).**

Two-sided gap, identical pattern class to RR. Recommendation: schedule Slice 5 (RR) and Slice 7 (Routing Op) as **paired slices, but separate PRs** so each remains testable in isolation. They share the same template (`mmd-fullstack-14B` pattern), differ in entity / action code / lifecycle precondition.

### 4.1 Verdict reasoning

| Criterion | Result |
|---|---|
| Backend write API present and authorized? | ✅ Yes (POST/PATCH/DELETE under routing, action code `routing.manage`) |
| FE expected to surface write intent for production use? | ✅ Yes — IE engineers maintain routing/operation definitions |
| BOM-binding capability-guard pattern applicable? | ✅ Yes |
| Asymmetric risk if shipped without capability envelope? | ⚠️ Yes — same risk as RR |
| Slice small enough to ship as one safe boundary? | ✅ Yes — Routing operation is a child of routing; capability is computed from routing lifecycle + caller perm |

### 4.2 What MMD-ROUTING-OP-FE-WRITE-01 must include

Backend:
- Compute per-operation capabilities in a pure function: `can_update`, `can_delete` per row; page-level `can_create` for the routing.
- Capability conditions (recommended, confirm in slice prompt):
  - `can_create` (operation under routing): routing.lifecycle_status = DRAFT AND caller has `routing.manage`
  - `can_update`: same condition + operation must exist (not soft-deleted)
  - `can_delete`: same as `can_update`
- Decide where capabilities surface:
  - **Option A**: extend `RoutingItem` to include `operation_capabilities` envelope + per-row `allowed_actions` on each operation.
  - **Option B**: new endpoint `GET /routings/{rid}/operations/{opid}` returning operation + capabilities wrapper.
  - **My opinion**: Option A — cheaper, fewer endpoints, no extra round-trip; FE already loads full routing.
- AND-semantics: confirm whether operation mutation should also require any non-routing action. Recommendation: **no** — single-action `routing.manage`. Operation is a child of routing; routing.manage is sufficient ADMIN-family authorization.

Frontend:
- Render Edit / Delete buttons on RoutingOperationDetail gated by per-operation `allowed_actions`.
- Render Add Operation button on RouteDetail gated by `operation_capabilities.can_create`.
- Wire RouteDetail row click → RoutingOperationDetail (closes v1.0 GAP-MMD-08 if still open).
- Surface the v1.0 GAP-MMD-09 rich fields if backend already exposes them; otherwise file a separate `MMD-BE-OP-FIELDS-01` (out of scope for this slice).
- No lifecycle-status inference.

Tests:
- BE: capability matrix tests across routing lifecycle × per-operation existence × per-permission combination.
- FE regression: new Section in `mmd-read-integration-regression-check.mjs` asserting RoutingOperation buttons gated by capability, not lifecycle.

### 4.3 Out of scope for MMD-ROUTING-OP-FE-WRITE-01

- Routing header-level write intent — that is GAP-MMD-13 (Routing FE Save/Edit/Release/Retire), separate slice.
- Adding new fields to the operation schema (rich fields belong to its own BE slice if missing).
- Reordering operations / sequence_no reorganization UX — that is its own UX slice (deferred).
- Per-operation QC checkpoint linkage UX (belongs to Quality domain integration).
- Cross-domain consequences — no execution/material/ERP behavior triggered by operation mutation.

---

## 5. Stop Conditions Inherited from Parent Roadmap

- If operation capability requires touching execution/material to compute → halt.
- If operation mutation tries to relax `routing.manage` requirement → halt.
- If FE buttons enable based on lifecycle status anywhere in the slice → halt.

---

## 6. Next Agent Prompt

> Implement **MMD-ROUTING-OP-FE-WRITE-01 — Routing Operation FE Write Intent + Capability Guard**.
>
> **Read first (block on completion, ack each by name in first reply):**
> 1. `docs/audit/mmd-routing-op-write-audit-01-report.md` (this audit verdict)
> 2. `docs/audit/mmd-rr-write-audit-01-report.md` (sibling audit; same pattern)
> 3. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (pattern reference)
> 4. `docs/audit/mmd-fullstack-14b-bom-product-version-binding-capability-guard.md`
> 5. `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
>
> Then execute the spec in §4.2 above.
>
> Verification gates (paste exit codes — PASS claim without exit code will be rejected):
> ```powershell
> g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_routing_foundation_api.py tests/test_routing_foundation_service.py tests/test_mmd_rbac_action_codes.py
> cd g:\Work\FleziBCG\frontend
> npm.cmd run check:mmd:read
> npm.cmd run build
> npm.cmd run lint
> npm.cmd run lint:i18n:registry
> npm.cmd run check:routes
> ```
>
> All must exit 0.

---

## 7. Definition of Done (this audit slice)

- ✅ Verdict published: OPEN.
- ✅ File-line evidence cited for each finding.
- ✅ GAP-MMD-11 / GAP-MMD-14 referenced from `mmd-current-state-report.md` v2.0.
- ✅ Next-agent prompt drafted in §6.
- ✅ Stop conditions inherited and listed.
- ✅ Sub-gap (rich fields, v1.0 GAP-MMD-09) noted and routed.

End of audit MMD-ROUTING-OP-WRITE-AUDIT-01 v1.0.
