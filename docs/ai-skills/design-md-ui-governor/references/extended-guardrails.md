# Extended Guardrails — FleziBCG UI

> Concerns the original MOM UI guardrails did not cover. These exist because
> FleziBCG runs on a shopfloor, not in a browser tab.

## 1. Offline & Degraded Network

Shopfloor Wi-Fi/Ethernet is not perfectly reliable. UI must degrade gracefully,
not lie.

**Connectivity states the UI must distinguish:**

| State | UI behavior |
|---|---|
| Online + backend healthy | Normal |
| Online + backend slow (>2s ack) | Show inline progress at 500ms; show "Still working…" + cancel at 2s |
| Online + backend errored | Show error in `BlockerBanner` with retry; keep last-known state visible |
| Offline (browser detects) | Top-level banner "Offline — read-only mode"; disable commands; allow read of cached |
| Stale data (no successful refresh in N min) | Last-known data dimmed + stale-since timestamp |

**Rules:**

- Never silently retry a failed command — operator must see and acknowledge.
- Never show "Success" toast until backend has confirmed.
- Never disable the screen entirely on connectivity loss; allow reading the
  last known state.
- Optimistic UI is permitted ONLY for non-state-changing UX (e.g., expanding a
  panel, filtering a list). Backend-truth-affecting commands must wait for
  backend ack.

**Implementation hint:** use a single `useConnectivity()` hook + `<OfflineBanner>`
in the app shell rather than per-screen logic.

---

## 2. Scanner / Barcode Input

Operators use barcode scanners for lot, equipment, operator badge, container,
etc. Scanners emulate keyboard input.

**Required patterns:**

- **Auto-focus the expected input** on screen mount and after every command.
- **Visible "Scanner ready" indicator** so operator knows scan will land.
- **Scan-then-confirm**: scan populates field; operator taps Confirm. No
  auto-submit on destructive or governed actions.
- **Manual fallback** in the same field for when scanner is broken.
- **Debounce** at 50–80ms typical scanner inter-character delay; commit on
  Enter/CR.
- **Echo + Undo** for 5 seconds after each scan.

**Scanner-vs-keyboard heuristic:** if input arrives faster than 50ms/char,
treat as scan. Otherwise treat as manual typing.

**Anti-pattern:** modal with scanner input but no clear focus signal. Operator
scans, nothing happens, scans again, double-submit risk.

---

## 3. Alert Hierarchy & Dedupe

Alert noise is the second-most cited operator complaint (after clutter).

**Severity levels:**

| Level | Display | Sound | Sticky | Dismissal |
|---|---|---|---|---|
| P1 (line stop / safety) | Full-screen modal + sound | Yes | Yes | Requires reason code |
| P2 (station blocked) | `BlockerBanner` (top of screen) | Optional | Until cleared | One-tap ack |
| P3 (advisory / soon) | Inline status badge + toast | No | Toast 6s | Auto-dismiss |
| P4 (info) | Inline note | No | No | None |

**Dedupe rules:**

- Same alert (same `alertId`) firing twice within 60s → suppress second display.
- Same alert source (same `stationId`) firing different `alertId` within 5s →
  group into one banner with "+N more".
- Acknowledged alerts re-fire only on new occurrence after ack timestamp.

**Anti-pattern:** stacking toasts. Maximum 1 toast visible at a time; subsequent
queue and replace.

---

## 4. Multi-Station Scaling

A supervisor may watch 10–50+ stations. Naive rendering is unacceptable.

**Rules:**

- Use `react-window` for grids/lists with >12 cells.
- Each cell renders at most 60–80ms (measure with React Profiler).
- Use stable keys; avoid index keys for stations.
- Throttle live updates to ≤2 Hz per cell; coalesce updates within 500ms
  windows.
- Provide density tiering: `comfortable` (12 cells), `compact` (24), `tight`
  (48). Above 48 → switch to list view.

**Anti-pattern:** real-time SSE updating every cell on every event. Use a
debounced reducer + `react-window`.

---

## 5. Long-Running Operations

Lot runs can take hours. Some commands (close session, post to ERP) can take
seconds to minutes.

**Patterns:**

- Operations <500ms: no progress UI, just inline button spinner.
- 500ms–5s: inline progress on the button + global progress bar in header.
- 5s–60s: dedicated progress panel with current step text + estimated time +
  cancel button.
- >60s: convert to backgrounded job with a job-status surface; allow operator
  to leave the screen.

**Anti-pattern:** modal "Please wait…" that blocks the entire UI for 30s.
Operator cannot escape; cannot see other state.

---

## 6. Optimistic UI Boundary

Tension with "backend is source of truth" rule.

**Allowed optimistic updates** (no backend truth at stake):

- Local UI state: expanded/collapsed panels, filter chips, sort order.
- Form field focus, draft text.
- Cursor position, scroll offset, table column width.

**Disallowed optimistic updates** (backend owns truth):

- Execution state transitions (RUNNING → COMPLETED).
- Quality decisions (PASSED / FAILED / HOLD).
- ERP posting confirmation.
- Acceptance gate approval.
- Permission changes.
- Resource binding (operator/equipment/lot).

**Reconciliation rule:** when an optimistic update is disallowed by backend,
revert UI to backend truth and surface the rejection in `BlockerBanner`. Do
not silently swallow rejection.

---

## 7. Governed Action Confirmation

Some actions are governed (acceptance gate, quality release, scrap, override).
These need confirmation patterns beyond a simple "Are you sure?".

**Pattern:**

```
[Trigger action]
  → AlertDialog opens
    - Reason for action (Select or text input, required for some)
    - Confirmer identity check (current user displayed)
    - "Type STATION_ID to confirm" for destructive (Cmd-K-style typed confirm)
    - Cancel (default focus) | Confirm (requires interaction)
  → On Confirm: command sent to backend
  → On Backend reject: BlockerBanner with reason
```

**E-signature note:** full 21 CFR Part 11 e-sig is a future scope. For phase 1,
use the typed-confirm pattern + audit log (backend records `actorId`,
`actionId`, `reason`, `timestamp`).

---

## 8. Audit Trail Surfacing

When the user takes a governed action or views a governed entity, the audit
log must be reachable in ≤2 taps.

- Detail screens for lot, work order, session, quality hold, ERP posting, etc.
  have a "Audit log" drawer or tab.
- Audit entries: actor, action, timestamp (with timezone), source (UI / API /
  system), correlation ID.
- No editing or deletion of audit entries in UI.
- Export to CSV/PDF is acceptable for offline review.

---

## 9. Multi-Tenant / Scope Awareness

Many users work across multiple tenants/lines/cells.

- Always display the current scope in the header (e.g., "Plant A / Line 2").
- Scope switcher in user menu; opening it does not lose unsaved form state
  (warn first).
- Cross-scope leakage is a security incident — backend must enforce, but UI
  should not display scope-mismatched data even on stale API responses.

---

## 10. Print and Export

Some operators print run sheets, lot tickets, defect reports.

- Use `@media print` styles; do not invent a separate print template.
- Hide sidebar, header buttons, and interactive controls.
- Show: title, scope, generated timestamp, generated-by user, content.
- Page break before each major section.
- For long lists, paginate; do not stretch to single huge page.

---

## 11. Accessibility Beyond WCAG Numbers

- Every actionable element has a Radix-provided or explicit `aria-label`.
- Modal/Dialog focus trap (Radix `Dialog` handles this).
- Escape closes any top dialog; does not close root app.
- Tab order matches visual reading order.
- Screen reader announces state transitions (use `aria-live="polite"` for
  status updates, `assertive` for blocker arrival).
- Reduce-motion preference honored (see industrial-ux-standards § 8).

---

## 12. Time Display

Manufacturing happens in shifts across timezones.

- Display times in the **station's local timezone** by default, not user's.
- Show timezone abbreviation next to time when it differs from user's locale.
- Use 24-hour format on operator screens (no AM/PM confusion).
- Relative time ("3 min ago") for events <1 hour; absolute time for older.
- Always store and transmit in UTC; convert at display only.
