# Station Execution Policy and Master Data

## History

| Date | Version | Change |
|---|---|---|
| 2026-04-23 | v4.0 | Replaced claim-centric policy assumptions with session/operator/equipment policy families. |

Status: Canonical configuration/policy note for the approved next-step Station Execution design.

## 1. Execution policy truths

### PMD-EXEC-001 — One running execution per governing station/resource context
Safe default remains true.

### PMD-EXEC-002 — Active station session required for execution writes
`require_station_session_for_execution = true`

### PMD-EXEC-003 — Operator identification required in normal flow
`require_operator_identification = true`

### PMD-EXEC-004 — Equipment binding policy is configurable
- fixed-resource stations may resolve equipment by configuration
- multi-resource stations may require explicit binding

### PMD-EXEC-005 — Start does not require claim in target model
`allow_start_without_claim = true` in target semantics because claim is deprecated.
Ownership is resolved through the active station session.

### PMD-EXEC-006 — Report while paused
Default remains false in current discrete-first design.

### PMD-EXEC-007 — Complete with open downtime
Default remains false.

## 2. Closure policy truths

### PMD-CLOSE-001 — Manual close exists
Supported as post-execution closure foundation.

### PMD-CLOSE-002 — Close authorization phase rule
Current phase rule may remain SUP-owned.

### PMD-CLOSE-003 — Reopen foundation exists
Requires reason and controlled non-running reopen behavior.

## 3. Transition note

Any remaining claim-related implementation policy is compatibility debt during migration, not target-state policy.
