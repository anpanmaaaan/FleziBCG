# P0-C-08H16B Claim Model/Test Dependency Burn-Down

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Removed or rewrote remaining claim model/test dependencies before claim table drop migration. |

## 1. Executive Summary
H16B implemented claim dependency burn-down for the required backend test surface.

Completed in this slice:
- Removed claim model imports from required test files.
- Removed direct claim table fixture inserts from required tests.
- Removed claim teardown deletes from required tests.
- Rewrote legacy claim-dependent tests toward StationSession-native behavior.

Explicitly not done in H16B:
- No DB migration added.
- No claim table drop.
- No claim ORM model deletion.
- No StationSession guard behavior change.
- No queue contract shape change.

## 2. Scope and Non-Scope
In scope completed:
- Test dependency burn-down for required files in H16 contract.
- Claim import/fixture/teardown cleanup in targeted tests.
- Focused regression and frontend smoke verification.

Out of scope held:
- Table drops and migration authoring.
- Model class deletion in [backend/app/models/station_claim.py](backend/app/models/station_claim.py).
- Claim model registration deletion in [backend/app/db/init_db.py](backend/app/db/init_db.py).
- Queue compatibility field removal in [backend/app/schemas/station.py](backend/app/schemas/station.py).

## 3. Hard Mode Gate Evidence
## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Backend Implementation
- Hard Mode MOM: v3
- Reason: claim dependency burn-down affects execution-adjacent test truth, ORM boundaries, and migration readiness.

### Design Evidence Extract
| Fact | Source | Evidence |
|---|---|---|
| StationSession is target ownership truth | [docs/design/02_domain/execution/station-session-ownership-contract.md](docs/design/02_domain/execution/station-session-ownership-contract.md) | claim is migration debt |
| Execution mutation guard is StationSession-centric | [docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md](docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md) | missing/invalid session rejects command |
| Claim command semantics are deprecated target-side | [docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md](docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md) | claim_operation is transition debt |
| H16 requires burn-down before model/table drop | [docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md](docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md) | H16B before H17 |
| H16B must not add migration or drop tables | [docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md](docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md) | boundary enforced |

### Claim Dependency Burn-Down Map
| Reference | File | Current Purpose | H16B Action | H17 Deferred? | Risk |
|---|---|---|---|---|---|
| claim imports + active claim fixture helper + teardown claim deletes | [backend/tests/test_execution_route_claim_guard_removal.py](backend/tests/test_execution_route_claim_guard_removal.py) | legacy claim-guard compatibility | removed claim import/helper/teardown, kept StationSession guard assertions | No | High |
| claim imports/inserts/selects/teardown | [backend/tests/test_reopen_resumability_claim_continuity.py](backend/tests/test_reopen_resumability_claim_continuity.py) | legacy reopen claim continuity assertions | rewritten to StationSession-native reopen/resume continuity without claim rows | No | High |
| claim imports + teardown claim deletes | [backend/tests/test_reopen_operation_claim_continuity_hardening.py](backend/tests/test_reopen_operation_claim_continuity_hardening.py) | cleanup only | removed claim dependency | No | Medium |
| claim imports + teardown claim deletes | [backend/tests/test_station_queue_active_states.py](backend/tests/test_station_queue_active_states.py) | cleanup only | removed claim dependency | No | Medium |
| claim import + claim fixture insert + claim teardown | [backend/tests/test_start_downtime_auth.py](backend/tests/test_start_downtime_auth.py) | legacy negative fixture | removed claim dependency; preserved auth/session path | No | High |
| claim imports + teardown claim deletes | [backend/tests/test_status_projection_reconcile_command.py](backend/tests/test_status_projection_reconcile_command.py) | cleanup only | removed claim dependency | No | Medium |
| claim imports + teardown claim deletes | [backend/tests/test_work_order_operation_foundation.py](backend/tests/test_work_order_operation_foundation.py) | cleanup only | removed claim dependency | No | Medium |

### ORM / Metadata Impact Map
| Artifact | Current Dependency | H16B Action | H17 Action |
|---|---|---|---|
| [backend/app/models/station_claim.py](backend/app/models/station_claim.py) | claim models still defined | keep unchanged | remove in migration-governed slice |
| OperationClaim | still used by init and legacy scripts | removed from targeted tests | remove model usage in H17 retirement path |
| OperationClaimAuditLog | still used by init and legacy scripts | removed from targeted tests | remove model usage in H17 retirement path |
| [backend/app/db/init_db.py](backend/app/db/init_db.py) | model registry imports | keep unchanged in H16B | evaluate removal with model deletion in H17 |
| [backend/app/models/__init__.py](backend/app/models/__init__.py) | empty | no change | no change |
| [backend/app/db/base.py](backend/app/db/base.py) | Base only | no change | no change |
| migration metadata/scripts | legacy SQL + Alembic chain | no change | H17 forward revision for drop sequence |

### Test Rewrite Map
| Test File | Current Claim Dependency | H16B Action | Expected Assertion After H16B |
|---|---|---|---|
| [backend/tests/test_execution_route_claim_guard_removal.py](backend/tests/test_execution_route_claim_guard_removal.py) | claim imports/fixtures/teardown | removed claim dependencies | session-required rejection and valid-session success stay intact |
| [backend/tests/test_reopen_resumability_claim_continuity.py](backend/tests/test_reopen_resumability_claim_continuity.py) | claim inserts/selects/teardown | rewritten to claim-independent flow | reopen remains OPEN+PAUSED and resume works via StationSession |
| [backend/tests/test_reopen_operation_claim_continuity_hardening.py](backend/tests/test_reopen_operation_claim_continuity_hardening.py) | claim teardown imports | removed | hardening behavior unchanged |
| [backend/tests/test_station_queue_active_states.py](backend/tests/test_station_queue_active_states.py) | claim teardown imports | removed | queue active-state projection assertions unchanged |
| [backend/tests/test_start_downtime_auth.py](backend/tests/test_start_downtime_auth.py) | claim fixture insert/delete | removed | auth matrix still passes with StationSession fixture |
| [backend/tests/test_status_projection_reconcile_command.py](backend/tests/test_status_projection_reconcile_command.py) | claim teardown imports | removed | reconcile behavior unchanged |
| [backend/tests/test_work_order_operation_foundation.py](backend/tests/test_work_order_operation_foundation.py) | claim teardown imports | removed | tenant/hierarchy invariants unchanged |

### Migration Boundary Map
| Object | H16B Action | H17 Action |
|---|---|---|
| OperationClaim model | retained | retire with governed migration sequence |
| OperationClaimAuditLog model | retained | retire with governed migration sequence |
| operation_claims table | untouched | drop in H17 |
| operation_claim_audit_logs table | untouched | drop first in H17 |
| migration 0009 legacy SQL | untouched | keep immutable historical artifact |
| future Alembic drop revision | not added | create in H17 |

### Test Matrix
| Test / Check | Purpose | Required? |
|---|---|---|
| Execution/queue/reopen focused subset | protect StationSession/execution invariants | Yes |
| H16 dependency-file subset | validate burn-down targets | Yes |
| claim dependency sweep | verify removal status in targeted tests | Yes |
| frontend lint/build/routes | detect collateral frontend drift | Yes |
| full backend suite | broad confidence gate | Optional |

### Verdict before coding
ALLOW_IMPLEMENTATION

## 4. Claim Dependency Burn-Down Inventory
Post-edit sweep outcome:
- Zero claim model/table references in targeted H16B test files.
- Remaining references are in expected runtime/model/migration surfaces and in legacy scripts.

Residual references retained for later slices:
- [backend/app/models/station_claim.py](backend/app/models/station_claim.py)
- [backend/app/db/init_db.py](backend/app/db/init_db.py)
- [backend/scripts/migrations/0009_station_claims.sql](backend/scripts/migrations/0009_station_claims.sql)
- legacy script references in [backend/scripts/verify_station_claim.py](backend/scripts/verify_station_claim.py), [backend/scripts/verify_station_queue_claim.py](backend/scripts/verify_station_queue_claim.py), [backend/scripts/verify_clock_on.py](backend/scripts/verify_clock_on.py), [backend/scripts/verify_clock_off.py](backend/scripts/verify_clock_off.py), [backend/scripts/seed/common.py](backend/scripts/seed/common.py), [backend/scripts/seed/seed_station_execution_opr.py](backend/scripts/seed/seed_station_execution_opr.py)

## 5. Files Changed
- [backend/tests/test_execution_route_claim_guard_removal.py](backend/tests/test_execution_route_claim_guard_removal.py)
- [backend/tests/test_reopen_resumability_claim_continuity.py](backend/tests/test_reopen_resumability_claim_continuity.py)
- [backend/tests/test_reopen_operation_claim_continuity_hardening.py](backend/tests/test_reopen_operation_claim_continuity_hardening.py)
- [backend/tests/test_station_queue_active_states.py](backend/tests/test_station_queue_active_states.py)
- [backend/tests/test_start_downtime_auth.py](backend/tests/test_start_downtime_auth.py)
- [backend/tests/test_status_projection_reconcile_command.py](backend/tests/test_status_projection_reconcile_command.py)
- [backend/tests/test_work_order_operation_foundation.py](backend/tests/test_work_order_operation_foundation.py)

## 6. Test Dependency Rewrites
Summary of implemented rewrite pattern:
- Removed claim ORM imports.
- Removed claim table insert fixtures.
- Removed claim table teardown deletes.
- Preserved and strengthened StationSession-native assertions where relevant.

## 7. ORM / Metadata Boundary
Boundary decision in H16B:
- [backend/app/models/station_claim.py](backend/app/models/station_claim.py): keep.
- [backend/app/db/init_db.py](backend/app/db/init_db.py): keep claim model imports for metadata registration.
- No claim model deletion in this slice.

## 8. Migration Boundary
- No migration file added in H16B.
- No table drop executed.
- [backend/scripts/migrations/0009_station_claims.sql](backend/scripts/migrations/0009_station_claims.sql) unchanged.
- H17 remains owner of drop migration.

## 9. Queue Contract Boundary
No queue contract change in H16B.
- [backend/app/schemas/station.py](backend/app/schemas/station.py): `claim` compatibility field retained.
- [backend/app/services/station_claim_service.py](backend/app/services/station_claim_service.py): `claim` remains null-only projection.

## 10. Test / Verification Results
Required backend subset 1:
- 42 passed
- H16B_EXEC_QUEUE_REOPEN_EXIT:0

Required backend subset 2:
- 51 passed
- H16B_DEPENDENCY_BURN_DOWN_EXIT:0

Claim dependency sweep:
- H16B_CLAIM_DEPENDENCY_SWEEP_EXIT:0
- targeted tests: zero claim model/table refs
- residual refs remain in models/init/migration and legacy scripts

Frontend smoke:
- H16B_FRONTEND_LINT_EXIT:0
- H16B_FRONTEND_BUILD_EXIT:0
- H16B_FRONTEND_ROUTE_SMOKE_EXIT:0
- route smoke: PASS 24, FAIL 0, covered 77/78, excluded 1 redirect

Full backend suite:
- Not run in this H16B slice.

## 11. Remaining Claim References for H17
Remaining references requiring later handling:
- model + metadata surfaces: [backend/app/models/station_claim.py](backend/app/models/station_claim.py), [backend/app/db/init_db.py](backend/app/db/init_db.py)
- migration history: [backend/scripts/migrations/0009_station_claims.sql](backend/scripts/migrations/0009_station_claims.sql)
- legacy scripts listed in Section 4

H17 minimum migration-critical scope remains valid:
- child-first drop order: operation_claim_audit_logs then operation_claims.
- downgrade recreation policy required.

## 12. Recommendation
Proceed to a narrow pre-H17 cleanup (or fold into H17 prep) for legacy script claim references if those scripts remain part of required tooling.

Then execute H17 migration implementation with the existing boundary:
- keep queue contract unchanged,
- keep StationSession command behavior unchanged,
- perform only migration-governed claim table/model retirement sequence.

## 13. Final Verdict
P0_C_08H16B_COMPLETE_WITH_MODEL_REFERENCES_DEFERRED
