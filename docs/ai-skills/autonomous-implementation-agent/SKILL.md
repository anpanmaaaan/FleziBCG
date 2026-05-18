---
name: autonomous-implementation-agent
description: Runs FleziBCG autonomous implementation loop: plan, test first, code, build, test, verify, report, next slice.
---

# Autonomous Implementation Agent

## Mission

Implement FleziBCG slice-by-slice from authoritative design baseline.

Use:

```text
PLAN → HARD MODE v3 GATE → TEST FIRST → CODE → BUILD → TEST → VERIFY → UPDATE REPORT → NEXT SLICE
```

## Mandatory Reading

1. `.github/copilot-instructions.md`
2. `docs/design/INDEX.md`
3. `docs/design/AUTHORITATIVE_FILE_MAP.md`
4. `docs/governance/CODING_RULES.md`
5. `docs/governance/ENGINEERING_DECISIONS.md`
6. `docs/governance/SOURCE_STRUCTURE.md`
7. `docs/implementation/slice-strategy-for-flezibcg.md`
8. relevant design docs for the slice

## Public Work Packet

Before coding, output this compact packet:

```markdown
## Work Packet
- User goal:
- Slice boundary:
- Selected skills read:
- Hard Mode MOM v3: on/off + reason
- Coverage target: service | API | frontend | E2E | docs-only
- Files expected to change:
- Files intentionally not changed:
- Existing patterns to reuse:
- Validation commands:
- Stop conditions:
```

Use this as the implementation contract. If later evidence changes the contract,
pause, explain the change, and update the packet before editing further.

## Scope Rule

Do not implement future scope unless explicitly requested.

Current safe order:

1. P0-A Foundation
2. P0-B MMD Minimum
3. P0-C Execution Core
4. P0-D Quality Lite
5. P0-E Supervisory

## Coding Discipline

- Read the neighboring implementation and tests before writing new code.
- Make the smallest direct edit that satisfies the slice.
- Do not mix broad cleanup, formatting, or refactor with behavior work.
- Do not bypass service/domain layers to make tests pass.
- Do not change public API/schema/DB behavior unless the slice explicitly asks
  for it and Hard Mode v3 allows it.
- Keep test names and report wording aligned with the real coverage class.
- Do not run `git add`, `git commit`, `git push`, branch changes, or history
  edits unless the user/task explicitly asks for that git operation.
- Leave implementation changes unstaged for review by default.
- Never use `git add .`.
- Before reporting done, compare the actual diff with the report. Remove or
  correct every claim that is not backed by changed code, tests, or artifacts.
- Before reporting done, classify every dirty path from `git status --short` as
  `IN SCOPE` or `OUT OF SCOPE`. Never write "not touched" for a dirty file.
- Treat unrelated staged files as a blocker unless the task explicitly includes
  them.

## Test And Fixture Discipline

- Prefer behavior tests that assert source-of-truth state, emitted events, and
  backend-derived projections/allowed actions.
- Cover the happy path plus at least one invalid/blocked path for governed
  execution, quality, auth, tenant, state, or DB behavior.
- DB fixtures that persist rows must purge before and after the test, and call
  rollback before teardown purge.
- Unique prefixes reduce collisions but do not replace cleanup.
- Cleanup order must delete child rows before parent rows; verify against
  neighboring tests before inventing a purge sequence.
- If validation runs in Docker, verify whether the service mounts live source.
  If not, use the repo-approved live-source bind mount or rebuild the image.
- Never report a command as passed unless the exit code or captured log proves it.
- Non-zero Exit Honesty Rule: a command that exits non-zero is `FAIL`, even when
  the failures are baseline or unrelated to the current slice. Report baseline
  failures separately from failures introduced, fixed, or still affecting the
  slice.
- `git diff --check` is a verification command. If it reports trailing
  whitespace, conflict markers, or any other issue, report it as failed until
  fixed.
- Assertion failures must fail the command. Do not rely only on
  `process.exitCode = 1` while continuing to print pass-like output.
- If stdout/stderr contains assertion failures, the command must be reported as
  failed even when the process exits 0.

## Guard Regression Check

Before the final report, compare touched workflow guards against the previous
implementation whenever the slice changes buttons, route transitions,
enabled/disabled conditions, allowed actions, readiness checks, or workflow
progression.

Required behavior:

- Preserve existing guards during cleanup, refactor, visual redesign, and
  prop-contract fixes unless the task explicitly requests a behavior change.
- Treat weaker station/session/execution, quality, material, tenant, auth, or
  operator readiness gating as a regression unless explicitly authorized.
- If a guard changes intentionally, report the old condition, the new condition,
  the reason, and the verification.

## Pre-Final Self-Review Gate

Before the final report, run a self-review:

```markdown
## Implementation Self-Review
- `git status --short` checked:
- Expected changed files present:
- Unexpected changed files:
- OUT OF SCOPE dirty files:
- Untracked implementation files:
- Generated artifact paths:
- Files intended for commit:
- New files integrated/imported where claimed:
- Acceptance criteria backed by diff/tests/screenshots:
- Commands with reliable exit codes:
- Commands skipped or not trusted:
- Behavior preserved:
- Behavior intentionally changed:
- Behavior changed accidentally/fixed:
- Report claims match actual diff:
```

If any answer exposes a gap, fix it or report the slice as incomplete. Do not
write a successful final report while code is unintegrated, screenshot evidence
is stale, or required assertions are failing.

## Artifact And Commit Gates

- Generated screenshots, videos, and binary evidence under `docs/audit/**` are
  review artifacts unless the prompt explicitly says to commit them.
- Report artifacts under `Generated artifact paths`; report code/docs/test paths
  under `Files intended for commit`.
- Do not stage or commit PNG, JPG, JPEG, GIF, WebP, MP4, or WebM artifacts under
  `docs/audit/**` unless explicitly requested.
- If staging or committing is explicitly requested, run and report
  `git diff --cached --stat`, `git diff --cached --name-status`, and
  `No unrelated staged files: yes/no` before commit.
- If artifacts are already tracked/staged/committed against policy, report a
  blocker instead of a clean pass.

## Stop Conditions

Stop only if:

- all codeable items in current phase are complete
- remaining items require ADR/business/security decision
- remaining items are excluded future scope
- build/test environment is blocked
- Hard Mode v3 returns BLOCKED_NEEDS_DESIGN or BLOCKED_SCOPE_EXCLUDED

Stop and report a blocker if validation cannot be trusted because the command ran
against stale source, ambiguous logs, or a failed test environment.

## Reports to update

- `docs/implementation/autonomous-implementation-plan.md`
- `docs/implementation/autonomous-implementation-verification-report.md`
- slice-specific design/test report when relevant

## Final Report Requirements

Every final report must include:

- selected skills read;
- coverage class actually proven;
- files changed;
- `git status --short` summary;
- IN SCOPE / OUT OF SCOPE dirty file classification;
- files intended for commit;
- generated artifact paths;
- staged diff summary if git operations were explicitly requested;
- untracked implementation/artifact files;
- commands run with reliable results;
- what is not covered;
- known environment caveats;
- next slice recommendation.

Do not claim API/RBAC/E2E/pilot golden path coverage from service-only tests.

Also overwrite the canonical repo report file before marking done:

```text
docs/agent-reports/latest-agent-report.md
```

If this file cannot be written, stop and report the export failure as a blocker.
