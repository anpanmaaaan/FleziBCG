# Station Execution Component Map v1

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Created Station Execution component extraction map. |
| 2026-04-30 | v1.1 | Added note: narrow viewport blocker resolved by global app shell responsive drawer work (FE-LAYOUT-01), not Station Execution component logic. |

---

## Cross-Slice Note

The narrow viewport blocker identified in FE-SE-UX-03B (`Layout.tsx` persistent sidebar squeezing Station Execution content) was resolved by **global app shell work** in FE-LAYOUT-01.

This was intentionally fixed in shell components (`Layout.tsx` and `TopBar.tsx`) and not through Station Execution component-level workarounds.

---

## 1. Source Files Inspected

| File | Role | Status |
|---|---|---|
| `frontend/src/app/pages/StationExecution.tsx` | Monolithic page component | Active — all logic, sub-components, and rendering in one file (~1 700 lines) |
| `frontend/src/app/api/stationApi.ts` | Station queue and claim API client | Active — connected |
| `frontend/src/app/api/operationApi.ts` | Execution command API client | Active — connected |
| `frontend/src/app/components/PageHeader.tsx` | Reusable page header shell | Active — used in Mode A |
| `frontend/src/app/components/StatusBadge.tsx` | Status chip component | Active — used throughout |
| `frontend/src/app/components/MockWarningBanner.tsx` | Phase/compatibility warning banner | Active — used in both modes |
| `frontend/src/app/components/ScreenStatusBadge.tsx` | Route status badge | Active — used in Layout |
| `frontend/src/app/screenStatus.ts` | Screen status registry | Active — `stationExecution` entry: PARTIAL/BACKEND_API |
| `frontend/src/app/routes.tsx` | Route registration | Active — `/station` and `/station-execution` |
| `frontend/src/app/persona/personaLanding.ts` | Persona-based routing | Active — OPR/SUP can access |
| `frontend/src/app/i18n/registry/en.ts` | English locale registry | Active — ~60+ `station.*` keys |
| `frontend/src/app/i18n/registry/ja.ts` | Japanese locale registry | Active — mirrored keys |

---

## 2. Current Components to Preserve

These file-local sub-components exist inside `StationExecution.tsx` and work correctly. Do not extract or rename until explicitly planned:

| Component | Lines (approx.) | Preserve reason |
|---|---|---|
| `ReopenOperationModal` | ~50 | Wired to backend reopen; correct behavior; small enough to stay inline for now |
| `StartDowntimeModal` | ~80 | Wired to backend start_downtime + fetchDowntimeReasons; correct behavior |
| `NumericKeypad` | ~60 | Touch keypad overlay for quantity input; self-contained |
| `Stepper` | ~80 | Quantity input stepper with quick-add; self-contained; reusable pattern |
| `QueueList` | ~130 | Queue rendering + filter; functional; candidate for extraction in future slice |
| `KpiCard` | ~15 | Simple stat card; inline, acceptable |
| `TimeCluster` | ~30 | Two-stat time display; inline, acceptable |

---

## 3. Components to Extract

Target extraction plan — ordered by priority and safety. Each row is a potential future implementation slice.

| Component | Purpose | Source Input | Backend Truth Dependency | Reusable? | Build Phase |
|---|---|---|---|---|---|
| `StationExecutionPage` | Top-level page shell; routes between Mode A/B/C/D | Operation state, session state | Session validity (future) | No — page-specific | Current (refactor host) |
| `StationExecutionHeader` | Mode C compact header: station scope, operation name, status badges, controls | `operation`, `stationScope`, handlers | `operation.status`, `operation.closure_status` | No — execution-specific | FE-UI-04 (safe slice) — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/StationExecutionHeader.tsx`. All props typed. No behavior change. Build/lint/routes PASS. |
| `StationQueuePanel` | Full Mode B queue page: summary stats + filter bar + operation card list | `queueItems`, `filter`, `onSelect` | `item.status`, `item.claim` | No — station-specific | FE-SE-UX-02B — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/StationQueuePanel.tsx` |
| `QueueFilterBar` | Filter chip row for queue | `filter`, `onFilterChange`, summary counts | None (local filter state) | Yes — queue-scoped | FE-SE-UX-02B — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/QueueFilterBar.tsx` |
| `QueueOperationCard` | Single queue row: name, number, status badge, claim hint | `StationQueueItem` | `item.status`, `item.claim.state` | Yes — queue-specific | FE-SE-UX-02B — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/QueueOperationCard.tsx` |
| `ExecutionStateHero` | Block 1: operation name, status, downtime banner, closed overlay | `operation`, `getStatusLabel` | `operation.status`, `operation.closure_status`, `operation.downtime_open` | No — execution-specific | FE-SE-UX-02C — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/ExecutionStateHero.tsx` |
| `AllowedActionZone` | Block 4: renders correct action buttons from allowed_actions | `operation`, `canDo`, all action handlers, loading states | `operation.allowed_actions`, `operation.status` | No — critical execution | FE-SE-UX-02C — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/AllowedActionZone.tsx` |
| `QuantitySummaryPanel` | Totals display: good_qty, scrap_qty, remaining | `operation` | `operation.good_qty`, `operation.scrap_qty`, `operation.quantity` | Potentially | FE-SE-UX-02C — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/QuantitySummaryPanel.tsx` |
| `ReportQuantitySection` | Inline steppers + Report Qty button | `goodQty`, `scrapQty`, setters, `reportQuantity`, `canReportProduction` | `allowed_actions.report_production` | No — inline in cockpit | FE-SE-UX-02C |
| `DowntimeStatusPanel` | Full-width downtime banner when active | `downtime_open`, operation detail | `operation.downtime_open` | Yes — signal banner | FE-SE-UX-02D — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/DowntimeStatusPanel.tsx` |
| `StartDowntimeDialog` | Downtime reason dialog (extract from inline modal) | `open`, `onClose`, `onSubmit`, reasons | Downtime master data | Yes — could be reused | FE-SE-UX-02D — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/StartDowntimeDialog.tsx` |
| `EndDowntimeAction` | End downtime single-button | `canEndDowntimeAction`, `endDowntime`, loading | `allowed_actions.end_downtime` | No — inline in action zone | FE-SE-UX-02C |
| `ClosureStatePanel` | Closure status display + close/reopen buttons | `operation.closure_status`, `canCloseOperation`, `canReopenOperation` | `allowed_actions`, `closure_status` | No — execution-specific | FE-SE-UX-02D — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/ClosureStatePanel.tsx` |
| `ReopenOperationModal` | Reopen reason dialog (already inline; extract when cockpit splits) | `open`, `onClose`, `onSubmit`, loading | `allowed_actions.reopen_operation` | No | FE-SE-UX-02D — **EXTRACTED 2026-04-30** into `frontend/src/app/components/station-execution/ReopenOperationModal.tsx` |
| `BlockerReasonPanel` | Blocked state message when no downtime open | `operation.status` | `operation.status = BLOCKED` | Yes | FE-SE-UX-02C |
| `OperationIdentityCard` | Header: WO, PO, started-at context row | `operation` | `operation.work_order_number`, etc. | Potentially | FE-SE-UX-02C |
| `OperationTimelinePanel` | Event history / audit trail (Mode D) | `operationId` → fetch history | `GET /execution/operations/{id}/history` | No | FE-UI-08 (future) |
| `BackendRejectBanner` | Inline rejection reason display | rejection code string | Backend error codes | Yes | FE-SE-UX-02C |
| `StationSessionBanner` | Mode A session-not-available placeholder | None (static) | None yet | No | FE-UI-09 (future placeholder) |
| `OperatorIdentityPanel` | Mode A operator identification (future) | `sessionState` | Backend session API | No | FUTURE — backend required |
| `EquipmentBindingPanel` | Mode A equipment binding (future) | `sessionState` | Backend binding API | No | FUTURE — backend required |
| `EmptyState` | Generic empty state card with optional action | `message`, `action?` | None | Yes — reusable | Any slice |
| `LoadingState` | Generic loading state card | `message` | None | Yes — reusable | Any slice |
| `ErrorState` | Generic error state card with retry | `message`, `onRetry` | None | Yes — reusable | Any slice |

---

## 4. Components Not to Build Yet

Do not extract or build the following until the prerequisite backend or slice work is confirmed:

| Component | Reason to defer |
|---|---|
| `OperatorIdentityPanel` | Backend operator identification API not yet available |
| `EquipmentBindingPanel` | Backend equipment binding API not yet available; policy per station type unclear |
| `StationSessionPanel` (full) | Backend session open/close API (P0-C) not yet available |
| `OperationTimelinePanel` (live) | Backend history API connectivity unconfirmed; do not fake events |
| Quality disposition panel | Backend quality API not integrated in execution flow |
| Acceptance Gate panel | Not implemented in backend |
| AI recommendation panel | Not implemented; must not fake AI decisions |

---

## 5. Props / Data Contract Notes

### StationQueueItem (from stationApi.ts)
```typescript
interface StationQueueItem {
  operation_id: number;
  operation_number: string;
  name: string;
  work_order_number: string;
  production_order_number: string;
  status: OperationExecutionStatus;
  planned_start: string | null;
  planned_end: string | null;
  claim: { state: QueueClaimState; expires_at: string | null; claimed_by_user_id: string | null };
  downtime_open: boolean;
}
```

### OperationDetail (from operationApi.ts)
Key fields for component props:
- `id`, `name`, `operation_number`
- `work_order_number`, `production_order_number`
- `status: OperationExecutionStatus`
- `closure_status: "OPEN" | "CLOSED"`
- `allowed_actions: string[]`
- `quantity`, `completed_qty`, `good_qty`, `scrap_qty`
- `actual_start`, `actual_end`, `planned_start`, `planned_end`
- `downtime_open: boolean`
- `paused_total_ms`, `downtime_total_ms`
- `reopen_count`, `last_closed_at`, `last_closed_by`, `last_reopened_at`, `last_reopened_by`

### canDo pattern
```typescript
const canDo = (action: string) =>
  Array.isArray(operation?.allowed_actions) && operation!.allowed_actions.includes(action);
```
This pattern must be preserved in all extracted components that render action buttons.  
Never replace with local status-based derivation.

---

## 6. i18n Key Groups

| Key group prefix | Coverage | Status |
|---|---|---|
| `station.action.*` | Button labels (claim, release, clockOn, pause, resume, etc.) | Complete |
| `station.queue.*` | Queue titles, filters, summary labels, states | Complete |
| `station.claim.*` | Claim ownership badge, taken warning, single-active hint | Complete (compatibility path) |
| `station.input.*` | Stepper labels, hints, aria labels | Complete |
| `station.timer.*` | Elapsed, target, paused-total, downtime-total | Complete |
| `station.qty.*` | Target, completed, remaining, total good, total scrap | Complete |
| `station.block.*` | Section titles (context, summary, input/reporting, guidance) | Complete |
| `station.hint.nextAction.*` | Contextual guidance messages | Complete |
| `station.downtime.*` | Reason label, note, group prefix, loading, helpers, banners | Complete |
| `station.closure.*` | Section title, open/closed state, helper text | Complete |
| `station.reopen.*` | Dialog copy, audit display, reason fields | Complete |
| `station.toast.*` | Success/failure toast messages | Complete |
| `station.reject.*` | Backend rejection code translations | Partial — add future codes |
| `station.context.*` | WO/PO/startedAt labels | Complete |
| `station.session.*` | Session entry surface (FUTURE PLACEHOLDER strings) | **Missing — add when Mode A placeholder implemented** |
| `station.operator.*` | Operator identification (FUTURE strings) | **Missing — add when Mode A placeholder implemented** |
| `station.equipment.*` | Equipment binding (FUTURE strings) | **Missing — add when Mode A placeholder implemented** |
| `station.detail.*` | Operation detail / Mode D strings | **Missing — add when Mode D placeholder implemented** |
| `station.timeline.*` | Event timeline (FUTURE strings) | **Missing — add when timeline implemented** |
| `station.blocker.*` | Blocked-without-downtime state messages | **Partial — add clear supervisor-contact message** |
| `screenStatus.banner.deprecation.*` | Compatibility path warning | Complete |

---

## 7. Test Targets

Components extracted from StationExecution should eventually have:

| Test target | Test type | Priority |
|---|---|---|
| `canDo()` pattern: returns false when allowed_actions missing | Unit | Critical |
| `canDo()` pattern: returns false when action not in list | Unit | Critical |
| `canDo()` pattern: returns true when action in list | Unit | Critical |
| Queue filter matching: each filter key | Unit | High |
| `isBackendClaimableQueueStatus()` | Unit | High |
| Cockpit does not render action buttons when operation is null | Component | High |
| Cockpit does not render Clock On when closure_status=CLOSED | Component | High |
| Cockpit hides runtime actions when CLOSED | Component | High |
| Downtime banner renders when downtime_open=true | Component | High |
| Downtime banner full-width with only End Downtime action | Component | High |
| Report Qty button disabled when !canReportProduction | Component | High |
| Queue card locked when claim.state=other | Component | Medium |
| KpiCard highlighted for remaining qty | Component | Low |
| TimeCluster shows over-by when elapsed > target | Component | Medium |
| Modal submit disabled until input valid | Component | Medium |
| Reopen modal submit disabled when reason empty | Component | Critical |
| Close button hidden when not in allowed_actions | Component | Critical |

---

## 8. Implementation Slice Recommendation

Slices are ordered by safety and dependency. Each slice should be independently verifiable (build/lint/route smoke).

| Slice | ID | Scope | Safety level | Pre-requisites |
|---|---|---|---|---|
| Mode B header extraction | FE-UI-04 | Extract `StationExecutionHeader` from Mode B header div; preserve all handlers | Low risk — visual only | None (Mode B currently polished) — **COMPLETED 2026-04-30** |
| Queue panel extraction | FE-SE-UX-02B | Extract `StationQueuePanel`, `QueueFilterBar`, `QueueOperationCard` | Medium — preserves queue select logic | FE-UI-04 — **COMPLETED 2026-04-30** |
| Cockpit body split | FE-SE-UX-02C | Extract `ExecutionStateHero`, `AllowedActionZone`, `QuantitySummaryPanel`, `BlockerReasonPanel` | High risk — action zone critical | FE-SE-UX-02B — **COMPLETED 2026-04-30** |
| Closure/downtime dialogs | FE-SE-UX-02D | Extract `ClosureStatePanel`, `StartDowntimeDialog`, `ReopenOperationModal` | Medium — dialogs are self-contained | FE-SE-UX-02C — **COMPLETED 2026-04-30** |
| Operation detail / history panels | FE-SE-UX-02E | Inspect and extract `OperationDetailPanel`, `OperationTimelinePanel`, `BackendRejectBanner` if inline source exists | Low risk — mechanical extraction only | FE-SE-UX-02D — **COMPLETED 2026-04-30. No new components created. Inspection confirmed: no Mode D, no inline operation detail/history rendering, and no inline BackendRejectBanner UI in current StationExecution.tsx. All rejection display is via toast.error() calls. OperationTimelinePanel deferred — backend history API not available. OperationDetailPanel deferred — Mode D not implemented. No behavior change.** |
| Responsive / touch polish | FE-SE-UX-03A | Polish all existing station-execution components for tablet/kiosk/touch usability. Gap, disabled-state, active-scale, touch targets, modal widths, KPI grid responsive, filter bar horizontal scroll, queue summary grid responsive. No behavior change. | Low risk — layout/class changes only | FE-SE-UX-02E — **COMPLETED 2026-04-30. See slice report for full file list.** |
| Mode D placeholder | FE-UI-08 | Add operation detail tab/page with header + qty summary + timeline placeholder | Low risk — no backend needed | FE-SE-UX-03A |
| Mode A placeholder | FE-UI-09 | Add session entry placeholder screen before queue | Low risk — static placeholder | FE-UI-08 |
| Operation timeline (live) | FE-UI-10 | Connect `GET /execution/operations/{id}/history`; render timeline | Backend-dependent | P0-C history API |
| Session/operator/equipment | FE-UI-11 | Implement session open + operator identification when backend P0-C available | Backend-dependent | P0-C session API |

**Current recommended next slice:**
→ **FE-UI-08** — Add Mode D operation detail placeholder surface aligned with current router and screen-status boundaries, without introducing backend-contract assumptions.
