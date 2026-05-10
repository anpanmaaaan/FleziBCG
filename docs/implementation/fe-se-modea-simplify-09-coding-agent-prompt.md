# FE Coding-Agent Prompt — FE-SE-MODEA-SIMPLIFY-09

> **Audience**: FleziBCG FE coding agent (autonomous implementation).
> **Authority**: Spec `docs/design/07_ui/station-execution-mode-a-simplify-spec-v1.md` v1.1 — SIGNED OFF 2026-05-10.
> **Branch policy**: autocode (consolidated). Do **not** create a new branch. Sandbox edits files; final commit is performed by the human PO from Windows.
> **Do not** modify backend, contracts under `docs/design/02_domain/`, or pages outside the explicit file list.

Copy the entire block below as the prompt to the FE coding agent.

---

## ROLE

You are the FleziBCG FE coding agent operating under Hard Mode MOM v3 with explicit slice scope. You are implementing **slice `FE-SE-MODEA-SIMPLIFY-09`**: simplification of the Station Session (Mode A) operator surface.

The slice is fully specified and signed off. **You do not invent product decisions.** If you encounter a question not answered by the spec, stop and emit a "stop-condition report"; do not improvise.

---

## STEP 0 — MANDATORY READS BEFORE ANY CODE CHANGE

Read these files **in full** before touching any source. The spec is authoritative; the others are background you must respect.

1. `docs/design/07_ui/station-execution-mode-a-simplify-spec-v1.md` (v1.1) — **canonical for this slice**.
2. `docs/design/07_ui/station-execution-redesign-contract-v1.md` (target operator UX, MOM safety rules §16).
3. `docs/design/07_ui/station-execution-ui-contract-v4.md` (canonical screen contract, truth boundaries).
4. `docs/design/07_ui/station-shopfloor-token-system-v1.md` (visual hierarchy, hit-target tier).
5. `docs/design/02_domain/execution/station-session-ownership-contract.md` (StationSession aggregate boundary — read-only context).
6. `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md` (backend revalidation contract — read-only context).
7. `docs/governance/CODING_RULES.md` (engineering rules, lint/build/route gates).
8. `frontend/src/app/pages/StationSession.tsx` (target page).
9. `frontend/src/app/components/station-execution/{OpenSessionPanel,IdentifyOperatorPanel,BindEquipmentPanel,CloseSessionPanel,StationEntryPanel,StationWorkflowShell,stationCommandErrorMessages}.tsx` and `.ts`.
10. `frontend/src/app/api/stationApi.ts` (API surface — must remain unchanged in this slice).
11. `frontend/src/app/i18n/registry/en.ts` and `ja.ts` (existing key namespace, `stationSession.*`).
12. `frontend/src/app/routes.tsx` and `frontend/src/app/screenStatus.ts` (verify no change needed).

**You may not start coding before completing all 12 reads.** In your implementation report, list each file by path and state "read".

---

## INTENT

Reduce visual clutter and information redundancy in `pages/StationSession.tsx` per spec §1:

1. Replace the current 8-section vertical stack with a single 3-row card pattern.
2. Remove duplicate context display between `StationWorkflowShell` and `StationEntryPanel`.
3. Consolidate command-error display to a single banner.
4. Surface a single primary CTA ("Enter queue") with deterministic enable/disable rule.
5. Close the stage-logic bug by removing `StationWorkflowShell` from Mode A.

Out of intent: this slice does not modal-ize operator identification or equipment binding (that is `FE-SE-MODEA-MODAL-10`, future). Routes remain unchanged.

---

## TRUTH BOUNDARIES (NON-NEGOTIABLE)

Inherited from spec §2. **Violation of any of these means stop and report.**

1. Backend remains source of truth for session state, operator identity, and equipment binding.
2. Frontend sends intent only; frontend never derives session/operator legality from local state.
3. No backend / API / event / projection change.
4. No new authorization rule.
5. No new route, no route deletion, no route rename.
6. No `screenStatus.ts` phase change (stays `CONNECTED`).
7. No change to `StationWorkflowShell` API. (Other pages still use it.)
8. No change to `pages/OperatorIdentification.tsx`, `pages/EquipmentBinding.tsx`, `pages/StationExecution.tsx`.
9. The 9 locked decisions D-01..D-09 in spec §6 are not negotiable. If something blocks any of them, stop and report.

---

## IN SCOPE (LITERALLY AND ONLY)

Per spec §7.

1. Refactor `pages/StationSession.tsx` to single-card 3-row pattern (D-03).
2. Drop `StationWorkflowShell` and `StationEntryPanel` from Mode A page (D-01, D-02).
3. Consolidate error display to top banner (D-04).
4. Move primary CTA to bottom of card as a single full-width button (D-05).
5. Adjust empty state for missing `stationId` (D-08).
6. Remove inline error block from `OpenSessionPanel.tsx`; remove `commandError`, `closing`, `stationId` props (IR-02).
7. Refactor `IdentifyOperatorPanel.tsx` and `BindEquipmentPanel.tsx` to row-friendly layout (smaller footprint, no own border, no own header icon; per IR-03, IR-04).
8. Add new i18n keys under `stationSession.row.*` and `stationSession.cta.*` and `stationSession.empty.*` per IR-08. **Do not delete** existing keys.
9. Apply visual tokens per IR-11 (`border-t border-slate-200`, focus-visible mandate, `aria-hidden="true"` on decorative symbols).
10. Mark `StationEntryPanel.tsx` orphan with TODO comment per IR-10.

---

## EXPLICITLY OUT OF SCOPE

You **must not** do any of the following in this slice. If anything in your task seems to require it, stop and report.

1. Modal-ization of `OperatorIdentification` or `EquipmentBinding` — separate slice.
2. Removal of `StationEntryPanel.tsx` file from repo — separate cleanup slice.
3. Any change to `pages/OperatorIdentification.tsx`, `pages/EquipmentBinding.tsx`, `pages/StationExecution.tsx`.
4. Backend / API / event / projection changes.
5. New routes, route deletions, or route renames.
6. `screenStatus.ts` phase change.
7. `StationWorkflowShell` API changes.
8. `StationEntryHandoff` changes.
9. Andon, takt strip, time-in-state additions.
10. A11y modal/touch-target work for cockpit (covered by `FE-SE-A11Y-04`, separate slice).
11. Dark mode, theme, animation tokens.
12. Persona/role visibility changes.
13. i18n key deletion (mark orphan only; deletion is `FE-I18N-HYGIENE-01`).

---

## IMPLEMENTATION ORDER (RECOMMENDED)

Follow this order to minimize regression risk. Each step should leave the build green.

**Step 1 — i18n keys (additive, lowest risk)**
- Add new keys to `frontend/src/app/i18n/registry/en.ts` and `frontend/src/app/i18n/registry/ja.ts` per spec §9 IR-08.
- Verify `npm run lint:i18n:registry` passes.
- Do not delete or rename existing keys.

**Step 2 — Refactor child components (`OpenSessionPanel`, `IdentifyOperatorPanel`, `BindEquipmentPanel`)**
- Update prop interfaces per spec IR-02, IR-03, IR-04.
- Strip own `<section>` border, own header icon, own error block.
- Output is a `<div>` row that fits inside a parent `<section>`.
- Add `aria-hidden="true"` on decorative symbols, `focus-visible:` classes on action buttons (IR-11).
- Verify the page still compiles (it will look temporarily worse — fine, fix in Step 3).

**Step 3 — Refactor `pages/StationSession.tsx` page composition**
- Remove imports: `StationWorkflowShell`, `StationEntryPanel`.
- Restructure render function per spec IR-01:
  1. Header (h1 + ScreenStatusBadge + Refresh).
  2. Conditional top error banner (single source per IR-05).
  3. Conditional empty-state card if `!stationId` (IR-07).
  4. Otherwise: single `<section>` 3-row card (Session/Operator/Equipment rows).
  5. Primary CTA "Enter queue" full-width below the card (IR-06).
  6. Helper text below CTA (when disabled).
  7. `<CloseSessionPanel/>` rendered at page level as sibling — owns close-confirm dialog (IR-01).
- Implement local variable `canNavigateToQueueByVisibleSetupState` exactly as named (IR-06). Add JSDoc above it referencing BT-CORE-004.
- Remove `currentStage` computation from this file. Verify no `STX_009_END_SESSION` remains.
- Lift error display to single top banner; remove inline error from anywhere else.
- Remove `toast.error()` calls for normalized command-guard codes; keep success toasts; UNKNOWN errors also surface via banner only (IR-05).

**Step 4 — Lifecycle marker on `StationEntryPanel.tsx`**
- Add header comment exactly: `// TODO(FE-SE-DEAD-CODE-01): Remove this file. No consumers as of FE-SE-MODEA-SIMPLIFY-09 (2026-05-10).`
- Do not delete the file; do not delete its exports; just add the TODO comment.

**Step 5 — Verify**
- Run mandatory gates per spec §11.
- Run conditional gates if test runner available (see spec §10 conditional rule).
- Perform manual walk-through and capture evidence per spec §11.

**Step 6 — Author implementation report**
- Path: `docs/audit/fe-se-modea-simplify-09-implementation-report.md`.
- Required sections listed below.

---

## CONCRETE FILE ACTIONS

| File | Action |
|---|---|
| `frontend/src/app/pages/StationSession.tsx` | Major refactor per spec IR-01. Remove `StationWorkflowShell`, `StationEntryPanel` imports/uses. |
| `frontend/src/app/components/station-execution/OpenSessionPanel.tsx` | Remove `commandError`, `closing`, `stationId` props (IR-02). Remove inline error block. Remove `<section>` border. Remove `Power` icon header. Add `aria-hidden`, `focus-visible:` per IR-11. |
| `frontend/src/app/components/station-execution/IdentifyOperatorPanel.tsx` | Row-friendly: drop `<section>` border, drop `User` icon header. Add `aria-hidden`, `focus-visible:`. |
| `frontend/src/app/components/station-execution/BindEquipmentPanel.tsx` | Row-friendly: drop `<section>` border, drop header icon. Add `aria-hidden`, `focus-visible:`. |
| `frontend/src/app/components/station-execution/CloseSessionPanel.tsx` | **No edit unless minimal alignment needed**. It owns close-confirm per IR-01. Verify it accepts page-state-driven `showCloseConfirm`, `closing`, `commandError` if it currently does. Do not introduce duplicate confirmation logic. |
| `frontend/src/app/components/station-execution/StationEntryPanel.tsx` | Add TODO comment header (IR-10). No other change. |
| `frontend/src/app/components/station-execution/StationWorkflowShell.tsx` | **No edit**. Read-only inspection. |
| `frontend/src/app/components/station-execution/StationEntryHandoff.tsx` | **No edit**. Read-only inspection. |
| `frontend/src/app/components/station-execution/stationCommandErrorMessages.ts` | **No edit**. Read-only inspection. |
| `frontend/src/app/i18n/registry/en.ts` | Add new keys per IR-08. Do not modify or delete existing keys. |
| `frontend/src/app/i18n/registry/ja.ts` | Mirror en.ts additions. |
| `frontend/src/app/routes.tsx` | **No edit**. Read-only verification. |
| `frontend/src/app/screenStatus.ts` | **No edit**. Read-only verification. |
| `frontend/src/app/api/stationApi.ts` | **No edit**. Read-only verification. |

Any file not listed: do not edit.

---

## MANDATORY ANTI-PATTERNS

If you find yourself doing any of these, stop:

- **Do not** name the readiness variable `canEnterQueue`, `canExecute`, `isReady`, `isAuthorized`, `canStart`. Use `canNavigateToQueueByVisibleSetupState` exactly.
- **Do not** put a `commandError` prop on `OpenSessionPanel`, `IdentifyOperatorPanel`, `BindEquipmentPanel`. Banner is page-owned.
- **Do not** call `toast.error(...)` for any normalized command-guard code or UNKNOWN failure. Use the top banner.
- **Do not** call `toast.success(...)` for failures. Success toasts retained as-is for `opened`/`closed`.
- **Do not** add a confirmation dialog inside the Session row's End-session button. The button only sets `showCloseConfirm = true`; `<CloseSessionPanel/>` owns the dialog.
- **Do not** wrap the page body in `<StationWorkflowShell>`. Remove the import.
- **Do not** import `StationEntryPanel` into Mode A.
- **Do not** assign `currentStage` anywhere in `pages/StationSession.tsx`.
- **Do not** use arbitrary `0.5px` border classes. Use `border-t border-slate-200`.
- **Do not** add 4 separate cards for Session/Operator/Equipment. Use a single `<section>` with 3 rows.
- **Do not** invent operator identity or equipment binding from frontend state.
- **Do not** add or remove routes.
- **Do not** delete any existing i18n key.
- **Do not** edit any backend file.

---

## VERIFICATION (per spec §11)

### Mandatory gates (must pass — block merge if any fails)

```bash
cd frontend
npm run build
npm run lint
npm run check:routes
npm run lint:i18n:registry
```

### Conditional gate (per spec §10 runner-availability rule)

```bash
# Run only if test runner is configured and was green on the autocode baseline
# before this slice. If runner is missing/broken, document gap and skip.
npm test -- --run
```

### Optional gate

```bash
npm run a11y:scan   # if available; expect 0 serious/critical on /station-session
```

### Mandatory manual walk-through (capture evidence in implementation report)

Walk through the following 7 scenarios at `/station-session`. For each, record observed behavior and a screenshot or DOM snapshot.

1. `?stationId=ST-WELD-04` + open session + identified operator + equipment ok → CTA enabled, no banner.
2. `?stationId=ST-WELD-04` + open session + no operator → CTA disabled, helper "Identify operator".
3. `?stationId=ST-WELD-04` + no session → CTA disabled, helper "Open session".
4. No `stationId` → exactly 1 amber notice; no Shell, no row card.
5. Trigger a session-required command failure → exactly 1 banner; **no toast**.
6. Simulate UNKNOWN error (network failure or unhandled code) → 1 banner with fallback copy; **no toast**.
7. Successful session open → 1 success toast; **no banner**.

Plus keyboard-only walkthrough: Tab through all interactive elements, verify focus ring visible at each step.

---

## STOP CONDITIONS (per spec §14)

Stop implementation immediately and emit a stop-condition report (do not finish the slice) if any of the following occurs:

1. Existing `OperatorIdentification` or `EquipmentBinding` route page test fails after Mode A refactor.
2. `StationWorkflowShell` API change is required to make this slice work.
3. New i18n keys exceed 35 (revisit consolidation strategy).
4. `screenStatus.ts` requires a phase change.
5. The Session row "End session" path cannot be made functional without altering `CloseSessionPanel.tsx` significantly (>30 lines diff).
6. Build, lint, route smoke, or i18n registry gate fails after refactor and you cannot make it pass without changing scope.
7. Any backend, command, event, or projection change is required.
8. PO feedback during review changes a locked decision (D-01..D-09).

A stop-condition report is a short markdown file at `docs/audit/fe-se-modea-simplify-09-stop-condition-report.md` containing: which stop condition triggered, what code state preceded it, what attempt was made, and your recommendation.

---

## DEFINITION OF DONE (per spec §15)

The slice is complete when **all** of these are true:

1. `pages/StationSession.tsx` renders exactly 3 row entries within a single shared `<section>` card (verified by component test or grep + manual walk-through).
2. `grep "StationWorkflowShell" frontend/src/app/pages/StationSession.tsx` returns no match.
3. `grep "StationEntryPanel" frontend/src/app/pages/StationSession.tsx` returns no match.
4. `commandError` is rendered in exactly one location at any given time (top banner).
5. No `toast.error(...)` call fires for any normalized command-guard code or UNKNOWN failure. Success toasts retained.
6. Primary CTA "Enter queue" is the only top-level full-width CTA on the page; helper text reflects missing prerequisite when disabled.
7. Empty state for missing `stationId` renders exactly one notice card (no Shell, no row card, no checklist).
8. `grep "STX_009_END_SESSION" frontend/src/app/pages/StationSession.tsx` returns no match.
9. Routes `/station-session`, `/operator-identification`, `/equipment-binding`, `/station` remain registered and reachable (`npm run check:routes` 24/24).
10. Mandatory gates pass on autocode (build, lint, check:routes, lint:i18n:registry). Conditional unit-test gate passes if applicable.
11. All 7 manual walk-through scenarios in §Verification produce expected behavior.
12. Implementation report `docs/audit/fe-se-modea-simplify-09-implementation-report.md` exists and references this prompt + spec by ID.
13. No backend file is modified.
14. No file under `docs/design/02_domain/` is modified.

---

## IMPLEMENTATION REPORT

At slice close, author `docs/audit/fe-se-modea-simplify-09-implementation-report.md` with these sections:

1. **History** — single row "v1.0 — implementation report".
2. **Routing** — mirrors spec §Routing block.
3. **Slice ID** — `FE-SE-MODEA-SIMPLIFY-09`.
4. **Spec reference** — link to `docs/design/07_ui/station-execution-mode-a-simplify-spec-v1.md` v1.1.
5. **Read evidence** — list each file from §Step 0 with status "read".
6. **Files modified** — table: file path / lines changed / brief diff summary.
7. **Files inspected (read-only)** — list per §Concrete File Actions.
8. **i18n keys added** — list of new keys, grouped by namespace.
9. **i18n keys orphaned (not deleted)** — list of v1.0 keys now unused but kept per scope.
10. **Decision-by-decision compliance** — table mapping D-01..D-09 → "implemented" + brief evidence.
11. **Implementation rule compliance** — table mapping IR-01..IR-11 → "implemented" + brief evidence (cite line numbers).
12. **Verification gate results** — pass/fail per command + console output excerpt.
13. **Manual walk-through evidence** — 7 scenarios with screenshot or DOM-snapshot reference.
14. **Stop-condition status** — none triggered, OR the stop-condition report path.
15. **Definition-of-Done compliance** — checklist of 14 items per spec §15.
16. **Risks observed during implementation** — any deviation from §13 risk register or new risk.
17. **Follow-up slice recommendations** — `FE-SE-MODEA-MODAL-10`, `FE-SE-DEAD-CODE-01`, `FE-I18N-HYGIENE-01` if relevant.

---

## OUTPUT EXPECTED FROM YOU AT EACH STEP

While running, emit short progress markers in chat:

- "Step 0 reads complete — N files read."
- "Step 1 i18n keys added — K keys, lint:i18n:registry PASS."
- "Step 2 child components refactored — build PASS."
- "Step 3 page refactored — build PASS, lint PASS."
- "Step 4 TODO comment added."
- "Step 5 mandatory gates: build PASS / lint PASS / check:routes 24/24 / lint:i18n:registry PASS / unit-test [PASS|SKIPPED:reason]."
- "Step 5 manual walk-through: 7/7 scenarios verified."
- "Step 6 implementation report committed at docs/audit/fe-se-modea-simplify-09-implementation-report.md."

If you hit a stop condition, emit "STOP — condition #N — see report at <path>" and halt.

---

## FINAL REMINDER

You are not redesigning the surface. The redesign is locked in spec v1.1. Your job is faithful, surgical implementation of decisions D-01..D-09 and rules IR-01..IR-11, nothing more, nothing less. If a question is not answered by the spec, the answer is: stop and report.

End of prompt.
