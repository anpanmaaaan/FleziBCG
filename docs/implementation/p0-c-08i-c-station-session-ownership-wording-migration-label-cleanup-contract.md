# P0-C-08I-C StationSession Ownership Wording / Migration Label Cleanup Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-03 | v1.0 | Defined cleanup contract for StationSession ownership wording and migration-era labels after claim active-source purge. |

## 1. Executive Summary
This is a review-only contract slice. No backend/frontend behavior changes are implemented here.

Decisions:
- Keep StationSession control invariants and backend command guard semantics unchanged.
- Keep queue projection field `ownership` for now (non-breaking path).
- Mark `ownership_migration_status` and literal `TARGET_SESSION_OWNER` as transitional labels and candidates for removal in H08I-D.
- Move operator-facing wording from ownership-heavy language toward session/control language.
- Defer any breaking API rename (`ownership` -> `session_control`) to a separate compatibility contract slice.

Verdict before recommendation: `ALLOW_CONTRACT_REVIEW`

## 2. Scope Reviewed
Mandatory instruction files read in this session:
- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`

Optional addenda inspected:
- `.github/copilot-instructions-design-md-addendum.md`
- `.github/copilot-instructions-hard-mode-mom-v2-addendum.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `.github/prompts/flezibcg-ai-brain-v6-auto-execution.prompt.md` (missing)

Required implementation/design sources reviewed:
- All requested H13/H14B/H15B/H16B/H16C/H17/H08I/H08I-B reports and trackers
- `docs/design/02_domain/execution/*` contracts requested
- `docs/design/00_platform/product-business-truth-overview.md`
- Requested `docs/design/00_platform/system-invariants.md` was missing; closest canonical source used: `docs/design/00_platform/system-overview-and-target-state.md`
- Requested `docs/design/00_platform/canonical-api-contract.md` was missing; closest canonical source used: `docs/design/05_application/canonical-api-contract.md`

Source sweep artifacts generated:
- `h08ic_ownership_reference_sweep.txt` (`H08IC_OWNERSHIP_REFERENCE_MATCHES:299`)
- `h08ic_target_file_ownership_map.txt` (`H08IC_TARGET_FILE_OWNERSHIP_MATCHES:109`)
- `h08ic_backend_tests_ownership_refs.txt` (`H08IC_BACKEND_TEST_OWNERSHIP_REFS:28`)

## 3. Hard Mode Gate Evidence

### Design Evidence Extract
| Evidence | Source | Conclusion |
|---|---|---|
| Session-owned execution is target truth | `docs/design/02_domain/execution/station-session-ownership-contract.md`, `docs/design/02_domain/execution/station-execution-state-matrix-v4.md` | Ownership/control must remain backend-derived from StationSession context. |
| Claim retired from active source | `docs/implementation/p0-c-08i-b-active-claim-source-purge-report.md` | Claim is no longer active runtime path. |
| Ownership is not claim | `docs/design/INDEX.md`, `docs/design/00_platform/product-business-truth-overview.md` | Ownership terms now represent StationSession-derived control, not claim compatibility. |
| Queue needs ownership/control projection | `backend/app/services/station_queue_service.py`, `backend/app/schemas/station.py` | Queue readiness/locking display depends on projection block. |
| Frontend cannot be truth source | `docs/governance/CODING_RULES.md`, `docs/design/00_platform/system-overview-and-target-state.md` | UI wording cleanup must not shift authority from backend. |
| Backend command guards remain authoritative | `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md`, `backend/app/services/operation_service.py` | No guard/behavior change in this contract. |
| `ownership_migration_status` appears transitional | `backend/app/services/station_queue_service.py`, `backend/app/schemas/station.py`, queue migration tests | Candidate removal in H08I-D if tests/contracts updated together. |
| H08I-C is contract-only | User scope + this document | No implementation edits to runtime logic. |

### Ownership / Session-Control Reference Map
| Reference | File | Category | Keep / Rename / Remove / Defer | Reason | Risk |
|---|---|---|---|---|---|
| `ownership` object in queue payload | `backend/app/services/station_queue_service.py` | BACKEND_QUEUE_PROJECTION | Keep | Carries session readiness/owner state for queue UX and command gating context explanation. | High if removed |
| `ownership_migration_status` | `backend/app/services/station_queue_service.py` | BACKEND_TRANSITIONAL_LABEL | Remove in H08I-D | Transitional migration tag; no runtime guard dependency. | Medium |
| `TARGET_SESSION_OWNER` literal | `backend/app/services/station_queue_service.py` | BACKEND_TRANSITIONAL_LABEL | Remove in H08I-D | Transitional marker only. | Medium |
| `SessionOwnershipSummary.ownership_migration_status` | `backend/app/schemas/station.py` | BACKEND_TRANSITIONAL_LABEL | Remove in H08I-D | Schema-level transitional field. | Medium |
| `StationQueueItem.ownership` | `backend/app/schemas/station.py` | BACKEND_RUNTIME_INVARIANT | Keep | API compatibility + UI lock/readiness semantics rely on it. | High if removed |
| ownership comments in operation service/schema | `backend/app/services/operation_service.py`, `backend/app/schemas/operation.py` | BACKEND_COMMENT_ONLY | Rename wording | Clarify session-control semantics; avoid migration-era phrasing. | Low |
| ownership status i18n errors | `backend/app/i18n/messages_en.py`, `backend/app/i18n/messages_ja.py` | BACKEND_I18N | Rename values only (later) | Can be operator-friendlier without changing keys immediately. | Low |
| `SessionOwnershipSummary` TS type | `frontend/src/app/api/stationApi.ts` | FRONTEND_RUNTIME_TYPE | Keep, but deprecate migration label field | Needed by queue rendering and type safety. | High if removed now |
| `ownership_migration_status` TS field | `frontend/src/app/api/stationApi.ts` | FRONTEND_RUNTIME_TYPE | Remove in H08I-D with backend/schema sync | Transitional and non-functional. | Medium |
| ownership-driven queue filtering/lock display | `frontend/src/app/components/station-execution/StationQueuePanel.tsx`, `frontend/src/app/components/station-execution/QueueOperationCard.tsx` | FRONTEND_UI_WORDING | Keep logic, rename visible wording | Core UX signal for in-use/ready states. | Medium |
| ownership badge text keys | `frontend/src/app/i18n/registry/en.ts`, `frontend/src/app/i18n/registry/ja.ts` | FRONTEND_UI_WORDING | Rename wording in H08I-D | Operator-facing language can be clearer. | Low |
| ownership assertions in queue migration tests | `backend/tests/test_station_queue_active_states.py`, `backend/tests/test_station_queue_session_aware_migration.py` | TEST_ASSERTION | Update in H08I-D | Must align with field cleanup if transitional labels removed. | Medium |
| session-owned execution guidance in design docs | `docs/design/**` | DESIGN_CONTRACT | Keep | Canonical target direction. | None |

### Event Map (contract impact)
| Command / Action | Required Event | Event Type | Payload Minimum | Projection Impact | Source |
|---|---|---|---|---|---|
| H08I-C contract review | none | none_required | n/a | none | contract-only slice |
| Future H08I-D wording cleanup | none expected for wording-only | none_required | n/a | read-model labels only | this contract |

### Invariant Map
| Invariant | Category | Enforcement Layer | DB Constraint Needed? | Test Required | Source |
|---|---|---|---:|---|---|
| Backend is execution truth | authorization / execution | backend service + route | No | Yes | `docs/governance/CODING_RULES.md` |
| Frontend not ownership truth | authorization | UX boundary | No | Yes | `docs/design/00_platform/system-overview-and-target-state.md` |
| Session context required for guarded execution commands | state_machine | service guard | No | Yes | `docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md` |
| Queue ownership projection must remain until compatible replacement exists | projection_consistency | backend + frontend contract | No | Yes | `backend/app/schemas/station.py`, `frontend/src/app/api/stationApi.ts` |
| Transitional labels can be removed if no behavior dependency | migration_boundary | schema/API/read model contract | No | Yes | sweep + tests inventory |

### State Transition Map (stateful reference, no change in H08I-C)
| Entity | Current State | Command | Allowed? | Event | Next Projection State | Invalid Case Test | Source |
|---|---|---|---:|---|---|---|---|
| Execution operation | PLANNED/IN_PROGRESS/PAUSED/BLOCKED | guarded execution commands | yes per existing guards | existing execution events only | unchanged | existing queue/session guard tests | `docs/design/02_domain/execution/station-execution-state-matrix-v4.md` |
| Reopen/close path | CLOSED/OPEN closure axis | reopen/close | unchanged in this slice | existing reopen/close events | unchanged | reopen continuity tests | same |

### Test Matrix
| Test / Check | Purpose | Required for H08I-D? |
|---|---|---|
| `backend/tests/test_station_queue_active_states.py` | queue projection contract | Yes |
| `backend/tests/test_station_queue_session_aware_migration.py` | transitional ownership field assertions | Yes |
| `backend/tests/test_reopen_resumability_claim_continuity.py` | reopen/resume continuity semantics | Yes (regression) |
| `backend/tests/test_reopen_resume_station_session_continuity.py` | session guard continuity after reopen | Yes |
| `backend/tests/test_start_downtime_auth.py` | auth/session enforcement remains | Yes |
| frontend lint/build/routes | wording/key integrity and route safety | Yes |
| active wording/reference sweep | detect leftover migration labels | Yes |
| backend import smoke | service import safety | Yes |

Verdict before recommendation: `ALLOW_CONTRACT_REVIEW`

## 4. Ownership / Session-Control Reference Map
| Reference Family | Current Usage | Decision |
|---|---|---|
| Runtime `ownership` block | Queue item projection and UI lock/availability display | Keep |
| `owner_state`, `has_open_session`, `session_id`, `operator_user_id` | Runtime status context | Keep |
| `ownership_migration_status` | Transitional metadata string in payload/schema/tests | Remove in H08I-D |
| `TARGET_SESSION_OWNER` | Transitional literal asserted in tests | Remove in H08I-D |
| Ownership-heavy UI labels | i18n and comments in queue/execution screens | Rename in H08I-D |

## 5. Migration Label / Legacy Wording Map
| Label / Wording | Current Usage | Is Transitional? | H08I-D Action | Risk |
|---|---|---|---|---|
| `ownership_migration_status` | backend payload + schema + TS type + tests | Yes | Remove field and all assertions | Medium |
| `TARGET_SESSION_OWNER` | payload literal and test assertions | Yes | Remove literal usage | Medium |
| phrase `migration` in ownership comments | comments/docs around queue migration | Usually yes in active source | Rename to stable StationSession semantics | Low |
| `claim fallback retired` comments | FE component comments | Yes | Remove migration framing | Low |
| `ownership migration` phrasing | mixed comments/docs | Yes | Replace with StationSession control projection language | Low |
| `claim retired` phrasing | design/history docs | Historical | Keep in historical docs, avoid in active UX copy | Low |
| `owned by me` / `owned by another` | operator-facing queue labels | No (runtime meaning), but wording can improve | Rename to "My active session" / "In use by another operator" | Low |
| `ownership` operator-facing labels | badges/hints/errors | Partly | Rename toward "session control" / "active session" | Low |

## 6. API Shape Compatibility Map
| API Field | Current Consumer | Rename Now? | Recommended Action | Risk |
|---|---|---|---|---|
| `ownership` | backend queue response, frontend queue cards/panel/execution page, queue tests | No | Keep in H08I-D | High breaking risk |
| `ownership.target_owner_type` | queue tests and frontend typings | No | Keep (or freeze constant) | Low |
| `ownership.owner_state` | frontend mode selection and lock display | No | Keep | High if removed |
| `ownership.has_open_session` | frontend `canExecute`/filter logic | No | Keep | High if removed |
| `ownership.session_id` | tests/diagnostics/context display potential | No | Keep | Medium |
| `ownership.operator_user_id` | tests and ownership interpretation | No | Keep | Medium |
| `ownership_migration_status` | schema + TS + tests only | No field rename; remove instead | Remove in H08I-D with coordinated test/type cleanup | Medium |
| Future `session_control` replacement field | none today | Not in H08I-D | Defer to H08I-E contract-only compatibility slice | Medium/High |

## 7. UI / Frontend Wording Map
| UI Text / Key / Variable | Current Wording | Recommended Wording | H08I-D Candidate? |
|---|---|---|---|
| `station.ownership.ownedBadge` | Owned by your session | My active session | Yes |
| `station.queue.ownedByOther` | Owned by another operator session | In use by another operator | Yes |
| `station.ownership.required` | Operator session ownership required | Active station session required | Yes |
| `station.ownership.singleActiveHint` | Finish your active operation before selecting another | Complete or release your active session task before selecting another | Yes |
| `station.ownership.takenWarning` | currently owned by another operator session | currently in use by another operator | Yes |
| `StationExecution` variable `canExecuteByOwnership` | technical internal naming | `canExecuteBySessionControl` (optional internal rename) | Yes (non-breaking internal) |
| header comment `ownership badge` | technical term | `session control badge` | Yes |

## 8. What Must Not Be Removed
| Artifact | Why It Must Stay | Risk If Removed |
|---|---|---|
| StationSession command guard enforcement | Enforces backend ownership truth for execution mutations | Unauthorized/invalid execution writes |
| Queue ownership/control projection block | Explains ready/locked state from backend truth | Queue cannot reliably communicate lock context |
| Backend can-execute/readiness computation | Protects state and identity invariants | Command path regressions and false-positive UI affordances |
| Session/operator context fields in queue | Required for ownership state (`mine/other/none`) | Loss of concurrency explanation and UX safety |
| Frontend lock/availability display (derived from backend) | Prevents operator confusion and accidental conflicts | Ambiguous UI and more rejected commands |

## 9. Cleanup Strategy Options
| Option | Pros | Cons | Risk | Recommendation |
|---|---|---|---|---|
| A. Wording cleanup only | Lowest risk, no API break, immediate clarity | Transitional field still present unless included | Low | **Now** |
| B. Remove `ownership_migration_status` only | Removes obvious migration debt | Leaves broader wording debt | Low/Medium | Include inside A |
| C. Rename API `ownership` -> `session_control` | Terminology purity | Breaking contract across BE/FE/tests | Medium/High | Defer to H08I-E |
| D. Remove ownership/control projection | Eliminates term entirely | Breaks queue and readiness semantics | High | Reject |
| E. Keep everything unchanged | No immediate effort | Ongoing product confusion | Medium | Reject |

Recommended: Option A now, including B as part of A. Defer C. Reject D and E.

## 10. H08I-D Implementation Scope Proposal
Proposed next slice: `P0-C-08I-D StationSession Control Wording Cleanup Implementation`

In scope:
- Remove `ownership_migration_status` and `TARGET_SESSION_OWNER` from backend payload/schema/frontend type/tests if no runtime dependency remains.
- Rewrite active-source comments from migration framing to StationSession-native framing.
- Update operator-facing i18n wording from ownership-heavy labels to session/control labels.
- Update tests asserting transitional labels.
- Keep API field `ownership` and runtime semantics unchanged.

Out of scope:
- No rename of `ownership` API field.
- No command guard behavior changes.
- No queue semantic changes.
- No migration/history file edits.

## 11. Optional Future API Rename Slice
Proposed contract-only follow-up: `P0-C-08I-E Queue Ownership Field Rename Contract`

Purpose:
- Evaluate whether `ownership` should become `session_control` or `execution_control`.
- Define compatibility/versioning strategy for a breaking API shape change.
- Coordinate backend/frontend/tests in one governed rollout.

## 12. Test Strategy
| Test / Check | Why | Run in H08I-C |
|---|---|---|
| Backend import smoke | Ensure queue service import remains stable | Yes |
| Frontend lint | Ensure no pre-existing issues before contract recommendation | Yes |
| Frontend build | Ensure FE baseline is healthy | Yes |
| Frontend routes smoke | Ensure route registry unaffected | Yes |
| Optional backend queue pytest | Detect environment gating status | Optional (only if stable) |
| Ownership reference sweep | Evidence for label cleanup map | Yes |

## 13. Risk Register
| Risk | Impact | Mitigation |
|---|---|---|
| Removing `ownership` now | High FE/BE/test breakage | Keep field in H08I-D |
| Removing migration labels without test updates | Medium CI failures | Update queue migration tests in same slice |
| UI wording changes drift from backend truth | Medium operator confusion | Keep semantics backend-derived; wording only |
| Hidden dependency on `ownership_migration_status` | Medium runtime/type break | run grep + strict TS + tests before merge |
| Environment DB lock on pytest | Verification delay | keep optional; do not block wording-contract verdict |

## 14. Recommendation
- Proceed with `P0-C-08I-D StationSession Control Wording Cleanup Implementation`.
- Keep runtime StationSession ownership/control invariants and queue projection.
- Remove transitional labels (`ownership_migration_status`, `TARGET_SESSION_OWNER`) if accompanied by synchronized test/type updates.
- Keep `ownership` API field for now.
- Defer API rename decision to H08I-E contract.

## 15. Final Verdict
`READY_FOR_P0_C_08I_D_STATIONSESSION_CONTROL_WORDING_CLEANUP`
