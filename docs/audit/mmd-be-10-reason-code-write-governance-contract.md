# MMD-BE-10 — Reason Code Write Governance / Minimal Mutation Contract Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-04 | v1.0 | Created Reason Code write governance contract before mutation implementation. |

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Backend command-boundary design mode + Authorization / action-code governance mode + Lifecycle governance mode + Architecture boundary guardian mode + Hard Mode MOM v3 mode + Critical reviewer mode
- **Hard Mode MOM:** v3 ON
- **Reason:** Reason Codes are shared MMD classification truth consumed by execution (pause, downtime), quality (hold), material (scrap, yield), maintenance, and reporting contexts. A wrong write contract could accidentally make reason codes trigger operational events, move material, decide quality, or imply authorization. Hard Mode v3 is mandatory per copilot-instructions.md.

---

## 1. Scope

Documentation-only governance slice.

**In scope:**
- Define the Reason Code minimal mutation contract before any write API implementation
- Classify all candidate write commands
- Define lifecycle transition decisions
- Define authorization / action-code requirements
- Propose future API contract
- Define validation rules
- Define audit/event expectations
- Define cross-domain boundary guardrails
- Decide downtime_reason relationship

**Out of scope:**
- Backend write API implementation
- Frontend write UI implementation
- Database migration changes
- Runtime source changes (backend or frontend)
- Tests

**Expected output files (this slice only):**
1. `docs/design/02_domain/product_definition/reason-code-write-governance-contract.md` — ✅ Created
2. `docs/audit/mmd-be-10-reason-code-write-governance-contract.md` — this document

---

## 2. Baseline Evidence Used

### Required Audit Documents

| Document | Status | Key Finding |
|---|---|---|
| `docs/audit/mmd-bom-write-baseline-01-bom-write-freeze-handoff.md` | ✅ Inspected | BOM write baseline frozen; action code pattern (`admin.master_data.bom.manage`) established; capability projection pattern defined; all BOM boundary guardrails confirmed |
| `docs/audit/mmd-read-baseline-02-complete-read-integration-freeze-handoff.md` | ✅ Inspected | Complete MMD read integration frozen; Reason Code read baseline confirmed (MMD-BE-07 + MMD-FULLSTACK-08); 84 regression checks passing |
| `docs/audit/mmd-write-gov-01-command-boundary.md` | ✅ Inspected | Reason Code classified `DEFERRED_REQUIRES_CONTRACT` in write-gov-01; lifecycle transitions all DEFER/FORBID; no action code existed at that time |
| `docs/audit/mmd-be-06-reason-code-foundation-contract-boundary-lock.md` | ✅ Inspected | Foundation contract locked; 4 boundary decisions made: unified catalog, separate from downtime_reason, DRAFT/RELEASED/RETIRED lifecycle, single domain per code |
| `docs/audit/mmd-be-07-reason-code-minimal-read-model.md` | ✅ Inspected | Reason Code read model complete; 14 ORM fields; migration 0010; 22 tests; no write routes; downtime_reason untouched |
| `docs/audit/mmd-fullstack-08-reason-codes-fe-read-integration.md` | ✅ Inspected | FE read integration complete; `ReasonCodes.tsx` connected to backend; write buttons remain disabled; `reasonCodeApi.ts` read-only |
| `docs/audit/mmd-be-02-rbac-action-code-fix.md` | ✅ Inspected | Action code naming convention established; 3 MMD codes added in MMD-BE-02; governance rules require: (a) `rbac.py` entry, (b) registry doc entry, (c) regression test |

### Required Design Documents

| Document | Status | Key Finding |
|---|---|---|
| `docs/design/02_domain/product_definition/reason-code-foundation-contract.md` | ✅ Inspected | Entity shape: 14 fields, DRAFT/RELEASED/RETIRED lifecycle; separation from downtime_reason explicit; write-path deferred |
| `docs/design/02_domain/product_definition/mmd-write-path-governance-matrix.md` | ✅ Inspected | Reason Code: all write commands `DEFERRED_REQUIRES_CONTRACT`; RELEASED→DRAFT, RETIRED→* FORBID; confirms this slice is the governance contract |
| `docs/design/02_registry/action-code-registry.md` | ✅ Inspected | `admin.master_data.reason_code.manage` NOT present; registry ends at `admin.master_data.bom.manage`; governance rules require rbac.py + registry + test |
| `docs/design/00_platform/product-business-truth-overview.md` | ✅ Referenced (via MMD-BOM-WRITE-BASELINE-01) | MMD is definition truth, not ERP truth; no inventory/ERP coupling |

### Optional Documents

| Document | Status | Key Finding |
|---|---|---|
| `docs/audit/mmd-fe-qa-01-read-pages-runtime-visual-qa.md` | Referenced via MMD-READ-BASELINE-02 | 8 routes QA pass; Reason Codes read confirmed |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | ✅ Inspected | 134 checks (Sections A–J including J1–J12 BOM capability); Section I (17 checks) covers Reason Code read integration |

---

## 3. Source Inspection Summary

### Backend

| File | Status | Key Finding |
|---|---|---|
| `backend/app/models/reason_code.py` | ✅ Inspected | 14 ORM fields; `lifecycle_status` default=DRAFT; `UniqueConstraint(tenant_id, reason_domain, reason_code)`; `ReasonCodeLifecycleStatus` and `ReasonCodeDomain` enums defined |
| `backend/app/schemas/reason_code.py` | ✅ Inspected | `ReasonCodeItem` read-only; 14 fields; no write schemas (no `CreateRequest`, `UpdateRequest`); clean baseline for future write schema addition |
| `backend/app/repositories/reason_code_repository.py` | ✅ Inspected | `list_reason_codes_by_tenant`, `get_reason_code_by_id`; pure CRUD read; no write methods; no side effects |
| `backend/app/services/reason_code_service.py` | ✅ Inspected | `list_reason_codes`, `get_reason_code`; read-only; no write functions |
| `backend/app/api/v1/reason_codes.py` | ✅ Inspected | `GET /reason-codes`, `GET /reason-codes/{id}` only; `require_authenticated_identity`; no POST/PATCH/DELETE; no hidden write routes |
| `backend/app/security/rbac.py` | ✅ Inspected | `admin.master_data.reason_code.manage` **ABSENT**; registry ends at `admin.master_data.bom.manage` (line ~62); `admin.downtime_reason.manage` present for downtime_reason mutations |
| `backend/tests/test_reason_code_foundation_api.py` | ✅ Inspected | 11 API tests; tests confirm 405 Method Not Allowed on write routes (POST/PUT/DELETE); write paths explicitly blocked |
| `backend/tests/test_reason_code_foundation_service.py` | ✅ Inspected | 11 service tests; read-only coverage; no write service tests |
| `backend/tests/test_mmd_rbac_action_codes.py` | ✅ Referenced | Contains action code registry tests; `admin.master_data.bom.manage` is the most recent addition; `admin.master_data.reason_code.manage` not yet present |
| `backend/alembic/versions/0010_reason_codes.py` | ✅ Confirmed (via mmd-be-07) | Migration present; `reason_codes` table exists in schema; migration chain intact |

### Adjacent Source

| File | Status | Key Finding |
|---|---|---|
| `backend/app/models/downtime_reason.py` | ✅ Inspected | Completely separate model; no FK to reason_codes; `active_flag` (not `lifecycle_status`); execution-specific fields (`default_block_mode`, `requires_supervisor_review`, `planned_flag`); entirely operational model |
| `backend/app/api/v1/downtime_reasons.py` | ✅ Inspected | Uses `admin.downtime_reason.manage` (separate action code); no cross-reference to reason_codes; untouched |
| `backend/app/schemas/operation.py` | Referenced (via mmd-be-06) | `operation.reason_code` resolves to `downtime_reasons` master; independent of unified reason_codes |

### Frontend

| File | Status | Key Finding |
|---|---|---|
| `frontend/src/app/api/reasonCodeApi.ts` | ✅ Inspected (via FULLSTACK-08) | `ReasonCodeItemFromAPI` (14 fields), `reasonCodeApi.listReasonCodes()`, `reasonCodeApi.getReasonCode()` — read-only; no write methods |
| `frontend/src/app/api/index.ts` | ✅ Confirmed (via FULLSTACK-08) | `reasonCodeApi` exported |
| `frontend/src/app/pages/ReasonCodes.tsx` | ✅ Inspected | Read-only screen; write-action buttons remain disabled; no write intent wired |
| `frontend/src/app/screenStatus.ts` | ✅ Confirmed (via FULLSTACK-08) | `reasonCodes`: `phase: "PARTIAL"`, `dataSource: "BACKEND_API"` |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | ✅ Inspected | Section I: 17 Reason Code checks; total 134 checks; write capability projection checks (J1–J12) cover BOM pattern for reference |

---

## 4. Reason Code Write Decisions

### Baseline Evidence Extract

**Current Reason Code Read Baseline Summary:**

| Area | Evidence | Decision |
|---|---|---|
| ORM model | 14 fields; lifecycle_status DRAFT/RELEASED/RETIRED; unique (tenant, domain, code) | Solid foundation for write path |
| Read API | GET list + GET detail; read-only; authenticated; no write routes | No conflicts; clean write extension surface |
| Action code | `admin.master_data.reason_code.manage` absent from `rbac.py` and registry doc | **MMD-BE-10A must add it before MMD-BE-13** |
| Downtime Reason | Completely separate model; no FK; no coupling | Additive write path is safe |
| FE read integration | `ReasonCodes.tsx` connected; write buttons disabled; `reasonCodeApi.ts` read-only | FE write can be extended without breaking reads |
| No hidden write routes | Confirmed via `reason_codes.py` inspection and `test_reason_code_foundation_api.py` 405 tests | Safe to proceed |
| Migration chain | `0010_reason_codes.py` is Alembic head | Schema is stable; no migration needed for write path (service layer writes to existing table) |

### Reason Code Write Command Inventory

| Command | Decision | Reason | Future Guardrails |
|---|---|---|---|
| `create_reason_code` | READY_FOR_IMPLEMENTATION_NEXT | Foundation contract locked; model exists; lifecycle pattern mirrors BOM; no downstream side effects | tenant_id from JWT; lifecycle_status server-set to DRAFT; code unique within tenant+domain; `extra="forbid"` |
| `update_reason_code_metadata` | READY_FOR_IMPLEMENTATION_NEXT | DRAFT mutability well-established (BOM, Product, Routing); no cross-domain impact | source_state must be DRAFT; `reason_code`, `reason_domain`, `reason_category`, `lifecycle_status` not in schema |
| `release_reason_code` | READY_FOR_IMPLEMENTATION_NEXT | Explicit lifecycle command; mirrors BOM release; no operational events | source_state must be DRAFT; explicit route; audit record required |
| `retire_reason_code` | READY_FOR_IMPLEMENTATION_NEXT | Explicit lifecycle command; mirrors BOM retire; DRAFT and RELEASED allowed | source_state must be DRAFT or RELEASED; terminal; audit record required |
| `deactivate_reason_code` | DEFERRED_REQUIRES_CONTRACT | `is_active` governance policy undefined | must not bypass lifecycle; usage analysis required |
| `activate_reason_code` | DEFERRED_REQUIRES_CONTRACT | Inverse of deactivate; same gap | same as deactivate |
| `delete_reason_code` | FORBIDDEN | Historical classification records risk; no exception contract | Hard delete prohibited |
| `reactivate_reason_code` | FORBIDDEN | RETIRED is terminal; no reactivation path | Aligns with BOM, Product, Routing pattern |
| `clone_reason_code` | DEFERRED_REQUIRES_CONTRACT | Code uniqueness and lineage policy not defined | requires uniqueness, lineage audit record |
| `copy_from_existing_reason_code` | DEFERRED_REQUIRES_CONTRACT | Same as clone | same |
| `bulk_import_reason_codes` | DEFERRED_REQUIRES_CONTRACT | Transaction policy, duplicate handling, all-or-nothing vs. per-row error not defined | |
| `bulk_retire_reason_codes` | DEFERRED_REQUIRES_CONTRACT | Batch lifecycle policy, usage impact, audit rollup not defined | |
| `merge_reason_codes` | DEFERRED_REQUIRES_CONTRACT | Historical reference remapping policy not defined | |
| `split_reason_code` | DEFERRED_REQUIRES_CONTRACT | Lineage and historical classification policy not defined | |
| `map_to_downtime_reason` | DEFERRED_REQUIRES_CONTRACT | Explicit decision from MMD-BE-06: harmonization is a separate governance review | |
| `unmap_from_downtime_reason` | DEFERRED_REQUIRES_CONTRACT | Inverse of map; same gap | |
| `bind_to_execution_policy` | DEFERRED_REQUIRES_CONTRACT | Cross-domain coupling; execution domain governance required | |
| `bind_to_quality_policy` | DEFERRED_REQUIRES_CONTRACT | Quality domain governance required | |
| `bind_to_material_policy` | DEFERRED_REQUIRES_CONTRACT | Material domain governance required | |

---

## 5. Lifecycle Transition Decisions

### Reason Code Lifecycle Transition Map

| Transition | Decision | Reason |
|---|---|---|
| (new) → DRAFT | ALLOW_NEXT via `create_reason_code` | Server sets; client never specifies lifecycle on create |
| DRAFT → RELEASED | ALLOW_NEXT via explicit `release_reason_code` command | Explicit release command; no payload body; mirrors BOM pattern |
| RELEASED → RETIRED | ALLOW_NEXT via explicit `retire_reason_code` command | Explicit retire command; terminal; mirrors BOM pattern |
| DRAFT → RETIRED | ALLOW_NEXT via explicit `retire_reason_code` command | Permitted for unreleased codes; explicit command; audit record required |
| RELEASED → DRAFT | FORBID | Release is governance commitment; reverting breaks classification configurations; consistent with BOM/Product pattern |
| RETIRED → RELEASED | FORBID | Terminal state; no reactivation contract |
| RETIRED → DRAFT | FORBID | Terminal state; no reactivation contract |

### State Machine Diagram

```
(new) ──[create]──► DRAFT ──[release]──► RELEASED ──[retire]──► RETIRED
                      │                                              ▲
                      └──────────────────[retire]────────────────────┘
```

**Notes:**
- Identical pattern to BOM, Product, and Routing lifecycle state machines.
- No reactivation path from RETIRED.
- No downgrade path from RELEASED.
- `is_active` is orthogonal to `lifecycle_status` — it is an operational filtering flag, not a lifecycle state.

---

## 6. Authorization / Action-Code Decisions

### Authorization / Action-Code Map

| Endpoint / Command | Required Future Action Code | Decision |
|---|---|---|
| `GET /api/v1/reason-codes` | `require_authenticated_identity` (unchanged) | Read — no action code |
| `GET /api/v1/reason-codes/{id}` | `require_authenticated_identity` (unchanged) | Read — no action code |
| `POST /api/v1/reason-codes` | `admin.master_data.reason_code.manage` | ADMIN family |
| `PATCH /api/v1/reason-codes/{id}` | `admin.master_data.reason_code.manage` | ADMIN family |
| `POST /api/v1/reason-codes/{id}/release` | `admin.master_data.reason_code.manage` | ADMIN family |
| `POST /api/v1/reason-codes/{id}/retire` | `admin.master_data.reason_code.manage` | ADMIN family |

### Key Findings

1. **`admin.master_data.reason_code.manage` does NOT exist** in `backend/app/security/rbac.py` or in `docs/design/02_registry/action-code-registry.md` as of May 4, 2026.
2. The action code naming follows the established MMD convention: `admin.master_data.<entity>.manage`.
3. A single `manage` code covers both metadata mutations and lifecycle transitions — consistent with the note in the action-code-registry.md about coarse-grained action codes deferred to Phase C.
4. Read endpoints must remain `require_authenticated_identity`; do not add action code to read paths (governance rule #1 in action-code-registry.md).
5. The `admin.downtime_reason.manage` action code (used by `POST /downtime-reasons`) is a separate code and must remain separate.

---

## 7. Future API Contract Proposal

### Ready-for-Implementation Endpoints

| Endpoint | Command | Auth | Source State | Target State | Input Schema | Audit |
|---|---|---|---|---|---|---|
| `POST /v1/reason-codes` | create | `require_action(reason_code.manage)` | N/A | DRAFT | `ReasonCodeCreateRequest` (extra=forbid) | `ReasonCode.CREATED` |
| `PATCH /v1/reason-codes/{id}` | update metadata | `require_action(reason_code.manage)` | DRAFT | DRAFT | `ReasonCodeUpdateRequest` (extra=forbid) | `ReasonCode.UPDATED` |
| `POST /v1/reason-codes/{id}/release` | release | `require_action(reason_code.manage)` | DRAFT | RELEASED | (no body) | `ReasonCode.RELEASED` |
| `POST /v1/reason-codes/{id}/retire` | retire | `require_action(reason_code.manage)` | DRAFT or RELEASED | RETIRED | (no body) | `ReasonCode.RETIRED` |

### Create Request Schema Boundary

Allowed fields in `ReasonCodeCreateRequest`:
- `reason_domain` (required, enum)
- `reason_category` (required, string)
- `reason_code` (required, string)
- `reason_name` (required, string)
- `description` (optional, string | None)
- `requires_comment` (optional, bool, default false)
- `is_active` (optional, bool, default true)
- `sort_order` (optional, int, default 0)

Forbidden fields (extra=forbid):
- `lifecycle_status` — server sets to DRAFT
- `tenant_id` — from JWT identity
- `reason_code_id` — server-generated
- `created_at`, `updated_at` — server-managed

### Update Request Schema Boundary

Allowed fields in `ReasonCodeUpdateRequest`:
- `reason_name` (optional)
- `description` (optional)
- `requires_comment` (optional)
- `is_active` (optional)
- `sort_order` (optional)

Forbidden fields (extra=forbid):
- `reason_code` — immutable
- `reason_domain` — immutable
- `reason_category` — immutable (classification identity)
- `lifecycle_status` — changed only via explicit commands
- `tenant_id`, `reason_code_id` — immutable

### Out-of-Scope Side Effects for All 4 Endpoints

No execution commands, downtime start/end, quality decisions, material movement, inventory reservation, scrap posting, backflush, ERP posting, traceability genealogy, maintenance work orders, or automatic downtime_reason mapping.

---

## 8. Audit / Event Expectations

### Audit / Event Expectation Map

| Command | Audit / Event Expectation | Forbidden Side Effects |
|---|---|---|
| `create_reason_code` | `ReasonCode.CREATED` — governance audit record via `record_security_event()` | No execution command; no downtime_reason insert; no quality/material/ERP event |
| `update_reason_code_metadata` | `ReasonCode.UPDATED` — contains changed fields; audit log | Same forbidden list |
| `release_reason_code` | `ReasonCode.RELEASED` — lifecycle transition record; previous_status=DRAFT | Same forbidden list |
| `retire_reason_code` | `ReasonCode.RETIRED` — lifecycle transition record; previous_status from DRAFT or RELEASED | Same forbidden list |

All events emitted via `record_security_event()` — the established governance audit pattern (same as BOM, Product, Routing).

---

## 9. Boundary Guardrails

### Cross-Domain Boundary Map

| Boundary | Decision | Risk if Violated |
|---|---|---|
| Reason Code vs Downtime Reason | Separate table; no FK; no auto-mapping | Coupling would break operational downtime behavior; require migration governance |
| Reason Code vs Execution | Classification reference only; no execution event ownership | Execution events cannot originate from reason code mutations |
| Reason Code vs Quality | Classification reference only; no quality decision | Quality disposition must not be triggered from reason code writes |
| Reason Code vs Material/Inventory | Classification reference only; no material movement | Material movement, scrap, backflush must not originate from reason code writes |
| Reason Code vs ERP | No ERP posting; no PLM sync | ERP is enterprise domain; reason codes are MMD reference only |
| Reason Code vs Traceability | No genealogy record creation | Genealogy is execution domain truth |
| Reason Code vs IAM/Authorization | `reason_domain` is classification; not an authorization scope | `reason_domain` values do not grant permissions |
| `reason_category` vs Domain Workflow | Display/filter classification only | Must not trigger downtime, quality, or material behavior by value |
| `admin.master_data.product.manage` vs `admin.master_data.reason_code.manage` | Separate action codes; no cross-inference | Product manage must not grant reason code manage |
| `admin.downtime_reason.manage` vs `admin.master_data.reason_code.manage` | Separate action codes | Downtime Reason admin is a separate domain from MMD reason codes |
| Frontend UI vs Authorization Truth | FE disables using capability flags; backend `require_action` is final | If FE enables controls locally, bypasses authorization truth |

---

## 10. Downtime Reason Relationship

### Explicit Decisions

| Aspect | Decision | Evidence |
|---|---|---|
| Tables | Separate: `reason_codes` vs `downtime_reasons` | MMD-BE-06 boundary decision; confirmed in source inspection |
| FK relationship | **NONE** — no FK, no auto-mapping | `downtime_reason.py` and `reason_code.py` inspected; no cross-reference |
| `operation.reason_code` field | Continues to resolve against `downtime_reasons` — UNCHANGED | `backend/app/schemas/operation.py` (via MMD-BE-06) |
| `map_to_downtime_reason` command | **DEFERRED** — separate harmonization governance | MMD-BE-06 explicit decision preserved |
| Automatic mapping on create | **FORBIDDEN** — no silent coupling | This would couple MMD definition to operational execution without governance |
| Future harmonization | Explicitly deferred pending operational evidence | Requires dedicated slice + migration planning |

### Why Separate Is Correct Now

| Aspect | `downtime_reasons` (Operational) | `reason_codes` (MMD Reference) |
|---|---|---|
| Scope | Tenant → Plant → Area → Line → Station | Tenant only |
| Purpose | Execution pause/downtime selection | Multi-domain reference classification |
| Lifecycle | `active_flag` (operational) | DRAFT/RELEASED/RETIRED (governance) |
| Specific fields | `planned_flag`, `default_block_mode`, `requires_supervisor_review` | `requires_comment`, `sort_order` |
| Action code | `admin.downtime_reason.manage` | `admin.master_data.reason_code.manage` (future) |
| Merge risk | HIGH — would break execution behavior | N/A |

---

## 11. Future Test Requirements

### Required Tests for MMD-BE-10A (Action Code Registry Patch)

| Test Area | Required |
|---|---|
| `admin.master_data.reason_code.manage` present in ACTION_CODE_REGISTRY | ✅ Add to `test_mmd_rbac_action_codes.py` |
| Maps to `ADMIN` family | ✅ Add to `test_mmd_rbac_action_codes.py` |

### Required Tests for MMD-BE-13 (Reason Code Write API Foundation)

| Test Area | Required Tests |
|---|---|
| Create (success) | POST → 201; lifecycle_status=DRAFT; tenant isolated |
| Create (uniqueness) | Duplicate (tenant, domain, code) → 409 |
| Create (forbidden fields) | lifecycle_status in body → 422; tenant_id in body → 422 |
| Create (missing required) | reason_domain missing → 422; reason_code missing → 422 |
| Update (success, DRAFT) | PATCH allowed fields → 200 |
| Update (forbidden, RELEASED) | PATCH on RELEASED → 409 |
| Update (forbidden, RETIRED) | PATCH on RETIRED → 409 |
| Update (immutable fields) | reason_code in PATCH → 422; reason_domain in PATCH → 422 |
| Release (success) | DRAFT → 200; lifecycle=RELEASED |
| Release (forbidden, RELEASED) | 409 |
| Release (forbidden, RETIRED) | 409 |
| Retire (success, from DRAFT) | 200; lifecycle=RETIRED |
| Retire (success, from RELEASED) | 200; lifecycle=RETIRED |
| Retire (forbidden, already RETIRED) | 409 |
| Auth (unauthenticated) | 401 on all write routes |
| Auth (no manage action) | 403 on all write routes |
| Auth (cross-tenant) | 404 or 403 |
| Boundary (no execution events) | Write produces no execution event records |
| Boundary (no downtime mapping) | Write does not touch downtime_reasons table |

---

## 12. Recommended Next Slice

**Recommended: MMD-BE-10A — Reason Code Action Code Registry Patch**

**Justification:** `admin.master_data.reason_code.manage` is **absent** from `backend/app/security/rbac.py` and `docs/design/02_registry/action-code-registry.md`. Per governance rule #4 in action-code-registry.md: "Adding a new action code requires: (a) entry in `rbac.py`, (b) entry in this file, (c) a regression test." This must be completed before any Reason Code mutation endpoint can be implemented.

**After MMD-BE-10A:** Proceed to **MMD-BE-13 — Reason Code Write API Foundation**.

### Evaluated Alternatives

| Alternative | Recommendation | Condition |
|---|---|---|
| **MMD-BE-10A — Reason Code Action Code Registry Patch** | ✅ **RECOMMENDED DEFAULT** | Proceed now — action code is absent |
| MMD-BE-13 — Reason Code Write API Foundation | ❌ Cannot proceed yet | Requires `admin.master_data.reason_code.manage` to exist first |
| MMD-FULLSTACK-13 — Reason Code FE Write Intent | ❌ Premature | Requires backend write API + server-derived capability projection |
| MMD-FE-QA-02 — Browser Screenshot Runtime QA | ❌ Not blocking | Optional; can be deferred unless visual evidence is explicitly required |

---

## 13. Verification / Diff

This is a documentation-only slice. No backend runtime source, frontend runtime source, tests, or migrations were modified.

```bash
git diff -- \
  docs/design/02_domain/product_definition/reason-code-write-governance-contract.md \
  docs/audit/mmd-be-10-reason-code-write-governance-contract.md
```

**Expected result:** Both files appear as new additions (green `+` lines only). No diffs in source files.

```bash
git status --short
```

**Expected result:**
```
?? docs/design/02_domain/product_definition/reason-code-write-governance-contract.md
?? docs/audit/mmd-be-10-reason-code-write-governance-contract.md
```

No other files modified.

---

## 14. Final Verdict

**GOVERNANCE CONTRACT ESTABLISHED — Reason Code Write Governance v1.0 — May 4, 2026**

### Hard Mode MOM v3 Evidence Maps — Produced

| Evidence Map | Status |
|---|---|
| Design Evidence Extract | ✅ §2 — all baseline inputs reviewed |
| Event Map | ✅ §8 — 4 allowed audit events; forbidden side effects listed |
| Invariant Map | ✅ §9 — boundary guardrails established; §4 command boundary decisions |
| State Transition Map | ✅ §5 — 7 transitions decided; state machine diagram |
| Authorization / Capability Map | ✅ §6 — action code absent; MMD-BE-10A required |
| Test Matrix | ✅ §11 — MMD-BE-10A and MMD-BE-13 test requirements defined |
| Verdict | This section |

### What Is Established by This Slice

- 4 write commands: `READY_FOR_IMPLEMENTATION_NEXT` (create, update-metadata, release, retire)
- 15 write commands: `DEFERRED` or `FORBIDDEN`
- Lifecycle: DRAFT → RELEASED → RETIRED; direct DRAFT → RETIRED allowed; all reversal paths FORBIDDEN
- Action code `admin.master_data.reason_code.manage`: ABSENT — must be added by MMD-BE-10A before MMD-BE-13
- Future API contract proposal: 4 endpoints with full schema boundaries
- Validation rules: complete for all 4 commands
- Audit events: 4 allowed events; 14+ forbidden side effects
- Boundary guardrails: 11 cross-domain boundaries locked
- Downtime Reason separation: confirmed additive; `map_to_downtime_reason` deferred
- No runtime source was modified ✅
- No tests were modified ✅
- No migrations were modified ✅

### Stop Conditions — Resolved

| Condition | Status |
|---|---|
| Reason Code foundation contract missing | ✅ Present (`reason-code-foundation-contract.md`) |
| Reason Code source cannot be inspected | ✅ Inspected all 5 required source files |
| Foundation contract conflicts with this prompt | ✅ No conflict — aligns with MMD-BE-06 decisions |
| Hidden write APIs in current source | ✅ None found; read-only confirmed; 405 tests pass |
| Action code source cannot be inspected | ✅ Inspected `rbac.py`; absence confirmed |
| Write governance requires immediate runtime changes | ✅ No — documentation only; runtime changes deferred to MMD-BE-10A |
| Source silently maps reason_code to downtime_reason | ✅ None found; separate tables confirmed |
| Unresolved merge conflicts | ✅ None (git state clean per context) |

**Next slice: MMD-BE-10A — Reason Code Action Code Registry Patch**
