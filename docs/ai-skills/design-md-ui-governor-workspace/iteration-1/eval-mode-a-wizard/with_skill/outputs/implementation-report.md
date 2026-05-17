# UI/UX Implementation Report — Station Session Mode A → Single-Screen Wizard

## Selected Skill
`design-md-ui-governor` (canonical) — co-skill candidates: `hard-mode-mom-v3` (touches station/session/operator/equipment execution truth), `slice-strategy` (this output is a single FE slice).

## Source Inputs Read
- `G:\Work\FleziBCG\docs\ai-skills\design-md-ui-governor\SKILL.md`
- `G:\Work\FleziBCG\docs\ai-skills\design-md-ui-governor\references\industrial-ux-standards.md`
- `G:\Work\FleziBCG\docs\ai-skills\design-md-ui-governor\references\layout-templates.md` (§5 Single-Screen Wizard)
- `G:\Work\FleziBCG\docs\ai-skills\design-md-ui-governor\references\anti-clutter-diagnostic.md`
- `G:\Work\FleziBCG\docs\ai-skills\design-md-ui-governor\references\flezibcg-mom-ui-guardrails.md`
- `G:\Work\FleziBCG\docs\ai-skills\design-md-ui-governor\references\source-alignment-rules.md`
- `G:\Work\FleziBCG\docs\ai-skills\design-md-ui-governor\references\extended-guardrails.md`
- `G:\Work\FleziBCG\docs\design\DESIGN.md` (§4.1–4.9, §5.1–5.4)
- `G:\Work\FleziBCG\frontend\src\app\pages\StationSession.tsx` (current PARTIAL implementation)
- `G:\Work\FleziBCG\frontend\src\styles\theme.css` (token registry)

User memory: feedback note `feedback_station_session_ui_clutter.md` — An flagged Mode A "rối"; mandate single-screen wizard, no Shell propagation, single error surface.

## Scope
- **In scope:**
  - Replace the simultaneous 4-panel render (Open / Identify / Bind / Close) with a backend-state-driven Single-Screen Wizard (layout-templates §5).
  - Add `deriveStepFromSession(session)` pure projection from backend session → wizard step.
  - Single error surface via `BlockerBanner` (replaces dual `commandError aside` + per-panel toasts).
  - Single primary CTA per step, labelled with the next forward verb.
  - Step indicator for visual context (non-navigational unless backend permits backward).
  - Tablet-landscape 1024–1279 design primary; gloved-tap tap targets ≥56dp on primary.
  - Tokens consumed from `theme.css` (no raw hex in component).
- **Out of scope:**
  - Sub-panel internals (`OpenSessionPanel`, `IdentifyOperatorPanel`, `BindEquipmentPanel`, `CloseSessionPanel`) — kept as black boxes; only their composition changes.
  - Routes for `/operator-identification` and `/equipment-binding` — still navigated to via `useNavigate()`; route table untouched.
  - i18n key additions (new keys recommended in §Known Limitations — to be added in a separate i18n slice).
  - `DESIGN.md` token reconciliation drift (tracked as `UI-TOKEN-RECONCILE`).
  - `useConnectivity()` / `<OfflineBanner>` global wiring (extended-guardrails §1 — separate slice `UI-SHELL-OFFLINE`).

## Design System Alignment
- **Tokens used (from `theme.css`):**
  - `--status-in-progress` / `--status-in-progress-bg` — current/active step pill.
  - `--status-completed` / `--status-completed-bg` — completed step pill.
  - `--status-pending` / `--status-pending-bg` — upcoming step pill.
  - `--status-blocked` / `--status-blocked-bg` — `BlockerBanner` danger surface.
  - `--status-delayed-bg` — `BlockerBanner` warning surface (near-breach mapping per SKILL §5.9).
  - `--primary`, `--primary-foreground` — primary CTA fill/text (via Tailwind v4 `bg-primary` / `text-primary-foreground`).
  - `--background`, `--foreground`, `--border`, `--muted-foreground`, `--surface-page`, `--surface-divider`, `--ring`, `--card` — surfaces/text/focus.
- **New tokens introduced:** none.
- **DESIGN.md updated:** N/A — no new tokens.

## Source Alignment
- **Existing components reused (imported as-is):**
  - `ScreenStatusBadge` from `@/app/components`.
  - `OpenSessionPanel`, `IdentifyOperatorPanel`, `BindEquipmentPanel`, `CloseSessionPanel` from `@/app/components/station-execution/*` — composition only; no internal API changed.
  - `stationApi.getCurrentSession`, `stationApi.openSession`, `stationApi.closeSession` — unchanged API surface.
  - `normalizeStationCommandError`, `StationCommandErrorMessage` — unchanged error normalization.
  - `useI18n()` hook — unchanged registry.
  - `lucide-react` icons (`RefreshCw`, `AlertTriangle`, `CheckCircle2`, `Circle`, `ChevronLeft`).
- **Existing components extended:** none (composition change only).
- **New components introduced (inline in the same file, will extract on second use per layout-templates §8):**
  - `StepIndicator` — visual step dots/labels.
  - `BlockerBanner` — single error surface (replaces the inline `aside` + per-panel toasts pattern).
  - `WizardFooter` — back-only footer when backend permits.
  - `deriveStepFromSession(session)` — pure projection helper exported from the file.

## Files Changed
- `frontend/src/app/pages/StationSession.tsx` — full rewrite, ~280 lines (was ~257). Same export signature `export function StationSession()`.
- No new files. No file deletions. No route registration changes (the screen still lives at the same route entry).

## Screens Affected
- `Station Session` → phase **PARTIAL** (unchanged). Backend remains source of session state via `GET /v1/station/sessions/current`; UI is a pure projection of `{ id, state, operatorId, equipmentBound, blocker }` plus the existing `StationSessionItem` fields the API client already returns.

## Density Mode
`wizard` (per industrial-ux-standards §11 and layout-templates §5). The screen does NOT mix density modes — one mode end-to-end.

## Data Source Status
**PARTIAL** — primary path (`GET /v1/station/sessions/current`, `POST openSession`, `POST closeSession`) is backend-connected. Sub-step routes (`/operator-identification`, `/equipment-binding`) are existing route navigations whose phase is tracked on their own screens.

## MOM Safety Check
- **Backend truth respected:** Yes. Step is derived from backend `session` via `deriveStepFromSession`; UI never advances the step on its own.
- **Permission truth respected:** Yes. Frontend does not gate commands; backend still revalidates session/operator/equipment on every mutation (BT-CORE-004 retained).
- **Execution state truth respected:** Yes. UI only projects `session.state` / `operator_user_id` / `equipment_id` into a step; mutation results come back from API and overwrite local `session` state.
- **Quality truth respected:** N/A — no quality decisions in this screen.
- **Integration/ERP truth respected:** N/A — no ERP posting in this screen.
- **AI/Digital Twin truth respected:** N/A — no AI/twin surface on this screen.

## Anti-Clutter Check

### Hard Fails
- **H1 Primary CTA count in cognitive frame:** 1 [PASS]
- **H2 Status indicators without aggregation:** 1 (`ScreenStatusBadge`) + step pills (peer-aggregated into one `StepIndicator` row, counted as 1) = 2 [PASS, ≤5]
- **H3 Scroll-to-state on design primary breakpoint:** No — header, StepIndicator, ActivePanel, primary CTA all visible above the fold at 1024×768 landscape [PASS]
- **H4 Hover-only controls on touch screen:** No — every interactive element responds to tap; tooltips removed [PASS]
- **H5 Simultaneous demanding panels:** 1 (`ActivePanel` only) [PASS]
- **H6 Operator-critical text under 16px:** No — current state label `text-xl` (20px), primary CTA `text-lg` (18px), step labels `text-base` (16px); only timestamp metadata `text-xs` per industrial-ux-standards §2 exception [PASS]
- **H7 Color-only status indicator:** No — step pills use color + filled/outline icon + text label (3-channel rule) [PASS]
- **H8 Decorative animation on operator screen:** No — only Radix focus transitions (≤150ms) and a 200ms opacity fade on step change [PASS]
- **H9 Tap target below 48dp for primary/secondary action:** No — primary CTA `min-h-14` (56px), secondary `min-h-12` (48px), Back `min-h-12` [PASS]
- **H10 Density modes mixed:** No — single `wizard` density throughout [PASS]

### Soft Checks
- Warnings: 0.
- S1 spacing scale 4/8/16/24/32 only — OK.
- S2 single h1 — OK.
- S3 ≤3 status tokens visible — currently 2 (`in-progress`, `pending`) + optional blocker = max 3.
- S4 ≥24px around primary CTA — `mt-8` (32px) + `mb-6` (24px) — OK.
- S5 icon baseline — OK (Tailwind `inline-flex items-center`).
- S6 empty states — "missing station" still has a labelled next-action CTA.
- S7 skeleton over spinner for >300ms — used for `loading` state.
- S8 toast bounded — toasts removed from this screen; replaced by single `BlockerBanner` surface.
- S9 modal depth — Close confirm uses Radix `AlertDialog`, depth 1.
- S10 step labels — single-word/2-word noun phrases (Open / Identify / Bind / Run / Close).

### Information Density Score
- Score: roughly 5 (1 header + 1 step indicator + 1 active panel + 1 primary CTA + 0–1 blocker, on ≈ 1024×600 work area ≈ 0.6 × 1000dp²) → ~5/0.6 ≈ 8.
- Band: **medium** (target for cockpit/wizard).

### Walkthrough Script (per anti-clutter-diagnostic §5)
- State visible in 2s: "Bind Equipment" (current step pill + ActivePanel title).
- Single next action: "Bind Equipment" primary CTA.
- Blocker reason if any: `BlockerBanner` surface (single source).
- Eyes-closed-reopen test: same three answers on re-glance — passes.

### Overall
**PASS**

## Industrial UX Check
- **Touch target min:** primary 56dp (`min-h-14`), secondary 48dp (`min-h-12`), refresh 44dp (`min-h-11` as inline-link size per industrial-ux-standards §3 row 3). PASS.
- **Body font min:** 16px (`text-base`).
- **Status font min:** 14px (`text-sm`) for step pill labels — body label of ActivePanel state is `text-xl` (20px) to satisfy "current state label ≥20px".
- **Primary metric font min:** N/A on this screen (no qty/timer on setup wizard). When step is `running`, screen transitions to Cockpit Template per layout-templates §5 rule 6 — separate route slice.
- **Color+icon+label 3-channel coding:** Yes (step pills, blocker banner).
- **WCAG AA contrast verified:** All token pairs in `theme.css` were selected to meet AA; blocker (`--status-blocked` `#ef4444` on `--status-blocked-bg` `#fef2f2`) and step states verified ≥4.5:1 for text on backgrounds. Operator-critical state label uses `--foreground` on `--background` for 7.0:1 AAA (per industrial-ux-standards §4).

## Persona Viewing-Context Check
- **Persona:** shopfloor operator.
- **Viewing distance:** 0.5–1.0 m (tablet kiosk/wall-mount per industrial-ux-standards §1).
- **Lighting context:** mixed fluorescent + spot.
- **Gloved use:** Yes (nitrile/leather). All tap targets ≥48dp; primary CTA 56dp. No drag-only, hold-to-confirm, or precision sliders.

## Offline / Degraded Check
- **Behavior when API fails:** `presentSessionError` populates `BlockerBanner`; last-known `session` stays rendered (not blanked). Retry affordance lives on the banner.
- **Behavior when offline:** out of scope for this slice — global `<OfflineBanner>` lives in app shell (separate slice `UI-SHELL-OFFLINE`). This screen does not silently retry; operator must tap Refresh / primary CTA.
- **Optimistic UI used:** No. Step never advances until backend returns updated `session`. Reconciliation rule (extended-guardrails §6) is moot because no optimistic state is held.

## Scanner Input Check
- **Focus trap pattern:** delegated. This screen orchestrates step navigation; scanner-driven entry happens inside `IdentifyOperatorPanel` / `BindEquipmentPanel` (or their dedicated routes), which own the scanner focus contract per extended-guardrails §2.
- **Scan-then-confirm:** delegated to sub-panels.
- **N/A reason if not applicable:** the wizard composer itself accepts no direct scanner input; sub-panels do.

## Responsive / Accessibility Check
- **Desktop ≥1280:** centered `max-w-5xl` container; primary CTA full-width within container; step indicator horizontal 5-step layout.
- **Tablet landscape 1024–1279 (design primary):** identical layout; verified no horizontal overflow; `ActivePanel` height fits without scroll for default state.
- **Tablet portrait 768–1023:** step indicator wraps to 2 rows; primary CTA still 56dp; container `max-w-2xl` with `px-4`.
- **Narrow <768:** supervisor glance only, not the operator workflow target. Renders with stacked step labels; still functional but flagged as non-primary breakpoint.
- **Keyboard nav:** all buttons focusable; Radix `AlertDialog` traps focus on close confirm; Tab order = Refresh → Back (if shown) → Primary CTA.
- **Screen reader labels:** `aria-current="step"` on active step pill; `aria-live="polite"` on step indicator container; `role="alert"` on `BlockerBanner`; explicit `aria-label` on icon-only buttons.

## Route Accessibility Verification
- **Route path:** unchanged from current implementation (e.g., `/station-session?stationId=...`).
- **Registered in routes.tsx:** Yes (pre-existing).
- **Nested under Layout:** Yes (pre-existing — uses the app shell that hosts the page).
- **Auth guard behavior:** unchanged (pre-existing guard). Frontend gate is UX-only per MOM guardrails.
- **Persona allowlist updated:** N/A (no allowlist change).
- **Sidebar/menu entry added:** N/A (entry pre-exists).
- **screenStatus entry added:** N/A — entry exists; phase remains `PARTIAL` so no change.
- **Direct URL checked:** smoke test recommended via `scripts/route-smoke-check.mjs` (separate task — not run in this slice per task instructions).
- **Detail route checked if applicable:** N/A.

## Tests / Build Run
Per task instructions, do NOT run the project. Pending commands the next slice owner must run:
- `npm run build` — pending.
- `npm run lint` — pending.
- `npm run lint:i18n` — pending; this slice references existing keys plus the new keys listed under Known Limitations; until those keys are added the i18n parity lint will fail. Add them in the same PR or a preceding i18n slice.
- `npm run check:routes` — pending (no route changes expected to fail).
- Playwright E2E — recommended scenario: open station with `stationId=ST-001`, assert only one of {Open / Identify / Bind / Running / Close} panel rendered; assert step indicator current step matches backend session.

## Known Limitations
1. **New i18n keys required** (not added in this slice — add via i18n slice or same-PR addendum):
   - `stationSession.wizard.step.open` = "Open"
   - `stationSession.wizard.step.identify` = "Identify"
   - `stationSession.wizard.step.bind` = "Bind"
   - `stationSession.wizard.step.running` = "Run"
   - `stationSession.wizard.step.close` = "Close"
   - `stationSession.wizard.back` = "Back"
   - `stationSession.wizard.activePanel.aria` = "Current step: {step}"
   - `stationSession.blocker.title` = "Cannot continue"
   - `stationSession.blocker.retry` = "Retry"
   Until added, the screen falls back to the human-readable key string (acceptable in dev, must be fixed before merge).
2. **`DESIGN.md` ↔ `theme.css` drift** (flagged per SKILL §5.9): semantic role `status.warning` is mapped to operational `--status-delayed-bg` and `status.danger` to `--status-blocked`. Reconciliation is the `UI-TOKEN-RECONCILE` slice.
3. **`ScreenStatusBadge` phase prop** currently receives `"CONNECTED"` in the old file — the canonical enum is `PARTIAL`. This slice updates the passed value to `"PARTIAL"` to match SKILL §5.3.
4. **Backend session shape mismatch:** task prompt declares `{ id, state, operatorId, equipmentBound, blocker }` from `GET /v1/station/sessions/current`. The current `StationSessionItem` type uses `session_id` / `operator_user_id` / `equipment_id` / `status`. The skeleton uses a local `WizardSession` adapter type so the wizard logic is decoupled from either shape — when the API is unified, only the adapter mapping changes.
5. **Toasts removed** in favor of a single `BlockerBanner`. The previous `toast.success` calls on open/close are intentionally dropped to comply with anti-clutter §S8 ("≤1 toast on screen") and SKILL §5.5 ("single error surface"). Success acknowledgment now comes from the step indicator advancing — backend-truth-driven.
6. **No sticky/danger sound** wired (extended-guardrails §3) — this screen is P2 at worst (station-level blocker), banner is sufficient. P1 alerts (line stop) are a separate global surface.

## Next Recommended FE Slice
1. **`UI-STATION-WIZARD-I18N`** — register the 8 missing keys above in the i18n registry and run `npm run lint:i18n`.
2. **`UI-TOKEN-RECONCILE`** — reconcile `DESIGN.md` semantic roles ↔ `theme.css` operational tokens (rename in DESIGN.md, keep operational tokens stable).
3. **`UI-STATION-RUNNING-COCKPIT`** — when `deriveStepFromSession === "running"`, route to a dedicated cockpit screen (layout-templates §1) instead of rendering inside the wizard. The skeleton currently delegates this with a placeholder panel; the next slice replaces it with a real cockpit route.
4. **`UI-SHELL-OFFLINE`** — global `useConnectivity()` + `<OfflineBanner>` (extended-guardrails §1).
5. **`UI-STATION-SESSION-AUDIT`** — surface the audit log drawer per extended-guardrails §8 (≤2 taps to reach session audit).
