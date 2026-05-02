# P0-C-08H16C Legacy Script Claim Dependency Burn-Down Report

## History

| Date | Version | Change |
|---|---:|---|
| 2026-05-02 | v1.0 | Removed and rewrote legacy script claim dependencies to StationSession-compatible verification/seed behavior. |

## 1. Executive Summary
H16C completed the remaining script-layer claim dependency burn-down that was explicitly deferred by H16B.

Completed in this slice:
- deleted two legacy claim verification scripts,
- rewrote remaining claim-dependent script checks to StationSession guard semantics,
- removed claim model cleanup dependencies from seed helpers.

Not done in H16C:
- no model deletion,
- no `init_db` claim import removal,
- no migration/table drop,
- no execution behavior change.

## 2. Scope and Non-Scope
In scope completed:
- script-level claim dependency removal under `backend/scripts/**`,
- script verification parity with StationSession ownership model,
- seed script cleanup to avoid claim-model hard dependency.

Out of scope held:
- `backend/app/models/station_claim.py`,
- `backend/app/db/init_db.py`,
- `backend/scripts/migrations/0009_station_claims.sql`,
- Alembic migration authoring for claim table drop.

## 3. Hard Mode Gate Evidence
## Routing
- Selected brain: MOM Brain
- Selected mode: Strict / Single-Slice Backend Implementation
- Hard Mode MOM: v3
- Reason: H16C is a migration-readiness dependency slice for claim retirement and touches execution-adjacent verification tooling.

### Design Evidence Extract
| Fact | Source | Evidence |
|---|---|---|
| StationSession is ownership truth | [docs/design/02_domain/execution/station-session-ownership-contract.md](docs/design/02_domain/execution/station-session-ownership-contract.md) | claim is compatibility debt |
| StationSession command guard governs execution mutations | [docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md](docs/design/02_domain/execution/station-session-command-guard-enforcement-contract.md) | missing/closed/mismatch session rejects guarded commands |
| H16B deferred script claim references | [docs/implementation/p0-c-08h16b-claim-model-test-dependency-burn-down-report.md](docs/implementation/p0-c-08h16b-claim-model-test-dependency-burn-down-report.md) | script burn-down required before H17 |
| H16 contract requires staged dependency cleanup before drop migration | [docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md](docs/implementation/p0-c-08h16-claim-model-table-drop-migration-contract.md) | model/table drop not immediate |

### Script Burn-Down Map
| Script Surface | Previous Claim Dependency | H16C Action | Result |
|---|---|---|---|
| [backend/scripts/verify_station_claim.py](backend/scripts/verify_station_claim.py) | direct claim endpoint verification | delete | complete |
| [backend/scripts/verify_station_queue_claim.py](backend/scripts/verify_station_queue_claim.py) | direct claim queue/claim endpoint verification | delete | complete |
| [backend/scripts/verify_clock_on.py](backend/scripts/verify_clock_on.py) | claim-based ownership assumptions and cleanup | rewrite to StationSession guard checks | complete |
| [backend/scripts/verify_clock_off.py](backend/scripts/verify_clock_off.py) | claim-based ownership assumptions and cleanup | rewrite to StationSession guard checks | complete |
| [backend/scripts/verify_station_execution_seed.py](backend/scripts/verify_station_execution_seed.py) | claim-affordance assumptions | rewrite to queue/session guard satisfiability checks | complete |
| [backend/scripts/seed/common.py](backend/scripts/seed/common.py) | claim model cleanup path in reset | remove claim model deletes/import reliance | complete |
| [backend/scripts/seed/seed_station_execution_opr.py](backend/scripts/seed/seed_station_execution_opr.py) | claim model cleanup path in reset | remove claim model deletes/import reliance | complete |

### Invariant Map
| Invariant | Category | H16C Status |
|---|---|---|
| backend execution truth unchanged | execution | preserved |
| StationSession guard behavior unchanged | guard | preserved |
| claim model/init registry untouched in this slice | migration boundary | preserved |
| historical claim migration files untouched | migration boundary | preserved |

### Verdict before coding
ALLOW_IMPLEMENTATION

## 4. Files Changed
Deleted:
- [backend/scripts/verify_station_claim.py](backend/scripts/verify_station_claim.py)
- [backend/scripts/verify_station_queue_claim.py](backend/scripts/verify_station_queue_claim.py)

Modified:
- [backend/scripts/verify_clock_on.py](backend/scripts/verify_clock_on.py)
- [backend/scripts/verify_clock_off.py](backend/scripts/verify_clock_off.py)
- [backend/scripts/verify_station_execution_seed.py](backend/scripts/verify_station_execution_seed.py)
- [backend/scripts/seed/common.py](backend/scripts/seed/common.py)
- [backend/scripts/seed/seed_station_execution_opr.py](backend/scripts/seed/seed_station_execution_opr.py)

## 5. Boundary Confirmation
Confirmed unchanged:
- [backend/app/models/station_claim.py](backend/app/models/station_claim.py)
- [backend/app/db/init_db.py](backend/app/db/init_db.py)
- [backend/scripts/migrations/0009_station_claims.sql](backend/scripts/migrations/0009_station_claims.sql)

## 6. Verification Results
Backend subset batch 1:
- `40 passed`

Backend subset batch 2:
- `50 passed`

Script compile gate:
- `H16C_COMPILEALL_EXIT:0`

Frontend smoke:
- `H16C_FRONTEND_LINT_EXIT:0`
- `H16C_FRONTEND_BUILD_EXIT:0`
- `H16C_FRONTEND_ROUTE_SMOKE_EXIT:0`
- route smoke summary: 24 PASS, 0 FAIL, 77/78 covered, 1 excluded redirect

Script claim sweep:
- initial relative-path run was invalid for workspace root context
- corrected absolute-path run: `H16C_SCRIPT_CLAIM_SWEEP_EXIT:0`

## 7. Residual Claim References (Expected)
H16C intentionally leaves claim model/migration retirement for later slices:
- [backend/app/models/station_claim.py](backend/app/models/station_claim.py)
- [backend/app/db/init_db.py](backend/app/db/init_db.py)
- [backend/scripts/migrations/0009_station_claims.sql](backend/scripts/migrations/0009_station_claims.sql)

Next owner slice for destructive retirement remains H17.

## 8. Final Verdict
P0_C_08H16C_COMPLETE_SCRIPT_SURFACE_CLEAN
