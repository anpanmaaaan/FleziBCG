# P0-C-08E-V2 DB Fixture Deadlock / Teardown Stabilization Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: SINGLE-SLICE
- Hard Mode MOM: v3
- Reason: stabilize full-suite DB fixture/migration deadlocks without modifying 08E business behavior.

## Scope Guard Confirmation
- No business logic change.
- No execution command behavior change.
- No reopen/resume behavior change.
- No StationSession guard semantic change.
- No claim removal.
- No claim API deprecation.
- No close_operation enforcement addition.
- No additional queue migration.
- No frontend/UI change.

## Part 0 Safety Checks
- `git status --short`: workspace dirty from pre-existing changes (observed, not reverted).
- `Get-Process python,pytest`: stale venv pytest process identified during V2 and removed.
- `docker ps`: db/backend/frontend containers healthy.

## Part 1 Reproduction Baseline
Deadlock evidence was captured from the in-flight full-suite stream before stabilization:

| Failure # | Test / Module | Phase | Error Type | SQL/Table Evidence | Blocking/Cascade |
|---|---|---|---|---|---|
| 1 | `tests/test_report_quantity_command_hardening.py` | setup | `DeadlockDetected` | `ALTER TABLE operations ADD COLUMN IF NOT EXISTS station_scope_value ...` | blocks setup, then transaction-aborted cascades |
| 2 | `tests/test_start_downtime_auth.py` | teardown | `DeadlockDetected` | `DELETE FROM scopes WHERE scopes.id = ...` | teardown blocked by DDL lock chain |
| 3 | `tests/test_start_pause_resume_command_hardening.py` | setup | `DeadlockDetected` | same migration DDL on `operations` | setup blocked by concurrent relation lock |

## Part 2 Ordered Subset Reproduction

| Run | Command Group | Result | Interpretation |
|---|---|---|---|
| S1 | `report_quantity + start_downtime_auth + start_pause_resume` | `29 passed`, `V2_SUBSET_EXIT:0` | failure is interaction-sensitive, not deterministic per subset |
| S2 | first failing test alone (`test_report_quantity_rejects_negative_scrap_qty`) | `1 passed`, `V2_FIRST_TEST_EXIT:0` | not a standalone functional regression |

## Fixture / Cleanup Archaeology
- Repeated pattern across multiple tests: function-scoped fixtures call `init_db()` followed by DML purge/teardown.
- `init_db()` always called `_apply_sql_migrations()` and executed all SQL migration statements each invocation.
- Under overlapping/stale runners, repeated migration DDL (AccessExclusive locks) collided with teardown DML (`DELETE ... scopes`, related RBAC/session cleanup), causing lock-order deadlocks.

## Minimal Infra Stabilization Patch
- File changed: `backend/app/db/init_db.py`
- Changes:
  - added process-local migration de-duplication (`_MIGRATIONS_APPLIED`);
  - added in-process lock (`threading.Lock`) around migration apply path;
  - added PostgreSQL advisory lock around migration execution to serialize cross-process migration runners.
- Rationale:
  - removes repeated per-fixture DDL churn;
  - reduces cross-process lock contention without changing domain logic.

## Verification After Patch
### Required 08E Matrix
- M1: `5 passed` (`M1_EXIT:0`)
- M2: `21 passed` (`M2_EXIT:0`)
- M3: `22 passed` (`M3_RETRY_EXIT:0`)
- M4: `10 passed` (`M4_RETRY_EXIT:0`)
- M5: `58 passed` (`M5_EXIT:0`)
- M6: `45 passed` (`M6_FINAL_EXIT:0`)

### Full Backend Suite
- Final run: `284 passed, 1 skipped in 50.48s`
- Exit marker: `V2_FINAL_FULL_EXIT:0`

## Root-Cause Verdict
- Classification: `DB_FIXTURE_MIGRATION_LOCK_CONTENTION`
- 08E contract/API regression evidence: none.
- Stabilization status: recovered to clean verification.

## Final Verdict
- `ALLOW_IMPLEMENTATION_COMPLETE`
- P0-C-08E status after V2: `IMPLEMENTATION_COMPLETE_VERIFICATION_CLEAN`
- 08F/P0-D remain blocked by explicit user scope constraint, not by 08E verification instability.
