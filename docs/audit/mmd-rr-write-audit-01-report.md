# MMD-RR-WRITE-AUDIT-01 — Resource Requirement FE Write Parity Audit

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-20 | v1.0 | PO-SA agent audit. No source code modified. |

---

## 1. Scope

Audit whether the Resource Requirement (RR) sub-domain of MMD has frontend write-intent + server-derived capability gating parity with the BOM, Reason Code, and BOM↔PV binding pattern set by `mmd-fullstack-13B/13C` and `mmd-fullstack-14B`.

---

## 2. Baseline Sources Read

| Document | Status |
|---|---|
| `docs/implementation/p0-b-mmd-closeout-review.md` | ✅ Read — §“P0-B Resource Requirement API (nested under routing operation)” lists POST/PATCH/DELETE endpoints |
| `docs/design/02_domain/product_definition/resource-requirement-mapping-contract.md` | ✅ Inspected — status `IMPLEMENTED_AND_CANONICAL_FOR_P0_B` |
| `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` | ✅ Read — pattern reference for capability guard |
| `docs/audit/mmd-fullstack-14b-bom-product-version-binding-capability-guard.md` | ✅ Read — pattern reference for FE side |
| `backend/app/api/v1/routings.py` | ✅ Inspected — lines 237–354 |
| `backend/app/schemas/operation.py`, `routing.py` | ✅ Inspected for RR schema shape |
| `frontend/src/app/pages/ResourceRequirements.tsx` | ✅ Inspected — 276 lines |
| `frontend/src/app/api/routingApi.ts` | ✅ Inspected — RR types live here |
| `backend/tests/test_resource_requirement_api.py`, `test_resource_requirement_service.py` | ✅ Listed; not re-run in this audit slice |

---

## 3. Findings

### 3.1 Backend RR API (present)

From `backend/app/api/v1/routings.py`:

| Method | Path | Auth | Line |
|---|---|---|---|
| GET (list) | `/routings/{routing_id}/operations/{operation_id}/resource-requirements` | `require_authenticated_identity` (inferred) | 237–253 |
| GET (one) | `/routings/{routing_id}/operations/{operation_id}/resource-requirements/{requirement_id}` | same | 255–276 |
| POST | `/routings/{routing_id}/operations/{operation_id}/resource-requirements` | `require_action("admin.master_data.resource_requirement.manage")` | 278–306 |
| PATCH | same path with `/{requirement_id}` | same action code | 308–338 |
| DELETE | same | same action code | 340–360 |

Action code `admin.master_data.resource_requirement.manage` is registered in `docs/design/02_registry/action-code-registry.md` (added 2026-05-02 by `MMD-BE-02`).

### 3.2 Backend RR response schema (gap)

`backend/app/schemas/operation.py` contains the comment `# Per-operation command capabilities derived from current backend guards` (line 55) — indicating intent to surface capabilities, but a grep for `capabilities` field on the RR response (`grep -nE "capabilit|ResourceRequirementResp" backend/app/schemas/*.py`) returns hits only for:

- `product.py` (PV / BOM / binding capabilities — present)
- `reason_code.py` (reason code capabilities — present)

It does **not** return a hit for a Resource-Requirement response schema embedding `capabilities`. Conclusion: **RR GET response does not embed a server-derived `capabilities` envelope.** The pattern set by BOM/Reason/Binding is not yet applied to RR.

### 3.3 Frontend RR page (gap)

`frontend/src/app/pages/ResourceRequirements.tsx` (276 lines):

- Imports: `HttpError, routingApi, ResourceRequirementItemFromAPI, RoutingItemFromAPI, RoutingOperationItemFromAPI` — no write API import, no capability type import.
- State: `reqs`, `loading`, `errorMessage` — no `submitting`, `actionError`, `capabilities` state.
- The grep `can_create|can_update|can_delete|allowed_actions|capabilities` returns **0 hits** in the file.
- Line 260 contains a literal `Edit` label — appears to be a placeholder text with no handler bound (consistent with the imports `Lock, Server` from `lucide-react` suggesting a locked button).

**FE is read-only and does not consume any capability field.** If a future agent enables RR write from FE without surfacing backend capability, the pattern from `mmd-bom-pv-binding-baseline-01-freeze-handoff.md` §15 rule 12 (“Do NOT infer authorization from lifecycle status alone in the frontend”) would be at risk of violation.

### 3.4 Test coverage (carry-forward from P0-B closeout)

P0-B closeout reports `test_resource_requirement_service.py` and `test_resource_requirement_api.py` passing. The audit did not re-run them; they are not regressed in scope of this audit. They cover RR API behaviors but do not assert a capability matrix (because backend does not return one).

---

## 4. Verdict

**OPEN — proceed to MMD-RR-FE-WRITE-01 (Slice 5).**

The gap is bilateral (BE response schema + FE consumption) and matches the BOM-binding pattern. Closing it before MMD-MASTER-BASELINE-01 freezes the foundation is preferable, because the master baseline should not bake in pattern asymmetry. If timing is tight, the alternative is to freeze MASTER-BASELINE-01 first and call out GAP-MMD-12 / GAP-MMD-14 as a known parity-debt item with explicit owning slice MMD-RR-FE-WRITE-01.

### 4.1 Verdict reasoning

| Criterion | Result |
|---|---|
| Is backend write API present and authorized? | ✅ Yes (action code + AND-auth on `routing` not currently required — RR uses single-action `resource_requirement.manage`) |
| Is FE expected to surface write intent for production use? | ✅ Yes — IE engineers govern RR mapping; without FE, only API users can mutate |
| Is the BOM-binding capability-guard pattern applicable? | ✅ Yes — RR is a write-governed master-data entity, same class as BOM/PV/Reason Code |
| Is there asymmetric risk if shipped without capability envelope? | ⚠️ Yes — if FE later adds buttons enabled by lifecycle status (DRAFT routing → enable), that violates the binding-freeze §15 rule 12 |
| Is the slice small enough to ship as one safe boundary? | ✅ Yes — add `capabilities` to RR response, add FE write intent + buttons (~150 LOC FE + 50 LOC BE) |

### 4.2 What MMD-RR-FE-WRITE-01 must include

Backend:
- Compute capabilities in a pure function: `can_create`, `can_update`, `can_delete` per RR row + page-level `can_create` for the operation.
- Capability conditions (recommended, to be confirmed in slice prompt):
  - `can_create`: routing.lifecycle_status = DRAFT AND caller has `resource_requirement.manage`
  - `can_update`: routing.lifecycle_status = DRAFT AND row is not soft-deleted (if soft delete exists) AND caller has the action
  - `can_delete`: same as `can_update`
- Wrap RR list response with `{ items: [...], capabilities: { can_create: bool, reason: str|null } }` per `mmd-fullstack-14B` shape.
- Per-row `allowed_actions: { can_update: bool, can_delete: bool }`.
- AND-semantics: confirm whether RR mutation should also require `routing.manage` (my opinion: **no** — single-action `resource_requirement.manage` is sufficient because RR is its own ADMIN action; differs from BOM-binding which mutates two domains).

Frontend:
- Consume `capabilities.can_create` for page-level Create button.
- Consume `allowed_actions.can_*` per row for Edit / Delete.
- No lifecycle-status inference (regression Section added to `mmd-read-integration-regression-check.mjs`).
- i18n keys for buttons (en + ja parity).

Tests:
- BE: capability matrix tests (one row per lifecycle × per perm combination).
- FE regression: new Section to assert RR buttons gated by capability, not lifecycle.

### 4.3 Out of scope for MMD-RR-FE-WRITE-01

- Plant/scope-specific RR applicability (deferred — MMD-SCOPE-APPLICABILITY-01).
- RR effective-dating (not in any current contract).
- Cross-domain side effects (RR must not touch execution, material, ERP).
- New action codes (use existing `admin.master_data.resource_requirement.manage`).
- Migration changes (RR schema already exists; capability is computed in service, not stored).

---

## 5. Stop Conditions Inherited from Parent Roadmap

(See `docs/roadmap/mmd-completion-roadmap-2026-05-20.md` Part 2 §2.3 — applied here.)

- If RR capability requires touching execution/material to compute → halt; capability must be computable from MMD-only context.
- If RR slice tries to relax the action-code authorization → halt.
- If FE buttons enable based on lifecycle status anywhere in the slice → halt.

---

## 6. Next Agent Prompt

> Implement **MMD-RR-FE-WRITE-01 — Resource Requirement FE Write Intent + Capability Guard**.
>
> **Read first (block on completion, ack each by name in first reply):**
> 1. `docs/audit/mmd-rr-write-audit-01-report.md` (this audit verdict)
> 2. `docs/audit/mmd-bom-pv-binding-baseline-01-freeze-handoff.md` (pattern reference)
> 3. `docs/audit/mmd-fullstack-14b-bom-product-version-binding-capability-guard.md` (pattern reference for FE)
> 4. `docs/audit/mmd-fullstack-13b-reason-code-server-derived-capability-guard.md` (pattern reference)
> 5. `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
>
> Then execute the spec in §4.2 above.
>
> Verification gates (paste exit codes — PASS claim without exit code will be rejected):
> ```powershell
> g:\Work\FleziBCG\.venv\Scripts\python.exe -m pytest -q tests/test_resource_requirement_api.py tests/test_resource_requirement_service.py tests/test_mmd_rbac_action_codes.py
> cd g:\Work\FleziBCG\frontend
> npm.cmd run check:mmd:read
> npm.cmd run build
> npm.cmd run lint
> npm.cmd run lint:i18n:registry
> npm.cmd run check:routes
> ```
>
> All must exit 0.
>
> Stop conditions: if backend response schema change breaks any existing FE consumer (other RR consumers), halt and bring back to PO-SA review.

---

## 7. Definition of Done (this audit slice)

- ✅ Verdict published: OPEN (proceed to MMD-RR-FE-WRITE-01).
- ✅ File-line evidence cited for each finding.
- ✅ Gap referenced from `mmd-current-state-report.md` v2.0 (GAP-MMD-12, GAP-MMD-14).
- ✅ Next-agent prompt drafted in §6.
- ✅ Stop conditions inherited and listed.

End of audit MMD-RR-WRITE-AUDIT-01 v1.0.
