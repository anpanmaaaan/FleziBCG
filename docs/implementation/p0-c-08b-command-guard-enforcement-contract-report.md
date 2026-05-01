# P0-C-08B Command Guard Enforcement Contract Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-04-30 | v1.0 | Created StationSession command guard enforcement contract before P0-C-08C implementation. |
| 2026-05-01 | v1.1 | Finalized contract decisions, enforcement subset recommendation, and verification evidence for P0-C-08C handoff. |

## 1. Executive Summary

P0-C-08B completed as DOC/CONTRACT ONLY.

Outcome:
- Contract created for StationSession command guard enforcement migration.
- No runtime behavior, schema, API payload, or frontend changes made.
- Contract recommends subset implementation for P0-C-08C (7 command endpoints), with close/reopen deferred.

## 2. Files Created

- docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md
- docs/implementation/p0-c-08b-command-guard-enforcement-contract-report.md

No runtime source files changed.

## 3. Contract Decisions

Primary decisions:
- StationSession is target ownership truth for execution command authorization.
- Claim remains compatibility layer during migration.
- Transitional order for 7 claim-guarded routes: StationSession guard first, claim guard second.
- No claim removal in P0-C-08C.
- No queue rewrite in P0-C-08C.
- No reopen continuity rewrite in P0-C-08C.

## 4. Command Guard Applicability Summary

Recommended P0-C-08C enforcement scope:
- Enforce now: start, pause, resume, report_quantity, start_downtime, end_downtime, complete.
- Defer: close_operation, reopen_operation.

Reason for defer:
- reopen continuity currently depends on claim restoration semantics (`_restore_claim_continuity_for_reopen`).
- close/reopen policy is supervisor-driven and not yet fully contracted to session ownership.

## 5. Error Contract Summary

StationSession guard error set defined as candidate contract codes:
- STATION_SESSION_REQUIRED
- STATION_SESSION_CLOSED
- STATION_SESSION_STATION_MISMATCH
- STATION_SESSION_OPERATOR_MISMATCH
- STATION_SESSION_TENANT_MISMATCH
- STATION_SESSION_NOT_AUTHORIZED (optional policy alias)

Status:
- CANDIDATE_FOR_P0_C_08_STATION_SESSION_GUARD
- NEEDS_ERROR_REGISTRY_FINALIZATION

## 6. Claim Compatibility Decision

Claim compatibility remains in force during P0-C-08C:
- Keep claim_operation and release_operation_claim.
- Keep ensure_operation_claim_owned_by_identity temporarily.
- Keep get_station_queue and get_operation_claim_status.
- Keep _restore_claim_continuity_for_reopen until P0-C-08E.

Constraint:
- Claim cannot override failed StationSession guard.

## 7. Reopen / Queue Boundary Decision

Reopen boundary:
- Reopen excluded from first enforcement subset.
- No continuity rewrite in P0-C-08C.
- Continuity replacement explicitly deferred to P0-C-08E.

Queue boundary:
- Queue migration excluded from P0-C-08C.
- Session-aware queue migration deferred to P0-C-08D.

## 8. P0-C-08C Readiness

Readiness result:
- READY for subset implementation only.
- Preconditions captured in contract: explicit validation order, error contract, compatibility ordering, and stop conditions.

## 9. Tests Required Next

Before and during P0-C-08C:
- StationSession required/mismatch tests for each enforced command.
- Event no-write-on-failed-guard assertions.
- Existing command state guard parity assertions.
- Claim regression suites remain green.
- StationSession lifecycle/diagnostic suites remain green.
- Full backend suite sequential pass with exit code capture.

Verification run during this P0-C-08B contract task:
- StationSession suite: 25 passed
- Claim regression subset: 36 passed
- Command hardening subset: 71 passed
- Full backend suite: 255 passed, 1 skipped, exit code 0

## 10. Final Verdict

READY_FOR_P0_C_08C_SUBSET_IMPLEMENTATION
