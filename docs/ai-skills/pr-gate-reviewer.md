# Skill: PR Gate Reviewer

Use this skill to review a pull request before merge.

## Inputs

- PR title
- PR description
- changed files
- diff
- test results
- relevant design/governance docs

## Required routing

First classify:

- Selected brain: Generic / MOM
- Selected mode: Fast / Strict / QA / Architecture / Product / Refactor / Debug / Release
- Hard Mode MOM: ON / OFF
- Reason

## Hard Mode MOM auto-trigger

Turn ON if PR touches:

- execution state machine
- execution command
- operational event
- projection/read model truth
- station/session/operator/equipment context
- production reporting
- downtime
- completion/closure
- quality hold affecting execution
- material/inventory execution impact
- tenant/scope/auth for operational commands
- critical invariant

## Reject PR if

- state machine is wrong
- required event is missing
- required invariant is missing
- execution state is mutated directly
- projection/read model is treated as source of truth
- frontend becomes execution or permission truth
- tenant/scope/auth is not enforced server-side
- service/application layer is bypassed
- critical invariant relies only on UI validation
- risky change has no test
- PR mixes mechanical refactor with behavior change without clear reason

## Output

```markdown
# PR Gate Review

## Verdict
APPROVE / REQUEST_CHANGES / COMMENT_ONLY

## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM:
- Reason:

## Summary
...

## Findings
| Severity | Area | Finding | Evidence | Required action |
|---|---|---|---|---|

## State machine check
...

## Event check
...

## Invariant check
...

## Tenant/auth check
...

## Test coverage check
...

## Release/docs check
...

## Required changes before merge
1. ...

## Suggested follow-up
1. ...
```
