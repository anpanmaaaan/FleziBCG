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
- Hard Mode MOM v3: ON / OFF
- Reason:

## Hard Mode MOM v3

Required if PR touches execution/state/event/invariant/tenant/auth/IAM/access/audit.

- [ ] Design Evidence Extract included
- [ ] Event Map included
- [ ] Invariant Map included
- [ ] State Transition Map included if stateful
- [ ] Test Matrix included
- [ ] Tests written and run
- [ ] Negative tests included
- [ ] Verification report updated

## Tests

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

## Quality Docs Sync (required when Quality behavior changes)

Applies to: QC applicability, measurement submission, pass/fail/hold evaluation,
disposition, quality-to-execution gate behavior, accepted-good derivation.

- [ ] Not a Quality behavior change
- [ ] Design truth reviewed (quality-domain-contracts + quality-lite business truth)
- [ ] API/schema/error contract docs updated in same PR
- [ ] Behavior docs updated for evaluation + hold/disposition ownership
- [ ] Execution interaction docs updated when gating/allowed-actions changed
- [ ] Quantity semantics docs updated (reported good vs accepted good vs hold/scrap)
- [ ] Test evidence section updated for quality behavior and authz/tenant isolation
- [ ] Reviewer verified docs-to-code alignment

Reference checklist:
- docs/implementation/quality-pr-documentation-sync-checklist.md
