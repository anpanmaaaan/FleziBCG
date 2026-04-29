# Hard Mode MOM v3 — Review Checklist

## Design evidence gate

- [ ] Relevant design docs were read.
- [ ] Commands/actions were extracted from docs.
- [ ] Events were extracted or marked NEEDS_CONFIRMATION.
- [ ] States were extracted if stateful.
- [ ] Invariants were extracted.
- [ ] Exclusions were checked.
- [ ] No invented behavior was introduced.

## Generated map gate

- [ ] Event map exists.
- [ ] Invariant map exists.
- [ ] State transition map exists if stateful.
- [ ] Test matrix exists.
- [ ] Every command has required event decision.
- [ ] Every critical invariant has enforcement layer.
- [ ] Every critical invariant has test.

## Test-first gate

- [ ] Tests were written before or with implementation.
- [ ] Happy path exists.
- [ ] Negative path exists.
- [ ] Tenant/scope test exists where relevant.
- [ ] Permission test exists where relevant.
- [ ] Duplicate/idempotency test exists where relevant.
- [ ] Event payload assertion exists.
- [ ] Invariant assertion exists.
- [ ] Projection consistency test exists where relevant.

## Implementation gate

- [ ] Route/controller remains thin.
- [ ] Service owns business logic.
- [ ] Repository is data access only.
- [ ] Event append happens in service/domain layer.
- [ ] Projection is not source of truth.
- [ ] Frontend is not source of truth.
- [ ] No excluded future scope was implemented.

Reject if any critical gate fails.
