# P0-C-08H15 Claim Service / Schema / Model Removal Contract

## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Contract-Only Review
- Hard Mode MOM: v3
- Reason: Claim retirement touches execution ownership compatibility debt, audit/event remnants, ORM registration/loading boundaries, test dependency graph, and migration sequencing.

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Defined claim service, schema, and model removal readiness after route/client/queue-loop removal. |

## 1. Executive Summary

H15 contract review confirms H14B removed all claim API route/client/queue-loop runtime surfaces, and claim ownership is no longer part of active execution behavior. Remaining claim code is now compatibility debt concentrated in service dead code, schemas retained for response shape, ORM model registration, tests, and scripts.

Contract conclusion:
- Service function removal readiness: READY (no runtime callers in backend app layer).
- Schema removal readiness: READY for route-only request/response claim schemas; queue claim field should remain nullable until final API contract cleanup.
- Model removal readiness: NOT READY for the same slice as service/schema unless additional test/script cleanup is included. Current model file is still imported by DB init and multiple test/script fixtures.
- Migration boundary: Table drop remains strictly deferred to H16/H17.

Pre-contract gate verdict:

`ALLOW_CONTRACT_REVIEW`

## 2. Scope Reviewed

Required docs reviewed:
- H14B implementation report
- H14 contract
- H13 policy
- H12B implementation report
- H11B implementation report
- H10 implementation report
- H8 implementation report
- Station session ownership/guard/execution contracts
- autonomous implementation plan / verification / HM3 map

Required source reviewed:
- backend claim service/model/schema/router/db init/base/operations/service
- frontend station API surface
- requested test files plus repo-wide dependency sweep for claim references
- migration references under backend scripts/alembic

Missing requested source files:
- `docs/design/00_platform/canonical-api-contract.md` (not present in repo)
- `docs/design/00_platform/system-invariants.md` (not present in repo)

Fallback used:
- `docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md`
- `docs/design/02_domain/execution/station-execution-state-matrix-v4.md`
- `docs/governance/CODING_RULES.md`

## 3. Hard Mode Gate Evidence

### Design Evidence Extract

| Fact | Source | Confirmed |
|---|---|---|
| StationSession is target ownership truth | station-session-ownership-contract.md | Yes |
| Claim API routes removed in H14B | H14B report + station router | Yes |
| Queue no longer emits CLAIM_EXPIRED | H14B report + service code | Yes |
| Queue claim payload remains null-only for compatibility shape | H10/H14B + station schema/service | Yes |
| Reopen claim restoration retired | H11B report | Yes |
| Hard drop policy approved but staged | H13 policy | Yes |
| H15 must avoid table drop/migration | H13/H14/H14B boundaries | Yes |

### Runtime / Dead-Code Surface Map

| Surface | Current State | Runtime Active After H14B? | H15B Candidate? | Risk |
|---|---|---:|---:|---|
| `claim_operation` | Defined only in station_claim_service | No | Yes | Low |
| `release_operation_claim` | Defined only in station_claim_service | No | Yes | Low |
| `get_operation_claim_status` | Defined only in station_claim_service | No | Yes | Low |
| `_expire_claim_if_needed` | Called only by dead claim functions | No | Yes | Low |
| `_log_claim_event` / `_to_claim_state` | Called only by dead claim functions | No | Yes | Low |
| `get_station_queue` | Used by active station queue route | Yes | Keep | High if removed |
| `get_station_scoped_operation` / scope helpers | Used by active station detail route | Yes | Keep | High if removed |

### Schema / ORM Dependency Map

| Artifact | Current Dependency | Runtime Needed? | H15B Action |
|---|---|---:|---|
| `ClaimRequest` | No route consumers | No | Remove |
| `ReleaseClaimRequest` | No route consumers | No | Remove |
| `ClaimResponse` | No route consumers | No | Remove |
| `ClaimSummary` | Referenced by `StationQueueItem.claim` | Compatibility only | Keep until queue claim field cleanup slice |
| `StationQueueItem.claim` | Queue response shape still includes `claim: None` | Compatibility only | Keep nullable |
| `OperationClaim` model | Imported by db init + many tests/scripts | Indirectly yes | Defer model deletion or expand H15B scope |
| `OperationClaimAuditLog` model | Imported by db init + many tests/scripts | Indirectly yes | Defer model deletion or expand H15B scope |

### Test Dependency Map

| Test File | Claim Dependency | H15B Action |
|---|---|---|
| `test_claim_single_active_per_operator.py` | Direct service + model dependency | Delete with service removal |
| `test_release_claim_active_states.py` | Direct service + model dependency | Delete with service removal |
| `test_execution_route_claim_guard_removal.py` | Inserts claim rows as negative fixture + teardown | Rewrite in later slice before model/table drop |
| `test_station_queue_active_states.py` | Claim models in teardown only | Cleanup required before model drop |
| `test_station_queue_session_aware_migration.py` | Uses queue service only | Keep |
| `test_reopen_resumability_claim_continuity.py` | Direct claim service/model assertions | Rewrite or retire before model drop |
| `test_reopen_operation_claim_continuity_hardening.py` | Claim models in teardown only | Cleanup required before model drop |
| `test_start_downtime_auth.py` | Creates `OperationClaim` as legacy negative fixture | Rewrite before model drop |
| `test_status_projection_reconcile_command.py` | Claim models in teardown only | Cleanup before model drop |
| `test_work_order_operation_foundation.py` | Claim models in teardown only | Cleanup before model drop |

### Migration Boundary Map

| Boundary Item | Status | Rule |
|---|---|---|
| `operation_claims` drop | Deferred | H16/H17 only |
| `operation_claim_audit_logs` drop | Deferred | H16/H17 only; child drops first |
| Alembic migration | Not allowed in H15 contract slice | Must be separate H16/H17 contract+implementation |
| Historical audit rows | Retain in H15B | No deletion before migration slice |

### Verdict before contract recommendation

`ALLOW_CONTRACT_REVIEW`

## 4. Repo-Wide Claim Code Inventory

| Reference | File | Category | Active Runtime? | H15B Candidate? | Risk |
|---|---|---|---:|---:|---|
| `claim_operation` | backend/app/services/station_claim_service.py | SERVICE_FUNCTION | No | Yes | Low |
| `release_operation_claim` | backend/app/services/station_claim_service.py | SERVICE_FUNCTION | No | Yes | Low |
| `get_operation_claim_status` | backend/app/services/station_claim_service.py | SERVICE_FUNCTION | No | Yes | Low |
| `_expire_claim_if_needed` | backend/app/services/station_claim_service.py | SERVICE_FUNCTION | No (dead-path only) | Yes | Low |
| `_log_claim_event` | backend/app/services/station_claim_service.py | SERVICE_FUNCTION | No (dead-path only) | Yes | Low |
| `_to_claim_state` | backend/app/services/station_claim_service.py | SERVICE_FUNCTION | No (dead-path only) | Yes | Low |
| `OperationClaim` | backend/app/models/station_claim.py | MODEL | Indirectly (init/tests/scripts) | Conditional | Medium |
| `OperationClaimAuditLog` | backend/app/models/station_claim.py | MODEL | Indirectly (init/tests/scripts) | Conditional | Medium |
| `ClaimRequest` | backend/app/schemas/station.py | SCHEMA | No | Yes | Low |
| `ReleaseClaimRequest` | backend/app/schemas/station.py | SCHEMA | No | Yes | Low |
| `ClaimResponse` | backend/app/schemas/station.py | SCHEMA | No | Yes | Low |
| `ClaimSummary` | backend/app/schemas/station.py | SCHEMA | Compatibility shape | Defer removal | Medium |
| `StationQueueItem.claim` | backend/app/schemas/station.py | API_CONTRACT | Compatibility shape | Defer removal | Medium |
| claim models import | backend/app/db/init_db.py | ORM_REGISTRY | Yes (metadata load) | No (unless scope expands) | High |
| claim table DDL | backend/scripts/migrations/0009_station_claims.sql | MIGRATION | Historical/reference | No | Low |
| claim imports/functions | backend/tests/* (multiple files) | TEST | Yes (test runtime) | Mixed | High |
| claim imports | backend/scripts/verify_*.py, scripts/seed/common.py | DOC/UTIL | No production runtime | Defer/cleanup | Medium |

## 5. Service Dependency Review

| Function / Block | Current Caller | Runtime Role After H14B | H15B Action | Risk |
|---|---|---|---|---|
| `claim_operation` | tests only | Dead runtime | Remove | Low |
| `release_operation_claim` | tests only | Dead runtime | Remove | Low |
| `get_operation_claim_status` | tests only | Dead runtime | Remove | Low |
| `_expire_claim_if_needed` | dead claim funcs only | Dead runtime | Remove | Low |
| `_log_claim_event` | dead claim funcs only | Dead runtime | Remove | Low |
| `_to_claim_state` | dead claim funcs only | Dead runtime | Remove | Low |
| `_get_unreleased_claim_for_update` | dead claim funcs only | Dead runtime | Remove | Low |
| `_get_operator_unreleased_claims_for_station_for_update` | dead claim funcs only | Dead runtime | Remove | Low |
| `_validate_operation_for_station` | dead claim funcs only | Dead runtime | Remove | Low |
| `_validate_operation_for_active_claim_context` | dead claim funcs only | Dead runtime | Remove | Low |
| `_has_admin_support_override` | dead claim funcs only | Dead runtime | Remove | Low |
| `ensure_operation_claim_owned_by_identity` | no app caller | Dead runtime | Remove | Low |
| `get_station_queue` | station queue route | Active | Keep | High |
| `get_station_scoped_operation` | station detail route | Active | Keep | High |
| `resolve_station_scope`, `ensure_operator_context`, role helpers | queue/detail paths | Active | Keep | High |

## 6. Schema Dependency Review

| Schema / Type | Current Consumer | H15B Action | Risk |
|---|---|---|---|
| `ClaimRequest` | none | Remove | Low |
| `ReleaseClaimRequest` | none | Remove | Low |
| `ClaimResponse` | none | Remove | Low |
| `ClaimSummary` | referenced by queue item schema only | Keep temporarily | Medium |
| `QueueClaimState` | not present in backend schema (frontend retired) | N/A | None |
| `StationQueueItem.claim` | response still emits `claim: None` | Keep nullable in H15B | Medium |
| station queue/session ownership schemas | active queue responses | Keep | High |

Decision on queue claim field:
- Keep `StationQueueItem.claim` as nullable compatibility field until a dedicated API contract cleanup slice explicitly removes it from backend response and schema.

## 7. Model / ORM Dependency Review

| Model / Table | Current Import / Dependency | Can Remove Model in H15B? | Requires Migration? | Recommendation |
|---|---|---:|---:|---|
| `OperationClaim` model | db init import, tests, scripts | Not safely in minimal H15B | Table drop later | Defer model deletion unless H15B scope expands to dependent tests/scripts |
| `OperationClaimAuditLog` model | db init import, tests, scripts | Not safely in minimal H15B | Table drop later | Defer model deletion unless H15B scope expands to dependent tests/scripts |
| `operation_claims` table | physical DB table + legacy migration history | No | Yes | H16/H17 only |
| `operation_claim_audit_logs` table | FK child to claims table | No | Yes | Drop child first in H16/H17 |

Answer to deletion sequencing:
- `backend/app/models/station_claim.py` should not be deleted in the minimal H15B dead-code cleanup unless all dependent test/script imports and db-init registration are updated in the same slice.
- ORM model deletion can happen before table-drop migration only if model-loading and test dependencies are fully removed/replaced first; otherwise defer model deletion to migration-adjacent slice.

## 8. Test Dependency Review

| Test File | Claim Dependency | H15B Required Change | Defer? | Risk |
|---|---|---|---:|---|
| `test_claim_single_active_per_operator.py` | service + model direct | Delete | No | Low |
| `test_release_claim_active_states.py` | service + model direct | Delete | No | Low |
| `test_execution_route_claim_guard_removal.py` | claim fixture + teardown | Rewrite fixture to pure StationSession negative path before model drop | Yes | High |
| `test_operation_detail_allowed_actions.py` | none now | None | No | None |
| `test_operation_status_projection_reconcile.py` | none now | None | No | None |
| `test_station_queue_active_states.py` | teardown model imports | Cleanup before model drop | Yes | Medium |
| `test_station_queue_session_aware_migration.py` | no claim model usage | None | No | None |
| `test_reopen_resume_station_session_continuity.py` | none | None | No | None |
| `test_reopen_resumability_claim_continuity.py` | direct claim behavior assertions | Rewrite or retire before model drop | Yes | High |
| `test_reopen_operation_claim_continuity_hardening.py` | teardown model imports | Cleanup before model drop | Yes | Medium |

Additional non-requested but blocking references found:
- `test_start_downtime_auth.py`
- `test_status_projection_reconcile_command.py`
- `test_work_order_operation_foundation.py`

## 9. H15B Scope Proposal

Suggested slice name:

`P0-C-08H15B Claim Service / Schema Dead-Code Removal Implementation`

### H15B In Scope
- Remove dead claim service functions and helpers from `station_claim_service.py`.
- Keep `get_station_queue`, `get_station_scoped_operation`, scope/operator helpers.
- Remove dead claim route schemas: `ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse`.
- Delete claim service test files:
  - `test_claim_single_active_per_operator.py`
  - `test_release_claim_active_states.py`
- Keep queue response compatibility field `claim: None` and related schema shape.

### H15B Out of Scope
- Table drops / alembic migration.
- Historical audit data deletion.
- StationSession or execution behavior changes.
- Close/reopen behavior changes.
- Model deletion unless explicit expanded scope handles all dependent tests/scripts.

| H15B Candidate Action | Files | Tests Required | Risk |
|---|---|---|---|
| Remove dead claim service functions | `backend/app/services/station_claim_service.py` | targeted service/runtime regression suite | Medium |
| Remove dead claim request/response schemas | `backend/app/schemas/station.py` | import/runtime checks | Low |
| Delete claim service tests | 2 claim test files | deletion safety + regression | Low |
| Keep queue compatibility field | schema/service active path | queue/session regression | Low |
| Defer model deletion | `backend/app/models/station_claim.py`, `db/init_db.py` | none in H15B | Low |

## 10. H16 / H17 Roadmap

| Slice | Goal | Code? | Migration? | Preconditions | Stop Conditions |
|---|---|---:|---:|---|---|
| P0-C-08H16 Claim Model/Table Drop Migration Contract | Finalize model/table drop readiness and dependency closure | No | No | H15B complete; dependency sweep clean for model removal | Any claim model import still needed by tests/scripts/runtime |
| P0-C-08H17 Claim Model/Table Drop Migration Implementation | Remove claim model registration + add/drop migration (audit child first) | Yes | Yes | H16 contract approved; full dependency cleanup done | FK order violation risk or unresolved test fixtures |
| P0-C-08I Claim Retirement Closeout / Repo Sweep | Remove residual claim references in scripts/docs/tests, run full regression | Yes | No | H17 complete | Any runtime claim reference remains |

## 11. Test Strategy

Contract-time verification executed:
- `pytest -q tests/test_claim_single_active_per_operator.py tests/test_release_claim_active_states.py`
- `pytest -q tests/test_execution_route_claim_guard_removal.py tests/test_station_queue_active_states.py tests/test_station_queue_session_aware_migration.py tests/test_reopen_resume_station_session_continuity.py tests/test_reopen_resumability_claim_continuity.py tests/test_reopen_operation_claim_continuity_hardening.py`
- frontend: `npm run lint`, `npm run build`, `npm run check:routes`

Post-H15B required regression focus:
- queue/detail routes and execution guard suites
- reopen/session continuity suites
- full backend suite recommended before H16 contract signoff

## 12. Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| Deleting claim model too early breaks db init metadata load | High | Defer model deletion or include db init cleanup + broad test/script updates in same slice |
| Hidden test/script claim fixtures fail after model deletion | High | Run repo-wide dependency sweep and update all fixtures before H16/H17 |
| Premature queue schema cleanup breaks compatibility clients | Medium | Keep nullable queue claim field until dedicated API contract cleanup |
| Mixing dead-code cleanup with migration in one slice increases blast radius | Medium | Keep H15B code-only, migration deferred |

## 13. Recommendation

Proceed with H15B as service/schema dead-code cleanup only.

Do not delete `backend/app/models/station_claim.py` in minimal H15B unless scope is explicitly expanded to remove/update all model dependents discovered by repo-wide sweep (db init, tests, scripts). Otherwise defer model deletion to H16/H17 migration chain.

## 14. Final Verdict

`READY_FOR_P0_C_08H15B_WITH_MODEL_DEFERRED_TO_MIGRATION`
