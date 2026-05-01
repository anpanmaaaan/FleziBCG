# Station Execution Redesign Contract v1

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Created full Station Execution redesign contract. |

---

## 1. Purpose

This contract defines the target UX design for the Station Execution surface as a source-aligned, backend-truth-safe redesign.

It covers:
- current baseline behavior and known problems
- target operator experience
- screen/mode model
- information architecture
- state/action display contracts
- quantity reporting, downtime, close/reopen, blocker UX
- i18n, accessibility, and touch requirements
- MOM safety rules
- build-now vs placeholder vs future matrix
- acceptance criteria for implementation

This document does **not** change backend behavior.  
This document does **not** implement frontend code.  
It is a design contract only.

---

## 2. Current Source Baseline

### 2.1 Source file
`frontend/src/app/pages/StationExecution.tsx`

### 2.2 Route
- Primary: `/station`
- Compatibility alias: `/station-execution`

### 2.3 Screen status
- Phase: `PARTIAL`
- Data source: `BACKEND_API`
- Note in screenStatus: "Execution actions are connected to the real API. This screen uses the compatibility claim model. Target design is session-owned execution (STX-000/001/002 v4.0)."

### 2.4 Current modes
The current screen operates in two modes:

**Mode A — Operation Selection**
- Shows a queue list of operations
- Operator selects or manually enters an operation
- Claim-model: operator claims an operation before executing
- Includes manual entry fallback field

**Mode B — Execution Cockpit**
- Triggered when operator claims an operation
- Shows compact inline header (station scope, operation name, status, claim badge, controls)
- Shows hero summary card (WO/PO context, KPIs, time cluster)
- Shows quantity input/reporting section (steppers with keypad)
- Shows closure/reopen section when applicable
- Shows guidance callout (state-contextual next-action text)
- Shows primary action zone (Clock On / Pause / Resume / Start Downtime / End Downtime / Complete)

### 2.5 Backend connections (confirmed connected)
- `stationApi.getQueue()` — queue list
- `stationApi.claim()` — claim compatibility path
- `stationApi.release()` — release compatibility path
- `stationApi.getOperationDetail()` — operation detail
- `operationApi.start()` — start execution
- `operationApi.pause()` — pause execution
- `operationApi.resume()` — resume execution
- `operationApi.complete()` — complete execution
- `operationApi.reportQuantity()` — report production
- `operationApi.startDowntime()` — start downtime
- `operationApi.endDowntime()` — end downtime
- `operationApi.close()` — close operation
- `operationApi.reopen()` — reopen operation
- `fetchDowntimeReasons()` — master data

### 2.6 Compatibility / deprecated elements
- Claim/release pattern (`claim_operation`) is deprecated target; retained as compatibility debt
- `isExecutionMode` derived from `claimState === "mine"` — compatibility logic
- `canExecuteByClaim` — compatibility guard
- Queue filter "mine" — claim-model concept

### 2.7 Missing from current implementation
- No station session open/close
- No operator identification
- No equipment binding
- No operation history/timeline view
- No per-operation detail tab beyond inline cockpit data

### 2.8 Inline sub-components (currently file-local)
- `ReopenOperationModal`
- `StartDowntimeModal`
- `NumericKeypad`
- `Stepper`
- `QueueList`
- `KpiCard`
- `TimeCluster`

---

## 3. UX Problems to Solve

### P-01 — No station session entry surface
The target model (STX-000) requires opening a station session before work begins. There is no UI for this. Operators jump directly to the queue.

### P-02 — No operator identification surface
The target model requires an identified operator within the session. Operator identity is not collected or shown.

### P-03 — No equipment binding surface
Equipment binding is target-model required where policy mandates it. No UI surface exists.

### P-04 — Claim model leaks into UX
Claim-owned concepts (mine/other/none, single-active-claim warning, release button) are visible to operators as first-class concepts. Target model removes these.

### P-05 — No operation history / timeline
There is no inline timeline/event history panel in the current cockpit, despite the backend likely having an event log. Operators cannot see recent activity without leaving the screen.

### P-06 — Mode B header is compact but cramped
Even after FE-UI-03B polish (h-10/sm:h-11), the five header controls remain visually crowded at tablet widths. The header mixes context information and control buttons in the same row.

### P-07 — Guidance message is low-priority
The guidance callout (added in FE-UI-03A) correctly shows next-action text, but is placed after the input section, meaning on small screens it may appear below the fold.

### P-08 — Status color alone does not communicate urgency clearly enough
BLOCKED and PAUSED states could be more visually prominent at factory-floor distance.

### P-09 — No future-gap labels on unimplemented features
Session panel, operator identity, and equipment binding have no placeholder/future labels in the current UI. If they appear, they would look like working features.

### P-10 — Downtime state is not visually dominant
When `downtime_open` is true, only a small badge shows in the header. The cockpit body does not visually shift to communicate that execution is halted.

---

## 4. Target Operator Experience

The target Station Execution UX must:

1. **Feel session-aware.** The operator knows which station they are working at, who they are identified as, and what is bound.
2. **Be action-oriented.** The dominant visual element at all times is the next required action. The operator never has to scan to find what to do.
3. **Communicate blockers first.** If execution is blocked (downtime, hold, closed), that state dominates the visual layout — it is not a small badge.
4. **Not lie about state.** No button appears enabled unless the backend says it is allowed. No status label implies success before the backend responds.
5. **Be readable at distance.** Key numbers (remaining qty, status, current operation) are large. Secondary context (PO/WO numbers, audit trails) are smaller.
6. **Work touch-first.** Primary actions are at least 56px tall. Tap targets are never smaller than 44px. No critical control is hover-only.
7. **Not overwhelm.** Maximum 4 information blocks per screen state. No dense dashboard.

---

## 5. Screen / Mode Model

The redesigned Station Execution surface uses four named modes/panels.

### Mode A — Station Session Entry (STX-000)

**Purpose:** Open or restore an active station session, identify operator, bind equipment where required.

**When shown:**
- No active station session exists for this station
- Operator enters the station execution surface for the first time in a shift

**Primary information:**
- Station identity (code, name)
- Session state (no session / active session summary)
- Identified operator (if session already has one)
- Equipment context (if session already has one)

**Actions:**
- `open_station_session` → Backend-required. Currently not implemented. Show as FUTURE until P0-C session API exists.
- `identify_operator` → Backend-required. Currently not implemented. Show as FUTURE.
- `bind_equipment` → Backend-required/optional by policy. Currently not implemented. Show as FUTURE.
- Enter queue → Available once session/operator context is satisfied (or via compatibility path while claim model is active)

**Safety rules:**
- Do not invent a fake session locally
- Do not pre-fill operator from JWT without backend confirmation
- Equipment binding disabled placeholder must be clearly labeled "Future / requires backend support"

**Current implementation note:**
- No current Mode A equivalent. Current code jumps directly to queue.
- Implement this mode as a **FUTURE PLACEHOLDER ONLY** in the current redesign slice. Show "Station session is not yet available" notice and route directly to queue for compatibility.

---

### Mode B — Station Queue (STX-001)

**Purpose:** Show queued operations for the active station. Allow operator to select work.

**When shown:**
- Operator is in the station execution surface
- No operation is actively executing (or operator has backed out to selection)

**Primary information:**
- Queue summary: ready/paused/blocked/downtime counts
- Queue rows: operation name, number, WO/PO reference, status, claim hint (compatibility phase only)
- Active-selection highlight
- Filter bar

**Actions:**
- Select operation → navigate to cockpit
- Refresh queue
- Filter queue
- Manual operation ID entry (compatibility fallback only)

**No first-class claim action in target UX.** In the current compatibility path, the claim affordance remains but should be visually de-emphasised (not a primary CTA).

**Safety rules:**
- Do not show claim as a permanent primary action in redesigned UX
- Do not mark operations as claimable by deriving from status alone
- Queue counts come from backend response
- Claim state `state: "other"` → show locked indicator, do not enable

---

### Mode C — Execution Cockpit (STX-002)

**Purpose:** Run the primary execution lifecycle for the selected operation.

**When shown:**
- Operator has selected an operation (and claimed it in compatibility path)
- Execution is active, paused, blocked, or completed

**Layout structure (four blocks, ordered by priority):**

#### Block 1 — State Hero
Full-width, top.  
- Operation name (large)
- Execution status (large badge, color + text)
- Closure status badge (if CLOSED, visually dominant warning)
- Downtime banner (if downtime_open, full-width red/amber banner — NOT a small badge)
- WO / PO reference (smaller, below operation name)
- Operator identity (when available from session — shown as future placeholder now)

#### Block 2 — Guidance / Next Action
Sticky or near-top.  
- Guidance message (contextual, from `guidanceMessage` computed field)
- Error rejection reason (if last command was rejected)
- Compatibility path warning (MockWarningBanner — always visible in cockpit)

#### Block 3 — KPIs + Timer
Grid: Target qty / Completed qty / Remaining qty / Time cluster.  
- Large numbers, readable at distance
- Timer live-increments when IN_PROGRESS
- Paused-total and downtime-total shown when relevant
- Total-good and total-scrap shown as secondary row

#### Block 4 — Action Zone + Quantity Input
- Primary action buttons: Clock On / Pause / Resume / Complete / End Downtime
- Secondary actions: Start Downtime (when available)
- Quantity input steppers (when IN_PROGRESS and reporting allowed)
- Report Qty button (when reporting allowed)
- Closure/Reopen section (when applicable)

**Controls header (separate from blocks):**
- Station scope label
- Back to Queue
- Refresh
- Queue overlay toggle
- Release claim (compatibility path — visually de-emphasised, behind a separator)

**Blocked/Downtime visual state override:**
When `status = BLOCKED` and `downtime_open`:
- Block 1 changes to dominant RED downtime banner
- Block 4 shows only END DOWNTIME as primary action
- All other actions are hidden (not disabled — hidden, to reduce clutter)

When `status = PAUSED` with no downtime:
- Block 1 shows amber PAUSED state
- Block 4 shows RESUME as primary action and START DOWNTIME as secondary

**Closed state visual override:**
When `closure_status = CLOSED`:
- Block 1 shows black CLOSED badge
- All runtime action buttons hidden/disabled
- Closure block dominates action zone

**Safety rules:**
- All action button availability reads from `allowed_actions`
- After any mutation, refetch backend truth
- Never prefill quantities from backend total — deltas only
- Do not hide close/reopen section when backend returns it as available

---

### Mode D — Operation Detail / History (STX-004)

**Purpose:** Show deeper operational context, event timeline, and audit view.

**When shown:**
- Operator/supervisor taps "Detail" from cockpit
- Navigation target from other screens

**Primary information:**
- Operation header (same as cockpit block 1)
- Quantity summary
- Event timeline (from `GET /execution/operations/{id}/history`)
- Closure/audit trail (close/reopen history)

**Current implementation note:**
- Not implemented in current code. History API connectivity unknown.
- Implement as PARTIAL with static "Event timeline is not yet available" placeholder.
- Show operation header and quantity summary from existing data.
- No fake events.

---

## 6. Information Architecture

```
Station Execution Surface
├── [Mode A] Station Session Entry         ← FUTURE PLACEHOLDER
│   ├── Session state banner
│   ├── Operator identification panel      ← FUTURE PLACEHOLDER
│   └── Equipment binding panel            ← FUTURE PLACEHOLDER
├── [Mode B] Station Queue
│   ├── Queue summary stats
│   ├── Queue filter bar
│   └── Queue operation cards
├── [Mode C] Execution Cockpit
│   ├── Controls header (back/refresh/queue/release)
│   ├── Compatibility warning banner
│   ├── Block 1: State Hero
│   ├── Block 2: Guidance / Rejection
│   ├── Block 3: KPIs + Timer
│   ├── Block 4: Action Zone + Qty Input
│   └── Closure / Reopen section
└── [Mode D] Operation Detail              ← PARTIAL PLACEHOLDER
    ├── Operation header
    ├── Quantity summary
    └── Event timeline placeholder
```

---

## 7. State Display Contract

| Status | Block 1 color | Badge text | Dominant visual |
|---|---|---|---|
| `PLANNED` | Blue-50 | "Planned" | Blue badge, Clock On button visible |
| `IN_PROGRESS` | Green-50 | "In Progress" | Green badge, production reporting active |
| `IN_PROGRESS` + downtime_open | Red-100 | "Downtime" | Red full-width banner overrides |
| `PAUSED` | Amber-50 | "Paused" | Amber badge, Resume button visible |
| `PAUSED` + downtime_open | Red-100 | "Downtime" | Red full-width banner |
| `BLOCKED` + downtime_open | Red-100 | "Downtime Active" | Red full-width banner |
| `COMPLETED` | Slate-50 | "Completed" | Slate badge, runtime actions hidden |
| `ABORTED` | Slate-50 | "Aborted" | Slate badge, all actions hidden |
| Any + `closure_status=CLOSED` | Slate-900 (black) | "Closed" | Black CLOSED overlay on Block 1 |

**Rules:**
- Status badge always shows text + color, never color only
- Downtime open state takes visual precedence over execution status in Block 1
- CLOSED state takes visual precedence over everything
- Do not invent status values not returned by backend
- Do not derive action legality from the displayed status text

---

## 8. Action Display Contract

All primary action buttons are driven by `allowed_actions` from the backend response.

| Action | Backend key | Display when | Disabled when |
|---|---|---|---|
| Clock On | `start_execution` | status=PLANNED | not in allowed_actions OR closure=CLOSED |
| Pause | `pause_execution` | status=IN_PROGRESS | not in allowed_actions |
| Resume | `resume_execution` | status=PAUSED, no downtime | not in allowed_actions |
| Start Downtime | `start_downtime` | status=IN_PROGRESS or PAUSED | not in allowed_actions |
| End Downtime | `end_downtime` | downtime_open=true | not in allowed_actions |
| Report Qty | `report_production` | status=IN_PROGRESS | not in allowed_actions |
| Complete | `complete_execution` | status=IN_PROGRESS | not in allowed_actions |
| Close | `close_operation` | closure_status=OPEN + in allowed_actions | not in allowed_actions |
| Reopen | `reopen_operation` | closure_status=CLOSED + in allowed_actions | not in allowed_actions |
| Release (compat.) | n/a (local claim) | claimState=mine + PLANNED | not canReleaseClaim |

**Rules:**
- If `allowed_actions` is empty or absent (operation not yet loaded), no action buttons render
- After mutation, refetch `operation` and `queue` before re-rendering action zone
- Backend rejection reason codes must be surfaced via toast or inline banner
- Never show a primary action as enabled if backend would reject it

---

## 9. Quantity Reporting UX

**Inputs:**
- Good quantity delta (non-negative integer)
- Scrap quantity delta (non-negative integer)

**Controls:**
- Stepper with ± buttons, direct tap-to-keypad
- Quick-add buttons: +1, +5, +10, +20 for good; +1, +2, +5 for scrap
- Reset to 0 button

**Rules:**
- Inputs are **deltas for the next report**, not cumulative totals
- Reset to 0 on operation change or after successful report
- Submit disabled unless at least one delta > 0
- Submit disabled unless `report_production` in `allowed_actions`
- Report Qty button: minimum 56px height in cockpit
- On successful report: reset both steppers; backend refetch
- On failed report: show backend rejection; do not reset
- Display cumulative good/scrap (from backend `good_qty`, `scrap_qty`) separately as read-only

**Touch behavior:**
- Keypad overlay: full-screen centered, clear OK / CLR buttons, min 56px keys
- Stepper ± buttons: min 48px × 48px each

---

## 10. Downtime UX

### 10.1 Start Downtime Dialog
- Reason code: dropdown or list from backend master data (`fetchDowntimeReasons()`)
- Note: required when `requires_comment=true`, optional otherwise
- If master data load fails, show error + retry, disable submit
- Submit calls `start_downtime`; wait for backend before closing modal
- On success: close modal, refetch operation and queue

### 10.2 Downtime Active State
When `downtime_open = true`:
- Render a full-width RED/AMBER banner at the top of the cockpit body (Block 1)
- Banner text: "Downtime Active" + reason summary if available
- END DOWNTIME is the only primary action in the action zone
- All other runtime actions are hidden (not merely disabled)
- Report Qty inputs are hidden

### 10.3 End Downtime
- Single large button "End Downtime"
- Calls `end_downtime`; wait for backend before resetting state
- On success: hide banner, refetch, restore normal action zone
- On rejection: show rejection code

---

## 11. Close / Reopen UX

### 11.1 Close Operation
- Show "Close Operation" button only when `close_operation` in `allowed_actions`
- Require `window.confirm()` as a simple confirmation in current implementation (future: inline modal)
- After success: refetch; show CLOSED state visual override

### 11.2 Reopen Operation
- Show "Reopen Operation" button only when `reopen_operation` in `allowed_actions`
- Opens `ReopenOperationModal` requiring a non-empty reason string
- Reason is mandatory — submit disabled until non-empty
- After success: refetch; restore OPEN state

### 11.3 Closed state visual rules
- `closure_status = CLOSED` → render black CLOSED overlay on Block 1
- All runtime execution actions (start/pause/resume/report/downtime) are hidden
- Close/Reopen section remains visible
- If neither close nor reopen is in `allowed_actions`, show read-only closed message

### 11.4 Invariant — never fake close/reopen
- Close button must not appear enabled unless backend returns it in `allowed_actions`
- Reopen button must not appear enabled unless backend returns it in `allowed_actions`
- Closed-record mutation rejection (`STATE_CLOSED_RECORD`) must surface to operator

---

## 12. Blocker / Hold / Error UX

### 12.1 BLOCKED + downtime_open
- Full-width red downtime banner
- Action zone shows only END DOWNTIME

### 12.2 BLOCKED without downtime
- Status badge shows BLOCKED in red
- Action zone shows no primary action (backend currently doesn't enable any)
- Show guidance message: "Operation is blocked. Contact your supervisor."
- Do not invent an unblock action

### 12.3 Backend command rejection
- Display rejection error codes from backend:
  - `STATE_INVALID_TRANSITION` → "This action is not available for the current operation state."
  - `STATE_CLOSED_RECORD` → "This operation is closed. Reopen to continue."
  - `SESSION_REQUIRED` → "No active station session. Please open a session." (future)
  - `OPERATOR_IDENTIFICATION_REQUIRED` → "Operator not identified. Please identify operator." (future)
  - `EQUIPMENT_BINDING_REQUIRED` → "Equipment not bound. Please bind equipment." (future)
  - `REASON_CODE_INVALID` → "Selected downtime reason is no longer valid."
  - `FORBIDDEN` → "You do not have permission to perform this action."
- Show via toast (current pattern) or inline banner near the action that failed

### 12.4 Hold state
- Not currently implemented in backend projection
- If a `HOLD` status is later introduced, it must appear as a read-only blocking state with supervisor-required resolution
- Do not invent a hold release action

---

## 13. Empty / Loading / Error States

### Loading states
- Initial queue load: Spinner or skeleton row list; do not show empty queue message during load
- Operation load: Spinner or "Loading operation…"; do not show empty operation during load
- Downtime reasons load: Show "Loading reasons…" in dropdown; disable submit

### Empty states
- Queue empty: "No operations in queue for this station." with Refresh button
- Queue filtered empty: "No operations match this filter." with clear-filter affordance
- Operation not found: "Operation not found or no longer available." with Back to Queue

### Error states
- Queue load failed: "Queue could not be loaded." with Refresh button
- Operation load failed: "Operation details could not be loaded." with Retry / Back
- Downtime reasons failed: "Could not load downtime reasons." with retry; disable submit

---

## 14. i18n Requirements

All user-visible strings must use `useI18n` and have keys in both `en.ts` and `ja.ts`.

### Key groups to complete or add
- `station.session.*` — session entry surface strings (future placeholder text)
- `station.operator.*` — operator identification strings (future placeholder)
- `station.equipment.*` — equipment binding strings (future placeholder)
- `station.blocker.*` — blocked state messages
- `station.reject.*` — backend rejection code translations
- `station.detail.*` — operation detail/history strings
- `station.timeline.*` — event timeline strings

### Existing key groups to preserve
- `station.action.*`
- `station.queue.*`
- `station.claim.*`
- `station.input.*`
- `station.timer.*`
- `station.qty.*`
- `station.block.*`
- `station.hint.*`
- `station.downtime.*`
- `station.closure.*`
- `station.reopen.*`
- `station.toast.*`

---

## 15. Accessibility / Touch Requirements

### Touch targets
- Primary action buttons (Clock On, Pause, Resume, End Downtime, Complete): **minimum 56px height**
- Secondary action buttons (Start Downtime, Close, Reopen): **minimum 48px height**
- Header/control buttons: **minimum 44px height** (already `h-10 sm:h-11`)
- Stepper ± buttons: **minimum 48×48px**
- Keypad keys: **minimum 56×56px**

### Visual clarity
- Status badge always text + color
- Disabled buttons use `disabled:opacity-40 cursor-not-allowed`
- Blocked/downtime state changes must be visible at 3m distance on a factory-floor display

### ARIA
- Icon-only buttons must have `aria-label`
- Modal dialogs must trap focus
- Alert-level banners use `role="alert"`

### Color contrast
- Critical state colors (red, amber) must not be the only differentiator — text must also differ
- Minimum contrast ratio 4.5:1 for all body text

---

## 16. MOM Safety Rules

| Rule | Requirement |
|---|---|
| MON-SAFE-01 | Frontend must not decide execution legality from status text alone |
| MON-SAFE-02 | Action buttons must read from `allowed_actions` where connected |
| MON-SAFE-03 | After mutation, refetch backend truth before re-rendering action zone |
| MON-SAFE-04 | Backend rejection codes must surface to operator |
| MON-SAFE-05 | Do not invent claim/session/operator context locally |
| MON-SAFE-06 | Closed records must reject all runtime execution writes |
| MON-SAFE-07 | Do not fake QC, Acceptance Gate, Backflush, ERP posting, or AI decisions |
| MON-SAFE-08 | Operator identification / equipment binding must be backend-confirmed |
| MON-SAFE-09 | Do not derive authorization from persona/role display alone |
| MON-SAFE-10 | Timeline events must come from backend — no synthetic history |

---

## 17. Build Now / Placeholder / Future Matrix

| Feature | Build Status | Notes |
|---|---|---|
| Station Queue (Mode B) | **BUILD NOW** | Connected and working; improve UX only |
| Execution Cockpit (Mode C) | **BUILD NOW** | Connected and working; improve UX only |
| Quantity Reporting | **BUILD NOW** | Connected and working; improve UX only |
| Downtime Dialog | **BUILD NOW** | Connected and working; improve UX only |
| Close / Reopen | **BUILD NOW** | Connected and working; preserve behavior |
| Backend rejection surfacing | **BUILD NOW** | Improve clarity of existing toast pattern |
| Guidance callout (FE-UI-03A) | **DONE** | Already implemented |
| Mode B header polish (FE-UI-03B) | **DONE** | Already implemented |
| Station Session Entry (Mode A) | **PLACEHOLDER** | Requires backend P0-C session API; show "Session not yet available" notice |
| Operator Identity Panel | **PLACEHOLDER** | Requires backend session API + operator lookup |
| Equipment Binding Panel | **PLACEHOLDER** | Requires backend binding API |
| Operation Detail / Timeline (Mode D) | **PARTIAL PLACEHOLDER** | Show header + qty summary; timeline: "Event history not yet available" |
| Quality Hold Release | **FUTURE** | Not implemented — disabled placeholder only |
| Exception / Disposition | **FUTURE** | Not implemented |
| Acceptance Gate | **FUTURE** | Not implemented |
| Pre-Acceptance Check | **FUTURE** | Not implemented |
| Backflush | **FUTURE** | Not implemented |
| ERP Posting | **FUTURE** | Not implemented |
| AI Recommendation Actions | **FUTURE** | Not implemented |
| Digital Twin State | **FUTURE** | Not implemented |

---

## 18. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Claim model still active in backend; deprecation path unclear | High | Do not remove claim logic in UI; keep compatibility path visible with warning |
| Backend history/timeline API existence unconfirmed | Medium | Implement Mode D as placeholder only; do not fake events |
| Backend session API (P0-C) not yet available | High | Mode A is placeholder only; route directly to queue via compatibility path |
| Operator identification not yet in backend | High | Do not collect operator identity before backend is ready |
| Equipment binding policy varies by station type | Medium | Treat as optional placeholder; do not hardcode binding requirement |
| Large single-file StationExecution.tsx becomes hard to maintain | Medium | Component extraction plan (see component map) phased over slices |
| `window.confirm()` for close/reopen poor on kiosk | Low | Replace with inline modal in a future slice; acceptable now |

---

## 19. Acceptance Criteria

The Station Execution redesign implementation is accepted when:

1. Mode B (Queue) and Mode C (Cockpit) behavior is unchanged for all currently connected operations.
2. All action buttons read from `allowed_actions` where the backend returns them.
3. Close/reopen behavior is preserved exactly — no regression.
4. Downtime banner overrides cockpit body visually when `downtime_open = true`.
5. CLOSED state visual override prevents runtime actions from appearing enabled.
6. Mode A (Session Entry) is rendered as a PLACEHOLDER — no fake session behavior.
7. Mode D (Detail/History) is rendered as PARTIAL — header and qty summary shown; timeline shows "not yet available".
8. All new visible strings are in i18n registries.
9. No hardcoded product-critical copy exists.
10. Responsive behavior meets the targets in the responsive contract.
11. Touch targets meet minimum sizes defined in Section 15.
12. Build passes, lint passes, route smoke 24/24 passes.
13. No production source code changes until implementation slices are approved.
