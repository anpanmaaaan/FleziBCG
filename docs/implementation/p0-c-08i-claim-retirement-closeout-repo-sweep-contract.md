# P0-C-08I Claim Retirement Closeout / Repo Sweep Contract

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Defined final closeout contract for removing claim from active source after ORM/table drop migration. |

---

## 1. Executive Summary

The P0-C-08 claim retirement programme (H10–H17) has successfully removed all runtime claim infrastructure:

- H14B: Claim API routes + frontend claim API client removed.
- H15B: Claim service dead functions + dead route schemas removed.
- H16B: Claim model/table dependencies removed from backend tests.
- H16C: Legacy script claim dependencies removed/rewritten.
- H17: Claim ORM model file deleted, `init_db.py` import removed, Alembic migration `0009_drop_station_claims.py` applied. Tables confirmed absent. Full backend suite: 120 passed, 1 skipped.

**Remaining active-source claim surface** consists of:

1. `station_claim_service.py` filename (hosts active queue logic; claim name is historical)
2. `ClaimSummary` Pydantic class + `StationQueueItem.claim` field in backend schema (frontend type already clean)
3. Backend projects `"claim": None` in queue response (harmless; frontend ignores it)
4. i18n key names with "claim" terminology (`station.claim.*`, `station.queue.readyToClaim`, etc.)
5. `hasMineClaim` variable name in frontend queue components (driven by ownership, not claim data)
6. `CLAIM_API_DISABLED` in canonical error docs (no backend code uses it anymore)
7. Test function/file names referencing "claim" (functional logic is session-based)
8. Historical migration files and implementation docs (kept by convention)

**P0-C-08I-B** can eliminate all active-source claim references cleanly.

---

## 2. Scope Reviewed

- Backend app source: `app/api/`, `app/services/`, `app/schemas/`, `app/models/`, `app/db/`
- Backend tests: all `tests/*.py`
- Backend scripts: `scripts/`, `scripts/seed/`
- Alembic migrations: `alembic/versions/*.py`
- Historical SQL migrations: `scripts/migrations/*.sql`
- Frontend source: `src/app/api/`, `src/app/components/`, `src/app/pages/`, `src/app/i18n/`
- Design docs: `docs/design/**`
- Implementation docs: `docs/implementation/**`
- Canonical error registry: `docs/design/00_platform/`

---

## 3. Hard Mode Gate Evidence

| Fact | Source |
|---|---|
| StationSession is execution ownership truth | `station_claim_service.py:ownership_migration_status = "TARGET_SESSION_OWNER"` |
| Claim API routes absent | `station.py` router — no `/claim`, `/release`, `/claim` routes |
| Frontend claim type absent | `stationApi.ts` — `StationQueueItem` has no `claim` field; no `ClaimSummary` interface |
| Frontend does not read claim data | `QueueOperationCard.tsx`, `StationQueuePanel.tsx` — ownership-only logic post-H8 |
| Claim tables dropped | `alembic current` = 0009; Python inspector confirmed `operation_claims` and `operation_claim_audit_logs` absent |
| H13 approved dev hard drop | `CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED` |
| H17 full suite clean | 120 passed, 1 skipped |

---

## 4. Repo-Wide Claim Reference Map

### Active Backend Source

| Reference | File | Category | Active Source? | H08I-B Action | Risk |
|---|---|---|---|---|---|
| `class ClaimSummary(BaseModel)` | `app/schemas/station.py:6` | ACTIVE_BACKEND_SCHEMA | Yes | Delete class | Low — backend projects `None`; frontend type already clean |
| `claim: ClaimSummary \| None = None` on `StationQueueItem` | `app/schemas/station.py:34` | ACTIVE_BACKEND_SCHEMA | Yes | Remove field | Low — frontend `StationQueueItem` already has no `claim` field |
| `"claim": None` in queue projection dict | `app/services/station_claim_service.py:~175` | ACTIVE_BACKEND_SERVICE | Yes | Remove key | Low — frontend ignores unknown keys |
| `station_claim_service.py` filename | `app/services/station_claim_service.py` | ACTIVE_BACKEND_SERVICE | Yes (name only) | Rename → `station_queue_service.py` | Low — update 1 route import + 3 test imports |
| `from app.services.station_claim_service import ...` | `app/api/v1/station.py:12` | ACTIVE_BACKEND_ROUTE | Yes | Update import | Low |

### Active Frontend Source

| Reference | File | Category | Active Source? | H08I-B Action | Risk |
|---|---|---|---|---|---|
| i18n key `station.claim.ownedBadge` | `en.ts:126`, `ja.ts:153` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Rename key → `station.queue.mine` or keep translated text | Medium — must update all consumers |
| i18n key `station.claim.takenWarning` | `en.ts:125`, `ja.ts:152` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Rename key → `station.queue.takenByOther` | Medium |
| i18n key `station.claim.singleActiveHint` | `en.ts:127`, `ja.ts:154` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Rename key → `station.queue.singleOperatorHint` | Medium |
| i18n key `station.claim.required` | `en.ts:128`, `ja.ts:155` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Rename key → `station.execution.sessionRequired` | Medium |
| i18n key `station.queue.readyToClaim` | `en.ts:110`, `ja.ts:137` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Rename key → `station.queue.available` | Medium |
| i18n key `station.queue.claimedByOther` | `en.ts:109`, `ja.ts:136` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Rename key → `station.queue.takenByOther` | Medium |
| i18n keys `station.action.claim/claiming` | `en.ts:118`, `ja.ts:144-145` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Delete (claim action no longer exists) | Low |
| i18n key `station.toast.claimed/claimFailed` | `en.ts`, `ja.ts` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Delete (claim toast no longer exists) | Low |
| i18n key `station.reject.STATE_REOPEN_OWNER_HAS_OTHER_ACTIVE_CLAIM` | `ja.ts:200` | ACTIVE_FRONTEND_TYPE | Yes (key name) | Rename to session-based key | Medium |
| `hasMineClaim` variable/prop | `QueueOperationCard.tsx:13`, `StationQueuePanel.tsx:48` | ACTIVE_FRONTEND_TYPE | Yes (name only) | Rename → `hasMineSession` | Low |
| `station.claim.ownedBadge` usage | `StationExecutionHeader.tsx:79`, `QueueOperationCard.tsx:35` | ACTIVE_FRONTEND_TYPE | Yes | Update to new i18n key | Low |
| `station.claim.*` usages | `StationExecution.tsx:366,495,569,592,614,641,727,736` | ACTIVE_FRONTEND_TYPE | Yes | Update to new i18n keys | Low |
| comment "compatibility claim model" | `screenStatus.ts:133` | ACTIVE_FRONTEND_TYPE | Yes (comment) | Update comment | Trivial |
| comment "claim ownership" | `operationApi.ts:54` | ACTIVE_FRONTEND_TYPE | Yes (comment) | Update comment | Trivial |

### Active Tests

| Reference | File | Category | Active Source? | H08I-B Action | Risk |
|---|---|---|---|---|---|
| `from app.services.station_claim_service import get_station_queue` | `test_reopen_resumability_claim_continuity.py:25` | ACTIVE_TEST | Yes | Update import path after rename | Low |
| `from app.services.station_claim_service import get_station_queue` | `test_station_queue_active_states.py:33` | ACTIVE_TEST | Yes | Update import path | Low |
| `from app.services.station_claim_service import get_station_queue` | `test_station_queue_session_aware_migration.py:13` | ACTIVE_TEST | Yes | Update import path | Low |
| Function name `test_reopen_restores_last_claim_owner_path_...` | `test_reopen_resumability_claim_continuity.py:209` | ACTIVE_TEST | Yes | Rename to session-based name | Low |
| Function name `test_reopen_preserves_active_claim_continuity_...` | `test_reopen_resumability_claim_continuity.py:249` | ACTIVE_TEST | Yes | Rename to session-based name | Low |
| Function name `test_reopen_skips_claim_restoration_...` | `test_reopen_resumability_claim_continuity.py:272` | ACTIVE_TEST | Yes | Rename to session-based name | Low |
| `assert queue_item["claim"] is None` | `test_reopen_resumability_claim_continuity.py:236` | ACTIVE_TEST | Yes | Remove assertion (field will be gone) | Low |
| `_PREFIX = "TEST-REOPEN-CLAIM-CONTINUITY"` | `test_reopen_resumability_claim_continuity.py:32` | ACTIVE_TEST | Yes (name) | Rename prefix constant | Trivial |

### Canonical Error Docs

| Reference | File | Category | Active Source? | H08I-B Action | Risk |
|---|---|---|---|---|---|
| `CLAIM_API_DISABLED` entry | `docs/design/00_platform/canonical-error-codes.md:39` | CANONICAL_ERROR_DOC | Yes (doc only) | Remove entry (no backend code uses it) | Low |
| `CLAIM_API_DISABLED` entry | `docs/design/00_platform/canonical-error-code-registry.md:40` | CANONICAL_ERROR_DOC | Yes (doc only) | Remove entry | Low |

### Migration History (Keep)

| Reference | File | Category | Keep? | Reason |
|---|---|---|---|---|
| `operation_claim_audit_logs`, `operation_claims` table names | `alembic/versions/0009_drop_station_claims.py` | MIGRATION_HISTORY | Yes | Migration chain integrity |
| Full claim DDL | `scripts/migrations/0009_station_claims.sql` | LEGACY_SQL_HISTORY | Yes | Immutable historical artifact |
| `0009_drop_station_claims.py` comment block | `alembic/versions/0009_drop_station_claims.py` | MIGRATION_HISTORY | Yes | Migration governance record |
| Claim mention in Alembic revision comments | `alembic/versions/0001_baseline.py` (possibly) | MIGRATION_HISTORY | Yes | Historical context |

### Implementation History Docs (Keep)

| File | Category | Keep? |
|---|---|---|
| `docs/implementation/p0-c-08h*.md` (all 17+ reports) | IMPLEMENTATION_HISTORY_DOC | Yes |
| `docs/implementation/p0-c-08h7-*.md`, `h8-*.md`, etc. | IMPLEMENTATION_HISTORY_DOC | Yes |

### Design Docs

| Reference | File | Category | H08I-B Action |
|---|---|---|---|
| `CLAIM_API_DISABLED` narrative | `canonical-error-codes.md`, `canonical-error-code-registry.md` | CANONICAL_ERROR_DOC | Remove in H08I-B |
| Comment "Replaces claim-based ownership logic" | `stationApi.ts:7` | DESIGN_DOC | Update comment (still accurate as context but can simplify) |

---

## 5. Active Source vs Historical Reference Classification

| Reference Group | Examples | Can Delete in H08I-B? | Should Keep? | Reason |
|---|---|---|---|---|
| Active backend schema | `ClaimSummary`, `StationQueueItem.claim` | Yes | No | Schema sends `None`; frontend type already clean; safe to remove |
| Active backend service name | `station_claim_service.py` | Rename (not delete) | Rename only | File hosts active queue logic; rename to `station_queue_service.py` |
| Active backend queue projection | `"claim": None` in response dict | Yes | No | Backend sends null; safe to remove after schema field removed |
| Active frontend i18n keys | `station.claim.*`, `station.queue.readyToClaim` | Rename | No as-is | Must rename keys + update all consumers atomically |
| Active frontend prop names | `hasMineClaim` | Rename | No as-is | Rename to `hasMineSession` in panel + card |
| Active test imports | `from app.services.station_claim_service import` | Update | Updated form | Update after rename |
| Active test function names | `test_reopen_preserves_active_claim_continuity...` | Rename | No as-is | Rename functions; test logic stays |
| Active test assertions | `assert queue_item["claim"] is None` | Delete | No | Field will be removed from schema |
| Canonical error docs | `CLAIM_API_DISABLED` | Yes | No | No route can return it; no backend code references it |
| Alembic migration | `0009_drop_station_claims.py` | No | Yes | Migration chain integrity |
| Raw SQL migration | `0009_station_claims.sql` | No | Yes | Immutable historical artifact |
| Implementation reports | `p0-c-08h*.md` | No | Yes | Project audit history |
| Design docs (operational) | Execution contracts | No | Yes | Active design docs; claim described as retired |

---

## 6. Already Removed Claim Surface

| Claim Surface | Current Status | Evidence | Additional Action Needed? |
|---|---|---|---|
| Claim API routes (`/claim`, `/release`, `/claim` GET) | REMOVED | H14B; `station.py` router has none | No |
| Frontend claim API client (`claim()`, `release()`, `getClaim()`) | REMOVED | H14B; `stationApi.ts` clean | No |
| `ClaimSummary` interface in TypeScript | REMOVED | `stationApi.ts` inspected — not present | No |
| `StationQueueItem.claim` TypeScript field | REMOVED | `stationApi.ts` inspected — not present | No |
| Claim service dead functions | REMOVED | H15B | No |
| Claim route-only schemas (`ClaimRequest`, `ReleaseClaimRequest`, `ClaimResponse`) | REMOVED | H15B | No |
| Claim tests (`test_claim_api_deprecation_lock.py`, `test_claim_single_active_per_operator.py`, etc.) | REMOVED (deleted) | H16B | No |
| Claim scripts (`verify_station_claim.py`, `verify_station_queue_claim.py`) | REMOVED (deleted) | H16C | No |
| Claim seed imports | REMOVED | H16C | No |
| `OperationClaim` / `OperationClaimAuditLog` ORM models | REMOVED | H17 | No |
| `app/models/station_claim.py` | DELETED | H17 | No |
| `init_db.py` claim import | REMOVED | H17 | No |
| `operation_claims` DB table | DROPPED | H17 Alembic 0009 | No |
| `operation_claim_audit_logs` DB table | DROPPED | H17 Alembic 0009 | No |
| Frontend claim fallback in queue components | REMOVED | H8; `QueueOperationCard.tsx` ownership-only | No |
| `ownership_migration_status` = "TARGET_SESSION_OWNER_WITH_CLAIM_COMPAT" | REMOVED | Now `"TARGET_SESSION_OWNER"` in service | No |
| Reopen claim compatibility helper `_restore_claim_continuity_for_reopen` | REMOVED | H11B | No |

---

## 7. API / Service / Queue / Schema Cleanup Map

| Artifact | Current Claim Remnant | H08I-B Candidate Action | Risk | Test Needed |
|---|---|---|---|---|
| `station_claim_service.py` | Filename references "claim"; contents are pure queue/session logic | Rename → `station_queue_service.py`; update 1 route import + 3 test imports | Low | Yes — verify all imports after rename |
| `get_station_queue` function | No claim remnant in logic | No action needed | None | None |
| `get_station_scoped_operation` function | No claim remnant in logic | No action needed | None | None |
| `from app.services.station_claim_service import` (station.py) | Import path uses claim name | Update after rename | Low | Lint/import check |
| `ClaimSummary` Pydantic class | Active backend schema class | Delete class | Low | Update schema tests that assert claim field |
| `StationQueueItem.claim` backend field | Null-only compatibility field | Remove field | Low | Remove `assert queue_item["claim"] is None` in tests |
| `"claim": None` in queue dict | Compatibility projection | Remove key from response dict | Low | Queue response shape test |
| Frontend `hasMineClaim` variable/prop | Name references "claim"; logic uses ownership | Rename → `hasMineSession` | Low | Lint + build |
| Frontend `station.claim.*` i18n keys | Key names reference "claim" | Rename keys + update all consumers in 3 files | Medium — must be atomic | Build + route smoke |
| `station.queue.readyToClaim` i18n key | Key name references "claim" | Rename → `station.queue.available` | Medium | Build |
| `station.queue.claimedByOther` i18n key | Key name references "claim" | Rename → `station.queue.takenByOther` | Medium | Build |
| `CLAIM_API_DISABLED` in canonical error docs | Doc entry; no backend code uses it | Remove from both canonical-error-codes.md and canonical-error-code-registry.md | Low | None (doc only) |

---

## 8. Migration / History Boundary Map

| Historical Artifact | Contains Claim? | Keep / Remove / Defer | Reason |
|---|---|---|---|
| `alembic/versions/0009_drop_station_claims.py` | Yes (table names, comments) | **Keep** | Migration chain integrity — removing would break Alembic history |
| `alembic/versions/0001_baseline.py` | No direct claim | Keep | No-op baseline |
| `scripts/migrations/0009_station_claims.sql` | Yes (full DDL) | **Keep** | Immutable historical migration artifact; repo convention |
| `scripts/migrations/0001–0008.sql` | May contain `station_scope_value` ADD (claim-era) | Keep | Historical, immutable |
| `docs/implementation/p0-c-08h*.md` (all H-series reports) | Yes (extensive) | **Keep** | Project audit/governance history |
| `docs/implementation/autonomous-implementation-plan.md` | Yes (H-series entries) | Keep | Living plan — tracks H-series history |
| `docs/implementation/autonomous-implementation-verification-report.md` | Yes (H-series evidence) | Keep | Living verification record |
| `docs/implementation/hard-mode-v3-map-report.md` | Yes (HM3-033 to HM3-046) | Keep | HM3 implementation evidence |
| Design docs (`station-session-ownership-contract.md`) | Mentions claim retirement | Keep | Historical context; claim described as retired |
| `docs/design/00_platform/canonical-error-codes.md` | `CLAIM_API_DISABLED` entry | **Remove entry in H08I-B** | No route can return it; no backend code uses it; safe to delete |
| `docs/design/00_platform/canonical-error-code-registry.md` | `CLAIM_API_DISABLED` entry | **Remove entry in H08I-B** | Same as above |

**Policy conclusion:** True zero-text claim references would require rewriting migration history files. This is not recommended and requires explicit baseline-history rewrite approval (H08I-C if desired). All migration history files should stay as-is.

---

## 9. H08I-B Scope Options

| Option | Pros | Cons | Risk | Fits Human Intent? | Recommendation |
|---|---|---|---|---|---|
| **A — Active Source Purge Only** | Removes claim from all runtime code; service rename; schema cleanup; i18n key rename; canonical error cleanup | Migration/history files keep claim text | Low | Yes — satisfies "erase from active source" | **RECOMMENDED** |
| **B — Active Source + Design Doc Cleanup** | Option A plus update design docs to remove active claim descriptions | Design docs are governance records; touching them is lower priority | Low-Medium | Mostly yes | Acceptable — do after A |
| **C — Full Repo Text Purge** | Zero "claim" occurrences in repo | High risk; breaks migration chain; destroys project history; requires git history rewrite | HIGH | Technically yes but inadvisable | **REJECT** unless explicit baseline rewrite approved |
| **D — Keep Queue Compatibility Field** | No API shape change | Does not satisfy "erase from active source"; leaves `ClaimSummary` and `claim: None` in backend forever | None | No | **REJECT** — frontend type is already clean; backend field safe to remove |

**Decision: Option A (Active Source Purge Only) for H08I-B.**

---

## 10. H08I-B Implementation Scope Proposal

### Slice: P0-C-08I-B Active Claim Source Purge Implementation

#### In Scope

**Backend:**
1. Rename `backend/app/services/station_claim_service.py` → `backend/app/services/station_queue_service.py`
2. Update import in `backend/app/api/v1/station.py` (1 line)
3. Update imports in 3 test files:
   - `tests/test_reopen_resumability_claim_continuity.py`
   - `tests/test_station_queue_active_states.py`
   - `tests/test_station_queue_session_aware_migration.py`
4. Remove `ClaimSummary` class from `backend/app/schemas/station.py`
5. Remove `claim: ClaimSummary | None = None` field from `StationQueueItem` schema
6. Remove `"claim": None` projection key from `get_station_queue` response dict in `station_queue_service.py`
7. Remove `assert queue_item["claim"] is None` assertion from `test_reopen_resumability_claim_continuity.py`
8. Rename test function names in `test_reopen_resumability_claim_continuity.py` from claim-based to session/reopen-based names (optional in this slice; functional tests unchanged)
9. Remove `CLAIM_API_DISABLED` entry from `docs/design/00_platform/canonical-error-codes.md`
10. Remove `CLAIM_API_DISABLED` entry from `docs/design/00_platform/canonical-error-code-registry.md`

**Frontend:**
11. Rename `hasMineClaim` → `hasMineSession` in `StationQueuePanel.tsx` (local variable + prop pass)
12. Rename `hasMineClaim` prop → `hasMineSession` in `QueueOperationCard.tsx` (interface + parameter + usage)
13. Rename i18n keys atomically (key rename + all consumer updates in same slice):
    - `station.claim.ownedBadge` → `station.queue.owned`
    - `station.claim.takenWarning` → `station.queue.takenWarning`
    - `station.claim.singleActiveHint` → `station.queue.singleOperatorHint`
    - `station.claim.required` → `station.execution.sessionRequired`
    - `station.queue.readyToClaim` → `station.queue.available`
    - `station.queue.claimedByOther` → `station.queue.takenByOther`
14. Delete dead i18n keys (no frontend consumer after frontend cleanup):
    - `station.action.claim` / `station.action.claiming`
    - `station.toast.claimed` / `station.toast.claimFailed`
    - `station.reject.STATE_REOPEN_OWNER_HAS_OTHER_ACTIVE_CLAIM` (if no consumer remains after H14B)
15. Update comment in `stationApi.ts` line 7 (simplify; claim already retired)
16. Update comment in `operationApi.ts:54` (remove "claim ownership" reference)
17. Update comment in `screenStatus.ts:133` (remove "compatibility claim model" reference)

#### Out of Scope for H08I-B

- Delete Alembic migration `0009_drop_station_claims.py`
- Delete raw SQL migration `0009_station_claims.sql`
- Delete any H-series implementation report
- Rewrite git history
- StationSession behavior change
- Execution command behavior change
- New domain P0-D work
- Design doc narrative rewrite (separate H08I-C if desired)
- `test_execution_route_claim_guard_removal.py` rename (tests verify claim guard IS absent — this remains valuable regression guard; rename is optional)
- `test_reopen_operation_claim_continuity_hardening.py` rename (tests verify reopen+operation behavior; rename is optional low-priority)

---

## 11. Optional H08I-C Historical Cleanup Decision

If the product owner wants zero textual "claim" occurrences in the entire repo (including migrations and history docs):

### Slice: P0-C-08I-C Historical Claim Reference Policy / Baseline Rewrite Decision

This slice is **separate and requires explicit approval** before any work.

Scope:
- Rewrite or retitle `docs/implementation/p0-c-08h*.md` documents
- Edit comment blocks in Alembic migration `0009_drop_station_claims.py`
- Retitle/rename the migration file itself (would require Alembic version resolution change)
- Edit `0009_station_claims.sql` comment header (currently marked immutable)
- Update all design doc claim-mentions to explicit "retired" language
- Update `test_execution_route_claim_guard_removal.py` and `test_reopen_operation_claim_continuity_hardening.py` filenames

**Risk:** High for migration history edits. Medium for implementation doc edits.

**Recommendation:** Do not approve H08I-C unless the product owner explicitly asks to scrub history. The current approach satisfies "claim-free active source" without touching historical governance records.

---

## 12. Test Strategy

| Test / Check | Purpose | Required for H08I-B? |
|---|---|---|
| Backend station queue tests (`test_station_queue_active_states.py`) | Queue behavior unchanged after schema cleanup | Yes |
| Station session queue migration (`test_station_queue_session_aware_migration.py`) | Session-aware queue unchanged | Yes |
| Reopen resumability tests (`test_reopen_resumability_claim_continuity.py`) | Reopen + resume behavior after claim assertion removed | Yes |
| Reopen continuity hardening (`test_reopen_operation_claim_continuity_hardening.py`) | Reopen guards unchanged | Yes |
| Execution route claim guard removal (`test_execution_route_claim_guard_removal.py`) | Claim guard absence regression | Yes |
| Script compile (`compileall -q scripts`) | No import errors from service rename | Yes |
| Frontend lint | No TypeScript errors from i18n key rename + prop rename | Yes |
| Frontend build | No dead code or type errors | Yes |
| Frontend route smoke | No route accessibility regression | Yes |
| Full backend suite | Regression gate after rename + schema cleanup | Yes (H08I-B exit gate) |
| Active claim sweep post-H08I-B | Confirm no active claim references remain | Yes |

---

## 13. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| i18n key rename breaks untested consumer | Medium | Medium | Full i18n key audit before rename; grep all key usages across frontend |
| Service rename breaks test import not found in sweep | Low | Low | `compileall` + full backend suite |
| Removing `StationQueueItem.claim` from backend schema breaks an undiscovered consumer | Low | Low | Frontend type already has no `claim` field; `grep` shows no frontend consumption |
| `hasMineClaim` → `hasMineSession` prop rename misses prop pass-through | Low | Low | TypeScript type check catches at build |
| Dead i18n key deletion removes a key still used in a code path not searched | Low | Medium | Search all usages before delete; keep as fallback in i18n key type file |

---

## 14. Recommendation

**Proceed with P0-C-08I-B Active Claim Source Purge Implementation.**

Priority order within H08I-B:
1. Service rename (`station_claim_service.py` → `station_queue_service.py`) + import updates — foundational; everything else follows.
2. Backend schema cleanup (`ClaimSummary` removal, `claim` field removal, projection key removal).
3. Backend test assertion update (remove `assert queue_item["claim"] is None`).
4. Frontend prop rename (`hasMineClaim` → `hasMineSession`) + i18n key renames.
5. Canonical error doc cleanup (`CLAIM_API_DISABLED` removal).
6. Comment updates in `stationApi.ts`, `operationApi.ts`, `screenStatus.ts`.

**Do NOT** approve H08I-C (migration/history scrub) unless the product owner explicitly requests zero textual claim occurrences in migration files and history docs.

**Current baseline is strong**: H17 full suite 120 passed, 1 skipped. All focused tests pass. Frontend lint clean. The active source purge is low-risk.

---

## 15. Final Verdict

```
READY_FOR_P0_C_08I_B_WITH_MIGRATION_HISTORY_EXCEPTIONS
```

Active source (backend app, frontend components, backend tests, canonical error docs) can be fully purged of claim references in H08I-B. Migration files (`0009_drop_station_claims.py`, `0009_station_claims.sql`) and implementation history docs retain claim references by policy — this is documented and accepted. No further governance decision required to proceed with H08I-B.
