# UI/UX Implementation Report

## Selected Skill

`design-md-ui-governor` (primary), with cross-references to
`stitch-design-md-ui-ux` and `design-system-enforcer`.

Composite rationale: the task is a frontend screen refactor on a
station-execution cockpit (operator persona, tablet landscape). The
governor skill owns the report contract; the stitch skill informs the
React/Tailwind discipline and route-accessibility gate; the enforcer
skill drives the screen-purpose and status-color gates.

---

## Source Inputs Read

1. `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/baseline-snapshot/design-md-ui-governor/SKILL.md`
2. `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/baseline-snapshot/design-md-ui-governor/references/design-md-format-rules.md`
3. `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/baseline-snapshot/design-md-ui-governor/references/flezibcg-mom-ui-guardrails.md`
4. `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/baseline-snapshot/design-md-ui-governor/references/source-alignment-rules.md`
5. `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/baseline-snapshot/stitch-design-md-ui-ux/SKILL.md`
6. `docs/ai-skills/design-md-ui-governor-workspace/iteration-1/baseline-snapshot/design-system-enforcer/SKILL.md`
7. `docs/design/DESIGN.md` (color palette, typography, operator cockpit layout, responsive rules)
8. `frontend/src/app/pages/StationSession.tsx` (current 4-panel implementation)
9. `frontend/src/styles/theme.css` (CSS custom-properties and status tokens)

Not read (out of scope for this refactor slice): `.github/copilot-instructions.md`
(unavailable in the sandbox snapshot), `docs/audit/frontend-source-alignment-snapshot.md`
(not required for an intra-screen layout refactor that does not introduce a new
route or invent new API contracts).

---

## Scope

In scope:

- Refactor of the single page `StationSession.tsx` from a 4-panel stack
  (Open / Identify / Bind / Close, all visible at once) into a
  **single-screen step-driven cockpit** that shows only the current
  setup step plus a compact context strip.
- Operator persona, tablet landscape (1024–1366 wide), glove-friendly
  touch targets.
- Skeleton only. No changes to the four existing sub-panel components
  (`OpenSessionPanel`, `IdentifyOperatorPanel`, `BindEquipmentPanel`,
  `CloseSessionPanel`) — they are re-used through conditional rendering.
- No new routes. No router changes. No new API client method.

Out of scope:

- Backend changes. Backend session truth contract is preserved as-is
  (`GET /v1/station/sessions/current` returning `{ id, state,
  operatorId, equipmentBound, blocker }` — mapped to the existing
  frontend type `StationSessionItem`).
- Other station screens (`/operator-identification`, `/equipment-binding`,
  `/station` queue) — only navigation calls preserved.
- i18n keys. The skeleton re-uses the existing `stationSession.*` keys.
  Two new keys are proposed in the report for the step-indicator
  labels but their wiring is left to the i18n owner (see "Known
  Limitations").

---

## Design System Alignment

| DESIGN.md rule | How the refactor complies |
|---|---|
| Visual theme: industrial clarity, calm, low drama | One dominant CTA per step; no decorative gradients; no animation beyond a `transition` on hover/focus. |
| Color palette: semantic only | Uses `--primary` for active step, `--status-blocked` for blocker banner, `--status-completed` for completed steps, `--muted-foreground` for pending steps. No hard-coded `red-500` etc. Tailwind v4 arbitrary values consume the theme variables (e.g. `bg-[var(--status-completed-bg)]`). |
| Typography: large readable | Page title `text-2xl`, current step heading `text-xl`, primary CTA `text-lg font-semibold`, station id displayed as mono `font-mono`. |
| App shell: preserve sidebar/header | No shell change. The component remains a route child rendered by the existing layout. |
| Page header pattern | Title + domain subtitle + phase badge + secondary refresh action — already present and retained. |
| Operator cockpit layout: at most 5 zones | Now exactly 5 zones: (1) header, (2) context strip, (3) step indicator, (4) current-step panel, (5) blocker/error banner above the panel. |
| Buttons: 48–56px+ operator height | Step-advance and `Enter queue` CTAs use `min-h-14` (56px). Refresh and back actions use `min-h-11` (44px) for secondary touch. |
| Status badges: mapped to stable codes | `ScreenStatusBadge phase="CONNECTED"` retained; setup-step state mapped to `status.success` / `status.info` / `status.neutral`. |
| Responsive: stacked cards on tablet portrait | Layout uses `flex-col` with `max-w-4xl mx-auto`; step indicator collapses from horizontal stepper to vertical list under `sm:`. |
| Empty / loading / error states | `loading=true` shows a skeleton block; missing `stationId` shows the existing amber notice; backend command error shows `commandError` banner above the step panel. |
| Phase label | `PARTIAL — backend-connected` (preserved from current file header comment). |

---

## Source Alignment

Checked against `source-alignment-rules.md`:

1. **Preserve working screens** — Yes. Same route (`/station-session`),
   same component name `StationSession`, same default export shape,
   same `useSearchParams` `stationId` contract.
2. **Extend current app shell** — Yes. No shell touched.
3. **No invented route patterns** — Yes. Navigation to
   `/operator-identification`, `/equipment-binding`, `/station` is
   reused verbatim.
4. **No invented API fields** — Yes. Only fields already present on
   `StationSessionItem` are consumed: `session_id`, `status`,
   `opened_at`, `operator_user_id`, `equipment_id`. The task brief
   describes the contract as `{ id, state, operatorId, equipmentBound,
   blocker }`; the existing FE type uses snake_case
   (`session_id`, `status`, `operator_user_id`, `equipment_id`). The
   skeleton uses the existing FE field names — the brief's
   field-name divergence is flagged in "Known Limitations" rather
   than silently re-mapped, since renaming would invent a contract.
5. **No backend connectivity inferred from UI mocks** — Yes. No mock
   data is introduced. All session truth still comes from
   `stationApi.getCurrentSession`.
6. **Mocks separated from production paths** — N/A; no mocks added.
7. **Future screens marked** — N/A; this is an active screen refactor.
8. **Update screen inventory** — Recommendation in "Next Recommended
   FE Slice" below.
9. **Do not implement all screens in one PR** — Yes. Scope is one file.
10. **Report exact files changed and verification commands** — see
    "Files Changed" and "Tests / Build Run".

---

## Files Changed

| File | Change | Status |
|---|---|---|
| `frontend/src/app/pages/StationSession.tsx` | Replaced 4-panel stack with single-step wizard cockpit. | Skeleton delivered (under `outputs/StationSession.tsx`); not yet copied into the repo. |

No other files are modified by this slice.

---

## Screens Affected

- `StationSession` — refactored. Phase: **PARTIAL — backend-connected**.

Unaffected:

- `OperatorIdentification` — still reached via `goToOperatorIdentification`.
- `EquipmentBinding` — still reached via `goToEquipmentBinding`.
- `StationQueue` — still reached via `goToStationQueue` once the setup
  state allows it.

---

## Components Added / Updated

Added (local to `StationSession.tsx`):

- `SessionContextStrip` — compact read-only strip showing station id,
  session id (mono), opened-at, and the screen-status badge.
- `SetupStepIndicator` — horizontal-on-desktop / vertical-on-mobile
  step indicator with three steps: `open`, `identify-operator`,
  `bind-equipment`. Each step shows a state of
  `completed | current | pending | blocked`.

Updated:

- `StationSession` — now derives `currentStep` and renders exactly
  one of the four sub-panels at a time.

Unchanged (re-used as-is):

- `OpenSessionPanel`, `IdentifyOperatorPanel`, `BindEquipmentPanel`,
  `CloseSessionPanel` from `@/app/components/station-execution/*`.
- `ScreenStatusBadge`, `useI18n`, `stationApi`,
  `normalizeStationCommandError`.

---

## Data Source Status

| Surface | Source | Status |
|---|---|---|
| Current session truth | `GET /v1/station/sessions/current` via `stationApi.getCurrentSession(stationId)` | Real backend. |
| Open session | `stationApi.openSession({ station_id })` | Real backend. |
| Close session | `stationApi.closeSession(sessionId)` | Real backend. |
| Operator identity | Navigated to dedicated screen; no FE-derived identity. | Real backend (downstream screen). |
| Equipment binding | Navigated to dedicated screen; no FE-derived binding. | Real backend (downstream screen). |
| Allowed actions | Currently derived from `session.status` + presence of `operator_user_id` / `equipment_id`. | **UI navigation readiness only** — backend re-validates on mutation (already commented in the original file as BT-CORE-004). |
| Blocker text | Pass-through from `commandError` normalization. | Real backend error code. |

No mock data. No FE-only computed business state surfaced as truth.

---

## MOM Safety Check

Against `flezibcg-mom-ui-guardrails.md` and DESIGN.md §10:

- [x] FE does not decide session execution state — `session.status`
      and the navigation gate are explicitly documented as
      navigation-readiness only.
- [x] FE does not decide authorization — backend remains the auth
      boundary on `openSession` / `closeSession` / queue mutations.
- [x] FE does not fake quality, acceptance, ERP posting, or backflush.
- [x] No AI surfacing on this screen, so no advisory-vs-deterministic
      confusion possible.
- [x] No future-scope module is shown as active.
- [x] Status colors are semantic via theme tokens; no decorative
      red/green/orange.
- [x] Persona (shopfloor operator) is UX only — no permission
      hardcoded in this file.
- [x] Confirmation flow for `closeSession` preserved
      (`showCloseConfirm` state, kept inside `CloseSessionPanel`).

No hard-reject conditions tripped.

---

## Responsive / Accessibility Check

Target persona: shopfloor operator on tablet landscape, may wear
gloves, may stand 0.5–1.0 m from the screen.

| Concern | Treatment |
|---|---|
| Touch target — primary | `min-h-14` (56px) on `Enter queue`, on the primary CTA inside the active step panel (preserved from existing sub-panels), and on the step `Back` button. |
| Touch target — secondary | `min-h-11` (44px) on Refresh and on stepper chip buttons. |
| Hover-only controls | None. All interactive affordances have visible button shapes and labels. |
| Color-only status | Step indicator uses icon (Check / Dot / Lock) + label + color; blocker banner uses icon + title + body. |
| Focus ring | `focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] focus-visible:ring-offset-2` on every interactive element. |
| Distance readability | `text-2xl` page title, `text-xl` step heading, primary CTA `text-lg font-semibold`. Station id rendered mono so digits are unambiguous. |
| Tablet landscape (1024–1366) | `max-w-4xl mx-auto` keeps line length operator-friendly without stretching. |
| Tablet portrait / mobile | Stepper collapses to vertical list under `sm:`. Header refresh button retains its label, not icon-only. |
| Screen reader | Blocker banner uses `role="alert"`. Step indicator uses an `<ol>` with `aria-current="step"` on the active step. |
| Keyboard | Tab order: Refresh → step chips (if interactive) → step body actions → bottom CTA. `Enter queue` is a real `<button type="button">`. |
| Gloved input | Targets >=44px (44/56) with 8px+ spacing between adjacent buttons (`gap-2`/`gap-3`). |

Not validated automatically — see "Tests / Build Run".

---

## Tests / Build Run

Not run in this environment. The task brief explicitly forbids running
the project or installing dependencies, so the skeleton is delivered
without `pnpm build`, `pnpm lint`, or `pnpm test` results.

Recommended verification commands (to run from `frontend/`):

```
pnpm install
pnpm lint
pnpm typecheck
pnpm test -- StationSession
pnpm build
```

Direct-URL smoke test (per stitch-skill route-accessibility gate):
`/?stationId=ST-001` then navigate to `/station-session?stationId=ST-001`.

---

## Known Limitations

1. **Field-name divergence with task brief.** The brief states the
   contract is `{ id, state, operatorId, equipmentBound, blocker }`.
   The existing FE `StationSessionItem` type uses
   `{ session_id, status, operator_user_id, equipment_id, ... }`. The
   skeleton uses the existing FE names so as not to invent a renaming.
   If the brief is the authoritative new contract, a separate adapter
   slice should land before this refactor.
2. **i18n keys for the step indicator** (`stationSession.step.open`,
   `stationSession.step.identifyOperator`, `stationSession.step.bindEquipment`,
   `stationSession.step.back`) are referenced in the skeleton but
   their actual key definitions in `@/app/i18n/keys` need to be added
   by the i18n owner. The skeleton uses `as I18nSemanticKey` casts
   consistent with the rest of the file.
3. **No automated tests yet.** A `@testing-library/react` test for the
   step transitions and the navigation-blocked hint should be added.
4. **Screen inventory** under
   `docs/audit/frontend-source-alignment-snapshot.md` should be
   updated once this skeleton lands — phase remains `PARTIAL` but the
   layout description changes from "4-panel stack" to
   "single-step wizard cockpit".
5. **CloseSessionPanel placement.** It is rendered after the wizard
   block, not inside a step, to keep the "end session" action
   reachable from any step. Confirm with An that this matches the
   intended Mode A pattern.
6. **No offline / scanner / multi-station concerns** addressed — the
   older skill does not require them and the brief does not request
   them. Flag for the new skill iteration.

---

## Next Recommended FE Slice

Pick ONE of:

- **SLICE-A (small):** Add the four new i18n keys
  (`stationSession.step.*`) and corresponding Vi/En strings; remove
  the `as I18nSemanticKey` casts.
- **SLICE-B (medium):** Update
  `docs/audit/frontend-source-alignment-snapshot.md` to reflect the
  new `StationSession` layout, and add a Vitest covering: empty
  station, loading, open with operator missing, open with operator
  but equipment missing, fully ready (queue CTA enabled), close
  confirm.
- **SLICE-C (medium, only after A):** Apply the same
  single-step-wizard pattern to `OperatorIdentification` and
  `EquipmentBinding` so the three setup screens feel like one
  continuous Mode-A wizard rather than three independent forms.
- **SLICE-D (small, only after backend confirms):** If the brief's
  `{ id, state, operatorId, equipmentBound, blocker }` is the
  authoritative new contract, add an adapter in `stationApi.ts` and
  rename the FE type. Do **not** combine with this UI refactor.

Recommended order: SLICE-A → SLICE-B → SLICE-C.
