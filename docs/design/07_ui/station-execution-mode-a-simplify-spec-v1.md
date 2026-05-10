# Station Execution — Mode A Simplification Spec

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-10 | v1.0 | Initial spec for `FE-SE-MODEA-SIMPLIFY-09`. Authored after operator/PO feedback that current Station Session Mode A UI is cluttered (`feedback_station_session_ui_clutter`). DOC-ONLY slice; FE implementation gated on slice acceptance. |
| 2026-05-10 | v1.1 | Patched per PO conditional sign-off verdict. Corrections: (1) IR-01 close-confirm ownership lock; (2) IR-02 remove `commandError` prop from `OpenSessionPanel`; (3) IR-05 UNKNOWN error surface unified to top banner only; (4) D-05/IR-06 rename `canEnterQueue` → `canNavigateToQueueByVisibleSetupState` to honor BT-CORE-004 (visibility ≠ authorization); (5) D-09/IR-11 a11y — `aria-hidden` on decorative symbols, `focus-visible` on row buttons + primary CTA; (6) IR-11 border rule replaced with idiomatic Tailwind `border-t border-slate-200`; (7) §10/§11/§15 unit-test gate made conditional on runner availability. No decision reversed; all v1.0 directions preserved. |

---

## Routing

- Selected brain: MOM Brain (Station Execution UI)
- Selected mode: Product / UI / Implementation contract
- Hard Mode MOM: v3 ON
- Reason: Slice changes operator-facing setup composition, error surfacing, and primary-CTA logic. Touches multiple pages and i18n surfaces; must remain backend-truth-safe and avoid breaking deep-link routes.

---

## Slice ID

`FE-SE-MODEA-SIMPLIFY-09`

---

## Status

Draft for implementation. Awaiting PO approval.

This slice supersedes nothing. It refines composition of existing Mode A surface in line with `station-execution-redesign-contract-v1.md` §4.1, `station-execution-ui-contract-v4.md` §4.1, and `station-shopfloor-token-system-v1.md` Principle 3 (One Primary Action Per Mode).

---

## 1. Purpose

Reduce visual clutter and information redundancy in the Station Session (Mode A) operator surface.

Concretely:

1. Replace the current 8-section vertical stack with a single 3-row card pattern.
2. Remove duplicate context display between `StationWorkflowShell` and `StationEntryPanel`.
3. Consolidate command-error display to a single banner.
4. Surface a single primary CTA ("Enter queue") with deterministic enable/disable rule.
5. Fix the stage-logic bug that flags an open session as `STX_009_END_SESSION`.

Out of intent: this slice does not modal-ize operator identification or equipment binding (defer to a follow-up slice). Routes remain unchanged.

---

## 2. Non-Negotiable Truth Boundaries

Inherited from `station-execution-redesign-contract-v1.md` §16 and `station-execution-ui-contract-v4.md` §2:

1. Backend remains source of truth for session state, operator identity, and equipment binding.
2. Frontend sends intent only; frontend never derives session/operator legality from local state.
3. Frontend renders backend-derived `StationSessionItem` and ownership context.
4. No new authorization rules.
5. No new event schema or projection behavior.
6. No backend command/state/API changes.

---

## 3. Source-of-Truth Precedence Used in This Spec

1. User feedback (2026-05-10): Mode A is "rối" — see `feedback_station_session_ui_clutter`.
2. `docs/design/07_ui/station-execution-redesign-contract-v1.md` (target operator experience and screen-mode model).
3. `docs/design/07_ui/station-execution-ui-contract-v4.md` (canonical screen contract, three-screen flow).
4. `docs/design/07_ui/station-execution-screen-pack-v4.md` (STX-000 purpose).
5. `docs/design/07_ui/station-shopfloor-token-system-v1.md` (visual hierarchy, action hierarchy, density).
6. `docs/design/02_domain/execution/station-session-ownership-contract.md` (StationSession aggregate boundary).
7. `docs/governance/CODING_RULES.md` (engineering rules, lint/build/route gates).

No conflict identified between these sources for the Mode A composition decisions in this spec.

---

## 4. Baseline Evidence

### Source files inspected

| File | Role | Observed problem |
|---|---|---|
| `frontend/src/app/pages/StationSession.tsx` | Mode A page (285 lines) | Renders 8 sections vertically; duplicate context tokens vs Shell; commandError surfaced in 2 places + toast; stage-logic bug at line ~186 |
| `frontend/src/app/components/station-execution/StationWorkflowShell.tsx` | Generic shell with stage chips + 4 context cards | Compact mode still renders 4 context cards even when `StationEntryPanel` shows the same fields below |
| `frontend/src/app/components/station-execution/StationEntryPanel.tsx` | Mode A 4-card setup checklist | Redundant with Shell's 4 context cards |
| `frontend/src/app/components/station-execution/OpenSessionPanel.tsx` | Session card | Inline `commandError` block duplicates Shell `recoveryBanner` |
| `frontend/src/app/components/station-execution/IdentifyOperatorPanel.tsx` | Wrapper | 44 lines for one route-nav button |
| `frontend/src/app/components/station-execution/BindEquipmentPanel.tsx` | Wrapper | Same pattern as Operator |
| `frontend/src/app/components/station-execution/CloseSessionPanel.tsx` | Close confirm | OK; no change needed by this slice |
| `frontend/src/app/pages/OperatorIdentification.tsx` | Standalone route page | Out of scope; uses its own `StationWorkflowShell` |
| `frontend/src/app/pages/EquipmentBinding.tsx` | Standalone route page | Out of scope; uses its own `StationWorkflowShell` |
| `frontend/src/app/routes.tsx` | Route registry | Routes `/station-session`, `/operator-identification`, `/equipment-binding` registered; preserved by this slice |
| `frontend/src/app/screenStatus.ts` | Screen registry | `stationSession.phase = "CONNECTED"` |
| `frontend/src/app/i18n/registry/en.ts` | English locale | `stationSession.*` keys present (≥30) |

### Component reuse inventory

`StationWorkflowShell` is used by 4 pages:
- `pages/StationSession.tsx` (Mode A) — **remove use in this slice**
- `pages/OperatorIdentification.tsx` — keep
- `pages/EquipmentBinding.tsx` — keep
- `pages/StationExecution.tsx` (Mode B) — keep

`StationEntryHandoff` is used by 3 pages (OperatorIdentification, EquipmentBinding, StationExecution). Mode A does not currently use it. **Not touched by this slice.**

`StationEntryPanel` is used only by `pages/StationSession.tsx`. Once removed from Mode A, the file has no consumers.

---

## 5. Problems to Solve

| ID | Problem | Source observation |
|---|---|---|
| P-01 | 4 context tokens (station/session/operator/equipment) rendered twice in different formats — once in `StationWorkflowShell` compact mode, once in `StationEntryPanel` checklist. | Lines 77-94 of `StationWorkflowShell.tsx` vs lines 54-89 of `StationEntryPanel.tsx`. |
| P-02 | 8 vertical sections of equal visual weight; no primary card; no clear next-step focus. | `StationSession.tsx` render function lines 162-280. |
| P-03 | The same `commandError` is rendered in three places: Shell `recoveryBanner` slot, `OpenSessionPanel` inline block, and `toast.error()`. | `StationSession.tsx` lines 192-199, `OpenSessionPanel.tsx` lines 70-79, `StationSession.tsx` line 42. |
| P-04 | Mode A primary CTA ("Enter queue") is buried inside a sub-section blue card alongside helper text rather than a top-level affordance. | `StationSession.tsx` lines 252-266. |
| P-05 | Stage-logic bug: when session is OPEN, `currentStage` is set to `STX_009_END_SESSION`, but operator may still need to identify operator or bind equipment. Stage UI mismatches business state. | `StationSession.tsx` line 186. |
| P-06 | `IdentifyOperatorPanel` and `BindEquipmentPanel` are 40-50 line components for what is functionally a single status row + nav button each. | `IdentifyOperatorPanel.tsx` (44 lines), `BindEquipmentPanel.tsx`. |
| P-07 | Empty state when `stationId` is missing: 4 visual elements (Shell tokens empty + yellow notice + EntryPanel checklist not_confirmed + gray "no active session") for one piece of information. | `StationSession.tsx` lines 210-221. |

---

## 6. Decisions Locked by This Spec

### D-01 — Drop `StationWorkflowShell` from Mode A
Rationale: Stage chips and context tokens are pre-cockpit redundant. Mode A is a 3-step in-page wizard, not a multi-stage execution surface.
Affected files: `pages/StationSession.tsx` only.
`StationWorkflowShell` component itself is not removed; other pages continue to use it.

### D-02 — Drop `StationEntryPanel` from Mode A
Rationale: 4-card checklist is redundant with inline status indicators per row.
Affected files: `pages/StationSession.tsx`. Component file `components/station-execution/StationEntryPanel.tsx` is left in place but becomes orphan; flagged for removal in a future cleanup slice (`FE-SE-DEAD-CODE-01`).

### D-03 — 3-row single card pattern for Session / Operator / Equipment
Rationale: Aligns with token-system Principle 3 (One Primary Action Per Mode) and Principle 7 (max 4 information blocks).
Pattern: one `<section>` with three numbered rows; each row carries its own status pill, primary fact line, and inline action button. Rows are separated by a single 1px top border (Tailwind `border-t border-slate-200`, see IR-11), not full card breaks.

### D-04 — Single error banner at top of Mode A page
Rationale: Reduces visual noise; matches `redesign-contract` §12.3 which says rejection codes should appear inline near the failing action OR via toast — not both.
Behavior:
- `commandError !== null` → render top banner with title + message + recovery (1 banner).
- Toasts retained for **success** confirmations only (`stationSession.toast.opened`, `stationSession.toast.closed`).
- Toast on **failure** is removed for command-guard codes; `commandError` banner is sufficient. Keep generic toast only for fallback unknown errors.
- `OpenSessionPanel` must not render its own inline error block.
- Any reuse of `StationWorkflowShell.recoveryBanner` slot is unaffected (other pages keep current behavior).

### D-05 — Primary CTA "Enter queue" is the only top-level CTA
Rationale: Operator next action is queue entry. End-session is destructive secondary; reachable via inline End-session button on the Session row, not as a primary CTA.
Enable rule (UI navigation readiness only — **not backend approval**): `stationId && session?.status === "open" && session.operator_user_id` (operator identified). Equipment is optional unless `equipmentChecklistState === "required_missing"` — in that case CTA disabled with helper text explaining equipment requirement.
Disable hint: helper text below the CTA describes the missing prerequisite, not a generic "not ready".

**Truth-boundary note (BT-CORE-004)**: Enable rule is **UI navigation readiness only**. It does not authorize execution and does not imply backend approval. Backend revalidates session/operator/equipment context on every execution mutation command per `station-session-command-guard-enforcement-contract.md`. The CTA only governs whether the operator may navigate from Mode A to the Queue surface; even when enabled, the backend may still reject a downstream execution command if context drifts.

### D-06 — Operator and Equipment routes preserved
Rationale: Backward compatibility for deep-link, supervisor override, screenStatus registry. This slice does not modal-ize them.
Behavior: `IdentifyOperatorPanel` and `BindEquipmentPanel` continue to navigate to `/operator-identification` and `/equipment-binding`. They are simplified to inline status rows in Mode A; the full route page UI remains.
Modal-ization is deferred to slice `FE-SE-MODEA-MODAL-10`.

### D-07 — Stage-logic bug closed by D-01
Rationale: Removing `StationWorkflowShell` from Mode A makes the stage assignment moot. No need to compute `currentStage` for Mode A. Other pages (`OperatorIdentification`, `EquipmentBinding`, `StationExecution`) retain their own stage logic, which is unaffected.

### D-08 — Empty state simplification
Rationale: When `stationId` is missing, render exactly one notice card explaining the missing parameter and how to acquire it. No Shell, no checklist, no session card.
Pattern: yellow/amber notice with `role="alert"`, title, message, and a single "Back to landing" or "Go to dashboard" action.

### D-09 — Single-row compose: status pill vocabulary
For each row, status pill uses one of:
- ● Open (emerald) — for session status
- ● Identified (emerald) — for operator
- ● Bound (emerald) — for equipment
- ○ Not yet (amber) — for required-but-missing
- − Optional (slate) — for equipment when policy says optional
- ○ Not confirmed (slate) — for unloaded state

Status pill text uses i18n keys; do not hardcode English. New keys allowed under `stationSession.row.status.*` namespace.

**A11y note**: The decorative symbols (●, ○, −) are visual only. They MUST be wrapped in `<span aria-hidden="true">` so screen readers announce only the i18n status text. Color is not the sole differentiator — text label is the screen-reader source of truth and the visual fallback for color-blind operators.

---

## 7. Scope

### In Scope

1. Refactor `pages/StationSession.tsx` to single-card 3-row pattern per D-03.
2. Drop `StationWorkflowShell` and `StationEntryPanel` from Mode A page (D-01, D-02).
3. Consolidate error display to top banner (D-04).
4. Move primary CTA to bottom of card as a single full-width button (D-05).
5. Adjust empty state for missing `stationId` (D-08).
6. Remove inline error block from `OpenSessionPanel.tsx` (D-04 enforcement).
7. Update `IdentifyOperatorPanel.tsx` and `BindEquipmentPanel.tsx` to render as inline rows fitting the new 3-row card (smaller footprint, no own border).
8. Add new i18n keys under `stationSession.row.*` (status, hint) and `stationSession.cta.*` (enter queue, helper text). Keep existing keys for backward compatibility.
9. Build/lint/route/i18n gates pass.
10. Test coverage adjustments to match new composition.

### Explicitly Out of Scope

1. Modal-ization of OperatorIdentification or EquipmentBinding — separate slice `FE-SE-MODEA-MODAL-10`.
2. Removal of `StationEntryPanel.tsx` file from repo — separate cleanup slice.
3. Any change to `pages/OperatorIdentification.tsx`, `pages/EquipmentBinding.tsx`, `pages/StationExecution.tsx`.
4. Backend / API / event / projection changes.
5. New routes, route deletions, or route renames.
6. `screenStatus.ts` phase change (remains `CONNECTED`).
7. `StationWorkflowShell` API changes (still used by other pages).
8. `StationEntryHandoff` changes.
9. Andon, takt strip, time-in-state additions.
10. A11y modal/touch-target work — covered by `FE-SE-A11Y-04`.
11. Dark mode, theme, animation tokens.
12. Persona/role visibility changes.

---

## 8. Files / Areas to Inspect

### Must edit

| File | Type of change |
|---|---|
| `frontend/src/app/pages/StationSession.tsx` | Major composition refactor |
| `frontend/src/app/components/station-execution/OpenSessionPanel.tsx` | Remove inline `commandError` block; adjust to fit row layout |
| `frontend/src/app/components/station-execution/IdentifyOperatorPanel.tsx` | Adjust to fit row layout; smaller footprint |
| `frontend/src/app/components/station-execution/BindEquipmentPanel.tsx` | Adjust to fit row layout; smaller footprint |
| `frontend/src/app/i18n/registry/en.ts` | Add `stationSession.row.*` and `stationSession.cta.*` keys |
| `frontend/src/app/i18n/registry/ja.ts` | Mirror en.ts keys |

### Must inspect (read-only verification)

| File | Reason |
|---|---|
| `frontend/src/app/components/station-execution/StationWorkflowShell.tsx` | Verify other pages still work after Mode A drops it |
| `frontend/src/app/components/station-execution/StationEntryPanel.tsx` | Confirm it has no other consumer after Mode A change |
| `frontend/src/app/components/station-execution/CloseSessionPanel.tsx` | Confirm no change required |
| `frontend/src/app/components/station-execution/stationCommandErrorMessages.ts` | Confirm `normalizeStationCommandError` API surface unchanged |
| `frontend/src/app/api/stationApi.ts` | Confirm `getCurrentSession`, `openSession`, `closeSession` signatures unchanged |
| `frontend/src/app/routes.tsx` | Confirm routes preserved |
| `frontend/src/app/screenStatus.ts` | Confirm phase unchanged |

### Must NOT edit

- `frontend/src/app/pages/OperatorIdentification.tsx`
- `frontend/src/app/pages/EquipmentBinding.tsx`
- `frontend/src/app/pages/StationExecution.tsx`
- Any backend file
- Any contract under `docs/design/02_domain/execution/`

---

## 9. Implementation Rules

### IR-01 — `pages/StationSession.tsx` target shape

The page renders, top-down:

1. `<header>` block — h1 "Station setup" + ScreenStatusBadge + Refresh button.
2. (Conditional) `<aside role="alert">` — single error banner if `commandError !== null`.
3. (Conditional) Empty-state card if `!stationId` — replace all subsequent rendering.
4. `<section>` 3-row card containing Session / Operator / Equipment rows, separated by `border-t border-slate-200` (1px) per IR-11.
5. `<button>` primary CTA "Enter queue" full-width below the card.
6. (Conditional) `<p>` helper text below CTA explaining what is missing if disabled.

Removed from page:
- `<StationWorkflowShell ...>` wrapper.
- `<StationEntryPanel ...>` block.
- Inline blue "Continue to queue" sub-card.
- Subtitle paragraph (folded into header).

**Close-session ownership (single owner — locked)**:

- The Session row's "End session" button **only triggers close intent** by calling `onEndSessionClick()` which sets `showCloseConfirm = true`.
- `<CloseSessionPanel />` (the existing component) **owns** the confirmation dialog UI, the `closing` loading state, and the call to `stationApi.closeSession(...)` via `onConfirmClose`.
- `<CloseSessionPanel />` continues to render at page level **as a sibling of the 3-row card**, not nested inside it. It only renders its dialog when `showCloseConfirm === true` and `session?.status === "open"`.
- `OpenSessionPanel` (the Session row) **must not** duplicate confirm-modal logic. It does not own `closing`, does not call `stationApi.closeSession`, and does not render any confirmation surface.
- Page-level state owns: `commandError`, `closing`, `opening`, `showCloseConfirm`, `loading`.

This ensures exactly one component owns the close lifecycle and prevents two parallel close paths.

### IR-02 — Session row composition

Inputs (props passed to `OpenSessionPanel` after refactor): `session?.session_id`, `session?.status`, `session?.opened_at`, `loading`, `opening`, `onOpenSession`, `onEndSessionClick`, `onRefresh`.

**Removed from props** (versus v1.0 / current code):
- `commandError` — banner is owned by parent page (IR-05). Row receives no error prop.
- `closing` — owned by `<CloseSessionPanel />` (IR-01).
- `stationId` — derive disabled state from session-related props only.

If a "disabled because of recent error" visual cue is required, the parent page may pass a `disableActions: boolean` flag, but **never the full `commandError` object**.

Layout:
- Step number badge (1)
- Title "Session" + status pill (Open / Closed / Missing / Loading)
- Subtext: `#{session_id} · opened {opened_at} · {elapsed}` when open; "No active session" when missing
- Right-aligned action button:
  - When `status === "open"` → `End session` (secondary, calls `onEndSessionClick` → parent flips `showCloseConfirm` → `<CloseSessionPanel />` handles dialog)
  - When no session → `Open session` (primary blue, action `onOpenSession`)
  - When session is closed → `Open new session` (primary blue, action `onOpenSession`)

The Session row may live as the existing `OpenSessionPanel.tsx` adapted to render as a `<div>` (not its own `<section>`) so it can sit inside the parent `<section>` card. **Drop the inline error block** (D-04 + IR-05). Drop the `Power` icon header — replaced by step-number badge.

### IR-03 — Operator row composition

Inputs: `session?.operator_user_id`, `session?.status` (must be open), `onIdentifyOperator`.

Layout:
- Step number badge (2)
- Title "Operator" + status pill (Identified / Not yet / Not confirmed)
- Subtext: operator user id when identified; "No operator identified" when missing; "Open session first" when no session
- Right-aligned action button: `Identify ▶` when session is open and operator missing; hidden when session is missing or operator already identified

Adapted from `IdentifyOperatorPanel.tsx`. Drop the `User` icon header. Drop the section border.

### IR-04 — Equipment row composition

Inputs: `session?.equipment_id`, `equipmentChecklistState`, `session?.status`, `onBindEquipment`.

Layout:
- Step number badge (3)
- Title "Equipment" + status pill (Bound / Not yet / Optional / Not confirmed)
- Subtext: equipment id when bound; policy-driven hint when optional; "Required for this station" when required but missing
- Right-aligned action button: `Bind ▶` when session is open and equipment is missing or required-missing; hidden when bound or session not open or fully optional

Adapted from `BindEquipmentPanel.tsx`. Drop section border and own header.

### IR-05 — Single error banner

`commandError` derived from `normalizeStationCommandError`. When non-null:

```jsx
<aside
  role="alert"
  className={`rounded-lg border px-4 py-3 ${
    commandError.severity === "danger"
      ? "border-red-200 bg-red-50 text-red-800"
      : "border-amber-200 bg-amber-50 text-amber-800"
  }`}
>
  <p className="font-semibold">{t(commandError.titleKey)}</p>
  <p className="mt-1 text-sm">{t(commandError.messageKey)}</p>
  <p className="mt-1 text-xs">{t(commandError.recoveryKey)}</p>
</aside>
```

`OpenSessionPanel.tsx` removes its own version of this block.

**Single error surface — locked**:

| Error class | Surface | Toast? |
|---|---|---|
| Normalized command-guard codes (`STATION_SESSION_*`, `EQUIPMENT_*`, `AUTH_SCOPE_FAIL`, `OPERATION_CLOSED`, `STATE_*`, `OPERATION_QUALITY_HOLD_OPEN`) | Top banner only | No |
| `UNKNOWN` fallback (no normalized code matched) | Top banner only (with generic title/message/recovery from `FALLBACK_ERROR` template in `stationCommandErrorMessages.ts`) | No |
| Network failure / fetch rejection | Top banner only (treated as `UNKNOWN`) | No |
| Operation success (`opened`, `closed`) | No banner | Yes (existing toast retained) |

Rule: failure → exactly one banner, never a toast. Success → exactly one toast, never a banner. This eliminates the double-display problem (P-03) for both known and unknown error paths.

### IR-06 — Primary CTA enable rule (UI navigation readiness only)

**Naming requirement**: the local variable **must** be named `canNavigateToQueueByVisibleSetupState` (or equivalent making the navigation-readiness intent explicit). Do not name it `canEnterQueue`, `canExecute`, `isReady`, `isAuthorized`, or any term that implies backend authorization.

```ts
// Visible setup readiness — UI navigation gating only.
// Does NOT imply backend approval. Backend revalidates on every execution
// command per station-session-command-guard-enforcement-contract.md.
const canNavigateToQueueByVisibleSetupState =
  Boolean(stationId) &&
  session?.status === "open" &&
  Boolean(session?.operator_user_id) &&
  equipmentChecklistState !== "required_missing";

const navigationBlockedHint =
  !stationId
    ? t("stationSession.cta.helper.selectStation")
    : !session
    ? t("stationSession.cta.helper.openSession")
    : session.status !== "open"
    ? t("stationSession.cta.helper.openSession")
    : !session.operator_user_id
    ? t("stationSession.cta.helper.identifyOperator")
    : equipmentChecklistState === "required_missing"
    ? t("stationSession.cta.helper.bindEquipment")
    : null;
```

CTA renders disabled with hint when `navigationBlockedHint !== null`; enabled with no hint otherwise.

**Implementation rule**: a comment block (or JSDoc) above the variable declaration must reference BT-CORE-004 and explicitly state "UI navigation readiness only — not backend authorization". This protects future readers from re-introducing visibility-as-permission patterns.

### IR-07 — Empty stationId state

When `!stationId`:

```jsx
<aside role="alert" className="rounded-lg border border-amber-200 bg-amber-50 p-4 sm:p-5">
  <p className="font-semibold text-amber-900">{t("stationSession.empty.missingStation.title")}</p>
  <p className="mt-1 text-sm text-amber-800">{t("stationSession.empty.missingStation.message")}</p>
  <button onClick={() => navigate("/")} className="mt-3 min-h-11 ...">{t("stationSession.empty.missingStation.cta")}</button>
</aside>
```

No Session/Operator/Equipment rows rendered. No `StationWorkflowShell`. No `StationEntryPanel`.

### IR-08 — i18n keys

Add (do not rename existing):

```
stationSession.row.session.title
stationSession.row.session.subtext.open
stationSession.row.session.subtext.missing
stationSession.row.session.action.open
stationSession.row.session.action.endSession
stationSession.row.operator.title
stationSession.row.operator.subtext.identified
stationSession.row.operator.subtext.missing
stationSession.row.operator.subtext.sessionFirst
stationSession.row.operator.action.identify
stationSession.row.equipment.title
stationSession.row.equipment.subtext.bound
stationSession.row.equipment.subtext.optional
stationSession.row.equipment.subtext.required
stationSession.row.equipment.subtext.sessionFirst
stationSession.row.equipment.action.bind
stationSession.row.status.open
stationSession.row.status.identified
stationSession.row.status.bound
stationSession.row.status.notYet
stationSession.row.status.optional
stationSession.row.status.notConfirmed
stationSession.cta.enterQueue
stationSession.cta.helper.selectStation
stationSession.cta.helper.openSession
stationSession.cta.helper.identifyOperator
stationSession.cta.helper.bindEquipment
stationSession.empty.missingStation.title
stationSession.empty.missingStation.message
stationSession.empty.missingStation.cta
```

Existing keys (`stationSession.setup.title`, `stationSession.setup.checklist.*`, `stationSession.setup.section.*`, `stationSession.setup.continue.*`) remain in the registry but become orphan. They are flagged for cleanup in a future i18n hygiene slice (`FE-I18N-HYGIENE-01`); do not delete in this slice.

`registry/ja.ts` mirrors all new keys.

### IR-09 — Stage-logic bug

The bug is closed transitively by IR-01 (Shell removed from Mode A). No `currentStage` computation remains in `pages/StationSession.tsx`. Verify by grep that `STX_009_END_SESSION` is no longer set in this file.

### IR-10 — Component file lifecycle

- `StationEntryPanel.tsx`: file remains in repo, no consumers after this slice. Add a header comment in repo TODO convention:
  ```ts
  // TODO(FE-SE-DEAD-CODE-01): Remove this file. No consumers as of FE-SE-MODEA-SIMPLIFY-09 (2026-05-10).
  ```
  Use the same convention for any other deprecated artifact added by this slice.
- `OpenSessionPanel.tsx`: kept; refactor to row-friendly shape (no own `<section>` border, no own error block, no `commandError`/`closing` prop).
- `IdentifyOperatorPanel.tsx`, `BindEquipmentPanel.tsx`: kept; refactor to row-friendly shape.
- `CloseSessionPanel.tsx`: kept unchanged in this slice. Continues to render at page level as a sibling of the 3-row card; owns the close-confirm dialog (IR-01).

### IR-11 — Visual tokens

Apply `station-shopfloor-token-system-v1.md` rules:
- Step badge: 28px circle with backgrounds `bg-emerald-50/text-emerald-900` (done), `bg-slate-100/text-slate-700` (current), `bg-slate-50/text-slate-400` (pending).
- Status pill: 12px text, 2px vertical / 8px horizontal padding, rounded-md, color per state.
- Action button hit area: minimum 44px height for row buttons. Primary CTA "Enter queue" minimum 56px (per token-system).
- Border between rows: use idiomatic Tailwind utility `border-t border-slate-200` (1px) on each row except the first. Do not specify `0.5px` arbitrary values unless the project introduces a hairline token in the future. No gap between rows; rows share the parent `<section>` card.
- **Focus-visible (mandatory)**: every interactive element (row action buttons, primary CTA "Enter queue", End-session button, Refresh button, empty-state CTA) MUST include focus-visible styling. Use one of these idiomatic Tailwind classes consistently across this slice:
  - `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2`
  - or equivalent token-system-conformant focus ring.
  Default browser outline is often suppressed by Tailwind reset; explicit focus-visible rings are required for keyboard-only operators.
- **Decorative symbol a11y**: any visual ●, ○, − symbol used in status pills MUST be wrapped in `<span aria-hidden="true">`. The text label adjacent (e.g., "Open", "Not yet", "Optional") is the screen-reader source of truth.

---

## 10. Tests Required

**Test runner availability rule (per v1.1 patch)**:

- If frontend unit-test runner is configured and green on autocode (verify: `npm test -- --run` exits 0 on the autocode baseline before this slice), **all Component tests below are mandatory**.
- If runner is missing, broken, or quarantined, the FE agent MUST:
  1. Document the gap in the implementation report.
  2. Replace each Component test with a grep/source-assertion equivalent (see `Source assertion` column).
  3. Run the lint/build/route/i18n gates plus a manual walk-through documented in the implementation report.

| Test | Preferred type | Source-assertion fallback | Priority |
|---|---|---|---|
| Mode A renders 1 card with 3 rows when `stationId` present and session open | Component | Grep `pages/StationSession.tsx`: exactly one `<section ...>` wraps the 3 rows; no `<StationWorkflowShell` import | Critical |
| Mode A renders 1 amber notice when `stationId` is missing — no Shell, no rows | Component | Grep: empty-state path renders `role="alert"` and short-circuits before row rendering | Critical |
| `commandError` non-null → exactly 1 alert banner rendered (not duplicated in OpenSessionPanel) | Component | Grep `OpenSessionPanel.tsx`: no `commandError` prop in interface; no inline `<aside role="alert">` block | Critical |
| Primary CTA disabled when `!session?.operator_user_id` | Component | Grep: variable name `canNavigateToQueueByVisibleSetupState` exists; disabled binding ties to it | Critical |
| Primary CTA disabled when `equipmentChecklistState === "required_missing"` | Component | Grep: `equipmentChecklistState !== "required_missing"` appears in enable rule | High |
| Primary CTA enabled when session open + operator identified + equipment ok | Component | Manual walk-through in implementation report | Critical |
| Primary CTA helper text reflects missing prerequisite | Component | Grep: `navigationBlockedHint` switch covers all 5 cases per IR-06 | High |
| Session row "End session" button visible when `session.status === "open"` | Component | Manual walk-through | High |
| Session row "Open session" button visible when no session | Component | Manual walk-through | High |
| Operator row "Identify" hidden when `!session?.status === "open"` | Component | Manual walk-through | High |
| Equipment row hidden when session is missing | Component | Manual walk-through | Medium |
| Toast does NOT fire for normalized command-guard codes (`STATION_SESSION_*`, `EQUIPMENT_*`) | Component | Grep `pages/StationSession.tsx`: `toast.error` calls only inside the unmatched-code branch (or removed entirely) | High |
| `UNKNOWN` fallback also surfaces via banner only, not toast | Component | Grep: error path always sets `commandError`, never calls `toast.error` for failure | High |
| `STX_009_END_SESSION` no longer assigned in `StationSession.tsx` | Lint/grep | `grep -n "STX_009_END_SESSION" frontend/src/app/pages/StationSession.tsx` returns no match | Critical |
| `aria-hidden="true"` present on every decorative status symbol | Component | Grep: `aria-hidden="true"` count ≥ number of status pills rendered | High |
| Focus-visible class present on row action buttons + primary CTA + End-session + empty-state CTA | Component | Grep: `focus-visible:` class applied per IR-11 to each interactive element | High |
| Existing `OperatorIdentification` and `EquipmentBinding` route smoke unchanged | Smoke | Smoke gate is mandatory (independent of unit-test runner) | Critical |
| Existing `StationExecution` cockpit smoke unchanged | Smoke | Smoke gate is mandatory | Critical |

---

## 11. Verification Commands

**Mandatory gates** (must pass in all cases):

```bash
cd frontend
npm run build                       # PASS required
npm run lint                        # 0 errors required
npm run check:routes                # 24/24 PASS required
npm run lint:i18n:registry          # PASS, en/ja sync, no orphan-key explosion
```

**Conditional gate** (per v1.1 test runner availability rule in §10):

```bash
# Run only if unit-test runner is configured and green on autocode baseline.
# If runner is missing or broken, document as gap in implementation report
# and replace with grep/source assertions per §10 fallback column.
npm test -- --run                   # all tests pass when applicable

# Optional, run if available:
npm run a11y:scan                   # 0 serious/critical on /station-session
```

**Mandatory manual walk-through** (document evidence in implementation report regardless of unit-test outcome):

- with `?stationId=ST-WELD-04` and an open session containing operator → CTA enabled, no banner
- with `?stationId=ST-WELD-04` and no session → CTA disabled, helper "Open session"
- with no `stationId` → 1 amber notice only, no Shell, no row card
- triggering a session-required command failure at this surface → exactly 1 banner, no toast
- triggering an UNKNOWN error (e.g., simulate network failure) → exactly 1 banner with fallback copy, no toast
- successful session open → 1 success toast, no banner
- keyboard-only walkthrough: Tab through rows, Enter on each button, focus ring visible at every step

---

## 12. Documentation Updates

This slice updates these doc surfaces:

1. `docs/design/07_ui/station-execution-mode-a-simplify-spec-v1.md` — this file (canonical for this slice).
2. `docs/audit/fe-se-modea-simplify-09-implementation-report.md` — to be authored by FE agent at slice close, per project audit format.
3. No update required for `redesign-contract-v1.md`, `ui-contract-v4.md`, `screen-pack-v4.md`, `token-system-v1.md`, `component-map-v1.md`, `andon-proposal-v1.md`, `workflow-redesign-contract-v1.md`. Those remain canonical and unchanged.
4. `feedback_station_session_ui_clutter` memory entry remains active; mark "Slice candidate: ... created" once spec is accepted.

---

## 13. Risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-01 | Removing Shell from Mode A causes test regressions in pages that share Shell stage logic | Medium | Inspect Shell stage state — Shell takes `currentStage` as prop; removing one consumer does not affect others. Verify with build + route smoke. |
| R-02 | i18n key explosion (≥30 new keys) causes registry diff to dominate review | Medium | Keep new keys under one namespace `stationSession.row.*` and `stationSession.cta.*`; reuse `station.handoff.state.*` if possible to avoid duplicates. |
| R-03 | Operator/Equipment route nav becomes the only path to identify; if a tablet has flaky network the route round-trip degrades UX | Low | Acceptable for this slice; modal-ization deferred to FE-SE-MODEA-MODAL-10. |
| R-04 | Removed inline error block in `OpenSessionPanel` may reveal that error never reached top banner due to state ordering | Medium | Lift `commandError` state to page level (already there) and ensure single source of truth. Add component test to lock. |
| R-05 | Orphan `StationEntryPanel.tsx` file may confuse contributors | Low | Add deprecated header comment; tracker for FE-SE-DEAD-CODE-01. |
| R-06 | `CloseSessionPanel` removal from page-level rendering may break the close-confirm flow if Session row's End-session button does not invoke the same confirm | Medium | Either keep `CloseSessionPanel` inline-rendered when session open, or have Session row reuse `CloseSessionPanel`'s confirm modal. Test required. |
| R-07 | A11y: removing Shell removes `recoveryBanner` slot; new top banner must remain `role="alert"` and announce on appearance | Medium | IR-05 enforces `role="alert"`. Add unit test asserting role. |

---

## 14. Stop Conditions

Stop implementation immediately if any of the following occurs. Author a stop-condition report and return to PO before resuming.

1. Existing `OperatorIdentification` or `EquipmentBinding` route page test fails after Mode A refactor.
2. `StationWorkflowShell` API change is required to make this slice work — Shell must remain unchanged.
3. New i18n keys exceed 35 (revisit consolidation strategy).
4. `screenStatus.ts` requires a phase change — out of scope.
5. The Session row "End session" path cannot be made functional without altering `CloseSessionPanel.tsx` significantly (>30 lines diff). Revisit D-03 row composition.
6. Build, lint, route smoke, or i18n registry gate fails after refactor.
7. Any backend, command, event, or projection change is required.
8. PO feedback during review changes a locked decision (D-01..D-09) — re-spec, do not implement on the fly.

---

## 15. Acceptance Criteria

The slice is accepted when all of the following hold:

1. `pages/StationSession.tsx` renders exactly 3 row entries within a single shared `<section>` card (verified by component test).
2. `StationWorkflowShell` is not imported by `pages/StationSession.tsx`.
3. `StationEntryPanel` is not imported by `pages/StationSession.tsx`. The component file may remain orphan with a deprecation comment (IR-10).
4. `commandError` is rendered in exactly one location at any given time.
5. Toast on failure no longer fires for normalized command-guard codes; success toasts retained.
6. Primary CTA "Enter queue" is the only top-level full-width CTA on the page; helper text reflects missing prerequisite when disabled.
7. Empty state for missing `stationId` renders exactly one notice card.
8. `STX_009_END_SESSION` does not appear anywhere in `pages/StationSession.tsx`.
9. Routes `/station-session`, `/operator-identification`, `/equipment-binding`, `/station` remain registered and reachable.
10. Mandatory gates pass on autocode: `npm run build`, `npm run lint`, `npm run check:routes`, `npm run lint:i18n:registry`. Unit-test gate `npm test -- --run` passes **if and only if the runner is configured and was green on the autocode baseline before this slice**; otherwise the gap is documented in the implementation report and replaced by grep/source assertions per §10.
11. Manual walk-through (3 scenarios in §11) confirms expected behavior.
12. FE implementation report `docs/audit/fe-se-modea-simplify-09-implementation-report.md` is authored and references this spec by slice ID.
13. No backend file is modified.
14. No file under `docs/design/02_domain/` is modified.

---

## 16. Definition of Done (slice doc)

For this spec doc itself:

- File exists at `docs/design/07_ui/station-execution-mode-a-simplify-spec-v1.md`.
- History table records v1.0 entry.
- All 9 decisions (D-01..D-09) are explicit and self-consistent.
- All 7 problems (P-01..P-07) are mapped to at least one decision.
- All 11 implementation rules (IR-01..IR-11) are concrete enough for an FE agent to implement without further questions.
- All 16 test items (§10) are scoped to this slice (no cockpit, no backend).
- Stop conditions and acceptance criteria are verifiable by grep + automated gates + manual walk-through.
- PO sign-off captured in spec history before FE implementation begins.

---

## 17. Related Slices

| Slice | Status | Relation |
|---|---|---|
| `FE-SE-A11Y-04` | Proposed (review #1) | Independent; modal/touch-target a11y. May be merged before or after; no shared file conflict expected with this slice. |
| `FE-SE-MODEA-MODAL-10` | Future, not yet specced | Convert OperatorIdentification + EquipmentBinding pages into modal-launchable components; depends on this slice. |
| `FE-SE-DEAD-CODE-01` | Future cleanup | Remove orphan `StationEntryPanel.tsx` after this slice. |
| `FE-I18N-HYGIENE-01` | Future cleanup | Remove orphan `stationSession.setup.checklist.*` and `stationSession.setup.section.*` keys after this slice. |
| `FE-UI-08` (Mode D placeholder) | Existing in `component-map-v1.md` §8 | Independent; no shared file. |
| `FE-UI-09` (Mode A backend session API) | Existing in `component-map-v1.md` §8 | Predates this slice; this slice operates on the already-connected v4 session API surface, not the placeholder version. |

---

## 18. PO Sign-off

| Date | Reviewer | Decision | Note |
|---|---|---|---|
| 2026-05-10 | PO | CONDITIONAL on v1.0 | Direction approved (D-01..D-09 all approved; some with clarifications). Required corrections: IR-01 close ownership, IR-02 commandError prop, IR-05 UNKNOWN surface, D-05/IR-06 wording, D-09/IR-11 a11y, IR-11 border, test conditional. |
| 2026-05-10 | PO-SA agent | v1.1 patch applied | All 7 PO corrections applied inline. No decision reversed. Spec ready for re-review and final sign-off. |
| | | | |

---

*Spec authored 2026-05-10 by FleziBCG external PO-SA agent under Hard Mode MOM v3. v1.1 patch applied 2026-05-10 per PO conditional sign-off. Pending final PO acceptance before FE-SE-MODEA-SIMPLIFY-09 implementation.*
