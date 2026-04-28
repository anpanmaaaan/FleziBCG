# PR Summary

## Type

- [ ] Mechanical PR
- [ ] Intentional Behavior PR
- [ ] Architecture / Contract PR
- [ ] MOM Critical PR
- [ ] DB / Migration PR
- [ ] Docs-only PR

## Scope

### In scope

-

### Out of scope

-

### Deferred

-

## Routing

- Selected brain:
- Selected mode:
- Hard Mode MOM: ON / OFF
- Reason:

## Hard Mode MOM checklist

Required if PR touches execution/state/event/invariant/tenant/auth.

- [ ] State machine is valid.
- [ ] Required events are emitted.
- [ ] Required invariants are enforced.
- [ ] Projection/read model is not source of truth.
- [ ] Frontend does not decide execution or permission truth.
- [ ] Tenant/scope/auth checks are server-side.
- [ ] Service/application layer owns business logic.

## Tests

- [ ] Backend tests
- [ ] Frontend tests
- [ ] E2E tests
- [ ] Migration test/check
- [ ] Manual verification

Commands run:

```bash

```

## Risk / Rollback

-

## Docs / ADR impact

- [ ] No docs change needed
- [ ] Docs updated
- [ ] ADR needed
- [ ] ADR updated
