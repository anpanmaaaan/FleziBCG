# FE-SE-INTERRUPTED-MODE-11-CORRECTION — Harden interrupted-mode harness with visible text assertions

## Result

**GREEN.** All gates pass. Harness exit 0. 4 scenarios × 7 assertions = 28 PASS lines. One source bug surfaced and fixed (PAUSED + downtime_open showed the "paused/resume" reporting-disabled reason instead of the "downtime" reason expected by the prompt and consistent with the andon banner).

## Routing
- Selected brain: MOM Brain + FleziBCG Frontend
- Hard Mode MOM v3: kept from parent slice (yes)
- Coverage class: frontend
- Selected skills read:
  - `.github/copilot-instructions.md`
  - `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
  - `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
  - `docs/ai-skills/design-md-ui-governor/SKILL.md`
  - `docs/ai-skills/autonomous-implementation-agent/SKILL.md`
  - `docs/ai-skills/qa-e2e-layer/SKILL.md`
  - `frontend/scripts/station-execution-interrupted-qa-screenshots.mjs` (parent harness)
  - `frontend/src/app/components/station-execution/StationAndonBanner.tsx`
  - `frontend/src/app/pages/StationExecution.tsx`
  - `frontend/src/app/i18n/registry/en.ts` and `ja.ts` (verified exact strings)
  - `docs/agent-reports/latest-agent-report.md` (parent slice export)

## Problem fixed

Parent harness verified severity, primary action, allowed/forbidden actions, and reporting testid only. It did not assert the *visible operator guidance text* in the andon banner or the *visible reason text* in the disabled-reporting section. This correction adds those two text assertions per scenario.

While adding the text assertion to scenario C (PAUSED + downtime_open), the harness surfaced a real bug: the disabled-reporting reason said "Reporting is disabled while execution is paused. Resume to continue reporting." even though the andon banner correctly said "Next: end the open downtime." The reason precedence in `reportingHint` checked `BLOCKED && downtime_open` before plain `PAUSED`, so PAUSED + downtime_open fell through to the paused string. The fix promotes `downtime_open` to the top of the precedence (mirroring the andon banner).

## What changed

### 1. `frontend/scripts/station-execution-interrupted-qa-screenshots.mjs`

- Header docstring updated to mark FE-SE-INTERRUPTED-MODE-11-CORRECTION.
- Per scenario, added two new `expect` fields:
  - `bannerTextRegex`
  - `reportingTextRegex`
- Added two new assertion helpers:
  - `assertBannerGuidanceText(page, scenarioId, regex)` — reads `textContent` of `[data-testid="station-andon-banner"]` and matches the regex; fails with the observed text if it does not match.
  - `assertReportingDisabledReasonText(page, scenarioId, regex)` — reads `textContent` of `[data-testid="report-input-disabled"]` and matches the regex; fails with the observed text if it does not match.
- Both new assertions log the observed text on PASS for review traceability.
- `runScenario` now calls both new assertions after `assertReportingTestid`. The reason-text assertion only runs when `reportingTestid === "report-input-disabled"` (the only path under test in this slice).
- All existing assertions (severity, primary action, allowed/forbidden actions, reporting testid, nav-intent regression) and the 4-scenario structure are unchanged.

### 2. `frontend/src/app/pages/StationExecution.tsx`

- `reportingHint` precedence now checks `operation?.downtime_open` first, then `status === "BLOCKED"`, then `status === "PAUSED"`. This makes the visible reason text consistent with the andon banner whenever a downtime is open, regardless of `status`.
- No other behavior change. No new state, no new component, no change to `canReportProduction`, no change to action legality (`allowed_actions`), no change to nav-intent code paths, no change to closure or quality-hold paths, no change to JSX structure.

## Exact text assertions added

| Scenario | `bannerTextRegex` | `reportingTextRegex` |
| --- | --- | --- |
| A — PAUSED, no downtime, desktop | `/resume/i` | `/paused|resume/i` |
| B — BLOCKED, downtime_open, desktop | `/end.*downtime|open downtime/i` | `/downtime|end downtime/i` |
| C — PAUSED, downtime_open, desktop | `/end.*downtime|open downtime/i` | `/downtime|end downtime/i` |
| D — PAUSED, no downtime, tablet | `/resume/i` | `/paused|resume/i` |

Observed visible text recorded by harness (English locale, default):

- A banner: `"Guidance / Blockers" + "Next: resume execution to continue." + "Reporting is disabled while execution is paused. Resume to continue reporting."`
- A reporting-disabled: `"Input / Reporting" + "Reporting is disabled while execution is paused. Resume to continue reporting."`
- B banner: `"Guidance / Blockers" + "Next: end the open downtime." + "Reporting is disabled while downtime is open. End downtime before reporting."`
- B reporting-disabled: `"Input / Reporting" + "Reporting is disabled while downtime is open. End downtime before reporting."`
- C banner: same as B.
- C reporting-disabled: **after fix** matches B reporting-disabled. **Before fix** read "Reporting is disabled while execution is paused. Resume to continue reporting." (the bug the harness caught).
- D banner / reporting-disabled: same as A.

No new i18n keys added. Existing keys reused:
- `station.block.guidance`
- `station.hint.nextAction.resume`
- `station.hint.nextAction.endDowntime`
- `station.input.disabledHint.paused`
- `station.input.disabledHint.blocked`

## Files intended for commit (this correction slice)

- `frontend/scripts/station-execution-interrupted-qa-screenshots.mjs`
- `frontend/src/app/pages/StationExecution.tsx`

## Existing/parent changes observed (already dirty when this slice started)

- `frontend/src/app/components/station-execution/AllowedActionZone.tsx` — parent FE-SE-INTERRUPTED-MODE-11; not modified here.
- `frontend/src/app/components/station-execution/StationAndonBanner.tsx` — parent FE-SE-INTERRUPTED-MODE-11; not modified here.
- `frontend/src/app/pages/StationExecution.tsx` — parent slice already had testid additions; this correction adds the `reportingHint` precedence fix on top.
- `frontend/scripts/station-execution-interrupted-qa-screenshots.mjs` — parent file extended here with text assertions.
- `docs/audit/fe-se-interrupted-mode-11/` (4 PNGs) — parent slice artifact; re-generated this slice (timestamps reflect this run).
- `docs/audit/fe-se-nav-intent-11/` — parent slice artifact; untouched here.
- `.github/copilot-instructions.md`, `docs/ai-skills/autonomous-implementation-agent/SKILL.md`, `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`, `docs/prompts/copilot-agent-handoff-review-workflow.md`, `docs/agent-context/` — appeared modified/new in `git status` at the start of this run; **not authored or touched by this slice**, OUT OF SCOPE.

## Generated artifact paths (not commit payload)

- `docs/audit/fe-se-interrupted-mode-11/A-paused-no-downtime-desktop.png`
- `docs/audit/fe-se-interrupted-mode-11/B-blocked-downtime-open-desktop.png`
- `docs/audit/fe-se-interrupted-mode-11/C-paused-downtime-open-desktop.png`
- `docs/audit/fe-se-interrupted-mode-11/D-paused-no-downtime-tablet-tablet.png`
- `_corr_build.log`, `_corr_lint.log`, `_corr_routes.log`, `_corr_i18n.log`, `_corr_harness.log`, `_corr_diff.log`, `_corr_status.log` (workspace-root scratch logs)

## Full `git status --short` classification

```
 M .github/copilot-instructions.md                                                   OUT OF SCOPE — not authored or modified by this slice
 M docs/agent-reports/latest-agent-report.md                                         ARTIFACT — this canonical report
 M docs/ai-skills/autonomous-implementation-agent/SKILL.md                           OUT OF SCOPE — not authored or modified by this slice
 M docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md                       OUT OF SCOPE — not authored or modified by this slice
 M docs/prompts/copilot-agent-handoff-review-workflow.md                             OUT OF SCOPE — not authored or modified by this slice
 M frontend/src/app/components/station-execution/AllowedActionZone.tsx               OUT OF SCOPE THIS SLICE — parent FE-SE-INTERRUPTED-MODE-11
 M frontend/src/app/components/station-execution/StationAndonBanner.tsx              OUT OF SCOPE THIS SLICE — parent FE-SE-INTERRUPTED-MODE-11
 M frontend/src/app/pages/StationExecution.tsx                                       IN SCOPE — reportingHint downtime-first precedence fix
?? docs/agent-context/                                                               OUT OF SCOPE — not authored by this slice
?? docs/audit/fe-se-interrupted-mode-11/                                             ARTIFACT — 4 screenshots (refreshed this run)
?? docs/audit/fe-se-nav-intent-11/                                                   ARTIFACT — parent slice
?? frontend/scripts/station-execution-interrupted-qa-screenshots.mjs                 IN SCOPE — text assertions added (parent file was also untracked)
```

Note: parent slice files `AllowedActionZone.tsx`, `StationAndonBanner.tsx`, the parent edits inside `StationExecution.tsx`, and the parent harness `station-execution-interrupted-qa-screenshots.mjs` are still pending commit from FE-SE-INTERRUPTED-MODE-11 — when committing this correction they should be folded into a single fixup or paired commit per user direction.

No `git add` / `git commit` / `git push` performed by this slice.

## Commands run and reliable results

| Command (cwd) | Exit | Verdict |
| --- | --- | --- |
| `npm.cmd run build` (frontend) | 0 | PASS — vite v6.4.1 built in 10.47s |
| `npm.cmd run lint` (frontend) | 0 | PASS (cmd: LINT_OK) |
| `npm.cmd run check:routes` (frontend) | 0 | PASS (cmd: ROUTES_OK) |
| `npm.cmd run lint:i18n:registry` (frontend) | 0 | PASS (cmd: I18N_OK) |
| `node scripts/station-execution-interrupted-qa-screenshots.mjs 5173` (frontend) | 0 | PASS — 4 scenarios, 7 assertions each, 28 PASS lines (post-fix run) |
| `git diff --check` (root) | 0 | PASS (cmd: DIFF_OK) |
| `git status --short` (root) | 0 | classified above |

Pre-fix harness run captured the bug for scenario C:

```
FAIL: [C-paused-downtime-open]: report-input-disabled reason text did not match /downtime|end downtime/i.
Observed: "Input / ReportingReporting is disabled while execution is paused. Resume to continue reporting."
```

Post-fix harness run for the same scenario:

```
PASS [C-paused-downtime-open]: reporting-disabled reason text matches /downtime|end downtime/i.
Observed: "Input / ReportingReporting is disabled while downtime is open. End downtime before reporting."
```

This is the root cause evidence required by the Correction Task Gate: the fix was made in `frontend/src/app/pages/StationExecution.tsx#reportingHint`, not in the report or the harness regex.

## Screenshot evidence

Output directory: `docs/audit/fe-se-interrupted-mode-11/`

- [docs/audit/fe-se-interrupted-mode-11/A-paused-no-downtime-desktop.png](docs/audit/fe-se-interrupted-mode-11/A-paused-no-downtime-desktop.png) — PAUSED no downtime; banner /resume/i; reporting /paused|resume/i.
- [docs/audit/fe-se-interrupted-mode-11/B-blocked-downtime-open-desktop.png](docs/audit/fe-se-interrupted-mode-11/B-blocked-downtime-open-desktop.png) — BLOCKED + downtime_open; banner /end.*downtime/i; reporting /downtime/i.
- [docs/audit/fe-se-interrupted-mode-11/C-paused-downtime-open-desktop.png](docs/audit/fe-se-interrupted-mode-11/C-paused-downtime-open-desktop.png) — PAUSED + downtime_open; banner /end.*downtime/i; reporting /downtime/i (post-fix).
- [docs/audit/fe-se-interrupted-mode-11/D-paused-no-downtime-tablet-tablet.png](docs/audit/fe-se-interrupted-mode-11/D-paused-no-downtime-tablet-tablet.png) — PAUSED no downtime, tablet 834×1112; banner above the fold (y=311).

All screenshots regenerated by the post-fix harness run. Mocked API data — visual QA only.

## UI guard preservation

- `AllowedActionZone` legality unchanged; `backendAllowed.has(id)` still the only legality filter. No changes to primary precedence either.
- `canReportProduction`, `canDo`, `sessionGate`, closure lock, ownership, queue refresh stale-clear, nav-intent useEffect, deep-link selection — **all unchanged**.
- Only the *visible text* selected by `reportingHint` was reordered to match the andon banner. No new action is enabled or disabled by this change.

## Navigation intent classification (re-confirmed)

- `/station` LANDING — no auto-select; per-scenario regression PASS (4/4).
- `/station?operationId=42` DETAIL/COCKPIT via deep link.
- Implicit first-item selection present: **no**.
- Initial URL entity-id mutation present: **no**.

## Limitations / not covered

- No backend / API / RBAC coverage; visual QA with mocked `OperationDetail` only.
- Text assertions are English-locale dependent (default). `ja.ts` parity verified at registry level (`lint:i18n:registry` exit 0) but Japanese text is not asserted by this harness.
- Reporting-disabled reason text precedence change is FE-only and does not affect any allowed-action gating.
- Outstanding OUT OF SCOPE dirty files in repo were not touched by this slice; reviewer should resolve them out-of-band.

## Deviations from prompt

- Source change in `StationExecution.tsx#reportingHint` was made because the harness revealed scenario C's visible reason text was semantically wrong (said "paused/resume" while downtime was open). The prompt explicitly authorizes a fix when "current visible text is different but semantically correct" is not met. The change is the minimum required and does not alter any guard.

## Next recommended slice

- Mirror the same downtime-first precedence in any other status-derived operator hints (e.g. status pill subtitle) if they exist, to avoid divergent operator messaging.
- Add a Playwright E2E variant of these scenarios that drives a real backend so the assertions also gate backend `allowed_actions` and reason-text consistency.

## STOP

No staging, no commit, no push. Awaiting `GO` or `REQUEST CHANGES`.
