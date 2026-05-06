---
name: "FleziBCG Post-Bugfix"
description: "Use when closing a bug fix, failed test, failing validation, or unexpected behavior in FleziBCG. Names the root cause, guards against recurrence, and captures the lesson in repo memory."
---
# Post-Bugfix Workflow

Run this checklist after every bug fix, failed test resolution, or unexpected validation outcome.

## 1. Name the Root Cause

Before writing any fix:

- State explicitly what was wrong, not just what the symptom was.
- Distinguish between:
  - **Wrong assumption in the agent or spec** — the design was based on incorrect beliefs about the repo
  - **Missing guard or validation** — a rule existed but was not enforced at the right boundary
  - **Stale context** — the agent acted on outdated information (migration state, contract baseline, import path)
  - **Implementation mistake** — correct design, incorrect code

Do not write a fix without naming which of these applies.

## 2. Apply the Minimal Correct Fix

- Change only what the root cause demands.
- Do not refactor adjacent code unless it caused the bug.
- Re-run the narrowest available check to confirm the fix is sufficient.

Checks by area:

- Backend logic: `cd backend && python -m pytest -q -k "<test>"` or import check
- Frontend: `cd frontend && npm run lint && npm run build`
- i18n: `cd frontend && npm run lint:i18n && npm run lint:i18n:registry`
- Contract baseline: verify route hash or OpenAPI hash only if a route changed

## 3. Guard Against Recurrence

For each root cause type:

| Root cause | Guard to add |
|---|---|
| Wrong assumption | Record the correct fact in repo memory |
| Missing guard | Add or reference the test case that catches it |
| Stale context | Record what to verify before assuming current state |
| Implementation mistake | Note the pattern to avoid in repo memory if recurring |

## 4. Record the Lesson

1. Read `/memories/repo/` to find the best existing file.
2. Add one short factual note: root cause, what assumption was wrong, and the guard that prevents it next time.
3. Prefer updating an existing file over creating a new one.
4. Do not store speculative ideas; only verified facts.

## 5. Closeout Statement

The bugfix response must end with:

```
## Bugfix Closeout
- Root cause type: [wrong assumption / missing guard / stale context / implementation mistake]
- Root cause: [one sentence]
- Fix applied: [what changed]
- Validation: [command run and outcome]
- Recurrence guard: [test added / memory updated / rule enforced]
- Memory updated: [yes — what was recorded / no]
```
