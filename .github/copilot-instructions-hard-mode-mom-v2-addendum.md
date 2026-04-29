# Copilot Addendum — Hard Mode MOM v2

Use for FleziBCG execution-critical and governance-critical work.

Read:

`docs/ai-skills/hard-mode-mom-v2/SKILL.md`

## Auto-trigger

Hard Mode MOM v2 turns ON when work touches:

- execution state machine
- execution commands/events
- projections/read models
- station/session/operator/equipment
- production reporting
- downtime
- completion/closure
- quality hold
- material/inventory execution impact
- tenant/scope/auth
- IAM lifecycle
- role/action/scope assignment
- audit/security event
- critical invariant

## Required gates

Before coding:
- event map
- invariant map
- test-first plan

Reject if:
- missing event
- missing invariant
- happy-path-only tests
- direct state mutation
- projection as source of truth
- UI as permission/execution truth
- tenant/auth not server-side
