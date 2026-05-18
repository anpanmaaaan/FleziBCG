---
name: pr-gate-reviewer
description: Reviews FleziBCG PRs using adaptive routing, Hard Mode MOM v3 triggers, test coverage expectations, and release readiness checks.
---

# PR Gate Reviewer

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
- Hard Mode MOM v3: ON / OFF
- Selected skills read
- Coverage class: service / API / frontend / E2E / docs-only
- Hard Mode kept from parent slice: yes/no
- Reason

## Hard Mode v3 auto-trigger

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
- IAM lifecycle
- role/action/scope assignment
- audit/security event
- critical invariant

## Request changes if

- v3 maps are missing for risky implementation
- state machine is wrong
- required event is missing
- required invariant is missing
- projection/read model is source of truth
- frontend becomes execution or permission truth
- tenant/scope/auth is not server-side
- risky change has no negative tests
- PR mixes mechanical refactor with behavior change without clear reason
- follow-up work downgrades Hard Mode MOM v3 from the parent slice without a
  purely text/comment-only reason
- service-level tests are reported as API/RBAC/E2E or full pilot coverage
- DB tests persist tenant/test data or rely on unique prefixes instead of cleanup
- fixture teardown lacks rollback before purge after DB exceptions
- validation ran against stale container/source or ambiguous command output
- report/diff/worktree mismatch suggests the implementation agent needs a
  reusable skill or instruction hardening rule
- review output lacks a concrete next plan for cleanup, correction, or the next
  product slice

## Output

```markdown
# PR Gate Review

## Verdict
APPROVE / REQUEST_CHANGES / COMMENT_ONLY

## Routing
- Selected brain:
- Selected mode:
- Hard Mode MOM v3:
- Selected skills read:
- Coverage class:
- Hard Mode kept from parent slice:
- Reason:

## Findings
| Severity | Area | Finding | Evidence | Required action |
|---|---|---|---|---|

## Required changes before merge
1. ...

## Suggested follow-up
1. ...

## Skill Improvement Decision
- Needed: yes/no
- Reason:
- Action: none / patch skill now / create correction prompt / defer with rationale
- Files to patch or re-read next:

## Next Plan
- Decision: accept / cleanup first / correction agent prompt / next product slice
- Next action owner:
- Exact next step:
- Expected files in scope:
- Verification required:

## Report export
- Canonical report file: docs/agent-reports/latest-agent-report.md
- Written before completion: yes/no
```

For non-trivial reviews, overwrite `docs/agent-reports/latest-agent-report.md`
with the final review report before marking done.

Every review must include `Skill Improvement Decision` and `Next Plan`. Do not
end with findings only. If skill changes are needed, name the active skill or
instruction file to patch; if no skill change is needed, explain why the current
instructions already cover the failure.
