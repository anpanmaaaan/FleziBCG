# P0-C-08H5 Claim Retirement Sequencing Contract (Review Only)

Date: 2026-05-01
Scope: Contract, sequencing, and readiness review only.
Change type: No runtime implementation.

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: Review/Contract Sequencing
- Hard Mode MOM: v3 (decision and sequencing safety gate)
- Reason: This slice touches governed execution contracts (claim compatibility, station session ownership projection, reopen continuity, audit retention) and requires invariant-safe retirement sequencing before any destructive removal.

## Hard Constraints Applied
- No backend implementation changes.
- No frontend implementation changes.
- No API removal.
- No model/table/migration changes.
- No station queue behavior changes.
- No command behavior changes.
- No close/reopen behavior changes.

## Design Evidence Extract
- Station claim compatibility APIs remain active with explicit deprecation headers and StationSession replacement signaling in backend route layer.
- Queue payload currently carries dual-shape compatibility: claim plus ownership block with migration marker TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT.
- Execution command routes are station-session guarded for the H4 command set; route-level claim guard is already removed.
- Reopen flow still invokes claim continuity compatibility helper and can emit CLAIM_RESTORED_ON_REOPEN audit events.
- Claim persistence and audit persistence are still first-class schema artifacts with foreign key relations.
- Frontend station execution path is ownership-first but still calls deprecated claim/release APIs and still consumes claim compatibility fields in queue/UI components.

## Event Map (Claim-Retirement Relevant)
| Event | Source | Current Role in System | Retirement Impact |
|---|---|---|---|
| CLAIM_CREATED | station_claim_service | Claim compatibility ownership marker and trace | Must remain until claim API retirement cutover is complete |
| CLAIM_RELEASED | station_claim_service | Compatibility release lifecycle trace | Must remain while claim endpoints still callable |
| CLAIM_EXPIRED | station_claim_service | Auto-expiry compatibility trace | Must remain while claim runtime table exists |
| CLAIM_RESTORED_ON_REOPEN | operation_service reopen helper | Compatibility continuity bridge for reopen path | Must be sequenced behind reopen continuity replacement |
| OPERATION_REOPENED | operation_service | Canonical execution event (source of truth) | Must remain unchanged |

## Invariant Map
| Invariant | Current Enforcement | Risk if Removed Too Early |
|---|---|---|
| Backend is execution source of truth | operation_service + event log | Frontend drift if compatibility removed without contract updates |
| StationSession gates execution commands | ensure_open_station_session_for_command | Command accessibility regressions if sequencing mixes concerns |
| Queue remains additive migration contract | queue returns ownership plus claim compatibility | Consumer breakage if claim fields dropped before frontend/API clients are cut over |
| Reopen remains resumable after closure | reopen helper currently restores/extends claim continuity compatibility | Resume path regressions in legacy claim-dependent scenarios |
| Audit traceability remains queryable | operation_claim_audit_logs linked to operation_claims | Compliance/reporting risk if table removed before retention decision |

## State Transition Map (Retirement-Relevant)
| Flow | Current Compatibility Coupling | Required Replacement Before Removal |
|---|---|---|
| Station queue selection readiness | claim.state fallback still present in backend payload and frontend filter/display | Ownership-only UI and payload contract finalized and deployed |
| Claim/release operations | Deprecated endpoints still functional | StationSession intent workflow fully replaces claim interactions |
| Reopen continuity | claim restoration helper can recreate active claim | Session-based reopen resumability continuity contract and tests |
| Audit lookback | claim audit log references claim rows | Explicit retention/archive strategy with schema-safe migration plan |

## Remaining Surface Inventory
| Surface | File Area | Current Status | Blocker Class |
|---|---|---|---|
| Claim compatibility endpoints | backend api station routes | Active + deprecated headers | External/API compatibility |
| Claim service ops and guard helper | station_claim_service | Active | Runtime compatibility |
| Queue claim payload block | station_claim_service and station schema | Active | Payload compatibility |
| Reopen claim continuity helper | operation_service | Active | Execution continuity |
| Claim tables and audit tables | model and migration layer | Active | Data retention/governance |
| Frontend claim API client methods | stationApi client | Active | Consumer compatibility |
| Frontend claim actions in StationExecution | StationExecution page | Active | UX/intent compatibility |
| Frontend claim fallback rendering | queue panel and card | Active | Compatibility rendering |

## Claim API Readiness Table
| Criterion | Evidence | Status |
|---|---|---|
| Deprecated headers published | claim/release/status routes return Deprecation + replacement headers | Ready |
| Replacement path exists | StationSession endpoints and command gating already in place | Partially Ready |
| Consumers no longer call claim APIs | frontend StationExecution still calls claim and release | Not Ready |
| API lock tests present | dedicated deprecation lock suite exists | Ready |

Readiness verdict: Not ready for removal; compatibility API must remain through H6.

## Queue Payload Readiness Table
| Criterion | Evidence | Status |
|---|---|---|
| Ownership block contract present | queue includes ownership fields and migration marker | Ready |
| Legacy claim shape preserved | queue still returns claim block | Ready (compat mode) |
| Frontend ownership-first adopted | queue panel/card use ownership first with claim fallback | Partially Ready |
| Frontend claim fallback removed | fallback logic still present | Not Ready |

Readiness verdict: Not ready for claim-block removal from queue payload; requires H7 consumer cutover then lock.

## Reopen Compatibility Readiness Table
| Criterion | Evidence | Status |
|---|---|---|
| Reopen command remains stable | reopen route/service behavior intact | Ready |
| Resume guarded by StationSession | resume enforces station session guard | Ready |
| Claim restoration still active | _restore_claim_continuity_for_reopen still invoked | Compatibility Active |
| Replacement continuity finalized | no ownership/session-native reopen replacement yet | Not Ready |

Readiness verdict: Not ready to remove reopen claim continuity compatibility in H5.

## Audit Retention Decision Table
| Decision Topic | Current State | Required Contract Decision |
|---|---|---|
| operation_claim_audit_logs lifecycle | Active table with claim_id FK | Decide retention horizon and access requirements |
| operation_claims dependency | audit rows can reference claim rows | Define whether claim rows are archived, tombstoned, or retained |
| Compliance trace obligations | No retirement decision encoded yet | Governance sign-off required before destructive schema changes |
| Migration ordering | No drop/transform plan accepted | Must be last stage after API and runtime retirement |

Retention verdict: Undecided. This blocks any table removal approval.

## Option Analysis
| Option | Description | Benefits | Risks | Verdict |
|---|---|---|---|---|
| A | Remove claim APIs immediately after H4 | Fast surface reduction | Breaks frontend and dependent consumers | Reject |
| B | Remove queue claim block first | Simplifies payload | Breaks compatibility while claim APIs still exposed | Reject |
| C | Remove reopen claim continuity first | Shrinks service coupling | Risks resumability regressions in compatibility paths | Reject |
| D | Keep all claim surfaces indefinitely | Zero short-term risk | Permanent complexity and migration stall | Reject |
| E | Staged retirement with explicit gates (H6-H9+) | Controlled risk and measurable readiness | Requires disciplined sequencing and lock tests | Accept |

Selected option: E.

## Recommended H6-H9+ Roadmap
| Slice | Goal | Allowed Change Type | Exit Gate |
|---|---|---|---|
| H6 | Frontend/API consumer cutover away from claim/release calls | Frontend + client contract updates only; keep backend compat active | No claim API invocations in StationExecution path; deprecation tests still pass |
| H7 | Queue payload consumer hard cut to ownership-only usage | Frontend logic cleanup + compatibility lock tests | No claim fallback usage in queue render/filter code |
| H8 | Reopen continuity replacement to StationSession-native behavior | Backend service logic change with MOM v3 artifacts and tests | Reopen/resume continuity proven without claim restoration |
| H9+ | Claim runtime and audit retirement (if approved) | Backend schema and migration work | Signed retention decision, archive strategy, and migration dry-run evidence |

## Test Strategy Table (Review-Safe)
| Test Suite | Purpose | Result |
|---|---|---|
| test_execution_route_claim_guard_removal | Confirms H4 route-level claim guard removal with station session enforcement intact | Pending run in this H5 review |
| test_claim_api_deprecation_lock | Locks claim endpoint deprecation headers and queue non-deprecated behavior | Pending run in this H5 review |
| test_station_queue_session_aware_migration | Locks queue additive ownership contract with claim compatibility | Pending run in this H5 review |
| test_reopen_resume_station_session_continuity | Locks station-session continuity after reopen | Pending run in this H5 review |

## Risk Register
| Risk ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | Consumer break from early claim API removal | High | H6 first: remove frontend/API consumer dependency before backend removal |
| R2 | Queue contract break from dropping claim block early | High | H7 ownership-only consumer cutover and contract lock tests |
| R3 | Reopen resumability regression if claim continuity removed early | High | H8 dedicated replacement with continuity tests |
| R4 | Audit/compliance gap from premature schema deletion | High | H9+ only after explicit retention governance decision |
| R5 | Mixed-mode migration drift across teams | Medium | Stage gates and mandatory lock suites per slice |

## Recommendation
Proceed with staged contract option E.

- H5 remains review-only and makes no runtime change.
- H6 should target frontend/API consumer cutover first while keeping compatibility APIs intact.
- H7 should complete ownership-only queue consumption and remove claim fallback usage in UI.
- H8 should replace reopen claim continuity compatibility with StationSession-native continuity logic.
- H9+ may consider claim table/audit retirement only after retention decision is approved.

## Final Verdict
H5 verdict: Contract accepted for staged retirement, with removal blocked in this slice.

Retirement approval matrix:
- Claim API removal now: No
- Queue claim payload removal now: No
- Reopen claim continuity removal now: No
- Claim/audit schema removal now: No

Advancement gate:
- Next implementation slice should be H6 (consumer cutover) under controlled compatibility mode.
