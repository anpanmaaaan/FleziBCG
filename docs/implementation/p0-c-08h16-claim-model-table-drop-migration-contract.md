# P0-C-08H16 Claim Model / Table Drop Migration Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Defined ORM model and DB table drop migration readiness after claim service/schema dead-code removal. |

## 1. Executive Summary
This is a contract-only, migration-readiness review for claim retirement after H15B.

Current readiness outcome:
- OperationClaim and OperationClaimAuditLog model removal now: not ready.
- operation_claims and operation_claim_audit_logs table drop now: not ready.
- Reason: unresolved test and script dependency surface still imports and uses claim models/tables.

Contract direction:
- Use a split path.
- H16 remains contract-only (this document).
- H16B should burn down model/test dependencies first.
- H17 should execute the table-drop migration after burn-down completion.

## 2. Scope Reviewed
Scope type:
- Review and contract only.
- No backend runtime implementation.
- No frontend implementation.
- No migration implementation.

Preflight workspace safety summary:

| File / Group | Related to H16? | Action |
|---|---|---|
| backend/.venv site-packages bytecode churn | No | Ignore and do not touch |
| Existing execution/claim/backend dirty files | Yes (evidence sources only) | Read-only analysis only |
| Existing frontend dirty files | No for H16 contract logic | Ignore and do not touch |
| New H16 contract and tracker docs | Yes | Allowed documentation updates only |

Preflight decision:
- Workspace is dirty but isolatable for contract-only documentation work.
- No destructive workspace cleanup performed.
- No unrelated dirty files modified.

## 3. Hard Mode Gate Evidence
## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Contract-Only Review
- Hard Mode MOM: v3
- Reason: task touches claim model retirement, DB migration strategy, audit/history table drop sequencing, execution-governance invariants, and test dependency safety.

### Design Evidence Extract

| Fact | Source | Evidence |
|---|---|---|
| StationSession is target ownership truth | docs/design/02_domain/execution/station-session-ownership-contract.md | Claim is compatibility debt; session is target |
| Execution commands remain session-guarded | docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md | Guarded command subset already enforced; no claim ownership truth required |
| Claim is deprecated in target execution contract | docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md | claim_operation is transition debt |
| Active state invariants require backend ownership truth | docs/design/02_domain/execution/station-execution-state-matrix-v4.md | session-owned mutation invariants |
| Backend is source of truth and migration slices must be controlled | docs/governance/CODING_RULES.md | architecture/contract PR gates and migration discipline |
| H14B removed route/client claim runtime surfaces | prior implementation reports | no active claim route/client contract |
| H15B removed service/schema dead code and deferred model/table drop | docs/implementation/p0-c-08h15b-claim-service-schema-dead-code-removal-implementation-report.md | model/table still deferred |

### Audit / History Map

| Audit Surface | Current Source | Current State | H16/H17 Decision |
|---|---|---|---|
| CLAIM_CREATED | operation_claim_audit_logs | historical only | retire with table drop migration |
| CLAIM_RELEASED | operation_claim_audit_logs | historical only | retire with table drop migration |
| CLAIM_EXPIRED | operation_claim_audit_logs | no active queue-loop emitter after H14B | retire with table drop migration |
| CLAIM_RESTORED_ON_REOPEN | operation_claim_audit_logs | historical only after H11B retirement | retire with table drop migration |
| StationSession events | execution/security event logs | active and canonical | keep; out of claim-drop scope |

### ORM / Metadata Dependency Map

| Artifact | Current Dependency | Can Remove Before Migration? | H16/H17 Action | Risk |
|---|---|---|---|---|
| backend/app/models/station_claim.py | defines both claim ORM models | No | remove in burn-down slice with dependency updates | High |
| OperationClaim | imported by db init, tests, scripts | No | remove after import/fixture rewrite | High |
| OperationClaimAuditLog | imported by db init, tests, scripts | No | remove after import/fixture rewrite | High |
| backend/app/db/init_db.py | imports claim models for metadata registration | No | remove claim imports only when model/tests/scripts no longer require them | High |
| backend/app/db/base.py | shared Base only (no direct claim import) | Yes (already independent) | no change required | Low |
| backend/app/models/__init__.py | empty | Yes | no change required | Low |

### Migration Impact Map

| Impact Item | Current State | H16/H17 Decision |
|---|---|---|
| Migration system | Alembic is canonical active runner (0001..0007) | use new forward Alembic revision for claim drop |
| Legacy SQL migration 0009_station_claims.sql | historical DDL source for claim tables | keep unchanged as immutable history |
| FK dependency | operation_claim_audit_logs.claim_id references operation_claims.id | drop audit table first, then claim table |
| Downgrade convention | active Alembic revisions include downgrade functions | provide downgrade recreating both claim tables + indexes |
| Baseline policy | no baseline rewrite needed | do not edit old migration files |

### Test Matrix

| Test ID | Scenario | Expected |
|---|---|---|
| HM3-H16-T1 | repo sweep for claim model/table references | identify all blockers before removal |
| HM3-H16-T2 | execution/queue/reopen focused backend subset | green baseline before burn-down |
| HM3-H16-T3 | operation detail/projection subset | green baseline before burn-down |
| HM3-H16-T4 | frontend lint/build/route smoke | green baseline (no UI drift) |
| HM3-H16-T5 | migration apply test (future H17) | claim tables dropped in safe order |
| HM3-H16-T6 | DB existence check post-migration (future H17) | both claim tables absent |
| HM3-H16-T7 | full backend suite (if feasible in H17) | no claim-model import regressions |

### Verdict before contract recommendation
ALLOW_CONTRACT_REVIEW

## 4. Repo-Wide Claim Model/Table Inventory

| Reference | File | Category | Active Runtime? | H16B/H17 Action | Risk |
|---|---|---|---|---|---|
| OperationClaim | backend/app/models/station_claim.py | ORM_MODEL | Metadata and test/script active | remove in H16B after burn-down | High |
| OperationClaimAuditLog | backend/app/models/station_claim.py | ORM_MODEL | Metadata and test/script active | remove in H16B after burn-down | High |
| operation_claims | backend/scripts/migrations/0009_station_claims.sql | DB_TABLE | still present in DB | drop in H17 migration | High |
| operation_claim_audit_logs | backend/scripts/migrations/0009_station_claims.sql | DB_TABLE | still present in DB | drop in H17 migration first | High |
| claim model import | backend/app/db/init_db.py | INIT_REGISTRY | active metadata import | remove in H16B with model removal | High |
| ClaimSummary | backend/app/schemas/station.py | SCHEMA | compatibility schema only | decide separately from table-drop, likely defer API shape change | Medium |
| StationQueueItem.claim | backend/app/schemas/station.py | QUEUE_CONTRACT | compatibility nullable field | keep in H16B/H17 unless dedicated API cleanup is approved | Medium |
| claim None projection | backend/app/services/station_claim_service.py | QUEUE_CONTRACT | active queue response shape | preserve in H16B/H17 | Low |
| operation_claims / audit refs | backend/tests and backend/scripts | TEST_FIXTURE / TEST_TEARDOWN | active | rewrite/remove before model deletion | High |
| claim events in docs | docs (non-runtime) | DOC / AUDIT_EVENT | historical only | keep documentation history | Low |

## 5. ORM / Metadata Dependency Review

| Artifact | Current Dependency | Can Remove Before Migration? | H16/H17 Action | Risk |
|---|---|---|---|---|
| backend/app/models/station_claim.py | direct model definitions | No | remove in H16B after dependent tests/scripts updated | High |
| OperationClaim | imported by db init; used in tests/scripts fixtures | No | rewrite fixtures/imports first, then delete model | High |
| OperationClaimAuditLog | imported by db init; used in tests/scripts teardown | No | rewrite teardowns/imports first, then delete model | High |
| backend/app/db/init_db.py | imports claim models for metadata registration and Alembic model loading | No | remove claim import line only when no model file remains | High |
| backend/app/db/base.py | no claim-specific registration | Yes | no action |
| backend/app/models/__init__.py | empty module | Yes | no action |
| backend/alembic/env.py | imports app.db.init_db side-effect model registry | No | remains unchanged; will observe updated init_db import set after H16B | Medium |

Answer:
- Can OperationClaim and OperationClaimAuditLog be removed now? No.
- Required init/model-registry change: remove claim import from backend/app/db/init_db.py only in same slice that removes model file and rewrites dependencies.

## 6. Migration Dependency Review

| Migration Artifact | Current Role | H16/H17 Decision | Risk |
|---|---|---|---|
| backend/scripts/migrations/0009_station_claims.sql | historical raw SQL claim DDL source | keep unchanged as historical reference | Low |
| backend/alembic/versions/0001_baseline.py | no-op baseline | unchanged | Low |
| backend/alembic/versions/0002..0007 | forward Alembic revisions with downgrade support | unchanged | Low |
| backend/alembic/env.py | canonical migration runner using Base metadata | unchanged | Medium |
| new H17 revision (to be created) | will execute claim table drop | add new forward migration; do not edit old files | High |

Migration decisions:
- Migration style is mixed history (legacy SQL folder + canonical active Alembic pipeline).
- For current governed changes, use Alembic forward migration only.
- Do not edit old migration 0009.
- Safe drop order: operation_claim_audit_logs first, then operation_claims.
- Downgrade should recreate both tables and indexes to match project downgrade conventions.
- Suggested future migration filename: 0008_drop_station_claim_tables.py (or next sequential revision ID at implementation time).

## 7. Test Dependency Review

| Test File | Claim Model/Table Usage | H16/H17 Action | Risk |
|---|---|---|---|
| backend/tests/test_execution_route_claim_guard_removal.py | imports models; inserts active claim fixture; teardown deletes claim rows | rewrite test to prove session-guard behavior without claim rows in H16B | High |
| backend/tests/test_reopen_resumability_claim_continuity.py | imports models; inserts/selects claim rows; teardown claim deletes | rewrite/retire claim-row assertions in H16B | High |
| backend/tests/test_reopen_operation_claim_continuity_hardening.py | imports models; teardown claim deletes | remove claim teardown/import dependency in H16B | Medium |
| backend/tests/test_operation_detail_allowed_actions.py | no claim import currently | no action | Low |
| backend/tests/test_operation_status_projection_reconcile.py | no claim import currently | no action | Low |
| backend/tests/test_station_queue_active_states.py | imports models; teardown claim deletes | remove claim teardown/import dependency in H16B | Medium |
| backend/tests/test_station_queue_session_aware_migration.py | no claim model import | no action | Low |
| backend/tests/test_reopen_resume_station_session_continuity.py | no claim model import | no action | Low |
| backend/tests/test_start_downtime_auth.py | imports/inserts OperationClaim | rewrite negative fixture in H16B | High |
| backend/tests/test_status_projection_reconcile_command.py | imports claim models in teardown | cleanup in H16B | Medium |
| backend/tests/test_work_order_operation_foundation.py | imports claim models in teardown | cleanup in H16B | Medium |

Test dependency status:
- unresolved for direct model deletion and table drop.
- burn-down required before H17 migration execution.

## 8. Queue Contract Review

| Artifact | Current Claim Compatibility | H16/H17 Action | Risk |
|---|---|---|---|
| backend StationQueueItem.claim | nullable compatibility field remains | keep in H16B/H17 unless explicit API contract cleanup slice approved | Medium |
| backend queue payload | claim projected as None | preserve behavior in H16B/H17 | Low |
| backend ClaimSummary schema | still present as compatibility type | keep for now; evaluate removal in separate API cleanup | Medium |
| frontend StationQueueItem type | no claim field in stationApi.ts | already removed; no frontend dependency on claim payload | Low |

Queue contract decision:
- Do not mix risky response-shape change with model/table drop migration.
- Keep backend compatibility claim field for H16B/H17.
- Plan a separate post-migration API contract cleanup if needed.

## 9. H16B / H17 Scope Options

| Option | Pros | Cons | Risk | Recommendation |
|---|---|---|---|---|
| Option A: single H16B model/table-drop implementation | fewer slices, faster retirement | high blast radius with unresolved test/script dependencies | High | Not recommended |
| Option B: H16B burn-down, H17 migration implementation | controlled sequencing; clear rollback points; lower coupling risk | one extra slice | Medium | Recommended |
| Option C: H16B burn-down, H17 migration contract, H18 migration implementation | maximal governance safety | slower delivery and extra overhead | Medium | Optional only if governance uncertainty increases |

Recommended path:
- Option B

## 10. H16B Implementation Scope Proposal
Recommended next slice name:
- P0-C-08H16B Claim Model/Test Dependency Burn-Down

In scope for H16B:
- rewrite/remove tests that import OperationClaim or OperationClaimAuditLog.
- remove claim-row fixtures and claim-row teardown logic from tests.
- remove claim model usage from verification scripts if included in scope.
- remove backend model file and init_db claim imports only when dependency sweep reaches zero in runtime/tests/scripts under approved scope.
- preserve station queue runtime behavior and StationSession guard behavior.

Out of scope for H16B:
- table drop migration.
- DB table deletion.
- execution/close/reopen behavior changes.
- queue contract shape changes.
- frontend feature changes.

Planned H17 scope after H16B completion:
- add Alembic migration to drop operation_claim_audit_logs then operation_claims.
- provide downgrade that recreates both tables/indexes.
- run migration verification and focused/full regressions.

## 11. Stop Conditions for Implementation

| Stop Condition | Why It Blocks | Required Resolution |
|---|---|---|
| tests still import OperationClaim | model deletion will break test runtime | complete burn-down rewrites |
| migrations runner unclear | unsafe table-drop execution path | use Alembic only and document revision chain |
| FK drop order unclear | migration may fail at runtime | enforce child-first drop order |
| rollback policy unclear | unrecoverable migration risk | define downgrade recreation policy |
| DB environment cannot verify migration | no confidence in drop behavior | run migration apply/rollback in controlled env |
| queue response still references ClaimSummary without decision | API drift risk if changed implicitly | defer or isolate API cleanup decision |
| frontend expects claim field | potential runtime break if backend shape changes | confirmed no frontend claim field dependency; keep backend field for now |
| unknown production/audit retention conflict detected | governance breach risk | stop and re-run retention decision |
| focused backend regressions fail with claim-related error | unstable baseline | fix burn-down regressions first |

## 12. Test Strategy for H16B/H17

| Verification | Purpose | Required For |
|---|---|---|
| repo-wide claim model/table sweep | prove dependency closure before deletion | H16B and H17 |
| backend focused execution/queue/reopen tests | protect operational invariants | H16B and H17 |
| operation detail/projection tests | protect projection/action contracts | H16B and H17 |
| migration apply test | validate drop order and schema effect | H17 |
| frontend lint/build/routes | ensure no collateral UI regressions | H16B and H17 |
| full backend suite if feasible | broad regression confidence | H17 strongly recommended |
| DB table existence check post-migration | confirm both claim tables removed | H17 |

Review command results captured in this contract session:
- H16_EXEC_QUEUE_REOPEN_EXIT:0 (43 passed)
- H16_OPERATION_DETAIL_PROJECTION_EXIT:0 (35 passed)
- H16_FRONTEND_LINT_EXIT:0
- H16_FRONTEND_BUILD_EXIT:0
- H16_FRONTEND_ROUTE_SMOKE_EXIT:0
- route smoke summary: PASS 24, FAIL 0, 77/78 covered, 1 excluded redirect route

## 13. Risk Register

| Risk | Severity | Mitigation |
|---|---|---|
| deleting models before fixture rewrite | High | enforce H16B burn-down gate |
| dropping tables while tests/scripts still reference them | High | require zero-reference sweep before H17 migration |
| FK order migration failure | High | drop operation_claim_audit_logs first |
| accidental API shape drift on queue | Medium | keep compatibility claim field in H16B/H17 |
| hidden dependency via init_db/alembic model registration | High | coordinate model deletion with init_db import cleanup |
| baseline dirty workspace contamination | Medium | modify docs only in this contract slice; avoid runtime files |

## 14. Recommendation
Proceed with Option B.

Recommendation summary:
1. Approve H16 contract outcome as readiness gate only.
2. Execute H16B dependency burn-down first.
3. Approve H17 migration implementation only after dependency sweep is clean.
4. Keep legacy SQL migration 0009 as immutable historical artifact.
5. Use new Alembic forward migration with child-first drop order and downgrade recreation.
6. Keep queue compatibility field unchanged during migration slices.

## 15. Final Verdict
READY_FOR_P0_C_08H16B_CLAIM_MODEL_TEST_DEPENDENCY_BURN_DOWN
