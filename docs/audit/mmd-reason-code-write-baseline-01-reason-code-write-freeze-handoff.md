# MMD-REASON-CODE-WRITE-BASELINE-01 — Reason Code Write Baseline Freeze / Handoff

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-06 | v1.0 | Frozen Reason Code write baseline after backend write API, boundary audit, frontend write intent, server-derived allowed actions, and page-level create capability. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Full-Stack Baseline Freeze + Authorization/Capability Projection Review + Hard Mode MOM v3
- **Hard Mode MOM:** v3 ON
- **Reason:** This report freezes Reason Code write behavior, authorization capability projection, lifecycle state machine, and boundary guardrails before any future expansion of Reason Code write paths (downtime mapping, policy binding, activate/deactivate, bulk import, or operational runtime usage). Hard Mode v3 is mandatory per `.github/copilot-instructions.md` for work touching authorization, capability projection, and MMD boundary guardrails.

---

## 1. Scope

**Task:** MMD-REASON-CODE-WRITE-BASELINE-01 — documentation-only baseline freeze.

**Covers slices:**
- MMD-BE-10 — Reason Code Write Governance / Minimal Mutation Contract
- MMD-BE-10A — Reason Code Action Code Registry Patch
- MMD-BE-13 — Reason Code Write API Foundation
- MMD-BE-13A — Reason Code Write Boundary Audit / Event Guardrail Patch
- MMD-FULLSTACK-13 — Reason Code FE Write Intent / Governance-Gated Integration
- MMD-FULLSTACK-13B — Reason Code Server-Derived Write Capability Guard
- MMD-FULLSTACK-13C — Reason Code Page-Level Create Capability / Empty List Guard

**What this report answers:**
- Which Reason Code write commands are implemented?
- Which write commands are permanently forbidden or deferred?
- Which backend routes exist and what protects them?
- Which frontend controls exist and what gates them?
- Which action code protects mutation endpoints?
- Which capability fields govern FE enabled state?
- Which lifecycle transitions are supported?
- Which audit/event behavior exists?
- Which regression tests guard the baseline?
- Which gaps remain open?
- What is the next safe expansion slice?

**Not covered (out of scope):**
- Downtime write path, execution state machine, quality hold, material/inventory
- Product Version / BOM write baselines (frozen separately in their own freeze reports)
- ISA-88 / recipe / formula / procedure
- Scope applicability / plant-area-line binding
- ERP integration

---

## 2. Baseline Inputs Reviewed

| Document | Status | Key Finding |
|---|---|---|
| `docs/audit/mmd-be-10-reason-code-write-governance-contract.md` | ✅ Inspected | Governance contract established; all commands classified; lifecycle transitions defined; action code proposed |
| `docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md` | ✅ Inspected | `admin.master_data.reason_code.manage` added to `rbac.py` and `action-code-registry.md`; RBAC marker test added |
| `docs/audit/mmd-be-13-reason-code-write-api-foundation.md` | ✅ Inspected | 4 write endpoints implemented; create/update/release/retire services; security events emitted; all forbidden commands excluded |
| `docs/audit/mmd-be-13a-reason-code-write-boundary-guardrail.md` | ✅ Inspected | Boundary audit complete; no FK coupling to downtime_reasons; `extra="forbid"` on all write schemas; forbidden payloads rejected at Pydantic layer |
| `docs/audit/mmd-fullstack-13-reason-code-fe-write-intent.md` | ✅ Inspected | FE write intent wired; action buttons added; governance messages added to i18n; frontend sends intent only |
| `docs/audit/mmd-fullstack-13b-reason-code-server-derived-capability-guard.md` | ✅ Inspected | `allowed_actions` block added to every read response; `_compute_allowed_actions()` pure function; row-level button gating complete |
| `docs/audit/mmd-fullstack-13c-reason-code-page-level-create-capability.md` | ✅ Inspected | `GET /reason-codes/capabilities` endpoint added; empty-list Create gap closed; `rcCapabilities.can_create` gates Create button |
| `docs/audit/mmd-write-gov-01-command-boundary.md` | ✅ Inspected | Write-path governance matrix established for all MMD entities; Reason Code all DEFERRED_REQUIRES_CONTRACT before this series |
| `docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md` | ✅ Inspected | Complete MMD read baseline frozen (16 slices); Reason Code read confirmed (MMD-BE-07 + MMD-FULLSTACK-08); 84 checks passing at read baseline |

### Design Documents Reviewed

| Document | Status | Key Finding |
|---|---|---|
| `docs/design/02_domain/product_definition/reason-code-write-governance-contract.md` | ✅ Inspected | Governance contract source; 4 supported commands; forbidden list; lifecycle rules; action code requirement |
| `docs/design/02_domain/product_definition/reason-code-foundation-contract.md` | ✅ Inspected | Entity shape: 14 fields; DRAFT/RELEASED/RETIRED lifecycle; no downtime_reason FK; write-path deferred at time of authoring |
| `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` | ✅ Inspected | Matrix confirms all 4 write commands now IMPLEMENTED; forbidden commands remain FORBID/DEFER |
| `docs/design/02_registry/action-code-registry.md` | ✅ Inspected | `admin.master_data.reason_code.manage: ADMIN` present at line 73 |
| `docs/design/00_platform/product-business-truth-overview.md` | ✅ Referenced | MMD is definition truth, not ERP truth; no inventory/ERP coupling for Reason Codes |

---

## 3. Source Inspection Summary

### Backend Source (confirmed current state)

| File | Status | Key Finding |
|---|---|---|
| `backend/app/api/v1/reason_codes.py` | ✅ Inspected | 7 routes: 3 read + 4 write; `/capabilities` registered before `/{id}` (route ordering correct); all write routes use `require_action("admin.master_data.reason_code.manage")` |
| `backend/app/schemas/reason_code.py` | ✅ Inspected | `ReasonCodeCapabilities` (can_create, reason); `ReasonCodeAllowedActions` (4 bool fields); `ReasonCodeItem` with `allowed_actions`; create/update schemas both `extra="forbid"` |
| `backend/app/services/reason_code_service.py` | ✅ Inspected | `_compute_allowed_actions()` pure function; `_to_item()` with `has_manage` param; all 4 mutation services emit security events; `lifecycle_status` never accepted from caller |
| `backend/app/repositories/reason_code_repository.py` | ✅ Referenced | CRUD operations; default filter is RELEASED; no downtime_reason interaction |
| `backend/app/security/rbac.py` | ✅ Inspected | `"admin.master_data.reason_code.manage": "ADMIN"` present at line 63 |
| `backend/app/models/reason_code.py` | ✅ Referenced | No `downtime_reason_id` column or FK |
| `backend/app/models/downtime_reason.py` | ✅ Inspected | Standalone table; has own `reason_code: str` column (free text, NOT FK to reason_codes) |
| `backend/app/api/v1/downtime_reasons.py` | ✅ Referenced | No reference to ReasonCode model |
| `backend/app/schemas/operation.py` | ✅ Referenced | No Reason Code fields |

### Frontend Source (confirmed current state)

| File | Status | Key Finding |
|---|---|---|
| `frontend/src/app/api/reasonCodeApi.ts` | ✅ Inspected | `ReasonCodeCapabilities`, `ReasonCodeAllowedActions`, `ReasonCodeItemFromAPI`; write helpers: create, update, release, retire, `getCapabilities`; no forbidden fields |
| `frontend/src/app/api/index.ts` | ✅ Inspected | All Reason Code types exported including `ReasonCodeCapabilities` |
| `frontend/src/app/pages/ReasonCodes.tsx` | ✅ Inspected | `rcCapabilities` state; capabilities effect on mount; Create button gated on `rcCapabilities?.can_create`; row buttons gated on `allowed_actions`; no lifecycle-only inference; no persona-derived permission |
| `frontend/src/app/i18n/registry/en.ts` | ✅ Referenced | `rcWrite.*` keys present; `rcWrite.tooltip.createForbidden` present; 1847 total keys |
| `frontend/src/app/i18n/registry/ja.ts` | ✅ Referenced | Key-synchronized with en.ts at 1847 keys |
| `frontend/src/app/i18n/namespaces.ts` | ✅ Referenced | Namespace structure intact |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | ✅ Inspected | 182 checks (Sections A–M); Section L = 12 Reason Code 13B checks; Section M = 8 Reason Code 13C checks |

---

## 4. Implemented Reason Code Write Baseline

The following write commands are fully implemented and verified:

1. **Create Reason Code as DRAFT** — `POST /api/v1/reason-codes`
2. **Update DRAFT Reason Code metadata** — `PATCH /api/v1/reason-codes/{id}`
3. **Release DRAFT Reason Code** — `POST /api/v1/reason-codes/{id}/release`
4. **Retire DRAFT or RELEASED Reason Code** — `POST /api/v1/reason-codes/{id}/retire`

The following capability infrastructure is implemented:

5. **Page-level Create capability** — `GET /api/v1/reason-codes/capabilities` → `{ can_create, reason }`
6. **Row-level allowed actions** — embedded in every read response → `{ can_update, can_release, can_retire, can_create_sibling }`

---

## 5. Backend API Baseline

### 9.1 Implemented Reason Code Command Matrix

| Command | Backend Route | FE Control | Auth | Lifecycle Rule | Status |
|---|---|---|---|---|---|
| Create Reason Code | `POST /api/v1/reason-codes` | Create button (gated by `rcCapabilities.can_create`) | `require_action("admin.master_data.reason_code.manage")` | Always creates DRAFT; lifecycle_status not in payload | ✅ Implemented |
| Update Reason Code metadata | `PATCH /api/v1/reason-codes/{id}` | Edit button (gated by `allowed_actions.can_update`) | `require_action("admin.master_data.reason_code.manage")` | DRAFT only; RELEASED/RETIRED rejected by service | ✅ Implemented |
| Release Reason Code | `POST /api/v1/reason-codes/{id}/release` | Release button (gated by `allowed_actions.can_release`) | `require_action("admin.master_data.reason_code.manage")` | DRAFT → RELEASED; RETIRED rejected; RELEASED re-release rejected | ✅ Implemented |
| Retire Reason Code | `POST /api/v1/reason-codes/{id}/retire` | Retire button (gated by `allowed_actions.can_retire`) | `require_action("admin.master_data.reason_code.manage")` | DRAFT or RELEASED → RETIRED; already RETIRED rejected | ✅ Implemented |

### Route Registration Order

```
GET  /capabilities          — before /{id} to prevent path-param capture
GET  /                      — list
GET  /{id}                  — detail
POST /                      — create (201)
PATCH /{id}                 — update
POST /{id}/release          — lifecycle transition
POST /{id}/retire           — lifecycle transition
```

### HTTP Status Codes

| Condition | Status |
|---|---|
| Create success | 201 |
| Update / release / retire success | 200 |
| Duplicate (tenant + domain + code) | 409 |
| Empty reason_name update | 400 |
| Wrong lifecycle state for update/release/retire | 409 |
| Record not found | 404 |
| Not authenticated | 401 |
| Missing manage permission | 403 |
| Invalid payload (extra fields, wrong type) | 422 |

### Payload Invariants (Schema-Enforced via `extra="forbid"`)

**`ReasonCodeCreateRequest` — FORBIDDEN fields (Pydantic rejects at 422):**
- `tenant_id` — from JWT only
- `lifecycle_status` — always DRAFT at create
- `reason_code_id` — server-generated UUID
- `downtime_reason_id` — no coupling allowed
- Any policy-binding field

**`ReasonCodeUpdateRequest` — FORBIDDEN fields (Pydantic rejects at 422):**
- `reason_code` — immutable after create
- `reason_domain` — immutable after create
- `reason_category` — immutable after create
- `lifecycle_status` — only changed by release/retire commands
- `tenant_id` — from JWT only
- `downtime_reason_id` — no coupling allowed

---

## 6. Frontend UI Baseline

### Write Controls on `ReasonCodes.tsx`

| Control | Location | Gate | Behavior |
|---|---|---|---|
| Create button | Page header | `disabled={actionBusy \|\| !rcCapabilities?.can_create}` | Opens create modal; disabled if capabilities null or `can_create=false` |
| Edit button (per row) | Row actions | `disabled={!aa.can_update \|\| actionBusy}` | Opens edit modal; only enabled for DRAFT + manage |
| Release button (per row) | Row actions | `disabled={!aa.can_release \|\| actionBusy}` | Opens confirm dialog; only enabled for DRAFT + manage |
| Retire button (per row) | Row actions | `disabled={!aa.can_retire \|\| actionBusy}` | Opens confirm dialog; enabled for DRAFT or RELEASED + manage |

### Create Button Tooltip

```typescript
title={rcCapabilities?.can_create === false ? t("rcWrite.tooltip.createForbidden") : ""}
```

i18n keys:
- `en`: `"rcWrite.tooltip.createForbidden": "Admin permission required to create reason codes."`
- `ja`: `"rcWrite.tooltip.createForbidden": "理由コードを作成するには管理者権限が必要です。"`

### Create Payload (what FE sends)

```typescript
{
  reason_domain: string,       // user input
  reason_category: string,     // user input
  reason_code: string,         // user input
  reason_name: string,         // user input
  description: string | null,  // user input (optional)
  requires_comment: boolean,   // default false
  sort_order: number | null     // default null
}
```

**NOT sent in create payload:** `lifecycle_status`, `tenant_id`, `downtime_reason_id`, `reason_code_id`, any policy binding.

### Update Payload (what FE sends)

```typescript
{
  reason_name?: string | null,
  description?: string | null,
  requires_comment?: boolean | null,
  sort_order?: number | null,
  is_active?: boolean | null
}
```

**NOT sent in update payload:** `reason_code`, `reason_domain`, `reason_category`, `lifecycle_status`, `tenant_id`, `downtime_reason_id`.

### Screen Status

`frontend/src/app/screenStatus.ts` entry for `reasonCodes` still references MMD-FULLSTACK-08 notes. This is a documentation drift gap (see Section 13).

---

## 7. Authorization / Capability Baseline

### Authorization Chain

```
JWT → RequestIdentity → has_action(db, IdentityLike, action_code)
```

- `has_action` is the single source of truth for permission evaluation.
- No frontend persona inference. No lifecycle-only gate.

### 9.3 Capability Matrix

| Capability | Level | Backend Source | FE Consumer | Rule |
|---|---|---|---|---|
| `can_create` | Page | `GET /capabilities` → `has_action(...manage)` | `rcCapabilities.can_create` on Create button | Manage user = true; non-manage = false; null = still loading (button disabled) |
| `allowed_actions.can_update` | Row | `_compute_allowed_actions(has_manage, lifecycle_status)` | Edit button `disabled` | DRAFT + manage only |
| `allowed_actions.can_release` | Row | `_compute_allowed_actions(has_manage, lifecycle_status)` | Release button `disabled` | DRAFT + manage only |
| `allowed_actions.can_retire` | Row | `_compute_allowed_actions(has_manage, lifecycle_status)` | Retire button `disabled` | DRAFT or RELEASED + manage |
| `allowed_actions.can_create_sibling` | Row | `_compute_allowed_actions(has_manage, lifecycle_status)` | Available in type; NOT primary Create gate | Any non-RETIRED or RETIRED + manage; `can_create_sibling` = true for all manage states |

### 9.4 Lifecycle Capability Matrix

| Lifecycle | has_manage | can_update | can_release | can_retire | can_create_sibling |
|---|---|---:|---:|---:|---:|
| DRAFT | true | ✅ | ✅ | ✅ | ✅ |
| RELEASED | true | ❌ | ❌ | ✅ | ✅ |
| RETIRED | true | ❌ | ❌ | ❌ | ✅ |
| DRAFT | false | ❌ | ❌ | ❌ | ❌ |
| RELEASED | false | ❌ | ❌ | ❌ | ❌ |
| RETIRED | false | ❌ | ❌ | ❌ | ❌ |

**Source:** `_compute_allowed_actions()` in `backend/app/services/reason_code_service.py`

### Action Code

| Code | Family | Protects |
|---|---|---|
| `admin.master_data.reason_code.manage` | ADMIN | All 4 Reason Code write endpoints |

**Registered in:** `backend/app/security/rbac.py` line 63 (runtime) and `docs/design/02_registry/action-code-registry.md` line 73 (governance doc).

---

## 8. Lifecycle Transition Baseline

```
         create
(none) ─────────→ DRAFT
                    │
                    │  release
                    ▼
                 RELEASED
                    │
                    │  retire (also: DRAFT → RETIRED)
                    ▼
                 RETIRED  ← terminal state
```

**Invariants:**
- RETIRED → RELEASED: **FORBIDDEN** (service raises ValueError)
- RELEASED → DRAFT: **FORBIDDEN** (no reactivation command)
- RETIRED → DRAFT: **FORBIDDEN**
- Double-retire: **FORBIDDEN** (service raises ValueError)
- `lifecycle_status` in write payload: **FORBIDDEN** (schema `extra="forbid"`)

---

## 9. Audit / Event Baseline

All Reason Code mutation services emit security events via `record_security_event()`:

| Command | Event Type |
|---|---|
| Create | `ReasonCode.CREATED` |
| Update | `ReasonCode.UPDATED` |
| Release | `ReasonCode.RELEASED` |
| Retire | `ReasonCode.RETIRED` |

Event payload includes: `reason_code_id`, `reason_code`, affected fields, `actor_user_id`, `tenant_id`.

Read operations (list, detail, capabilities) do **not** emit events.

---

## 10. Downtime Reason Boundary

| Boundary | Current Decision | Evidence |
|---|---|---|
| `reason_codes` table has no FK to `downtime_reasons` | **ENFORCED** | `backend/app/models/reason_code.py` — no `downtime_reason_id` column |
| `downtime_reasons` table has no FK to `reason_codes` | **ENFORCED** | `backend/app/models/downtime_reason.py` — has own free-text `reason_code: str` column, not FK |
| `downtime_reason_id` in create payload | **REJECTED** at 422 | `ReasonCodeCreateRequest` — `extra="forbid"` |
| `downtime_reason_id` in update payload | **REJECTED** at 422 | `ReasonCodeUpdateRequest` — `extra="forbid"` |
| `map_to_downtime_reason` command | **DEFERRED** | No route, service, or model — requires dedicated governance slice |
| Reason Code mutation triggers downtime event | **FORBIDDEN** | No execution path exists |
| Reason Code mutation changes OEE/Andon data | **FORBIDDEN** | No integration path exists |

**Architectural decision:** `downtime_reasons` is a separate operational master data catalog. `reason_codes` is a unified classification taxonomy. The two tables evolve independently. Mapping (if ever needed) requires a dedicated governance slice with explicit approval.

---

## 11. Regression Coverage Baseline

### 9.6 Regression Coverage Baseline

| Area | Coverage | Command / Evidence | Status |
|---|---|---|---|
| `test_reason_code_foundation_api.py` | 24 tests — create, update, release, retire, CRUD, error paths, auth | Backend pytest | ✅ 24 PASS |
| `test_reason_code_foundation_service.py` | 3 tests — service unit tests | Backend pytest | ✅ 3 PASS |
| `test_reason_code_allowed_actions_13b.py` | 10 tests — allowed_actions (7 from 13B) + capabilities endpoint (3 from 13C) | Backend pytest | ✅ 10 PASS |
| `test_mmd_rbac_action_codes.py` (reason_code tests) | 6 tests within 31 — action code registry, read/write route markers, forbidden scope markers | Backend pytest | ✅ 31 PASS (all 31 in file) |
| Adjacent: `test_product_foundation_api.py` | ~30 tests | Backend pytest | ✅ PASS |
| Adjacent: `test_product_version_foundation_api.py` | ~30 tests | Backend pytest | ✅ PASS |
| Adjacent: `test_bom_foundation_api.py` | ~23 tests | Backend pytest | ✅ PASS |
| MMD regression script | 182 checks — Sections A–M; Section L (12 checks, 13B); Section M (8 checks, 13C) | `npm.cmd run check:mmd:read` | ✅ 182 passed, 0 failed |
| Frontend build | No TypeScript errors, bundle built | `npm.cmd run build` | ✅ Clean |
| Frontend lint | 0 ESLint errors | `npm.cmd run lint` | ✅ 0 errors |
| Frontend i18n registry | 1847 keys, en.ts and ja.ts key-synchronized | `npm.cmd run lint:i18n:registry` | ✅ PASS |
| Route smoke | 0 failed routes | `npm.cmd run check:routes` | ✅ FAIL: 0 |
| `npm.cmd run lint:i18n` | CRLF/full lint (if available) | Optional | Note: may fail on CRLF encoding issue — documented as pre-existing, not Reason Code regression |

**Total backend tests in Reason Code test suite:** 37 direct (24 + 3 + 10) + 6 marker tests within RBAC test file = coverage complete for all 4 write commands + capabilities contract.

**Last verified run:** MMD-FULLSTACK-13C verification — 103 backend tests (37 reason code + 66 adjacent/RBAC) + 83 adjacent MMD tests + 182 frontend regression checks — all passing.

---

## 12. Boundary Guardrails

### 9.5 Boundary Guardrails

| Boundary | Current Decision | Evidence | Risk if Violated |
|---|---|---|---|
| Reason Code vs downtime_reason | No FK; no mapping command; separate tables | Model inspection; schema `extra="forbid"`; no route | Operational downtime taxonomy corrupted; execution events fire on wrong codes |
| Reason Code vs Execution | No execution command, state machine, or event path | No route references execution models | Reason Code mutation would incorrectly pause/resume production |
| Reason Code vs Downtime Runtime | No downtime_start/end side effect | Service layer inspection; no downtime model import | OEE / Andon data corrupted |
| Reason Code vs Quality | No quality hold trigger or pass/fail path | No quality model import | Quality decisions would be non-deterministic |
| Reason Code vs Material / Inventory | No material movement, backflush, scrap trigger | No inventory model import | Phantom WIP adjustments |
| Reason Code vs ERP | No ERP posting, ledger entry, integration hook | No ERP integration code present | ERP financial data corrupted |
| Reason Code vs Traceability / Genealogy | No genealogy record, lot/serial action | No traceability model import | Production traceability gaps |
| Reason Code vs Maintenance | No maintenance work order trigger | No CMMS integration | Maintenance scheduling errors |
| Reason Code vs Policy Binding | No `bind_to_policy` command; no policy FK | Schema forbids unknown fields; no route | Authorization or quality policy wrongly activated |
| Reason Code vs Authorization Truth | Reason Codes do not grant or revoke permissions | No IAM action in any service | Privilege escalation via master data manipulation |
| Frontend UI vs Authorization Truth | UI is gated by server-derived capability | `rcCapabilities?.can_create`; `allowed_actions` from backend; no persona inference | UI bypass leads to 403 at backend — backend 403 is final guard |

---

## 13. Known Gaps / Deferred Items

| Gap | Type | Risk | Deferred Until |
|---|---|---|---|
| `screenStatus.ts` `reasonCodes` entry still references MMD-FULLSTACK-08 notes ("Create/edit/retire actions remain disabled") | Documentation drift | Low — cosmetic only; does not affect runtime behavior | Next UI baseline or screen-status refresh slice |
| `can_create_sibling` still present in `ReasonCodeAllowedActions` but no longer primary Create gate (replaced by page-level `can_create`) | Minor redundancy | Very low — data is ignored by Create button but still delivered in API | Optional cleanup in a future contract tightening slice |
| `reason` field in `ReasonCodeCapabilities` always `null` | Feature gap | Low — tooltip uses hardcoded i18n key | Future UX enhancement if localized server messages are needed |
| `lint:i18n` full CRLF lint may fail on Windows | Pre-existing environment issue | Low — does not affect runtime or registry parity | CRLF normalization infrastructure slice |
| No E2E Playwright test for Reason Code write actions | Coverage gap | Medium — runtime visual QA deferred | MMD-FE-QA-02 |
| No activate/deactivate governance | Deferred | Medium — `is_active` flag exists; no dedicated command | Requires dedicated governance slice when active toggle is needed in UI |
| `map_to_downtime_reason` not governed or implemented | Deferred | High if built casually | Requires explicit mapping governance slice with FK contract and audit trail |
| `reactivate` (RETIRED → DRAFT) not governed or implemented | Deferred | Medium | Requires invariant review — RETIRED is currently terminal |
| Hard delete not governed or implemented | Deferred | High | Requires soft-delete vs hard-delete decision and audit trail governance |

---

## 14. Do-Not-Do Rules for Future Agents

These rules are in effect for all future slices that touch Reason Code write paths.

1. **DO NOT add a hard delete Reason Code route** without explicit governance contract and audit trail.
2. **DO NOT add a reactivate Reason Code command** without invariant review — RETIRED is currently terminal.
3. **DO NOT add activate/deactivate as a distinct command** — `is_active` flag update is gated through the existing `update` command on DRAFT only.
4. **DO NOT add clone/copy/bulk import/merge/split** without dedicated governance slice.
5. **DO NOT add `map_to_downtime_reason` or `unmap_from_downtime_reason`** without explicit FK contract, audit trail, and boundary review.
6. **DO NOT add any policy binding field** (`bind_to_execution_policy`, `bind_to_quality_policy`, `bind_to_material_policy`) to Reason Code write schemas.
7. **DO NOT add execution pause/resume, downtime start/end, quality pass/fail, quality hold release, material movement, inventory adjustment, scrap posting, backflush, ERP posting, traceability genealogy, or maintenance workflow** as Reason Code commands.
8. **DO NOT derive Reason Code permission from lifecycle status alone** on the frontend — always use server-derived `allowed_actions` or `capabilities`.
9. **DO NOT derive Reason Code permission from persona or role name** on the frontend — `has_action(db, identity, "admin.master_data.reason_code.manage")` is the only authority.
10. **DO NOT send `lifecycle_status`, `tenant_id`, `downtime_reason_id`, `reason_code`, `reason_domain`, or `reason_category` in write payloads** — all are server-controlled or immutable.
11. **DO NOT bypass `extra="forbid"` schema guards** by accepting or forwarding unknown payload fields.
12. **DO NOT use Product/BOM manage permissions as a proxy** for Reason Code manage permission — action codes are domain-specific.
13. **DO NOT turn Reason Code create capability into a frontend inferred decision** — `GET /reason-codes/capabilities` is the only source.
14. **DO NOT make Reason Code an authorization truth** — Reason Codes classify events, they do not grant or restrict access.
15. **DO NOT expand Reason Code write paths** without updating this freeze document and creating a new audit report.

---

## 15. Recommended Next Slices

### Recommended Default: **MMD-FE-QA-02 — Browser Screenshot Runtime QA / Visual Evidence Pack**

**Reason:** Product Version, BOM, and Reason Code write baselines are now governed and frozen. The MMD write UI (create/edit/release/retire on all three entities) is implemented but has not received runtime visual QA or browser evidence. Before expanding to Product Version binding (`set_current`, BOM binding), ISA-88 recipe/formula, or scope applicability, the UI should receive visual validation including:
- Screenshot evidence of Reason Code write controls in manage vs read-only user context
- Empty-list Create button state verification
- Create / Edit / Release / Retire modal flows
- Error state screenshots (409 conflict, 403 forbidden, 404 not found)
- Responsive layout verification

### Alternative Slices (lower priority unless business-driven)

| Slice | When to Choose |
|---|---|
| **MMD-BOM-WRITE-02 — BOM Product Version Binding Governance Contract** | Only if business explicitly prioritizes Product Version ↔ BOM binding before visual QA |
| **MMD-PV-WRITE-02 — Product Version set_current Governance Contract** | Only if current-version switching is now required before visual QA |
| **MMD-ISA88-00 — Recipe / Formula / Procedure / Phase Readiness Contract** | Only if process/batch manufacturing support is being pulled forward |
| **MMD-SCOPE-APPLICABILITY-01 — MMD Scope Applicability Governance Contract** | Only if plant/area/line/station applicability is now more urgent than runtime UI QA |

---

## 16. Verification Commands

The following commands were run during MMD-FULLSTACK-13C and results reused here. Source has not changed since (confirmed by context).

### Backend Reason Code + RBAC tests

```powershell
cd G:\Work\FleziBCG\backend
uv run --with pytest --with fastapi --with sqlalchemy --with httpx --with anyio --with passlib --with "python-jose" --with bcrypt --with pydantic-settings --with psycopg --with "psycopg-binary" --with alembic --python 3.12 python -m pytest -q tests/test_reason_code_foundation_api.py tests/test_reason_code_foundation_service.py tests/test_reason_code_allowed_actions_13b.py tests/test_mmd_rbac_action_codes.py
# Result: 103 passed
```

### Adjacent MMD tests

```powershell
uv run --with pytest --with fastapi --with sqlalchemy --with httpx --with anyio --with passlib --with "python-jose" --with bcrypt --with pydantic-settings --with psycopg --with "psycopg-binary" --with alembic --python 3.12 python -m pytest -q tests/test_product_foundation_api.py tests/test_product_version_foundation_api.py tests/test_bom_foundation_api.py
# Result: 83 passed
```

### Frontend regression + build + lint

```powershell
cd G:\Work\FleziBCG\frontend
npm.cmd run check:mmd:read    # Result: 182 passed, 0 failed
npm.cmd run build              # Result: built in ~7s, no errors
npm.cmd run lint               # Result: 0 errors
npm.cmd run lint:i18n:registry # Result: PASS — 1847 keys synchronized
npm.cmd run check:routes       # Result: FAIL: 0
```

**Evidence source:** MMD-FULLSTACK-13C verification run (see `docs/audit/mmd-fullstack-13c-reason-code-page-level-create-capability.md` Section 11). Source confirmed unchanged since that run.

---

## 17. Final Freeze Verdict

**FROZEN — REASON CODE WRITE BASELINE v1.0 APPROVED**

### Summary

| Area | Verdict |
|---|---|
| 4 write commands (create, update, release, retire) | ✅ IMPLEMENTED AND VERIFIED |
| Page-level `can_create` capability | ✅ IMPLEMENTED (GET /capabilities) |
| Row-level `allowed_actions` (4 bool fields) | ✅ IMPLEMENTED AND VERIFIED |
| Action code `admin.master_data.reason_code.manage` | ✅ REGISTERED in rbac.py + registry doc |
| Forbidden payload fields (schema-enforced) | ✅ ENFORCED via Pydantic `extra="forbid"` |
| No downtime_reason FK or mapping | ✅ CONFIRMED — no coupling exists |
| No execution/quality/material/ERP side effects | ✅ CONFIRMED — no path exists |
| Security events on all mutations | ✅ CONFIRMED — 4 event types emitted |
| Frontend uses server-derived capabilities only | ✅ CONFIRMED — no persona/lifecycle inference |
| Backend 403 final guard on all write routes | ✅ CONFIRMED — `require_action` on all 4 write endpoints |
| 103 backend tests passing | ✅ VERIFIED |
| 83 adjacent MMD tests passing | ✅ VERIFIED |
| 182 frontend regression checks passing | ✅ VERIFIED |
| Build / lint / i18n / routes all green | ✅ VERIFIED |

### What is frozen

The Reason Code write baseline is complete, governed, and verified. No further write commands, lifecycle transitions, schema fields, or FE controls should be added to this subsystem without:

1. A dedicated governance contract document (equivalent to MMD-BE-10 pattern)
2. A new audit slice report
3. Update to this freeze document
4. Hard Mode MOM v3 pre-coding evidence pass

### Next action

**→ MMD-FE-QA-02 — Browser Screenshot Runtime QA / Visual Evidence Pack**
