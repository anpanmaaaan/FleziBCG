# P0-C-08H2 Hard Mode MOM v3 Gate Analysis

**Date**: 2026-05-01  
**Phase**: P0-C-08H2 Frontend Queue Consumer Cutover to StationSession Ownership Contract  
**Status**: GATE ANALYSIS (pre-implementation)

---

## 1. Design Evidence Extract

### Authoritative Contracts

| Contract | Status | Version | Key Finding |
|---|---|---|---|
| Station Session Ownership Contract | CANONICAL | 1.0 (2026-04-29) | StationSession is target ownership truth; claim is compatibility debt |
| StationSession Command Guard Enforcement Contract | CANONICAL | 1.0 (2026-04-28) | Seven execution commands validate StationSession after 08C |
| P0-C-08G Claim Removal Readiness Check | COMPLETED | 1.0 (2026-04-30) | Verdict: READY_FOR_P0_C_08H_STAGED_REMOVAL_PLAN |
| P0-C-08F Claim API Deprecation Lock Report | COMPLETED | 1.0 (2026-04-29) | Claim APIs marked deprecated via response headers; no removal |
| P0-C-08D Station Queue Session-Aware Migration Report | COMPLETED | 1.0 (2026-04-27) | Queue ownership block added additively; claim preserved |

### Ownership Block Backend Contract

Backend schema (`backend/app/schemas/station.py`):

```python
class SessionOwnershipSummary(BaseModel):
    target_owner_type: str                    # "station_session"
    ownership_migration_status: str           # "TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT"
    session_id: str | None                    # active session identity
    station_id: str | None                    # station scope
    session_status: str | None                # "OPEN" | "CLOSED"
    operator_user_id: str | None              # operator bound to session
    owner_state: str                          # "mine" | "other" | "unassigned" | "none"
    has_open_session: bool = False            # session presence flag
```

Queue response (`backend/app/schemas/station.py`):

```python
class StationQueueItem(BaseModel):
    operation_id: int
    operation_number: str
    name: str
    work_order_number: str
    production_order_number: str
    status: str
    planned_start: datetime | None = None
    planned_end: datetime | None = None
    claim: ClaimSummary                       # LEGACY: compatibility only
    ownership: SessionOwnershipSummary        # TARGET: primary ownership truth
    downtime_open: bool = False
```

### Key Evidence

1. **Backend already exposes ownership block**: Queue response includes both `claim` and `ownership` as of 08D.
2. **Claim fields still present**: Backward compatibility maintained; no shape change in H2.
3. **Frontend type outdated**: Current `frontend/src/app/api/stationApi.ts` `StationQueueItem` lacks `ownership` field.
4. **Frontend logic claim-dependent**: Execution readiness gated primarily by `claimState === "mine"` in `StationExecution.tsx`.
5. **UI displays claim as authoritative**: Queue cards, headers, and filters treat claim as primary owner signal.
6. **Deprecation headers active**: Claim APIs (claim/release/status) marked deprecated since 08F; routes remain active.

---

## 2. Current Source Evidence Table

| File | Current Claim Usage | Type/Scope | Data Flow | Target H2 Change | Risk |
|---|---|---|---|---|---|
| `frontend/src/app/api/stationApi.ts` | `StationQueueItem` lacks `ownership` type; `ClaimSummary` only | TYPE | export/import | add `ownership: SessionOwnershipSummary` to `StationQueueItem` | MEDIUM |
| `frontend/src/app/api/stationApi.ts` | `claim(operationId)` POST function | API_CALL | execution flow | keep as deprecated/compat-only, not primary | LOW |
| `frontend/src/app/api/stationApi.ts` | `release(operationId)` POST function | API_CALL | execution flow | keep as deprecated/compat-only, not primary | LOW |
| `frontend/src/app/api/stationApi.ts` | `getClaim(operationId)` GET function | API_CALL | diagnostics | remove if unused; mark deprecated if kept | HIGH |
| `frontend/src/app/pages/StationExecution.tsx` | `claimState = item.claim.state ?? "none"` (line ~250) | LOGIC | ownership gate | replace with `ownership.owner_state + has_open_session` | BLOCKER |
| `frontend/src/app/pages/StationExecution.tsx` | `canExecuteByClaim = claimState === "mine"` (line ~254) | LOGIC | command gate | replace with `ownership.owner_state === "mine" && ownership.has_open_session` | BLOCKER |
| `frontend/src/app/pages/StationExecution.tsx` | `ownedClaimOperationId` calculation (line ~251) | LOGIC | single-claim rule | adapt to ownership session context | HIGH |
| `frontend/src/app/pages/StationExecution.tsx` | All `canXxx` checks derived from `canExecuteByClaim` | LOGIC | action affordance | inherit ownership-based gate | HIGH |
| `frontend/src/app/pages/StationExecution.tsx` | `stationApi.claim()` call before execution | API_CALL | pre-action | remove from primary flow; keep fallback only | BLOCKER |
| `frontend/src/app/components/station-execution/StationQueuePanel.tsx` | `item.claim.state === "mine"` in `matchesQueueFilter` (line ~16) | LOGIC | filter | replace with `ownership.owner_state === "mine"` | HIGH |
| `frontend/src/app/components/station-execution/StationQueuePanel.tsx` | `summary.mine` count uses `item.claim.state === "mine"` (line ~37) | LOGIC | summary display | replace with ownership count | HIGH |
| `frontend/src/app/components/station-execution/StationQueuePanel.tsx` | `hasMineClaim = items.some(item => item.claim.state === "mine")` (line ~42) | LOGIC | queue state | replace with ownership-based check | HIGH |
| `frontend/src/app/components/station-execution/QueueOperationCard.tsx` | `locked = item.claim.state === "other"` (line ~18) | LOGIC | card state | replace with `ownership.owner_state === "other" && has_open_session` | HIGH |
| `frontend/src/app/components/station-execution/QueueOperationCard.tsx` | `isMine = item.claim.state === "mine"` (line ~20) | LOGIC | card display | replace with ownership state | HIGH |
| `frontend/src/app/components/station-execution/QueueOperationCard.tsx` | `claimHint` rendering (line ~22-30) | DISPLAY | UI text | map ownership states to hint text | MEDIUM |
| `frontend/src/app/components/station-execution/StationExecutionHeader.tsx` | `"station.claim.ownedBadge"` label (line ~61) | DISPLAY | badge text | update to ownership label or mark as legacy | LOW |
| `frontend/src/app/components/station-execution/StationExecutionHeader.tsx` | `canReleaseClaim` prop (line ~15) | LOGIC | button enable | adapt to ownership context or mark as compat-only | MEDIUM |
| `frontend/src/app/components/station-execution/AllowedActionZone.tsx` | `canExecuteByClaim` prop gating all actions (line ~19) | LOGIC | action zone | adapt to ownership-based prop or rename | HIGH |
| `frontend/src/app/i18n/registry/en.ts` | `"station.claim.ownedBadge"`, `"station.claim.singleActiveHint"`, `"station.claim.required"`, etc. | I18N | UX text | add ownership-first strings; keep claim for compat | MEDIUM |
| `frontend/src/app/i18n/registry/ja.ts` | Same as en.ts | I18N | UX text | add ownership-first strings; keep claim for compat | MEDIUM |

---

## 3. Cutover Decision

### Primary Owner Truth (H2 → Persistent)

**Frontend will use `ownership` block fields as canonical ownership truth:**

- `ownership.owner_state` (replacing `claim.state` for owner relation)
- `ownership.has_open_session` (indicating active session presence)
- `ownership.operator_user_id` (identifying session operator)
- `ownership.session_id` (identifying active session)

### Compatibility Fallback (H2 → Retained, Defensive)

**Claim fields become fallback only, not authoritative:**

- `claim.state` used ONLY if `ownership` block is absent or null
- `claim.claimed_by_user_id` shown as legacy/diagnostics-only badge
- Claim APIs (`claim()`, `release()`, `getClaim()`) kept in client library but not called in primary execution flow

### Execution Readiness Gating (H2 → Ownership-First)

**Before**: `canExecuteByClaim = claimState === "mine"` (claim is gate)  
**After**: `canExecuteByOwnership = ownership?.owner_state === "mine" && ownership?.has_open_session === true` (ownership is gate)

Fallback (if ownership absent): `canExecuteByClaim` logic as compatibility bridge only.

### UI Labels and Copy (H2 → Ownership-Focused)

| Current Label | Target Label / Strategy |
|---|---|
| "station.claim.ownedBadge" | "You are assigned to this operation" / "Ownership badge" (replace `claim.ownedBadge`) |
| "station.queue.claimedByOther" | "Another operator owns this" / "Operator assigned" (replace `claim` language) |
| "station.claim.singleActiveHint" | "Complete or release current operation before starting another" / remove claim reference |
| "station.claim.required" | map to backend error detail; fallback to "Authorization required" |

---

## 4. Behavior Contract for H2

### Explicit Constraints (Mandatory)

1. **Frontend type cutover only**: No backend schema changes; no API response shape modifications.
2. **Claim compat survival**: Claim fields, routes, service, model, table remain unchanged.
3. **No command behavior drift**: Execution commands (`start_execution`, `report_production`, `pause_execution`, `start_downtime`, `complete_execution`, `resume_execution`, `end_downtime`, `close_operation`) behavior unchanged.
4. **No StationSession guard change**: Seven-command StationSession guard behavior unchanged (deferred to 08H3).
5. **No queue service rewrite**: Backend queue composition unchanged; ownership block consumed as-is.
6. **No migrations**: No DB schema changes.
7. **No claim removal**: Claim code/tests/routes/tables remain in source.

### H2 Responsibility (Frontend Consumer Only)

1. Update `StationQueueItem` type in `frontend/src/app/api/stationApi.ts` to include `ownership: SessionOwnershipSummary`.
2. Update execution readiness logic in `StationExecution.tsx` to prioritize `ownership.owner_state + has_open_session` over `claimState`.
3. Update queue filtering in `StationQueuePanel.tsx` to use `ownership.owner_state` for "mine" filter.
4. Update queue card display in `QueueOperationCard.tsx` to show ownership-based lock/badges.
5. Keep claim API functions in client for backward compat; mark as deprecated/compat-only in comments.
6. Update i18n strings to reflect ownership-first language; keep legacy claim strings for fallback.
7. Stop calling `claim()` / `release()` APIs before execution commands in primary flow.
8. Backend continues to enforce command permission via allowed_actions and route guards.

### H2 Not Responsible For

1. Removing claim from backend (blocked until 08H3+).
2. Removing claim APIs from backend (blocked until 08H4+).
3. Changing command behavior or guard (blocked until 08H3+).
4. Changing queue service/projection (blocked until 08H5+).
5. Changing reopen/resume behavior (blocked until 08H5+).

---

## 5. H2 Verification Plan

### Frontend Checks

```bash
# Static analysis
npm run lint                     # eslint check

# Type check (if available)
npm run typecheck               # typescript check

# Build (if available)
npm run build                   # vite/typescript build
```

### Backend Regression Checks (no backend changes, verify baseline stability)

```bash
# Claim API deprecation lock
pytest -q tests/test_claim_api_deprecation_lock.py

# Queue session-aware contract
pytest -q tests/test_station_queue_session_aware_migration.py

# StationSession command guard
pytest -q tests/test_station_session_command_guard_enforcement.py

# Optional: full suite if time allows
pytest -q
```

### Expected Outcomes

- Frontend lint: **pass**
- Frontend typecheck: **pass** or script unavailable (documented)
- Frontend build: **pass** or unavailable (documented)
- Backend claim deprecation: **pass** (unchanged)
- Backend queue session-aware: **pass** (unchanged)
- Backend command guard: **pass** (unchanged)
- Full suite (optional): **pass** with same baseline as 08F (289 passed, 1 skipped)

---

## 6. Stop Conditions for H2

STOP and report `NEEDS_REDESIGN` if:

- [ ] Backend ownership block fields unavailable or changed
- [ ] Backend API response shape requires modification
- [ ] Frontend cannot distinguish `ownership` from `claim` without backend type support
- [ ] Command behavior drifts during implementation
- [ ] Queue service behavior changes observed
- [ ] Frontend build/lint fails due to unresolved type conflicts
- [ ] Claim removal appears necessary for correctness

PROCEED if:

- [x] Backend ownership block present and stable (confirmed via `backend/app/schemas/station.py`)
- [x] Frontend type system can represent both `ownership` and `claim` distinctly
- [x] Claim compat fallback is viable without harming ownership-first logic
- [x] No backend changes required beyond consumer-side type adaptation
- [x] Claim APIs can remain callable but not authoritative in primary flow

---

## 7. Verdict

### HARD MODE MOM v3 GATE: ALLOW_IMPLEMENTATION

**Decision**: Proceed with P0-C-08H2 implementation.

**Reasoning**:
- Design evidence confirms StationSession is target ownership; claim is compat debt.
- Backend ownership block is complete, stable, and dual-produced with claim.
- Frontend can consume ownership block without backend schema changes.
- Claim compatibility fallback is architecturally viable.
- No behavioral dependencies prevent cutover.
- Stop conditions are not met; preconditions are satisfied.

**Assumptions**:
- Backend responds with `ownership` block on all queue items fetched during H2.
- Frontend can use `ownership.owner_state` and `has_open_session` for execution readiness without ambiguity.
- Claim fields present in response but not used as command authorization truth in primary flow.
- Claim APIs remain callable for diagnostics/fallback but not required for primary execution flow.

**Contingencies**:
- If `ownership` block is absent at runtime in H2, fallback to `claim.state` logic with defensive null checks.
- If new backend API shape is required, reject implementation and update report.
- If command behavior drifts, halt and investigate backend changes.

**Recommended Implementation Order**:
1. Update type in `stationApi.ts` to include `ownership` field
2. Update `StationExecution.tsx` ownership logic (highest risk, most impact)
3. Update queue filtering in `StationQueuePanel.tsx`
4. Update queue card display in `QueueOperationCard.tsx`
5. Update header/actions in `StationExecutionHeader.tsx` + `AllowedActionZone.tsx`
6. Update i18n strings to support ownership-first language
7. Frontend regression checks (lint, build, typecheck)
8. Backend regression checks (claim/queue/guard test trio)
9. Create implementation report with cutover summary
10. STOP after slice completion

---

## 8. Files to Change in H2

| File | Change Type | Reason | Priority |
|---|---|---|---|
| `frontend/src/app/api/stationApi.ts` | TYPE/CODE | Add `ownership: SessionOwnershipSummary` to `StationQueueItem` type; mark claim functions deprecated | P0 |
| `frontend/src/app/pages/StationExecution.tsx` | LOGIC/CODE | Replace claim-based ownership gate with ownership-first logic; update all action readiness checks | P0 |
| `frontend/src/app/components/station-execution/StationQueuePanel.tsx` | LOGIC/CODE | Replace `claim.state === "mine"` with `ownership.owner_state === "mine"` in filter and summary | P1 |
| `frontend/src/app/components/station-execution/QueueOperationCard.tsx` | LOGIC/CODE | Replace claim lock/badge logic with ownership-based logic; add compatibility fallback | P1 |
| `frontend/src/app/components/station-execution/StationExecutionHeader.tsx` | DISPLAY/CODE | Update badge label from claim-focused to ownership-focused; adapt props if needed | P2 |
| `frontend/src/app/components/station-execution/AllowedActionZone.tsx` | LOGIC/CODE | Adapt prop naming/logic to ownership context or document as compat-only | P2 |
| `frontend/src/app/i18n/registry/en.ts` | I18N | Add/update ownership-first strings; keep legacy claim strings for fallback | P2 |
| `frontend/src/app/i18n/registry/ja.ts` | I18N | Add/update ownership-first strings; keep legacy claim strings for fallback | P2 |
| `docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md` | DOC | Create final H2 report with cutover summary, changes, and verification | P3 |

---

## 9. Next Steps

1. ✅ Gate analysis complete; verdict: **ALLOW_IMPLEMENTATION**
2. → Begin implementation (Step 1: type cutover in `stationApi.ts`)
3. → Run frontend verification checks
4. → Run backend regression checks
5. → Create final report
6. → STOP after slice completion (do not start 08H3)

