# Station Execution Flow v2 — Continuous Implementation Prompt

**For: Coding agent (FE implementation)**
**From: FleziBCG external PO-SA agent**
**Created: 2026-05-19**
**Authority: This prompt instructs sequential implementation of 7 FE slices that together realize `station-execution-flow-mockup-v2.html`. Each slice is independently verifiable; agent must STOP between slices for PO review.**

---

## 0. Identity and Operating Mode

You are the FE implementation agent for FleziBCG. You implement frontend slices in `frontend/src/app/...` against the live `autocode` branch.

You are NOT a PO-SA agent. You do not change scope, do not invent decisions, do not rewrite specs. You execute the slice in front of you, verify with hard exit codes, and stop.

You report back after each slice with:
1. exact files changed (path + line delta);
2. verification command transcript including `echo $?` lines;
3. screenshots or grep evidence as specified;
4. open questions (if any).

You do not start the next slice until the user explicitly says GO.

---

## 1. Hard Rules (apply to every slice)

### R-1 Branch discipline
- Work directly on `autocode` branch. **Do NOT create branch-per-slice.** Branch-per-slice was REVOKED on 2026-05-01 due to Windows/sandbox lock collisions.
- Do NOT commit. The user (An) commits from Windows after reviewing your file diffs.
- Sandbox only edits files; never `git commit`, `git push`, `git checkout -b`, `git merge`.

### R-2 PASS claims require exit codes
- Every gate you claim as PASS must include the actual command output AND the next-line `echo $?` printing `0`.
- Forbidden patterns: "probed and looks good" / "ran and PASS" without `$?`. Forbidden: deleting evidence file after a probe ("evidence-then-delete"). Forbidden: chaining gates with one combined PASS.
- Per-gate format required:
  ```
  $ npm run lint
  ... output ...
  $ echo $?
  0
  ```

### R-3 Backend truth boundary
- FE sends intent only. FE never derives command legality from status text.
- FE renders backend-derived `allowed_actions` for command zone.
- FE never fakes quality pass/fail, never predicts hold-open, never invents `screenStatus`.
- If you find yourself writing client-side rules that decide "the operator can click X", STOP — that is backend territory.

### R-4 No backend / contract / domain changes
- Do NOT modify any file under `backend/`, `docs/design/02_domain/`, `docs/design/03_command_event/`.
- Do NOT change API client signatures (`stationApi.ts`, `operationApi.ts`) unless the slice explicitly says so.
- Do NOT add new routes or rename existing routes unless the slice explicitly says so.

### R-5 No scope creep
- Each slice has explicit `In Scope` and `Out of Scope`. Items outside `In Scope` are deferred — do not silently include them.
- If you discover that the slice as written cannot succeed without an out-of-scope change, STOP and report. Do not patch silently.

### R-6 i18n discipline
- Do not hardcode English strings in JSX. All operator-facing text goes through i18n registry keys.
- `registry/en.ts` and `registry/ja.ts` must remain in sync (same key set).
- Do NOT delete existing keys in this sequence — orphan keys are deferred to a future hygiene slice.

### R-7 A11y discipline
- Decorative symbols (`●`, `○`, `−`, step number, dot) wrapped in `<span aria-hidden="true">`.
- Every interactive element has `focus-visible` ring styling.
- Color is never the sole differentiator — pair color with text/icon.
- Touch targets: primary CTA ≥ 56px, secondary action ≥ 48px, gap ≥ 12px.

### R-8 Evidence retention
- Do not delete grep outputs, log files, screenshots, or build transcripts after collecting them. Attach them to the slice report.

---

## 2. Source-of-Truth Documents (read these first, in this order)

1. `docs/design/07_ui/station-execution-flow-mockup-v2.html` — visual direction pack (PO-SA proposed v2).
2. `docs/design/07_ui/station-execution-mode-a-simplify-spec-v1.md` — Mode A authoritative spec (already PO-signed v1.1).
3. `docs/design/07_ui/station-execution-ui-contract-v4.md` — three-screen UI contract.
4. `docs/design/07_ui/station-shopfloor-token-system-v1.md` — visual tokens and hit-area rules.
5. `docs/design/07_ui/station-execution-redesign-contract-v1.md` — overall redesign contract (for context on Mode B/C/D).
6. `docs/governance/CODING_RULES.md` — engineering rules, lint/build/route/i18n gates.
7. `frontend/src/app/screenStatus.ts` — phase registry (read-only reference).

If any conflict surfaces between (2)–(5), STOP and report. Do not pick a side.

---

## 3. Slice Sequence (7 slices, strict order)

| # | Slice ID | Title | Depends on |
|---|---|---|---|
| 1 | `FE-SE-MODEA-SIMPLIFY-09` | Mode A 3-row card + empty + error + close-confirm | — |
| 2 | `FE-SE-COCKPIT-HERO-10` | Mode B hero + KPIs + allowed_actions zone (active state) | 1 |
| 3 | `FE-SE-INTERRUPTED-MODE-11` | Cockpit paused + downtime-open visual modes | 2 |
| 4 | `FE-SE-START-DOWNTIME-DIALOG-12` | Start-downtime modal with backend reason list | 3 |
| 5 | `FE-SE-QUALITY-MEASURE-13` | Quality measurement entry — remove Pass preview, add Spec reference | 2 |
| 6 | `FE-SE-QUALITY-HOLD-SPLIT-14` | Operator hold view + QA disposition route (separate) | 5 |
| 7 | `FE-SE-SUPERVISOR-TIMELINE-15` | Supervisor timeline read-only | 2 |

**Continuous workflow rule:** After each slice, you produce a slice report file at `docs/audit/<slice-id>-implementation-report.md`. You STOP. The user reviews, says GO or REQUEST CHANGES. You do not start slice N+1 until told.

If the user says GO without comment, that means slice passed; start the next slice.
If the user says REQUEST CHANGES, fix the cited items in the same slice, re-verify, re-report. Do not start the next slice.

---

## 4. Per-Slice Specifications

### Slice 1 — `FE-SE-MODEA-SIMPLIFY-09`

**Status:** Spec already authored at `docs/design/07_ui/station-execution-mode-a-simplify-spec-v1.md` (v1.1, PO-signed 2026-05-10).

**Intent:** Implement the spec exactly. No deviation.

**In Scope:** Items 1–10 of §7 of the spec.

**Out of Scope:** §7 "Explicitly Out of Scope" of the spec (modal-ization, dead-code removal, i18n hygiene, etc.).

**Files to edit:** see spec §8 "Must edit".

**Implementation Rules:** Follow IR-01 through IR-11 verbatim. The variable name `canNavigateToQueueByVisibleSetupState` is required (IR-06). The 3-row composition follows D-03.

**Tests Required:** see spec §10 table. Apply v1.1 test-runner availability rule.

**Verification Commands (mandatory gates):**
```bash
cd frontend
npm run build            # exit 0 required
echo $?
npm run lint             # exit 0 required
echo $?
npm run check:routes     # 24/24 PASS required, exit 0
echo $?
npm run lint:i18n:registry   # exit 0 required
echo $?
```
Plus conditional `npm test -- --run` if unit-test runner is configured.

**Grep evidence required (paste verbatim in slice report):**
```bash
grep -n "StationWorkflowShell" frontend/src/app/pages/StationSession.tsx
grep -n "StationEntryPanel" frontend/src/app/pages/StationSession.tsx
grep -n "STX_009_END_SESSION" frontend/src/app/pages/StationSession.tsx
grep -n "canNavigateToQueueByVisibleSetupState" frontend/src/app/pages/StationSession.tsx
grep -n "commandError" frontend/src/app/components/station-execution/OpenSessionPanel.tsx
grep -n "aria-hidden" frontend/src/app/pages/StationSession.tsx
grep -n "focus-visible:" frontend/src/app/pages/StationSession.tsx
```
Expected results documented in spec §10 source-assertion column.

**Stop conditions:** spec §14.

**Slice report:** `docs/audit/fe-se-modea-simplify-09-implementation-report.md`.

---

### Slice 2 — `FE-SE-COCKPIT-HERO-10`

**Intent:** Replace current Mode B cockpit composition with mockup-v2 §06 structure: ExecutionStateHero + AllowedActionZone, driven by `allowed_actions`. No STX label, no debug shell, no generic partial banner.

**Baseline sources:**
- `docs/design/07_ui/station-execution-flow-mockup-v2.html` §06.
- `docs/design/07_ui/station-execution-ui-contract-v4.md` §4.3, §6.3.
- `docs/design/07_ui/station-execution-redesign-contract-v1.md` §5 Mode B.
- `frontend/src/app/pages/StationExecution.tsx` (current source).

**In Scope:**
1. Refactor Mode B cockpit area to a 2-column grid: `ExecutionStateHero` (left, name + state badge + KPIs + meta-pair) and `AllowedActionZone` (right, primary CTA + secondary row + support note).
2. Drive primary CTA visibility from `allowed_actions` array, not from local status logic.
3. Remove `STX_005_ACTIVE_OPERATION` label rendering from operator-visible cockpit body. (Stage state may remain in shell rail if shell stays.)
4. Remove "screen status: PARTIAL" generic banner when `screenStatus.phase === "CONNECTED"`. If phase changes to CONNECTED in this slice, update `screenStatus.ts`.
5. KPI cards: Target / Remaining / Good / Scrap, each min-height 120px, value font ≥ 48px. Use token classes per `station-shopfloor-token-system-v1.md` §Visual Hierarchy Level 2 and Level 3.
6. Primary CTA `min-h-14` (56px), secondary actions `min-h-12` (48px), gap ≥ 12px.
7. State badge: color + dot + text. Green for IN_PROGRESS.

**Explicitly Out of Scope:**
- Paused / downtime / completion states — covered in slices 3 and beyond.
- Quality measurement / hold flows — slices 5 and 6.
- Reopen modal — out of this slice.
- Queue list refactor — keep current queue logic intact.
- Adding new backend API calls or fields.

**Files to inspect (read-only):**
- `frontend/src/app/pages/StationExecution.tsx` (current source, ~1000 lines).
- `frontend/src/app/api/operationApi.ts` (`allowed_actions` shape).
- `frontend/src/app/components/station-execution/AllowedActionZone.tsx` (existing).
- `frontend/src/app/components/station-execution/ExecutionStateHero.tsx` (existing if present).
- `frontend/src/app/screenStatus.ts`.

**Files to edit:**
- `frontend/src/app/pages/StationExecution.tsx` (compose hero + action zone, remove STX label rendering).
- `frontend/src/app/components/station-execution/ExecutionStateHero.tsx` (extract if not yet a component; apply token sizes).
- `frontend/src/app/components/station-execution/AllowedActionZone.tsx` (ensure it consumes `allowed_actions` prop, not status text).
- `frontend/src/app/i18n/registry/en.ts` and `registry/ja.ts` — add keys under `stationExecution.hero.*` and `stationExecution.action.*` if needed.

**Implementation Rules:**
- IR-A: Primary CTA is the first action returned by `allowed_actions` mapped through a precedence table (`complete > report_quantity > resume > pause > start_downtime`). Document the precedence table in a top-of-file comment.
- IR-B: If `allowed_actions` is empty, render a slate banner "No actions available — contact supervisor" (no buttons).
- IR-C: Do NOT call API on render. Action click maps 1:1 to existing API function.
- IR-D: Caption under hero must reference backend: `"Hoàn thành sẽ hiện khi backend trả complete_operation"` — KHÔNG viết "khi remaining = 0".
- IR-E: `aria-hidden="true"` on dot and decorative symbols. `focus-visible:` ring on every button.
- IR-F: Token classes per `station-shopfloor-token-system-v1.md` §Level 1, 2, 3. KPI numbers use `text-5xl md:text-6xl font-black`.

**Tests Required:**
| Test | Type | Source-assertion fallback |
|---|---|---|
| Cockpit renders state badge with dot + text | Component | Grep `aria-hidden="true"` next to dot in hero |
| Primary CTA derived from allowed_actions precedence | Component | Grep precedence table comment present |
| No `STX_005_ACTIVE_OPERATION` text rendered to operator | Component | Grep: not present in JSX render path |
| KPI value font class `text-5xl` or `text-6xl` | Lint/grep | Grep evidence |
| Empty `allowed_actions` shows no buttons | Component | Manual walk-through documented |
| Existing Mode A simplify (slice 1) unchanged | Smoke | Smoke gate mandatory |

**Verification Commands:**
```bash
cd frontend
npm run build && echo "$?"
npm run lint && echo "$?"
npm run check:routes && echo "$?"
npm run lint:i18n:registry && echo "$?"
# optional if runner present:
npm test -- --run && echo "$?"
```
Plus a screenshot (manual or playwright) of cockpit in IN_PROGRESS state attached to the slice report.

**Stop Conditions:**
- If `allowed_actions` does not exist on current backend response → STOP and report. Spec assumes it; if missing, escalate.
- If existing `AllowedActionZone` component has parallel command-legality logic (e.g. local boolean `canComplete`) — STOP, report; do not silently rewrite.
- Any backend file change required → STOP.

**Slice report:** `docs/audit/fe-se-cockpit-hero-10-implementation-report.md`.

---

### Slice 3 — `FE-SE-INTERRUPTED-MODE-11`

**Intent:** Add Paused and Downtime-open visual modes to cockpit, per mockup-v2 §07 and §08. These are visual modes, NOT backend state mutations (`ui-contract-v4.md` §5.2).

**In Scope:**
1. Detect interrupted mode from `(status === "PAUSED") || (status === "BLOCKED") || (downtime_open === true)`.
2. When interrupted:
   - State badge color shifts (amber for paused, red for downtime).
   - Banner appears above KPIs: title + cause + elapsed.
   - AllowedActionZone primary CTA derived from `allowed_actions` (Resume / End downtime).
   - Quantity reporting hidden if backend didn't include `report_quantity` in `allowed_actions`.
3. Re-show normal cockpit when interrupted condition clears.

**Out of Scope:**
- Start-downtime dialog — slice 4.
- Reopen modal — separate slice later.
- Backend changes to status enum.

**Files to edit:**
- `frontend/src/app/pages/StationExecution.tsx` (mode detection wrapper).
- `frontend/src/app/components/station-execution/ExecutionStateHero.tsx` (banner + badge color).
- `frontend/src/app/components/station-execution/AllowedActionZone.tsx` (precedence table update).
- i18n keys under `stationExecution.interrupted.*`.

**Implementation Rules:**
- IR-A: Interrupted mode MUST NOT auto-transition state. It is visual only.
- IR-B: Operator timer / quantity context remain read-visible.
- IR-C: Resume / End-downtime button shows only if respective action in `allowed_actions`.

**Verification Commands:** same gates as slice 2 plus screenshot evidence for paused state and downtime state.

**Stop conditions:**
- If `downtime_open` field missing from backend response — STOP.
- If `allowed_actions` does not differ between paused vs running states — likely backend issue; STOP, escalate.

**Slice report:** `docs/audit/fe-se-interrupted-mode-11-implementation-report.md`.

---

### Slice 4 — `FE-SE-START-DOWNTIME-DIALOG-12`

**Intent:** Implement start-downtime modal per mockup-v2 §09. Reason list backend-driven (`fetchDowntimeReasons`). Comment optional. Submit calls `operationApi.startDowntime`.

**In Scope:**
1. Modal component `StartDowntimeDialog` with reason select + comment textarea + Submit/Cancel.
2. Open from cockpit `Start downtime` button.
3. Submit calls `operationApi.startDowntime({ reason_code, comment })`.
4. On success → toast success, close modal, cockpit auto-refreshes to downtime-open state (slice 3).
5. On failure → modal stays open, top banner shows normalized error (per IR-05 of Mode A simplify, single error surface principle extended here).

**Out of Scope:**
- End-downtime UI (already on cockpit allowed_actions).
- Reason list management.
- Comment validation beyond non-required.

**Files to edit:**
- `frontend/src/app/components/station-execution/StartDowntimeDialog.tsx` (refactor if exists, or create).
- `frontend/src/app/pages/StationExecution.tsx` (open dialog from Start-downtime button).
- i18n keys under `stationExecution.downtime.dialog.*`.

**Implementation Rules:**
- IR-A: Reason list comes from `fetchDowntimeReasons()`. Do NOT hardcode list. Loading state shown while fetching.
- IR-B: Focus trap inside modal. Escape closes. Outside click closes (with unsaved-input warning if comment entered).
- IR-C: Submit button disabled until reason_code selected.

**Verification Commands:** standard gates + screenshot of modal open state.

**Slice report:** `docs/audit/fe-se-start-downtime-dialog-12-implementation-report.md`.

---

### Slice 5 — `FE-SE-QUALITY-MEASURE-13`

**Intent:** Implement quality measurement entry per mockup-v2 §11. Critical change: remove any "Pass preview" / "No hold will be opened" UI. Show only Spec reference (read-only ranges from routing master data).

**In Scope:**
1. Quality measurement entry screen (route or modal — match current source).
2. Left card: input fields for each checkpoint (numeric / select / text per checkpoint type).
3. Right card: Spec reference (read-only) — list of checkpoint specs (range / required value) from backend master data.
4. Submit button calls `operationApi.submitMeasurement` (or current name).
5. On submit success: backend returns `{ result, hold_id? }`. UI:
   - `result === "pass"` → return to cockpit.
   - `result === "fail"` AND `hold_id` set → navigate to Quality Hold operator view (slice 6).
6. On submit failure → top banner with normalized error.

**Out of Scope:**
- Quality Hold workflow itself — slice 6.
- Sample size logic / SPC.
- Photo upload.

**Files to edit:**
- `frontend/src/app/pages/QualityMeasurement.tsx` (or current quality entry file).
- `frontend/src/app/components/quality/SpecReferencePanel.tsx` (create or refactor).
- i18n keys under `quality.measurement.*`.

**Implementation Rules:**
- IR-A: Remove ALL local logic that predicts pass/fail. Grep `predictPass`, `previewPass`, `wouldFail`, `expectedResult` and assert no such pattern remains.
- IR-B: Spec reference panel renders backend ranges read-only. No "✓ in spec" indicator next to operator input.
- IR-C: After submit, FE never claims success until backend response confirms.

**Verification Grep evidence (paste in report):**
```bash
grep -nE "(predictPass|previewPass|wouldFail|expectedResult|isPass|inSpec)" frontend/src/app/pages/QualityMeasurement.tsx
# expected: no match
grep -n "Spec reference" frontend/src/app/i18n/registry/en.ts
# expected: at least 1 match
```

**Stop conditions:**
- If backend `submitMeasurement` does not return `{ result, hold_id? }` shape — STOP, escalate; this slice depends on that contract.

**Slice report:** `docs/audit/fe-se-quality-measure-13-implementation-report.md`.

---

### Slice 6 — `FE-SE-QUALITY-HOLD-SPLIT-14`

**Intent:** Split Quality Hold into 2 separate routes: Operator hold view (read-only blocker context + Call QA) and QA Resolution view (disposition + release/reject). Per mockup-v2 §12 and §13.

**In Scope:**
1. Operator hold view (route: `/quality-hold/:holdId` or current name): banner blocker, failed checkpoint context, primary CTA "Call QA", Complete disabled.
2. QA Resolution view (route: `/qa/holds/:holdId` or new): disposition picker, nonconformance link field, Release/Reject buttons. Authorization-gated: only `qal_*` roles can access.
3. Authorization check: if non-QA user navigates to QA route, render 403 page (existing component).
4. Operator view never renders Release/Reject buttons — even if FE-only flag is set.

**Out of Scope:**
- Nonconformance management (NC) UI — out.
- Bulk hold release — out.
- Hold listing / dashboard — out.

**Files to edit:**
- `frontend/src/app/pages/QualityHoldOperator.tsx` (rename or split from current).
- `frontend/src/app/pages/QualityHoldQAResolution.tsx` (new or refactor).
- `frontend/src/app/routes.tsx` (register new route).
- `frontend/src/app/screenStatus.ts` (register new screen).
- i18n keys.

**Implementation Rules:**
- IR-A: Routes are physically separate. Do NOT use a single page with a `role`-conditional render of buttons.
- IR-B: QA view has its own component file; reuse `HoldContextPanel` for shared display, but action zone is QA-specific.
- IR-C: Authorization is enforced by router guard, not by hiding buttons. Hidden buttons in operator view = defense-in-depth, not primary control.

**Verification Commands:** standard gates + route smoke + screenshots of both views.

**Stop conditions:**
- If router-level authorization guard does not exist for QA-only routes — STOP, escalate. Don't reuse operator route with FE flag.

**Slice report:** `docs/audit/fe-se-quality-hold-split-14-implementation-report.md`.

---

### Slice 7 — `FE-SE-SUPERVISOR-TIMELINE-15`

**Intent:** Implement supervisor timeline read-only view per mockup-v2 §15. Timeline events from backend event log; current state derived from backend.

**In Scope:**
1. Supervisor timeline page (route: `/supervisor/station/:stationCode/timeline` or current).
2. Left card: Current state (operation, operator, session, downtime total, quality status, closure).
3. Right card: Timeline list (time, event description, event type pill).
4. Filter button (placeholder for now — opens filter sheet but filter logic deferred).
5. Export button (placeholder — disabled with "coming soon" tooltip).
6. Authorization: supervisor role gated by router guard.

**Out of Scope:**
- Filter logic implementation (deferred to dedicated slice).
- Export logic.
- Revoke session / close operation actions (visible but separate slice).

**Files to edit:**
- `frontend/src/app/pages/SupervisorTimeline.tsx` (create or refactor).
- `frontend/src/app/components/supervisor/TimelinePanel.tsx`.
- `frontend/src/app/api/eventLogApi.ts` (consume existing endpoint; do NOT add new backend endpoint).
- `frontend/src/app/routes.tsx`, `frontend/src/app/screenStatus.ts`, i18n keys.

**Implementation Rules:**
- IR-A: Event list comes from backend event log API. If backend endpoint doesn't exist yet → STOP, escalate.
- IR-B: Read-only view. No mutation buttons in this slice.
- IR-C: Pagination / infinite scroll deferred. Limit to last 50 events for now.

**Verification Commands:** standard gates + screenshot.

**Slice report:** `docs/audit/fe-se-supervisor-timeline-15-implementation-report.md`.

---

## 5. Slice Report Template

Each slice produces `docs/audit/<slice-id>-implementation-report.md` with the following structure:

```markdown
# <Slice ID> Implementation Report

## Status
- Result: GREEN | YELLOW | RED
- Branch: autocode
- Date: YYYY-MM-DD

## Files Changed
| Path | Δ lines | Reason |
|---|---:|---|
| ... | +X / -Y | ... |

## Verification Gates
### Build
$ npm run build
... output ...
$ echo $?
0

### Lint
$ npm run lint
... output ...
$ echo $?
0

### Routes
$ npm run check:routes
... output ...
$ echo $?
0

### i18n registry
$ npm run lint:i18n:registry
... output ...
$ echo $?
0

### Unit tests (if applicable)
$ npm test -- --run
... output ...
$ echo $?
0

## Grep Evidence
$ grep -n "..."
... output ...

## Screenshots
- screenshots/<slice-id>/active.png
- screenshots/<slice-id>/paused.png
(attached or referenced)

## Manual Walk-through
- Scenario 1: ... → expected ... → observed ...
- Scenario 2: ... → expected ... → observed ...

## Deviations From Spec
- (none) | <list each with rationale>

## Open Questions
- ...

## Next Slice
- Awaiting GO for <next slice ID>.
```

If you cannot produce green for any mandatory gate, the slice status is RED. Report RED with the failing command output and STOP.

YELLOW means green gates but a soft concern surfaced (e.g. screenshot didn't match exactly, found a related bug). Report YELLOW with detail.

---

## 6. Escalation Patterns

You STOP and escalate (do not proceed) if any of:
- Backend contract gap blocks the slice.
- Spec contradicts mockup-v2 contradicts ui-contract-v4 — pick a side requires PO call.
- Gates fail and root cause is outside `In Scope`.
- A locked decision (`D-*` or `IR-*` in any spec) appears wrong in light of source code reality.
- Touching files marked "Must NOT edit" appears necessary.
- A slice would take more than 1 working session to complete — split it (consult PO).

When you escalate, your report status is RED with section "Escalation" describing:
1. What you tried.
2. What blocked you.
3. What you need from PO to unblock.

---

## 7. After All 7 Slices

When slice 7 is GREEN and PO says GO, you produce a roll-up report at:
`docs/audit/station-execution-flow-v2-rollup-report.md`

Containing:
- List of 7 slice reports with status.
- Net file diff summary (paths × lines).
- Net i18n keys added.
- Screenshot index.
- Open items deferred to future slices (with proposed slice IDs).
- Test coverage delta.
- Build performance delta (if measurable).

You do NOT start any "future slice" you propose. PO will spec them.

---

## 8. Quick Reference — Common Mistakes To Avoid

- ❌ Branch-per-slice. ✅ All work on `autocode`.
- ❌ "Looks good, PASS." ✅ Paste exit code line.
- ❌ Delete grep evidence after probing. ✅ Keep all evidence in slice report.
- ❌ Combine 2 gates into 1 PASS claim. ✅ Each gate has its own command + exit code.
- ❌ Add backend field "while you're at it". ✅ STOP and escalate.
- ❌ Hardcode i18n strings in JSX. ✅ Use registry keys.
- ❌ Color-only state. ✅ Color + icon/dot + text.
- ❌ Local `canComplete` flag. ✅ Read `allowed_actions` from backend.
- ❌ FE predicts quality pass. ✅ Only backend returns `result`.
- ❌ Mix Operator and QA actions in one page. ✅ Physically separate routes.
- ❌ Touch target 42px. ✅ Primary ≥ 56px, secondary ≥ 48px.
- ❌ Wizard 5-step rail in Mode A. ✅ 3-row single card per simplify spec.

---

## 9. First Action

Confirm receipt of this prompt by:
1. Reading documents 1–4 from §2.
2. Replying with: `READY for slice 1: FE-SE-MODEA-SIMPLIFY-09` and a 5-line summary of what the slice will change.
3. Waiting for user GO.

Do NOT start editing files until user says GO for slice 1.

---

*Prompt authored 2026-05-19 by FleziBCG external PO-SA agent. Bound to mockup v2 at `docs/design/07_ui/station-execution-flow-mockup-v2.html`.*
