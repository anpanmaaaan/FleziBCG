# Skill: triage-issue

## Purpose
Investigate a bug, gap, or failing behavior and produce a root-cause analysis plus a TDD-based fix plan.

## Use when
- A bug is reported.
- Source code does not match design.
- Tests fail and the cause is unclear.
- A feature behaves inconsistently.

## Process
1. Restate the reported issue.
2. Identify expected behavior.
3. Identify actual behavior.
4. Inspect the relevant code paths.
5. Reproduce or reason about the failure.
6. Identify root cause.
7. Propose a minimal fix.
8. Propose regression tests.
9. Identify risks and out-of-scope areas.

## Output format
```md
# Triage Report: <Issue>

## Summary
## Expected Behavior
## Actual Behavior
## Evidence
## Root Cause
## Affected Files
## Proposed Fix
## Regression Tests
## Risks
## Out of Scope
```

## Rules
- Do not jump straight to implementation.
- Prefer evidence from code, tests, logs, or docs.
- If uncertain, state uncertainty explicitly.
- Fix root cause, not just symptoms.
