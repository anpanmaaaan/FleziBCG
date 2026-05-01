# P0-C-08H1 Claim Consumer / Queue Contract Cutover Plan

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Planned frontend/API consumer cutover from claim-shaped ownership to StationSession ownership contract. |

## 1. Executive Summary

This H1 slice is plan-only and review-only. No frontend code, backend code, schema, migration, route behavior, or command behavior was changed.

Current evidence confirms that claim remains the primary consumer-facing ownership signal in frontend station execution surfaces, while backend queue responses already contain the additive StationSession ownership block introduced in 08D. The safest next slice is H2 frontend consumer cutover to treat ownership as primary truth and claim as compatibility-only display metadata.

Primary conclusion:
- Backend queue ownership contract is sufficient for H2 consumer cutover without API shape changes.
- Claim removal remains blocked after H1 and after H2 until later backend/runtime and data-retention slices complete.

## 2. Scope Reviewed

- Governance/design/contracts and prior slices reviewed:
  - .github/copilot-instructions.md
  - .github/agent/AGENT.md
  - docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md
  - docs/ai-skills/hard-mode-mom-v3/SKILL.md
  - docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md
  - docs/design/02_domain/execution/station-session-ownership-contract.md
  - docs/design/02_registry/station-session-event-registry.md
  - docs/design/00_platform/canonical-error-code-registry.md
  - docs/design/00_platform/canonical-error-codes.md
  - docs/implementation/p0-c-08g-claim-removal-readiness-check.md
  - docs/implementation/p0-c-08f-claim-api-deprecation-lock-report.md
  - docs/implementation/p0-c-08e-v2-db-fixture-deadlock-stabilization-report.md
  - docs/implementation/p0-c-08e-reopen-resume-continuity-replacement-report.md
  - docs/implementation/p0-c-08d-station-queue-session-aware-migration-report.md
  - docs/implementation/p0-c-08c-station-session-command-guard-enforcement-report.md
  - docs/implementation/p0-c-08b-command-guard-enforcement-contract-report.md
  - docs/implementation/p0-c-08-station-session-enforcement-review.md
  - docs/implementation/p0-c-execution-command-hardening-closeout-review.md
  - docs/implementation/p0-c-04-claim-compatibility-deprecation-lock.md
  - docs/implementation/hard-mode-v3-map-report.md
  - docs/implementation/autonomous-implementation-plan.md
  - docs/implementation/autonomous-implementation-verification-report.md
  - docs/implementation/design-gap-report.md
  - docs/design/02_domain/execution/station-execution-state-matrix-v4.md
  - docs/design/02_domain/execution/station-execution-command-event-contracts-v4.md
  - docs/design/02_domain/execution/station-execution-policy-and-master-data-v4.md
  - docs/design/02_domain/execution/execution-state-machine.md

- Frontend consumer inventory reviewed:
  - frontend/src/app/api/stationApi.ts
  - frontend/src/app/api/index.ts
  - frontend/src/app/pages/StationExecution.tsx
  - frontend/src/app/components/station-execution/StationQueuePanel.tsx
  - frontend/src/app/components/station-execution/QueueOperationCard.tsx
  - frontend/src/app/components/station-execution/StationExecutionHeader.tsx
  - frontend/src/app/components/station-execution/AllowedActionZone.tsx
  - frontend/src/app/i18n/registry/en.ts
  - frontend/src/app/i18n/registry/ja.ts
  - frontend/src/app/screenStatus.ts

- Backend contract surfaces reviewed:
  - backend/app/api/v1/station.py
  - backend/app/api/v1/operations.py
  - backend/app/schemas/station.py
  - backend/app/services/station_claim_service.py

- Claim-relevant test surfaces reviewed:
  - backend/tests/test_claim_api_deprecation_lock.py
  - backend/tests/test_station_queue_active_states.py
  - backend/tests/test_station_queue_session_aware_migration.py
  - backend/tests/test_station_session_command_guard_enforcement.py
  - backend/tests/test_reopen_resume_station_session_continuity.py
  - backend/tests/test_reopen_resumability_claim_continuity.py

## 3. Consumer Usage Inventory

| Consumer | File | Current Claim Dependency | Current Usage Type | Replacement Field / API | Removal Risk |
|---|---|---|---|---|---|
| Station queue API client type | frontend/src/app/api/stationApi.ts | StationQueueItem includes claim; no ownership typing | TYPE_ONLY | ownership block typing on StationQueueItem | HIGH |
| Claim mutation client | frontend/src/app/api/stationApi.ts | claim(operationId) calls POST /station/queue/{id}/claim | CLAIM_API_CALL | REPLACE_WITH_STATIONSESSION_FLOW | BLOCKER |
| Claim release client | frontend/src/app/api/stationApi.ts | release(operationId) calls POST /station/queue/{id}/release | CLAIM_API_CALL | REPLACE_WITH_STATIONSESSION_FLOW | BLOCKER |
| Claim status client | frontend/src/app/api/stationApi.ts | getClaim(operationId) calls GET /station/queue/{id}/claim | CLAIM_API_CALL | REMOVE_CALL (or compatibility diagnostics only) | HIGH |
| API exports | frontend/src/app/api/index.ts | Re-exports ClaimSummary/ClaimResponse types | TYPE_ONLY | export ownership-first queue item contract | MEDIUM |
| Execution page ownership gate | frontend/src/app/pages/StationExecution.tsx | canExecuteByClaim and claimState drive execution mode and action affordance | QUEUE_CLAIM_OWNERSHIP_LOGIC | ownership.owner_state + has_open_session as primary | BLOCKER |
| Execution page claim actions | frontend/src/app/pages/StationExecution.tsx | claimOperation/releaseClaim call claim endpoints | CLAIM_API_CALL | REPLACE_WITH_STATIONSESSION_FLOW | BLOCKER |
| Execution page error UX | frontend/src/app/pages/StationExecution.tsx | station.claim.required used for command failures | QUEUE_CLAIM_FIELD_DISPLAY | map to session-required/owner-mismatch semantics from backend | HIGH |
| Queue panel filter logic | frontend/src/app/components/station-execution/StationQueuePanel.tsx | mine filter and summary mine count use item.claim.state | QUEUE_CLAIM_OWNERSHIP_LOGIC | ownership.owner_state | HIGH |
| Queue card lock/badge logic | frontend/src/app/components/station-execution/QueueOperationCard.tsx | lock, badge, and hint driven by item.claim.state | QUEUE_CLAIM_OWNERSHIP_LOGIC | ownership.owner_state + has_open_session | HIGH |
| Header claim affordance | frontend/src/app/components/station-execution/StationExecutionHeader.tsx | release button and badge are claim-labeled | QUEUE_CLAIM_FIELD_DISPLAY | ownership-first label; claim shown as legacy if retained | MEDIUM |
| Allowed action wrapper | frontend/src/app/components/station-execution/AllowedActionZone.tsx | canExecuteByClaim prop name and gate | QUEUE_CLAIM_OWNERSHIP_LOGIC | canExecuteByOwnership/session context gate | HIGH |
| i18n claim strings | frontend/src/app/i18n/registry/en.ts; frontend/src/app/i18n/registry/ja.ts | extensive claim wording and toasts | DOC_ONLY | ownership/session wording and compatibility-tagged legacy texts | MEDIUM |
| Screen status note | frontend/src/app/screenStatus.ts | explicitly declares compatibility claim model | DOC_ONLY | update to ownership-first guidance | LOW |
| Station queue route contract | backend/app/api/v1/station.py | queue route returns both claim and ownership blocks | TYPE_ONLY | unchanged in H2 (consumer-only cutover) | LOW |
| Claim APIs (deprecated) | backend/app/api/v1/station.py | claim/release/status routes remain active with deprecation headers | CLAIM_API_CALL | keep compatibility-only in H2 | HIGH |
| Execution command route compatibility guard | backend/app/api/v1/operations.py | seven commands still call ensure_operation_claim_owned_by_identity after StationSession guard | UNKNOWN | later H3 backend guard-removal slice | BLOCKER |
| Queue builder | backend/app/services/station_claim_service.py | computes claim and ownership blocks together | TYPE_ONLY | keep as-is in H2 | MEDIUM |
| Claim deprecation contract tests | backend/tests/test_claim_api_deprecation_lock.py | locks deprecation headers and queue non-deprecation | TEST_ONLY | keep green in H2 | LOW |
| Queue session-aware tests | backend/tests/test_station_queue_session_aware_migration.py | locks ownership additive contract | TEST_ONLY | keep green in H2 | LOW |
| StationSession command guard tests | backend/tests/test_station_session_command_guard_enforcement.py | locks seven-command StationSession guard behavior | TEST_ONLY | keep green in H2 | LOW |

## 4. Queue Contract Cutover Mapping

| Legacy / Claim Field | Current Meaning | Target Field | Target Meaning | Cutover Rule |
|---|---|---|---|---|
| claim_id | claim row identity (not exposed in queue payload) | session_id | active StationSession identity for station ownership context | Do not introduce claim_id to frontend ownership logic; use ownership.session_id if present |
| claimed_by_user_id | operator owning active claim | operator_user_id | operator bound to OPEN StationSession | ownership.operator_user_id is primary ownership truth; claimed_by_user_id becomes compatibility display/debug only |
| claim_status | claim-derived mine/other/none concept | owner_state | session-owner relation: mine/other/unassigned/none | replace claim_status decisions with ownership.owner_state |
| compatibility_claim_id | not present in current contract | session_id | canonical session ownership identity | not used in H2; if introduced later, keep compatibility-only |
| compatibility_claimed_by_user_id | not present in current contract | operator_user_id | ownership operator | not used in H2; avoid new compatibility fields |
| compatibility_claim_status | not present in current contract | owner_state | ownership relation for current user | not used in H2; owner_state is already available |
| target_owner_type | declares ownership migration target | target_owner_type | expected to be station_session | assert station_session as primary path; fallback to compatibility branch when absent |
| ownership_migration_status | migration marker | ownership_migration_status | indicates TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT | use for telemetry/debug only; do not drive command authorization |
| session_id | session identifier | session_id | current session context | use as session presence signal together with has_open_session |
| session_status | OPEN/CLOSED session state in queue ownership block | session_status | open/closed session for station | OPEN + owner_state=mine enables ownership-mode UI affordance |
| operator_user_id | operator bound to session | operator_user_id | session operator identity | use for owner labels and ownership diagnostics |
| owner_state | relation of current user to session operator | owner_state | mine/other/unassigned/none | primary frontend owner indicator in H2 |
| has_open_session | session presence bit | has_open_session | whether station has an OPEN session | primary gate for ownership/session availability UX |

H2 target interpretation:
- ownership block is primary consumer contract for ownership.
- claim block remains compatibility display/debug data only.
- frontend must not treat claim as command authorization truth.

## 5. API Call Cutover Mapping

| Current API Call | File | Current Purpose | Target API / Behavior | H2 Action |
|---|---|---|---|---|
| stationApi.claim(operation.id, {}) | frontend/src/app/pages/StationExecution.tsx | acquire claim before execution mode | rely on StationSession ownership context + backend command guard for execution actions | REPLACE_WITH_STATIONSESSION_FLOW |
| stationApi.release(operation.id, { reason }) | frontend/src/app/pages/StationExecution.tsx | release claim from selected operation | non-primary path in ownership model; if retained, expose as compatibility-only action | KEEP_COMPATIBILITY_ONLY |
| stationApi.getClaim(operationId) | frontend/src/app/api/stationApi.ts | claim status read helper | ownership status from queue ownership block and/or station session current endpoint | REMOVE_CALL |
| stationApi.getQueue() | frontend/src/app/pages/StationExecution.tsx | load queue rows and ownership indicators | unchanged endpoint; consumer logic switches from item.claim to item.ownership | LEAVE_UNCHANGED |
| stationApi.getOperationDetail(operationId) | frontend/src/app/pages/StationExecution.tsx | fetch operation details/actions | unchanged | LEAVE_UNCHANGED |
| operationApi.start/report/pause/resume/startDowntime/endDowntime/complete | frontend/src/app/pages/StationExecution.tsx | execution commands currently pre-gated by claim UI | keep calls unchanged; pre-gate by ownership/session UI hints, backend remains source of truth | LEAVE_UNCHANGED |

## 6. UI Behavior Cutover Rules

| UI Behavior | Current Claim-Based Behavior | Target Session-Aware Behavior | Compatibility Fallback |
|---|---|---|---|
| Queue owner badge | Uses claim.state mine/other/none | Use ownership.owner_state and operator_user_id | If ownership missing, render legacy claim badge with compatibility marker |
| Queue lock state | item.claim.state === other locks selection | lock/soft-lock by ownership.owner_state=other and has_open_session true | If ownership absent, keep current claim lock logic |
| Queue mine filter | filter mine uses claim.state === mine | filter mine uses owner_state === mine | fallback to claim mine when ownership block absent |
| Session exists but no claim | currently appears as claim none (ambiguous) | show session-owned state from ownership has_open_session and owner_state | keep claim as legacy secondary tag only |
| Claim exists but no session | currently appears as claim mine/other and drives action affordance | show warning: legacy compatibility ownership present, session missing; actions rely on backend guard outcomes | temporarily allow claim badge for diagnostics only |
| Execution mode toggle | isExecutionMode requires claimState mine | execution mode requires ownership owner_state=mine and has_open_session true | fallback to current claim mode only when ownership block absent |
| Command preconditions in UI | claim.required errors and claim-based guards | session/ownership hints (session required, owner mismatch) while still trusting backend response | map 403/409 backend detail to ownership messages; retain claim.required as legacy fallback text |
| Claim button visibility | claim button is primary affordance | claim action is not primary path; optional compatibility action only | can keep hidden behind compatibility flag during migration |
| Release button | release tied to claim mine + PLANNED | release becomes compatibility-only action, not ownership authority | keep current release behavior but label as compatibility |
| Frontend call claim before commands | yes | no for primary flow | optional compatibility action only |

Direct answers required by H1:
- Queue card owner should show session owner from ownership.owner_state/operator_user_id.
- If StationSession exists but claim does not, show session ownership as authoritative and proceed with ownership-based UX.
- If claim exists but no StationSession, show compatibility warning/legacy badge; backend guard remains authoritative.
- Claim badge should become legacy/compatibility badge, not primary ownership badge.
- Operator actions should rely on StationSession command guard semantics and ownership block UX, not claim.
- Frontend should not call claim before command execution in primary flow.
- Compatibility fallback remains available only while claim APIs/routes still exist.

## 7. Backend Contract Impact

| Backend Area | Current State | H2 Needs Backend Change? | Risk | Recommendation |
|---|---|---:|---|---|
| Queue response shape | includes claim + ownership blocks | No | LOW | keep shape unchanged in H2 |
| Queue ownership content | ownership block contains target_owner_type, ownership_migration_status, session_id, session_status, operator_user_id, owner_state, has_open_session | No | LOW | consume existing fields directly |
| Claim APIs | active but deprecated with compatibility headers | No | MEDIUM | keep active for compatibility during H2 |
| Execution routes | seven commands enforce StationSession then claim compatibility guard | No (for H2) | HIGH | defer claim guard removal to H3 |
| Claim service | still owns claim ops and queue composition | No (for H2) | MEDIUM | keep unchanged in H2 |
| Reopen continuity helper | still claim-backed compatibility path | No (for H2) | HIGH | defer redesign to H5 |

H2 backend change need: none required for core cutover; only potential optional backend type/docs clarification if frontend requires stricter typing support.

## 8. Test Plan for H2

| Test Area | Test File | Required Assertion | Blocking? |
|---|---|---|---|
| Frontend queue ownership typing | frontend/src/app/api/stationApi.ts (new/updated test file in frontend test stack) | StationQueueItem includes ownership as primary consumed contract | Yes |
| Frontend StationExecution ownership mode | frontend/src/app/pages/StationExecution.tsx (new/updated test file in frontend test stack) | execution-mode and action gating use ownership fields first | Yes |
| Frontend queue card render | frontend/src/app/components/station-execution/QueueOperationCard.tsx (new/updated test file in frontend test stack) | owner badge/lock logic driven by owner_state/has_open_session | Yes |
| Frontend queue panel filters | frontend/src/app/components/station-execution/StationQueuePanel.tsx (new/updated test file in frontend test stack) | mine filter and summary mine count use ownership owner_state | Yes |
| Frontend compatibility rendering | frontend station execution components test set | queue renders when claim fields null/absent but ownership exists | Yes |
| Frontend legacy fallback | frontend station execution components test set | compatibility badge path still works when ownership missing and claim present | Yes |
| Frontend API call behavior | frontend StationExecution tests | primary command flow does not call claim API before execution commands | Yes |
| Backend claim deprecation lock regression | backend/tests/test_claim_api_deprecation_lock.py | deprecated headers still on claim APIs, queue non-deprecated | Yes |
| Backend queue session-aware regression | backend/tests/test_station_queue_session_aware_migration.py | ownership block remains stable | Yes |
| Backend command guard regression | backend/tests/test_station_session_command_guard_enforcement.py | seven-command StationSession guard remains stable | Yes |
| Backend reopen/session continuity guardrail | backend/tests/test_reopen_resume_station_session_continuity.py | reopen/resume continuity behavior unchanged | No (recommended) |

Required pre-implementation verification baseline captured in H1:
- frontend lint: pass
- frontend typecheck script: unavailable (not defined in frontend/package.json)
- backend claim deprecation test: pass
- backend queue session-aware test: pass
- backend StationSession guard test: pass

## 9. H2 Implementation Scope Proposal

P0-C-08H2 Frontend Queue Consumer Cutover to StationSession Ownership Contract

In Scope
- update frontend queue types to use ownership block as primary ownership signal
- update StationExecution and queue components to treat StationSession ownership as primary
- stop calling claim APIs as primary execution ownership flow
- keep claim compatibility display only where useful
- update tests and type contracts for ownership-first behavior

Out of Scope
- backend claim removal
- claim route deletion
- DB migration
- claim audit cleanup
- backend queue rewrite
- command guard behavior changes

Exact safe implementation prompt for P0-C-08H2:

```text
Proceed with P0-C-08H2 Frontend Queue Consumer Cutover to StationSession Ownership Contract.

This is an IMPLEMENTATION slice for frontend consumer cutover only.

Hard constraints:
- Do NOT modify backend runtime behavior.
- Do NOT modify backend API response shape.
- Do NOT remove claim routes/service/model/table.
- Do NOT change execution command behavior.
- Do NOT change StationSession guard behavior.
- Do NOT add migrations.
- Do NOT start P0-D.

Required implementation outcomes:
1. Treat queue ownership block as primary ownership truth in frontend station execution flow.
2. Replace claim-driven ownership gating with ownership.owner_state + has_open_session logic.
3. Keep claim data as compatibility-only UI fallback (legacy badge/warning), not command authority.
4. Remove primary-flow dependency on claim/release/getClaim API calls for execution readiness.
5. Keep queue API call and execution command API calls unchanged.
6. Update/extend frontend tests to assert ownership-first behavior and compatibility fallback.

Required verification:
- frontend lint
- frontend test/type checks available in repo
- backend regression checks:
  - tests/test_claim_api_deprecation_lock.py
  - tests/test_station_queue_session_aware_migration.py
  - tests/test_station_session_command_guard_enforcement.py

Stop conditions:
- any backend contract change required
- any command behavior drift detected
- any queue shape change required

Deliverables:
- code changes limited to frontend consumer/type/test files
- implementation report documenting ownership-first cutover behavior and compatibility fallback
```

| Area | H2 Action | Files Likely Affected | Risk |
|---|---|---|---|
| Queue API types | define ownership-first contract use | frontend/src/app/api/stationApi.ts, frontend/src/app/api/index.ts | MEDIUM |
| Station execution ownership logic | replace claim-based gating with ownership-based gating | frontend/src/app/pages/StationExecution.tsx | HIGH |
| Queue panel filter and summaries | switch mine/owner calculations to ownership | frontend/src/app/components/station-execution/StationQueuePanel.tsx | HIGH |
| Queue card lock/badges | switch owner lock/hint logic to ownership | frontend/src/app/components/station-execution/QueueOperationCard.tsx | HIGH |
| Header/action labels | convert primary claim semantics to ownership semantics | frontend/src/app/components/station-execution/StationExecutionHeader.tsx, frontend/src/app/components/station-execution/AllowedActionZone.tsx | MEDIUM |
| i18n copy | add ownership-first wording, keep legacy compatibility copy | frontend/src/app/i18n/registry/en.ts, frontend/src/app/i18n/registry/ja.ts | MEDIUM |
| Frontend tests | add ownership-first and fallback tests | frontend test files around station execution components/api | HIGH |

## 10. Remaining Claim Removal Blockers After H2

| Blocker | Current Evidence | Resolved by H2? | Future Slice |
|---|---|---:|---|
| Backend execution route claim guard | operations routes still call ensure_operation_claim_owned_by_identity on seven commands | No | P0-C-08H3 |
| Claim API routes still active | station claim/release/status endpoints remain deprecated but callable | No | P0-C-08H4 |
| Claim service still present | station_claim_service still owns claim operations and queue claim compatibility fields | No | P0-C-08H5 |
| Reopen continuity still claim-backed | _restore_claim_continuity_for_reopen still writes claim restoration | No | P0-C-08H5 |
| Claim data/audit retention unresolved | operation_claim_audit_logs retention and claim_id FK lifecycle not finalized | No | P0-C-08H6 |
| Claim tests still required | claim compatibility regression suites still protect runtime behavior | Partially | P0-C-08H7 / P0-C-08I |
| DB migration/removal not prepared | no approved archival/removal migration sequence yet | No | P0-C-08H7 |

Answer to H1 question 8:
- Yes, claim removal is still blocked after H1 and remains blocked after H2.

Answer to H1 question 9 (must happen before claim route/service/table removal):
1. H2 frontend ownership-first cutover completed and verified.
2. H3 backend execution-route claim guard removal contract+implementation completed for seven commands.
3. H4 claim API runtime disablement/toggle and consumer retirement completed.
4. H5 queue/reopen decoupling from claim completed.
5. H6 audit retention/archive decision approved and implemented.
6. H7 removal migration and claim code deletion completed with full regression.

## 11. Proposed Staged 08H Roadmap

| Slice | Goal | Code? | Migration? | Tests Required | Stop Conditions |
|---|---|---:|---:|---|---|
| P0-C-08H1 Claim Consumer / Queue Contract Cutover Plan | produce controlled staged plan and H2 prompt | No | No | review-safe lint/tests | missing ownership contract evidence |
| P0-C-08H2 Frontend Queue Consumer Cutover to StationSession Ownership | switch frontend ownership logic from claim to ownership block | Yes | No | frontend ownership tests + claim/session backend regression trio | backend contract change needed |
| P0-C-08H3 Backend Execution Route Claim Guard Removal Contract | remove claim guard dependency from seven execution routes after parity gate | Yes | No | command guard parity matrix + auth/scope regressions | any behavior drift in commands |
| P0-C-08H4 Backend Claim Route Runtime Disablement / Compatibility Toggle | disable/decommission claim API runtime usage path safely | Yes | No | claim API deprecation/disablement tests + consumer impact tests | active production consumers unresolved |
| P0-C-08H5 Claim Service Decoupling from Queue/Reopen | remove claim coupling from queue projection and reopen continuity | Yes | No | queue contract regressions + reopen/resume continuity regressions | reopen continuity parity not proven |
| P0-C-08H6 Claim Data Archive / Retention Decision | finalize and implement claim audit retention strategy | Yes (policy + code) | Possible | retention/archive validation tests | retention decision not approved |
| P0-C-08H7 Claim Code/Table Removal Migration | remove claim models/service/routes/tables after zero-runtime-dependency gate | Yes | Yes | migration tests + full regression | any remaining runtime dependency |
| P0-C-08I Post-Removal Regression Closeout | full post-removal confidence and debt closeout | Yes (light) | No | full suite + targeted scenario matrix | non-green regression baseline |

## 12. Recommendation

Proceed to H2 as a frontend consumer cutover slice with ownership-first semantics using existing backend queue ownership fields. Keep all backend runtime contracts unchanged in H2 and retain claim APIs/services/tables as compatibility-only.

Do not attempt claim removal, route deletion, or migration work in H2.

## 13. Final Verdict

READY_FOR_P0_C_08H2_FRONTEND_QUEUE_CONSUMER_CUTOVER
