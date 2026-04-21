# Station Execution Status Incident Audit (PR-Ready)

**Date:** 2026-04-21  
**Scope:** Read-only audit with completed data remediation  
**Branch Context:** station_execution_hardening  
**PR Type (recommended):** Intentional Behavior PR

---

## 1. Incident Summary

Station queue showed many operations as PAUSED unexpectedly.

Investigation confirmed a snapshot/event mismatch:
- `operations.status` snapshot had 6 PAUSED operations.
- Event-derived status indicated only 1 PAUSED operation.
- 5 operations were logically IN_PROGRESS but stored as PAUSED.

Affected operation IDs at detection time:
- 905, 929, 930, 931, 932

---

## 2. What Was Remediated (Data Only)

A targeted SQL correction was applied to rows where:
- snapshot status = PAUSED
- event-derived status = IN_PROGRESS

Post-remediation verification:
- mismatch count (`snapshot != derived`) = 0
- current status distribution:
  - COMPLETED: 15
  - IN_PROGRESS: 5
  - PAUSED: 1

Note: this remediation fixed data consistency only. No application code was changed.

---

## 3. Evidence and Code Path Audit

### 3.1 Queue endpoint uses snapshot status
- Station queue route: [backend/app/api/v1/station.py](backend/app/api/v1/station.py#L35)
- Queue service filters by `Operation.status`: [backend/app/services/station_claim_service.py](backend/app/services/station_claim_service.py#L285)
- Queue payload returns `status: operation.status`: [backend/app/services/station_claim_service.py](backend/app/services/station_claim_service.py#L374)

### 3.2 Detail endpoint uses event-derived status
- Station detail route: [backend/app/api/v1/station.py](backend/app/api/v1/station.py#L131)
- Derivation logic (`_derive_status`): [backend/app/services/operation_service.py](backend/app/services/operation_service.py#L231)
- Detail response uses derived `status`: [backend/app/services/operation_service.py](backend/app/services/operation_service.py#L409)

### 3.3 Repair-event footprint found in DB
System-generated events were present with actor IDs:
- `system_data_repair_paused_orphan` (execution_resumed events)
- `system_cleanup_orphan_downtime` (downtime_ended events)

These repair events were appended, but snapshot rows were not fully synchronized for all impacted operations.

---

## 4. Root Cause Assessment

## Direct cause (incident trigger)

Data repair flow appended runtime events (notably `execution_resumed`) without guaranteeing snapshot reconciliation in the same integrity path, leaving stale `operations.status` values.

## Systemic cause (product bug)

Read-path inconsistency exists by design:
- queue reads snapshot status
- detail reads event-derived status

When snapshot drifts from event truth, screens diverge and operators see incorrect runtime state in the queue.

Conclusion: this incident was both:
- a data consistency failure (trigger), and
- a real system bug in status-source consistency (structural).

---

## 5. Impact

- Operator-facing queue status became misleading (false PAUSED).
- Potential downstream confusion in claim/release/resume workflow decisions.
- Elevated operational risk: wrong prioritization and unnecessary manual intervention.

No evidence was found of terminal-state corruption (COMPLETED/ABORTED) in this incident window.

---

## 6. PR-Ready Fix Plan (No Code Applied Yet)

## Goal

Guarantee consistent status truth across Station Execution reads.

## Recommended approach

1. Unify status source for station execution read APIs.
2. Keep event log as authoritative truth; snapshot remains projection only.
3. Ensure any repair/maintenance workflow that appends execution events also reconciles snapshot projection before completion.

## Implementation options

### Option A (preferred)
- Queue API computes/returns event-derived status (or uses a single reconciled read model fed from events).
- Benefits: removes snapshot drift exposure at read time.

### Option B
- Keep queue on snapshot, but enforce strict projection update guarantees:
  - service-level transactional sync after event append
  - reconcile job as safety net
- Benefits: lower immediate query complexity; still requires stronger invariants.

---

## 7. Rollout and Verification Plan

1. Add regression tests for snapshot-vs-derived divergence scenarios.
2. Add integration tests proving queue and detail return equivalent status semantics.
3. Run standard backend and frontend gates from governance.
4. Deploy with a one-time reconcile script in release checklist.

Success criteria:
- `snapshot != derived` mismatch metric remains 0 in production-like data.
- queue/detail status parity is maintained for all active operation states.

---

## 8. Monitoring and Guardrails

1. Add periodic mismatch audit query and alert on `count > 0`.
2. Log and monitor system-generated maintenance actors that append execution events.
3. Add runbook step: post-maintenance projection reconciliation must pass before close.

---

## 9. Out of Scope for This Audit

- No immediate redesign of execution state machine.
- No frontend UX/layout changes.
- No direct code change included in this document.
