# FleziBCG PR Hard Mode Checklist

## PR classification

- [ ] Mechanical PR
- [ ] Intentional Behavior PR
- [ ] Architecture / Contract PR
- [ ] MOM Critical PR
- [ ] DB / Migration PR
- [ ] Docs-only PR

## Scope

- [ ] In scope is clear.
- [ ] Out of scope is clear.
- [ ] Deferred work is clear.
- [ ] PR does not introduce future modules.
- [ ] PR does not mix mechanical refactor with behavior change.

## Hard Mode MOM v3 trigger

Turn ON if PR touches:

- [ ] execution state machine
- [ ] execution command
- [ ] operational event
- [ ] projection/read model truth
- [ ] station/session/operator/equipment context
- [ ] production reporting
- [ ] downtime
- [ ] completion/closure
- [ ] quality hold affecting execution
- [ ] material/inventory execution impact
- [ ] tenant/scope/auth for operational commands
- [ ] IAM lifecycle / role/scope / audit
- [ ] critical invariant

## v3 gates

- [ ] Design Evidence Extract exists.
- [ ] Event Map exists.
- [ ] Invariant Map exists.
- [ ] State Transition Map exists if stateful.
- [ ] Test Matrix exists.
- [ ] Tests include negative cases.
- [ ] Verification commands are included.

Reject if any critical item fails.
