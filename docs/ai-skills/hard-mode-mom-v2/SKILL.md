---
name: hard-mode-mom-v2
description: Strict Event-driven + Invariant-enforced + Test-first rejection layer for manual/smaller FleziBCG MOM reviews.
---

# FleziBCG Hard Mode MOM v2

## Purpose

Use v2 for focused review or smaller manual enforcement.

For autonomous implementation, use v3.

## Required command/action pattern

```text
command intent
→ load authoritative context
→ validate tenant/scope/auth
→ validate current state, if stateful
→ validate business invariants
→ write append-only domain/security event
→ update projection/read model if applicable
→ return backend-derived result / allowed actions
```

## Reject if

- state machine is wrong
- required event is missing
- required invariant is missing
- execution state is mutated directly
- projection/read model is treated as source of truth
- frontend becomes execution or permission truth
- tenant/scope/auth is not enforced server-side
- service/application layer is bypassed
- only happy path is tested

## Required review output

```markdown
## Verdict
ACCEPT / ACCEPT_WITH_FIXES / REJECT

## Event map
...

## Invariant map
...

## Test-first evidence
...

## Required fixes
...
```
