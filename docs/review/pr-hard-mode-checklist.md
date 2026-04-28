# FleziBCG PR Hard Mode Checklist

Use this checklist before merging a PR.

## 1. PR classification

Choose one:

- [ ] Mechanical PR
- [ ] Intentional Behavior PR
- [ ] Architecture / Contract PR
- [ ] MOM Critical PR
- [ ] DB / Migration PR
- [ ] Docs-only PR

## 2. Scope

- [ ] In scope is clear.
- [ ] Out of scope is clear.
- [ ] Deferred work is clear.
- [ ] PR does not silently introduce future modules.
- [ ] PR does not mix mechanical refactor with behavior change.

## 3. Hard Mode MOM trigger

Turn Hard Mode MOM ON if PR touches:

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
- [ ] critical invariant

## 4. State machine check

- [ ] Commands validate current state.
- [ ] Invalid transitions are rejected.
- [ ] No direct authoritative status mutation.
- [ ] Frontend does not decide transition truth.
- [ ] Backend returns authoritative result/allowed actions.
- [ ] Projection is read model only.

Reject if any critical item fails.

## 5. Event check

- [ ] Operational change emits append-only event.
- [ ] Event includes event_id.
- [ ] Event includes event_type.
- [ ] Event includes tenant_id or scoped context.
- [ ] Event includes entity_type/entity_id.
- [ ] Event includes actor context.
- [ ] Event includes occurred_at.
- [ ] Event includes business payload.
- [ ] Projection can be rebuilt or reconciled from events.
- [ ] Duplicate command behavior is defined.

Reject if required event is missing.

## 6. Invariant check

- [ ] Tenant/scope context is explicit.
- [ ] Permission is checked server-side.
- [ ] Critical FK/unique/check constraints exist where appropriate.
- [ ] Service-level validation exists.
- [ ] UI validation is not the only protection.
- [ ] Operator/session/station/equipment context is valid when required.
- [ ] Quantity/state/business rules are enforced.
- [ ] Support/admin path is auditable if used.

Reject if critical invariant is missing.

## 7. Tests

- [ ] Happy path test exists.
- [ ] Invalid state test exists.
- [ ] Invalid permission test exists.
- [ ] Wrong tenant/scope test exists where relevant.
- [ ] Duplicate request test exists where relevant.
- [ ] Missing/invalid context test exists.
- [ ] Event assertion exists.
- [ ] Projection assertion exists.
- [ ] DB invariant assertion exists where relevant.

## 8. Release readiness

- [ ] Migration is safe if present.
- [ ] Rollback/recovery path considered.
- [ ] Logs/errors are useful.
- [ ] Documentation/ADR impact checked.
- [ ] Known risks are stated.
- [ ] Verification commands are included in PR description.
