# P0-C-08E-V1 Full Suite Recovery / Failure Isolation Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: FAILURE ISOLATION + VERIFICATION RECOVERY
- Hard Mode MOM: v3
- Reason: User-requested 08E-V1 recovery to classify full-suite instability without expanding scope or changing governed behavior.

## Scope Guard Confirmation
- No claim removal.
- No close_operation StationSession enforcement.
- No additional queue migration.
- No API behavior change.
- No frontend change.
- No commit/push.

## Recovery Sequence
1. Reproduced full-suite failure:
- Command: `g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q --tb=short`
- Result: `283 passed, 1 skipped, 1 error`
- First failure: `tests/test_close_operation_command_hardening.py::test_close_operation_rejects_already_closed`
- Error family: PostgreSQL deadlock in fixture purge (`psycopg.errors.DeadlockDetected`) followed by transaction-aborted chain.

2. Isolated first failing test:
- Command: `g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -vv --tb=long tests/test_close_operation_command_hardening.py::test_close_operation_rejects_already_closed`
- Result: `1 passed`

3. Required sequential matrix rerun:
- Matrix 1: `5 passed` (`EXIT_CODE:0`)
- Matrix 2: `21 passed` (`EXIT_CODE:0`)
- Matrix 3: `22 passed` (`EXIT_CODE:0`)
- Matrix 4: `10 passed` (`EXIT_CODE:0`)
- Matrix 5: `58 passed` (`EXIT_CODE:0`)
- Matrix 6: `45 passed` (`EXIT_CODE:0`)

4. Recovery full-suite rerun (intermediate):
- Command: `g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q --tb=short`
- Result snapshot before interrupt: `194 passed, 1 skipped, 8 errors in 55.99s` then `KeyboardInterrupt`
- Error concentration expanded to multiple files, including:
  - `tests/test_report_quantity_command_hardening.py`
  - `tests/test_start_downtime_auth.py`
  - `tests/test_start_pause_resume_command_hardening.py`
- Dominant error family remained deadlock/aborted transaction contamination.

5. Recovery full-suite rerun (completed terminal capture):
- Command: `g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q --tb=short`
- Result: `283 passed, 1 skipped, 3 errors in 78.99s`
- Exit marker: `RECOVERY_FULL_EXIT:1`
- Error locations in this completed run:
  - `tests/test_claim_single_active_per_operator.py::test_claim_first_operation_succeeds` (teardown deadlock)
  - `tests/test_close_operation_command_hardening.py::test_close_operation_rejects_invalid_runtime_state` (setup deadlock + aborted transaction)
  - `tests/test_close_reopen_operation_foundation.py::test_reopen_operation_rejects_not_closed_and_missing_reason` (teardown deadlock)

## Failure Classification
| Failure | Location | Reproducible Alone? | Likely Cause | Severity | Fix Recommendation |
|---|---|---|---|---|---|
| Deadlock in fixture purge (`user_role_assignments`) | `tests/test_close_operation_command_hardening.py` fixture setup/teardown | No (isolated target passes) | DB teardown concurrency/lock-order instability | High | Stabilize test DB isolation/lock ordering; no 08E logic change |
| Deadlock during `init_db` migration statements | `tests/test_report_quantity_command_hardening.py` setup | Not established in this run | Cross-test migration/DDL + concurrent fixture activity | High | Ensure serialized migration/init path in tests |
| Deadlock in scope cleanup teardown | `tests/test_start_downtime_auth.py` teardown | Not established in this run | Teardown contention across shared relations | Medium/High | Make teardown idempotent and lock-order deterministic |
| Deadlock while applying Station Execution v2 DDL during setup | `tests/test_start_pause_resume_command_hardening.py` setup | Not established in this run | Concurrent DDL/DML lock conflict in shared DB test environment | High | Separate schema bootstrap from per-test fixture or isolate DB per worker/session |

## Root Cause Verdict
- Classification: `DB_TEARDOWN_STABILITY / TEST_ENV_LOCK_CONTENTION`
- 08E regression evidence: not found.
- Why: targeted 08E matrix (1-6) stayed green; failures are non-deterministic in full-suite context and span unrelated test modules with deadlock signatures.

## Decision
- P0-C-08E-V1 status: `IMPLEMENTATION_COMPLETE_VERIFICATION_NOT_FULLY_CLEAN`
- Minimal fix in this pass: none (no verified 08E functional regression requiring API/behavior change).
- Recommended next action before any 08F work: dedicated DB test isolation hardening slice focused on deadlock elimination.

## 08E-V2 DB Fixture Deadlock / Teardown Stabilization Update

### Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: SINGLE-SLICE IMPLEMENTATION
- Hard Mode MOM: v3
- Reason: full-suite deadlock/teardown stabilization while preserving 08E business semantics and scope boundaries.

### V2 Part 0 Safety Check Snapshot
- `git status --short`: dirty workspace confirmed (pre-existing); no destructive git operation executed.
- `Get-Process python,pytest`: stale venv pytest process observed during reproduction and cleared.
- `docker ps`: backend/db containers healthy.

### V2 Reproduction and Isolation
1. Deadlock evidence capture from failing full-suite stream:
- Deadlock family: `psycopg.errors.DeadlockDetected` and `InFailedSqlTransaction` cascades.
- Setup deadlock during migration apply in `init_db` (ALTER TABLE on `operations`).
- Teardown deadlock during fixture cleanup (`DELETE FROM scopes`).

2. Controlled clean reruns:
- Full suite retry: `284 passed, 1 skipped`, `V2_RETRY_PLAIN_EXIT:0`.
- Ordered failing-subset retry (`report_quantity + start_downtime_auth + start_pause_resume`): `29 passed`, `V2_SUBSET_EXIT:0`.
- First failing test alone: `1 passed`, `V2_FIRST_TEST_EXIT:0`.

### Root Cause Refinement
- Primary contention source: repeated per-fixture migration DDL via `init_db()` colliding with teardown DML under overlapping/stale runners.
- Secondary amplifier: orphaned in-flight pytest process caused cross-process lock-order conflicts.

### Minimal Infra Stabilization Applied
- File: `backend/app/db/init_db.py`
- Change type: test/runtime infra hardening only.
- Behavior:
  - process-local de-duplication so SQL migrations apply once per process lifetime;
  - process lock (`threading.Lock`) around migration application;
  - PostgreSQL advisory lock around migration execution to serialize cross-process migration DDL.
- Scope safety:
  - no command/business logic change;
  - no claim/reopen/resume semantic change;
  - no StationSession guard semantic change;
  - no API contract change.

### Post-Fix Verification
- Matrix 1: `5 passed` (`M1_EXIT:0`)
- Matrix 2: `21 passed` (`M2_EXIT:0`)
- Matrix 3: `22 passed` (`M3_RETRY_EXIT:0`)
- Matrix 4: `10 passed` (`M4_RETRY_EXIT:0`)
- Matrix 5: `58 passed` (`M5_EXIT:0`)
- Matrix 6: `45 passed` (`M6_FINAL_EXIT:0`)
- Final full suite: `284 passed, 1 skipped in 50.48s` (`V2_FINAL_FULL_EXIT:0`)

### V2 Verdict
- Classification after stabilization: `STABILIZED`
- P0-C-08E verification status: `IMPLEMENTATION_COMPLETE_VERIFICATION_CLEAN`
- 08F/P0-D gate: remains blocked by user scope instruction, not by 08E verification failure.
