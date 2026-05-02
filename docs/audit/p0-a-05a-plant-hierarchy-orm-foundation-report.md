# P0-A-05A — Plant / Area / Line / Station / Equipment ORM Foundation

**Slice:** P0-A-05A  
**Status:** COMPLETE — all 20 tests pass, zero regressions  
**Date:** 2025  
**Alembic head after this slice:** 0005

---

## Routing

- **Selected brain:** FleziBCG AI Brain v6 Auto-Execution  
- **Selected mode:** Hard Mode MOM v3  
- **Hard Mode MOM:** v3  
- **Reason:** Touches DB schema (new tables), ORM model registration, and Alembic migration chain — all Hard Mode MOM v3 triggers per governance rules.

---

## HMM v3 Gate

### Design Evidence Extract
- Five-level hierarchy: Plant → Area → Line → Station → Equipment  
- Each model has `tenant_id` as soft multi-tenant scope reference (no Tenant ORM table yet)  
- Parent FK columns (area.plant_id, line.area_id, station.line_id, equipment.station_id) declared with SQLAlchemy `ForeignKey()` in ORM + foreign key constraints in migration  
- `is_active` boolean with Python `__init__` default = True; `server_default="1"` in migration  
- `metadata_json TEXT` (nullable) for extensibility without schema change  
- `created_at` / `updated_at` with `server_default=func.now()` (UTC)  
- `station_type` / `equipment_type` nullable — optional classification  

### Event Map
- No domain events. This slice is ORM + schema foundation only. No event emission.

### Invariant Map
- `(tenant_id, plant_code)` must be unique per `plants` table → `uq_plants_tenant_code`  
- `(tenant_id, plant_id, area_code)` unique → `uq_areas_tenant_plant_code`  
- `(tenant_id, area_id, line_code)` unique → `uq_lines_tenant_area_code`  
- `(tenant_id, line_id, station_code)` unique → `uq_stations_tenant_line_code`  
- `(tenant_id, station_id, equipment_code)` unique → `uq_equipment_tenant_station_code`  
- PKs: `plant_id`, `area_id`, `line_id`, `station_id`, `equipment_id` (string, caller-assigned)

### State Transition Map
- Not applicable. No execution state machine touched.

### Test Matrix

| Test | Invariant | Result |
|------|-----------|--------|
| `test_plant_hierarchy_models_exist` | All 5 classes importable | ✅ PASS |
| `test_plant_fields_exist` | All Plant fields | ✅ PASS |
| `test_area_fields_exist` | All Area fields incl. plant_id | ✅ PASS |
| `test_line_fields_exist` | All Line fields incl. area_id | ✅ PASS |
| `test_station_fields_exist` | All Station fields incl. line_id, station_type | ✅ PASS |
| `test_equipment_fields_exist` | All Equipment fields incl. station_id, equipment_type | ✅ PASS |
| `test_all_hierarchy_models_have_tenant_id` | tenant_id on all 5 | ✅ PASS |
| `test_all_hierarchy_models_have_is_active` | is_active on all 5 | ✅ PASS |
| `test_hierarchy_relationship_columns_exist` | Parent FK columns verified | ✅ PASS |
| `test_plant_hierarchy_unique_constraints_exist` | 5 named unique constraints | ✅ PASS |
| `test_plant_hierarchy_indexes_exist` | tenant_id index on all 5 | ✅ PASS |
| `test_hierarchy_sqlite_create_and_query` | Full hierarchy round-trip | ✅ PASS |
| `test_hierarchy_is_active_default_true` | ORM Python init default | ✅ PASS |
| `test_hierarchy_optional_fields_nullable` | Nullable optional fields | ✅ PASS |
| `test_plant_hierarchy_migration_revision_exists` | 0005 in ScriptDirectory | ✅ PASS |
| `test_plant_hierarchy_migration_down_revision_is_0004` | down_revision == 0004 | ✅ PASS |
| `test_plant_hierarchy_migration_creates_expected_tables_only` | AST: exactly 5 tables | ✅ PASS |
| `test_plant_hierarchy_migration_does_not_modify_existing_tables` | AST: no alter/add on existing | ✅ PASS |
| `test_plant_hierarchy_downgrade_drops_tables_in_dependency_order` | AST: reverse drop order | ✅ PASS |
| `test_plant_hierarchy_sqlite_migration_upgrade` | Raw SQLite DDL simulation | ✅ PASS |

### Verdict
**APPROVED — all 20 tests pass, all invariants covered, migration chain verified, no existing table modification.**

---

## Files Inspected

- `backend/app/db/init_db.py` — ORM model registration pattern
- `backend/app/models/user.py` — `__init__` default pattern for Python-side defaults
- `backend/alembic/versions/0004_add_user_lifecycle_status.py` — migration style reference
- `backend/alembic/env.py` — metadata source for Alembic
- `backend/tests/test_alembic_baseline.py` — head assertion pattern
- `docs/design/` — design intent for hierarchy models

---

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/models/plant_hierarchy.py` | CREATED | Five ORM model classes |
| `backend/app/db/init_db.py` | MODIFIED | Import Plant/Area/Line/Station/Equipment for Alembic metadata registration |
| `backend/alembic/versions/0005_add_plant_hierarchy.py` | CREATED | Alembic migration: create 5 hierarchy tables |
| `backend/tests/test_alembic_baseline.py` | MODIFIED | Updated head assertion from `0004` → `0005` |
| `backend/tests/test_plant_hierarchy_orm_foundation.py` | CREATED | 20 P0-A-05A tests |

---

## Migration Added

**`backend/alembic/versions/0005_add_plant_hierarchy.py`**

- `revision = "0005"`, `down_revision = "0004"`
- Upgrade: creates `plants` → `areas` → `lines` → `stations` → `equipment` (dependency order)
- Downgrade: drops `equipment` → `stations` → `lines` → `areas` → `plants` (reverse)
- Each table: unique constraint (tenant-scoped) + `ix_*_tenant_id` index
- Additional indexes: `ix_areas_plant_id`, `ix_lines_area_id`, `ix_stations_line_id`, `ix_equipment_station_id`
- `is_active` uses `server_default="1"` (SQLite-safe boolean)
- No existing table modification, no data migration

---

## Tests Added / Updated

| File | Tests | Status |
|------|-------|--------|
| `tests/test_plant_hierarchy_orm_foundation.py` | 20 new | All PASS |
| `tests/test_alembic_baseline.py` | 1 updated (head assertion) | PASS |

---

## Verification Commands Run

```bash
# New hierarchy tests
wsl bash -c "cd /mnt/g/Work/FleziBCG/backend && PYTHONPATH=... python3.12 -m pytest tests/test_plant_hierarchy_orm_foundation.py --tb=short"
# Result: 20 passed

# Alembic baseline + migration smoke + init DB
wsl bash -c "... python3.12 -m pytest tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py --tb=short"
# Result: 14 passed, 3 skipped

# P0-A-04A regression + auth regression
wsl bash -c "... python3.12 -m pytest tests/test_user_lifecycle_status.py tests/test_user_lifecycle_service.py tests/test_refresh_token_foundation.py tests/test_refresh_token_rotation.py -q"
# Result: 51 passed
```

---

## Results

| Suite | Passed | Failed | Skipped |
|-------|--------|--------|---------|
| P0-A-05A new tests | 20 | 0 | 0 |
| Alembic baseline + smoke | 14 | 0 | 3 |
| P0-A-04A + auth regression | 51 | 0 | 0 |
| **Total** | **85** | **0** | **3** |

---

## Issues Found and Resolved

1. **Missing `ForeignKey()` in ORM mapped columns** — `area.plant_id`, `line.area_id`, etc. had no SQLAlchemy `ForeignKey()` declaration, causing `NoForeignKeysError` when SQLAlchemy tried to resolve relationships. Fixed by adding `ForeignKey("plants.plant_id", name="fk_areas_plant_id")` etc. in each child model's `mapped_column()`.

2. **`is_active` default not applied at Python init time** — SQLAlchemy `mapped_column(default=True)` only applies on INSERT, not on Python object construction. Fixed by adding `__init__` override with `kwargs.setdefault("is_active", True)` to all five models (same pattern as `User.lifecycle_status`).

---

## Existing Gaps / Known Debts

- `Operation.station_scope_value` and `StationSession.station_id` remain plain strings — FK binding to `stations.station_id` deferred to future slice per design.  
- `Tenant` ORM table not created — `tenant_id` is a soft reference string per current architecture.  
- No admin CRUD API for hierarchy models — deferred.  
- No frontend — deferred.  
- `updated_at` has no auto-update trigger on SQLite — `server_default` only sets INSERT value. Application or trigger must update on modification (accepted debt, consistent with existing models).

---

## Scope Compliance

| Constraint | Compliant |
|-----------|-----------|
| Backend only — no frontend | ✅ |
| No admin API | ✅ |
| No execution state machine touched | ✅ |
| No existing table modification | ✅ |
| No Operation.station_scope_value or StationSession.station_id modification | ✅ |
| No Tenant ORM table created | ✅ |
| No SCADA, CMMS, scheduling, ERP | ✅ |
| Alembic chain maintained (0004→0005) | ✅ |

---

## Risks

- **Low:** Five new tables add to schema surface; downgrade removes them cleanly.  
- **Low:** SQLite does not enforce FK integrity by default — integration tests may miss FK violations unless `PRAGMA foreign_keys=ON` is set.  
- **Accepted:** Relationship traversal (e.g., `plant.areas`) requires active SQLAlchemy session; not tested in all test paths by design.

---

## Recommended Next Slice

**P0-A-05B** — Admin CRUD API for Plant / Area / Line / Station / Equipment (create, read, update, deactivate endpoints with tenant scoping and auth guard).

Or **P0-A-05C** — Bind `Operation.station_scope_value` and `StationSession.station_id` to `stations.station_id` FK (deferred FK binding).

---

## Stop Conditions Hit

- None. All invariants covered, all tests pass, no scope violations.
