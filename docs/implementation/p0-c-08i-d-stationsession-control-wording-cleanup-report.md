# P0-C-08I-D StationSession Control Wording Cleanup Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: SINGLE-SLICE IMPLEMENTATION
- Hard Mode MOM: v3
- Reason: Remove transitional StationSession ownership migration labels and clean active-source wording while preserving queue/runtime semantics and API compatibility.

## 1. Preflight Workspace Safety

### Dirty-file classification
| Scope | Result | Action |
|---|---|---|
| Workspace wide | Dirty (large existing churn including `.venv` bytecode, CI files, tests, docs, temp artifacts) | Ignore unrelated files; do not revert |
| H08I-D primary target files | Clean except 3 tests | Proceed with scoped edits |
| Dirty target tests | `backend/tests/test_station_queue_active_states.py`, `backend/tests/test_reopen_resumability_claim_continuity.py`, `backend/tests/test_reopen_resume_station_session_continuity.py` | Existing dirty hunks are separable (`db.rollback()` additions only); no isolation block |

### Required doc/input read status
- Read: `.github/copilot-instructions.md`, `.github/agent/AGENT.md`
- Read: `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`, `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- Read addenda: design-md + hard-mode v2 + hard-mode v3 addenda
- Missing optional prompt: `.github/prompts/flezibcg-ai-brain-v6-auto-execution.prompt.md`
- Read authoritative governance/design inputs required by entry rule and H08I-D scope

## 2. Hard Mode MOM v3 Gate (Before Coding)

### Design Evidence Extract
| Evidence | Source | Conclusion |
|---|---|---|
| Backend is execution/authorization truth | `docs/governance/CODING_RULES.md` | Wording cleanup must not alter backend guard semantics |
| Session-owned execution is target model | `docs/design/02_domain/execution/*`, `docs/governance/ENGINEERING_DECISIONS.md` | Ownership wording should reflect StationSession control, not claim migration |
| Queue projection is required read model | `backend/app/services/station_queue_service.py`, `backend/app/schemas/station.py`, `frontend/src/app/api/stationApi.ts` | Keep `ownership` object for compatibility; remove only transitional labels |
| Transitional labels are compatibility debt | H08I-C contract + active-source sweep | `ownership_migration_status` and `TARGET_SESSION_OWNER` are removable with synchronized BE/FE/tests |
| UI must remain intent-only | `docs/design/00_platform/product-business-truth-overview.md`, `docs/design/DESIGN.md` | Wording updates allowed; frontend must not become execution truth |

### Ownership / Session-Control Reference Map
| Reference | File(s) | Decision |
|---|---|---|
| `ownership` queue projection object | backend schema/service + frontend queue consumers | KEEP |
| `ownership_migration_status` field | backend payload/schema + TS type + tests | REMOVE |
| `TARGET_SESSION_OWNER` literal | backend payload + tests | REMOVE |
| Ownership-heavy comments/labels | station queue components, execution page, session page, i18n text values | RENAME TO SESSION-CONTROL WORDING |

### Migration Label Cleanup Map
| Label | Current Location | Cleanup Action |
|---|---|---|
| `ownership_migration_status` | `backend/app/services/station_queue_service.py`, `backend/app/schemas/station.py`, `frontend/src/app/api/stationApi.ts`, queue tests | Delete field and assertions |
| `TARGET_SESSION_OWNER` | backend payload + tests | Delete literal usage |

### API Compatibility Boundary Map
| Contract Surface | Action | Why |
|---|---|---|
| `StationQueueItem.ownership` | Keep shape except transitional field removal | Preserve existing queue/session-control semantics |
| `target_owner_type`, `owner_state`, `has_open_session`, `session_id`, `station_id`, `session_status`, `operator_user_id` | Keep | Used by FE readiness/lock rendering and tests |
| Command guard behavior | No changes | Out of scope; guarded by backend invariants |

### UI / Frontend Wording Map
| Area | Action |
|---|---|
| Queue + execution comments/variables | Replace ownership-migration framing with session-control framing |
| Operator-facing text values (`station.ownership.*`, queue hints) | Update value text to session-control language; keep keys for compatibility |
| Session page governance message | Replace ownership wording with session-control wording |

### Event Map
- No new command/event introduced.
- No event name/status changes.

### Invariant Map
| Invariant | Status |
|---|---|
| Backend truth for execution and authorization | Preserved |
| StationSession command guard enforcement | Preserved |
| Queue projection remains read-model only | Preserved |
| Frontend remains intent-only consumer | Preserved |

### State Transition Map
- No state transition change in this slice.
- Existing operation/session state machine and command legality remain unchanged.

### Test Matrix (planned)
- `backend/tests/test_station_queue_active_states.py`
- `backend/tests/test_station_queue_session_aware_migration.py`
- `backend/tests/test_reopen_resumability_claim_continuity.py`
- `backend/tests/test_reopen_resume_station_session_continuity.py`
- `backend/tests/test_start_downtime_auth.py`
- Backend import smoke
- Frontend: lint, build, route smoke
- Post-cleanup ownership/migration label sweep

## Verdict Before Coding
`ALLOW_IMPLEMENTATION`

## 3. Implementation Changes

### Backend
- Removed transitional label from queue projection payload:
	- `backend/app/services/station_queue_service.py`
		- deleted `ownership.ownership_migration_status`
- Removed transitional schema field:
	- `backend/app/schemas/station.py`
		- deleted `SessionOwnershipSummary.ownership_migration_status`
- Updated session-control wording in backend comments only (no behavior change):
	- `backend/app/services/operation_service.py`
	- `backend/app/schemas/operation.py`

### Frontend
- Removed transitional type field:
	- `frontend/src/app/api/stationApi.ts`
		- deleted `SessionOwnershipSummary.ownership_migration_status`
- Updated active-source wording from ownership-migration framing to session-control framing:
	- `frontend/src/app/components/station-execution/StationQueuePanel.tsx`
	- `frontend/src/app/components/station-execution/QueueOperationCard.tsx`
	- `frontend/src/app/components/station-execution/StationExecutionHeader.tsx`
	- `frontend/src/app/pages/StationExecution.tsx`
	- `frontend/src/app/pages/StationSession.tsx`
- Updated operator-facing EN/JA text values while preserving key compatibility:
	- `frontend/src/app/i18n/registry/en.ts`
	- `frontend/src/app/i18n/registry/ja.ts`

### Tests
- Removed transitional label assertions:
	- `backend/tests/test_station_queue_active_states.py`
	- `backend/tests/test_station_queue_session_aware_migration.py`
- Updated migration-test module wording (comment/docstring only):
	- `backend/tests/test_station_queue_session_aware_migration.py`

### Explicitly Preserved Boundaries
- Kept `ownership` queue projection field and runtime semantics.
- No command guard behavior changes.
- No queue status/state-machine changes.
- No API route contract changes.
- No migration-history edits.

## 4. Verification Results

### Required command results
- Backend import smoke:
	- `H08ID_BACKEND_IMPORT_OK True`
- Focused backend regression suite:
	- `23 passed in 10.27s`
	- command:
		- `tests/test_station_queue_active_states.py`
		- `tests/test_station_queue_session_aware_migration.py`
		- `tests/test_reopen_resumability_claim_continuity.py`
		- `tests/test_reopen_resume_station_session_continuity.py`
		- `tests/test_start_downtime_auth.py`
- Frontend lint:
	- `npm.cmd run lint` completed with no ESLint violations
- Frontend build:
	- `npm.cmd run build` passed (`built in 8.27s`)
- Frontend route accessibility smoke:
	- `PASS: 24`
	- `FAIL: 0`
	- `77/78 covered`, `1 excluded` (`REDIRECT_ONLY`)

### Post-cleanup sweep results
- Transitional label sweep (direct H08I-D targets):
	- `H08ID_TARGET_TRANSITIONAL_LABEL_MATCHES:0`
- Legacy wording sweep (direct active-source wording set):
	- `H08ID_LEGACY_WORDING_MATCHES:0`

## 5. Final Verdict

`P0_C_08I_D_COMPLETE_VERIFICATION_CLEAN`
