# P0-C-08H3 Backend Execution Route Claim Guard Removal Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | Defined backend execution route claim guard removal contract after frontend ownership cutover. |

## 1. Executive Summary

This slice is contract-only and review-only.

Current source and verification evidence show that route-level claim guard usage remains active only on the seven execution endpoints already covered by 08C StationSession guard enforcement. Those seven routes are now candidates for next-slice claim guard removal at route level, while preserving all claim compatibility surfaces (claim APIs, claim service, claim model/table, queue claim payload, and claim audit logs).

`close_operation` and `reopen_operation` are not currently claim-guarded at route level and remain intentionally outside H4 claim-guard removal scope. Reopen continuity still uses claim compatibility internals in service logic.

Primary contract decision:
- H4 should remove route-level `ensure_operation_claim_owned_by_identity` only from the seven 08C-enforced execution routes.
- H4 must not include claim API removal, claim service/table removal, close/reopen StationSession policy expansion, or queue contract changes.

## 2. Scope Reviewed

Design and implementation references:
- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/implementation/p0-c-08h2-v1-frontend-verification-recovery-report.md`
- `docs/implementation/p0-c-08h2-frontend-queue-consumer-cutover-report.md`
- `docs/implementation/p0-c-08h1-claim-consumer-queue-contract-cutover-plan.md`
- `docs/implementation/p0-c-08g-claim-removal-readiness-check.md`
- `docs/implementation/p0-c-08f-claim-api-deprecation-lock-report.md`
- `docs/implementation/p0-c-08e-reopen-resume-continuity-replacement-report.md`
- `docs/implementation/p0-c-08d-station-queue-session-aware-migration-report.md`
- `docs/implementation/p0-c-08c-station-session-command-guard-enforcement-report.md`
- `docs/implementation/p0-c-08b-command-guard-enforcement-contract-report.md`
- `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`
- `docs/design/02_domain/execution/station-session-ownership-contract.md`
- `docs/design/02_registry/station-session-event-registry.md`
- `docs/design/00_platform/canonical-error-code-registry.md`
- `docs/design/00_platform/canonical-error-codes.md`
- `docs/implementation/autonomous-implementation-plan.md`
- `docs/implementation/autonomous-implementation-verification-report.md`
- `docs/implementation/hard-mode-v3-map-report.md`
- `docs/implementation/design-gap-report.md`

Runtime/source evidence reviewed:
- `backend/app/api/v1/operations.py`
- `backend/app/services/operation_service.py`
- `backend/app/services/station_claim_service.py`
- `backend/app/services/station_session_service.py`
- `backend/app/repositories/station_session_repository.py`

Test evidence reviewed:
- `backend/tests/test_station_session_command_guard_enforcement.py`
- `backend/tests/test_claim_api_deprecation_lock.py`
- `backend/tests/test_claim_single_active_per_operator.py`
- `backend/tests/test_release_claim_active_states.py`
- `backend/tests/test_station_queue_active_states.py`
- `backend/tests/test_station_queue_session_aware_migration.py`
- `backend/tests/test_reopen_resume_station_session_continuity.py`
- `backend/tests/test_reopen_resumability_claim_continuity.py`
- `backend/tests/test_reopen_operation_claim_continuity_hardening.py`
- `backend/tests/test_start_pause_resume_command_hardening.py`
- `backend/tests/test_report_quantity_command_hardening.py`
- `backend/tests/test_downtime_command_hardening.py`
- `backend/tests/test_complete_operation_command_hardening.py`
- `backend/tests/test_close_operation_command_hardening.py`
- `backend/tests/test_close_reopen_operation_foundation.py`

## 3. Route Claim Guard Inventory

Search target: `ensure_operation_claim_owned_by_identity`

| Route / Command | File | Current Claim Guard Location | Current StationSession Guard Coverage | Can Remove Claim Guard Next? | Risk |
|---|---|---|---|---|---|
| `POST /operations/{id}/start` (`start_operation`) | `backend/app/api/v1/operations.py` | route-level call after session guard | yes (route + service) | yes | MEDIUM |
| `POST /operations/{id}/report-quantity` (`report_quantity`) | `backend/app/api/v1/operations.py` | route-level call after session guard | yes (route + service) | yes | MEDIUM |
| `POST /operations/{id}/pause` (`pause_operation`) | `backend/app/api/v1/operations.py` | route-level call after session guard | yes (route + service) | yes | MEDIUM |
| `POST /operations/{id}/resume` (`resume_operation`) | `backend/app/api/v1/operations.py` | route-level call after session guard | yes (route + service) | yes | MEDIUM |
| `POST /operations/{id}/complete` (`complete_operation`) | `backend/app/api/v1/operations.py` | route-level call after session guard | yes (route + service) | yes | MEDIUM |
| `POST /operations/{id}/start-downtime` (`start_downtime`) | `backend/app/api/v1/operations.py` | route-level call after session guard | yes (route + service) | yes | MEDIUM |
| `POST /operations/{id}/end-downtime` (`end_downtime`) | `backend/app/api/v1/operations.py` | route-level call after session guard | yes (route + service) | yes | MEDIUM |
| `POST /operations/{id}/close` (`close_operation`) | `backend/app/api/v1/operations.py` | no claim guard call | no StationSession guard (role-gated SUP path) | not applicable in H4 | BLOCKER |
| `POST /operations/{id}/reopen` (`reopen_operation`) | `backend/app/api/v1/operations.py` | no claim guard call | no StationSession guard (role-gated SUP path) | not applicable in H4 | BLOCKER |

Inventory conclusion:
- Exactly 7 route-level claim guard usages remain, all on 08C StationSession-enforced commands.
- `close_operation` and `reopen_operation` are not in the removable set because they do not currently use route claim guard and remain policy-deferred.

## 4. Command-by-Command Replacement Coverage

| Command | 08C StationSession Guard? | 08E Continuity Coverage? | Frontend H2 Cutover? | Claim Guard Still Needed? | Recommendation |
|---|---|---|---|---|---|
| `start_operation` | yes | not required | yes | no (route-level) | remove route claim guard in H4 |
| `pause_operation` | yes | not required | yes | no (route-level) | remove route claim guard in H4 |
| `resume_operation` | yes | yes (resume-after-reopen) | yes | no (route-level) | remove route claim guard in H4 |
| `report_quantity` | yes | not required | yes | no (route-level) | remove route claim guard in H4 |
| `start_downtime` | yes | not required | yes | no (route-level) | remove route claim guard in H4 |
| `end_downtime` | yes | not required | yes | no (route-level) | remove route claim guard in H4 |
| `complete_operation` | yes | not required | yes | no (route-level) | remove route claim guard in H4 |
| `close_operation` | deferred in 08C | no direct 08E replacement target | frontend cutover not relevant | no route claim guard exists | keep unchanged; separate future policy contract |
| `reopen_operation` | deferred in 08C | yes, but continuity still claim-compat at service level | frontend cutover not relevant | no route claim guard exists | keep unchanged in H4; separate future contract |

Direct answers:
- Commands safely removable in H4 subset: start, pause, resume, report_quantity, start_downtime, end_downtime, complete.
- Commands not in H4 removal subset: close, reopen.

## 5. Route Guard Removal Behavior Contract

Behavior after H4 for approved routes (7-command subset):
- Command allow/deny is governed by StationSession guard + command state guards.
- Claim state must not block a command when StationSession guard passes.
- Claim state must not authorize a command when StationSession guard fails.
- Claim APIs remain callable (deprecated compatibility surface).
- Queue claim compatibility fields remain.
- Claim audit/history remains.
- No new command events on failed StationSession guard.
- No event rename.
- Success payload shape unchanged.

| Scenario | Current Behavior | Target Behavior After H4 | Test Required |
|---|---|---|---|
| valid OPEN StationSession, no active claim (7 commands) | route may reject via claim guard (`403`) | route proceeds to service/state guards and can succeed | yes |
| valid OPEN StationSession, conflicting claim owner (7 commands) | route may reject via claim guard (`403`) | route not blocked by claim; StationSession and state rules decide | yes |
| missing StationSession, active claim exists (7 commands) | rejected by StationSession guard today (before claim check) | unchanged rejection by StationSession guard | yes |
| invalid runtime state, valid StationSession (7 commands) | fails at service state guard | unchanged state-guard failure | yes |
| `close_operation` path | role-gated SUP path; no route claim guard | unchanged in H4 | yes (regression) |
| `reopen_operation` path | role-gated SUP path; claim continuity helper in service | unchanged in H4 | yes (regression) |

Error-order note:
- For the 7-command subset, claim-guard `403` outcomes are removed.
- Requests that previously failed only because of claim ownership can now reach service/state logic and may succeed or fail with existing StationSession/state errors.

## 6. Compatibility Risk Analysis

| Risk | Affected Area | Severity | Evidence | Mitigation |
|---|---|---|---|---|
| Route behavior change where claim-only failures become non-failures | operations route layer | HIGH | 7 endpoints still call route claim guard after session guard | add explicit H4 route-level parity tests |
| Legacy consumers still call deprecated claim APIs | station claim API surface | MEDIUM | 08F locked APIs as deprecated but active | keep claim APIs unchanged in H4 |
| Claim tests may encode old guard expectations | backend test suites | HIGH | existing claim suites remain broad | isolate route-removal contract tests and update only affected assertions |
| Error ordering/HTTP code drift | operations endpoint responses | MEDIUM | removal of route claim check changes possible first-failure condition | document expected deltas and assert stable StationSession/state outcomes |
| close/reopen ambiguity if bundled incorrectly | close/reopen command paths | HIGH | 08C deferred close/reopen; 08E continuity still claim-compat | keep close/reopen out of H4 subset |
| deprecated claim API confusion during transition | API consumers/docs | LOW | claim APIs remain active by design | maintain deprecation headers and clear H4 scope notes |
| claim audit/history retention unresolved | persistence/governance | MEDIUM | 08G readiness flagged audit retention as unresolved | defer to later retention/removal slices |

## 7. Test Update Plan for H4

| Test File | Required Change / New Test | Purpose |
|---|---|---|
| `backend/tests/test_execution_route_claim_guard_removal_contract.py` (new) | add route-level tests for 7 endpoints: valid session + no claim now succeeds | prove claim no longer gates 7 routes |
| `backend/tests/test_execution_route_claim_guard_removal_contract.py` (new) | add route-level tests: missing session + active claim still fails `STATION_SESSION_REQUIRED`/session errors | prove claim cannot bypass session guard |
| `backend/tests/test_execution_route_claim_guard_removal_contract.py` (new) | add route-level tests: conflicting claim owner does not block with valid session | prove claim conflict not authoritative in route subset |
| `backend/tests/test_station_session_command_guard_enforcement.py` | keep current seven-command service guard assertions green | ensure StationSession guard remains authoritative |
| `backend/tests/test_claim_api_deprecation_lock.py` | no behavior change expected; keep green | ensure claim API compatibility/deprecation unchanged |
| `backend/tests/test_station_queue_session_aware_migration.py` | no behavior change expected; keep green | ensure queue compatibility unchanged |
| `backend/tests/test_reopen_resume_station_session_continuity.py` | keep green, no scope change | ensure reopen/resume boundaries unchanged |
| `backend/tests/test_close_operation_command_hardening.py` and `backend/tests/test_close_reopen_operation_foundation.py` | keep unchanged and green | guard close/reopen non-scope behavior |
| full backend suite | run after H4 implementation | confirm no hidden regressions |

Minimum pre-merge H4 test gate:
1. New route-removal contract tests (7 commands)
2. `test_station_session_command_guard_enforcement.py`
3. `test_claim_api_deprecation_lock.py`
4. `test_station_queue_session_aware_migration.py`
5. `test_reopen_resume_station_session_continuity.py`
6. command hardening suites for start/pause/resume/report/downtime/complete
7. full backend suite

## 8. H4 Implementation Scope Proposal

Proposed next implementation slice:
- `P0-C-08H4 Backend Execution Route Claim Guard Removal for StationSession-Enforced Commands`

In scope:
- remove route-level `ensure_operation_claim_owned_by_identity` calls only for the approved seven execution routes
- keep service-level StationSession guards unchanged
- keep claim API routes unchanged
- keep claim service/model/table unchanged
- add/update tests per Section 7

Out of scope:
- close/reopen StationSession policy changes
- claim API route removal
- claim service removal
- claim model/table removal
- DB migrations
- queue backend changes
- frontend changes

| Area | H4 Action | Files Likely Affected | Risk |
|---|---|---|---|
| operations route guards | remove route-level claim guard calls from 7 endpoints only | `backend/app/api/v1/operations.py` | MEDIUM |
| claim compatibility APIs | no changes | `backend/app/api/v1/station.py`, `backend/app/services/station_claim_service.py` | LOW |
| close/reopen paths | no changes | `backend/app/api/v1/operations.py`, `backend/app/services/operation_service.py` | LOW |
| route-level contract tests | add new tests for no-claim success path and no-session fail path | `backend/tests/test_execution_route_claim_guard_removal_contract.py` | MEDIUM |
| regression suites | update only if assumptions changed by route-guard removal | targeted existing test files | MEDIUM |

## 9. Close / Reopen Decision

Decision:
- `close_operation` claim guard removal in H4: no (not applicable; no route claim guard exists there today)
- `reopen_operation` claim guard removal in H4: no (not applicable; no route claim guard exists there today)
- Add StationSession enforcement to close/reopen in H4: no
- Keep close/reopen for separate future contract slice: yes

Rationale:
- 08C explicitly deferred close/reopen StationSession enforcement.
- `reopen_operation` still interacts with claim continuity compatibility helper in service (`_restore_claim_continuity_for_reopen`), and 08E only made conflict-path behavior non-blocking, not claim-independent.
- Existing tests explicitly lock close/reopen behavior as unchanged without StationSession requirement.

## 10. Remaining Claim Removal Blockers After H4

| Blocker | Current Evidence | Resolved by H4? | Future Slice |
|---|---|---:|---|
| claim APIs still active (deprecated only) | 08F locks deprecation headers but routes remain callable | no | H5/H6 |
| claim service still used by station APIs/queue/reopen compatibility | `station_claim_service` and `_restore_claim_continuity_for_reopen` active | no | H5/H6 |
| claim data/audit retention unresolved | 08G readiness marks retention decision pending | no | H6 |
| claim route removal pending | no route removals approved in H4 | no | H5/H6 |
| claim table/code removal pending | no migration/removal approved | no | H6/H7 |
| close/reopen StationSession policy still deferred | tests and contracts keep behavior unchanged | no | separate close/reopen contract slice |

## 11. Recommendation

Proceed with H4 as a strict subset implementation:
- remove route-level claim guard calls only for the seven StationSession-enforced execution routes
- do not touch close/reopen, claim API routes, queue compatibility payload, claim service/model/table, or migrations
- add explicit route-level contract tests proving claim no longer authorizes/blocks those seven routes

Direct answers required by this contract:
1. Routes still calling `ensure_operation_claim_owned_by_identity`: seven execution routes (start, pause, resume, report_quantity, start_downtime, end_downtime, complete)
2. Equivalent StationSession guard coverage exists for those seven commands (route + service)
3. Safe next-removal set: those seven commands only
4. Not removable in this slice: close/reopen policy paths (separate contract)
5. Post-removal behavior: StationSession/state guards authoritative; claim cannot authorize or block approved subset
6. Tests to update: new route-level contract tests + existing guard/claim/queue/reopen regressions (Section 7)
7. Exact safe H4 scope: subset route-guard removal only (Section 8)
8. Claim API removal required for route guard removal: no
9. Claim service/table/model removal required for route guard removal: no
10. `close_operation` ready for StationSession guard enforcement now: deferred (not approved in H4)

## 12. Final Verdict

`READY_FOR_P0_C_08H4_ROUTE_GUARD_REMOVAL_SUBSET`
