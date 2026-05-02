# P0-C-08H17 Claim ORM Model / Table Drop Migration Implementation

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Removed legacy claim ORM model and dropped claim tables through governed migration after test/script dependency burn-down. |

---

## 1. Executive Summary

P0-C-08H17 finalises the claim retirement programme by:

1. Deleting the claim ORM model file (`backend/app/models/station_claim.py`).
2. Removing the claim model registry import from `backend/app/db/init_db.py`.
3. Adding Alembic migration `0009_drop_station_claims.py` that drops `operation_claim_audit_logs` then `operation_claims` with full downgrade recreation.

All prior retirement slices (H14B API/frontend, H15B service/schema, H16B test burn-down, H16C script burn-down) had removed every runtime claim reference. H17 is the clean terminal migration step.

Full backend suite: **120 passed, 1 skipped** (exit 0). Migration applied, tables confirmed absent.

---

## 2. Scope and Non-Scope

### In Scope
- Delete `backend/app/models/station_claim.py`
- Remove `from app.models.station_claim import OperationClaim, OperationClaimAuditLog` from `backend/app/db/init_db.py`
- Add `backend/alembic/versions/0009_drop_station_claims.py` (upgrade: drop both tables; downgrade: recreate both tables)
- Verification suite

### Explicitly Out of Scope
- `StationQueueItem.claim` — not removed (queue compatibility preserved)
- `station_claim_service.py` — not deleted (active queue service)
- `backend/scripts/migrations/0009_station_claims.sql` — not edited (immutable historical artifact)
- StationSession / execution / reopen / close behavior — unchanged
- Frontend queue API types — unchanged

---

## 3. Hard Mode Gate Evidence

| Fact | Evidence |
|---|---|
| StationSession is execution ownership truth | station-session-ownership-contract.md |
| H14B removed claim API routes + frontend client | p0-c-08h14b report |
| H15B removed dead claim service functions + schemas | p0-c-08h15b report |
| H16B removed claim model/table deps from tests | p0-c-08h16b report (context) |
| H16C removed/reworked legacy script claim deps | p0-c-08h16c report |
| H13 approved dev hard drop | CLAIM_RETENTION_POLICY_DEV_HARD_DROP_APPROVED |
| H16 contract approved drop order: audit_logs first, claims second | p0-c-08h16 contract |
| Queue compatibility field `StationQueueItem.claim` preserved | Not in H17 scope |
| `station_claim_service.py` has no ORM claim imports (H15B cleaned) | source inspection |

Verdict: `ALLOW_IMPLEMENTATION`

---

## 4. Remaining Claim Reference Inventory

Pre-implementation sweep (backend app/tests/scripts/alembic):

| Reference | File | Type | H17 Action |
|---|---|---|---|
| `OperationClaim` / `OperationClaimAuditLog` class defs | `app/models/station_claim.py` | ORM model | Deleted with file |
| `from app.models.station_claim import ...` | `app/db/init_db.py:38` | Registry import | Removed |
| `from app.services.station_claim_service import` | `app/api/v1/station.py:12` | Active service | **Kept** (service active) |
| `from app.services.station_claim_service import get_station_queue` | 3 test files | Active service | **Kept** (service active) |

Post-implementation sweep: no `OperationClaim` / `OperationClaimAuditLog` / `station_claim.py` references in app/tests/scripts. Only migration file and active service references remain.

---

## 5. Files Changed

| File | Action |
|---|---|
| `backend/app/models/station_claim.py` | DELETED |
| `backend/app/db/init_db.py` | Removed claim model import (line 38) |
| `backend/alembic/versions/0009_drop_station_claims.py` | CREATED — drop migration |

---

## 6. ORM Model Removal

`backend/app/models/station_claim.py` deleted. File contained:
- `class OperationClaim(Base)` — `__tablename__ = "operation_claims"` — 9 columns + relationship
- `class OperationClaimAuditLog(Base)` — `__tablename__ = "operation_claim_audit_logs"` — 10 columns + FK→operation_claims

`backend/app/db/init_db.py` line removed:
```python
from app.models.station_claim import OperationClaim, OperationClaimAuditLog  # noqa: F401
```

`backend/app/models/__init__.py` — empty, no action required.

---

## 7. Migration Implementation

File: `backend/alembic/versions/0009_drop_station_claims.py`

```
revision: 0009
down_revision: 0008
```

### Upgrade (drop order)

1. Drop all indexes on `operation_claim_audit_logs`
2. `op.drop_table("operation_claim_audit_logs")` — child first (FK: claim_id→operation_claims.id)
3. Drop all indexes on `operation_claims` (including partial unique index `uq_operation_claims_operation_active`)
4. `op.drop_table("operation_claims")` — parent second

### Alembic execution log

```
INFO Running upgrade 0008 -> 0009, drop operation_claims and operation_claim_audit_logs tables
H17_ALEMBIC_UPGRADE_EXIT:0
```

---

## 8. Downgrade / Rollback Behavior

Convention followed: full table recreation in downgrade (matching `0008_boms.py` pattern).

Downgrade recreates:
1. `operation_claims` first (parent) — all 9 columns + 5 regular indexes + partial unique index (`WHERE released_at IS NULL`)
2. `operation_claim_audit_logs` second (child) — all 10 columns + 4 indexes + FK→operation_claims.id

Schema sourced from `backend/scripts/migrations/0009_station_claims.sql` (read-only reference) and original ORM model. Legacy SQL file **not edited**.

---

## 9. Queue Contract Boundary

`StationQueueItem.claim` nullable field: **unchanged**.
`claim=None` projection in `get_station_queue`: **unchanged**.
Frontend queue API types: **unchanged**.
This is a separate API cleanup slice and is explicitly deferred.

---

## 10. Test / Verification Results

| Check | Result | Exit |
|---|---|---|
| `alembic current` before upgrade | `0008` | 0 |
| `alembic heads` after adding 0009 | `0009 (head)` | 0 |
| `alembic upgrade head` | `0008 -> 0009` applied | 0 |
| Table absence check (Python inspector) | Both tables absent | 0 |
| Exec/queue/reopen focused tests (23 tests) | 23 passed | 0 |
| Dependency burn-down tests (41 tests) | 41 passed | 0 |
| Script compile (`compileall -q scripts`) | Clean | 0 |
| Frontend lint | Clean | 0 |
| Frontend build | Built in 7.88s | 0 |
| Frontend route smoke | 24 PASS, 0 FAIL | 0 |
| Post-impl claim sweep | No app/test/script ORM references | 0 |
| **Full backend suite** | **120 passed, 1 skipped** | **0** |

---

## 11. Remaining Claim References

After H17:

| Reference | File | Type | Allowed? |
|---|---|---|---|
| `from app.services.station_claim_service import` | `app/api/v1/station.py` | Active queue service | Yes |
| `from app.services.station_claim_service import get_station_queue` | 3 test files | Active queue service | Yes |
| Table name strings in migration | `alembic/versions/0009_drop_station_claims.py` | Migration history | Yes |
| `0009_station_claims.sql` | `backend/scripts/migrations/` | Historical DDL | Yes, read-only |
| Implementation docs | `docs/implementation/` | Historical evidence | Yes |

No active ORM class references remain in app/tests/scripts.

---

## 12. Recommendation

H17 is complete. Alembic head is now `0009`. Claim tables are dropped. ORM model is removed. All verification gates pass.

Next slice: P0-D Quality Lite (per autonomous implementation plan), or continue with remaining queue `claim` field cleanup as a separate deferred slice.

Do NOT start P0-D until instructed.

---

## 13. Final Verdict

```
P0_C_08H17_COMPLETE_VERIFICATION_CLEAN
```

Full backend suite: 120 passed, 1 skipped. All focused tests, migration, and frontend gates: exit 0.
