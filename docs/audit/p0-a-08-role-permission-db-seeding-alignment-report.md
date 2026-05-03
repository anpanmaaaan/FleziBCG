# P0-A-08 Report: Role / Permission DB Seeding Alignment

**Slice:** P0-A-08  
**Date:** 2026-05-03  
**Status:** COMPLETE  
**Precondition Slice:** P0-A-07E (RBAC action registry closeout — all 3 P0-A-07A gaps resolved)

---

## Summary

Inspected `seed_rbac_core()` in `backend/app/security/rbac.py` and confirmed it
already dynamically iterates over `ACTION_CODE_REGISTRY` to produce `Permission` and
`RolePermission` rows for all action codes and all system roles. No seed production
code changes were required (**Option A — Tests only**).

Added `backend/tests/test_rbac_seed_alignment.py` (20 tests) proving:
- All 21 action codes have `Permission` rows with correct family
- All system roles have `Role` rows
- `RolePermission` rows align to `SYSTEM_ROLE_FAMILIES` (ADMIN, EXECUTE, APPROVE coverage)
- Separation of Duties: OPR has no ADMIN permissions; ADM has no EXECUTE permissions
- Seed is fully idempotent (no duplicate rows on double run)
- P0-A-07B/C/D action codes explicitly verified

Also identified and fixed a **pre-existing test drift**: `admin.master_data.product_version.manage`
was added to both `rbac.py` and `action-code-registry.md` by MMD-BE-08A (2026-05-03) but was
not added to `_EXPECTED_ADMIN_MMD_CODES` in `test_rbac_action_registry_alignment.py`, causing
a pre-existing `test_action_code_registry_contains_exactly_canonical_set` failure. Fixed by
adding the code to the expected set. Registry is now **21 codes**.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Backend implementation / verification + RBAC seed alignment + role/permission DB-row governance + authorization contract hardening + QA/regression
- **Hard Mode MOM:** v3
- **Reason:** Task touches persisted RBAC permission rows, role-permission seeding, authorization runtime readiness, privileged admin/action boundaries, and CI seed/test baseline. All criteria for MOM v3 trigger.

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Doc / Source | Evidence |
|---|---|
| `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md` | Registry closed at 20 codes; P0-A-07 gaps all resolved; seeding alignment identified as remaining debt |
| `backend/app/security/rbac.py ACTION_CODE_REGISTRY` | Now 21 codes (MMD-BE-08A added `admin.master_data.product_version.manage` on 2026-05-03) |
| `docs/design/02_registry/action-code-registry.md` | 21 codes; history entry for MMD-BE-08A present |
| `backend/app/security/rbac.py seed_rbac_core()` | Dynamically iterates over `ACTION_CODE_REGISTRY` and `SYSTEM_ROLE_FAMILIES`; uses `_get_or_create_action_permission` for every registry entry; uses `_get_or_create_role` for every system role; uses idempotent `_get_or_create_*` helpers throughout |
| `backend/app/security/rbac.py SYSTEM_ROLE_FAMILIES` | 11 system roles; OPR→EXECUTE; SUP→VIEW+EXECUTE; IEP→VIEW+CONFIGURE; QCI/EXE/PLN/INV→VIEW; QAL/PMG→VIEW+APPROVE; ADM/OTS→VIEW+ADMIN |
| `backend/app/models/rbac.py Permission` | `code` (unique), `family`, `action_code` (nullable); action-level rows have `action_code != None` |
| `backend/app/models/rbac.py RolePermission` | `UniqueConstraint(role_id, permission_id, scope_type, scope_value)` prevents duplicates |

### Invariant Map

| Invariant | Evidence | Tested |
|---|---|---|
| Every action code in `ACTION_CODE_REGISTRY` has a `Permission` row | `_get_or_create_action_permission` iterates full registry | Yes |
| `Permission.family` matches `ACTION_CODE_REGISTRY[code]` | `_get_or_create_action_permission` sets `family=family` | Yes |
| `Permission.action_code` is set to the code string (not None) | `_get_or_create_action_permission` sets `action_code=action_code` | Yes |
| All system roles in `SYSTEM_ROLE_FAMILIES` have `Role` rows | `_get_or_create_role` iterates `SYSTEM_ROLE_FAMILIES` | Yes |
| `RolePermission` rows exist for each role / allowed-family action code | Nested loop: for each role, for each action code whose family is in role's families | Yes |
| ADM / OTS receive all ADMIN-family action permissions | `SYSTEM_ROLE_FAMILIES["ADM"] = {"VIEW", "ADMIN"}` | Yes |
| OPR receives all EXECUTE-family action permissions | `SYSTEM_ROLE_FAMILIES["OPR"] = {"EXECUTE"}` | Yes |
| OPR has NO ADMIN-family permissions | ADMIN not in `{"EXECUTE"}` | Yes |
| ADM has NO EXECUTE-family permissions | EXECUTE not in `{"VIEW", "ADMIN"}` | Yes |
| VIEW-only roles have no action-level permissions | No action code maps to VIEW | Yes |
| Seed is idempotent | `_get_or_create_*` + `UniqueConstraint` + existence check before insert | Yes |
| P0-A-07B/C/D codes seeded | Dynamic iteration includes all new codes | Yes |

### Verdict

**`ALLOW_P0A08_ROLE_PERMISSION_DB_SEEDING_ALIGNMENT`**

Seed already aligned. Option A (tests only) appropriate. No production code changes
needed. Tests can be written against existing seed behavior.

---

## Selected Seed Alignment Option

**Option A — Tests only**

**Reason:** `seed_rbac_core()` dynamically iterates over `ACTION_CODE_REGISTRY` to produce
`Permission` rows and over `SYSTEM_ROLE_FAMILIES` to produce `RolePermission` rows. When
P0-A-07B, P0-A-07C, and P0-A-07D (and MMD-BE-08A) added new action codes to the registry,
those additions were automatically picked up by the seed loop. No seed production code
change was needed or safe.

---

## RBAC Seed Source Map

| Source Area | Current Evidence | Decision |
|---|---|---|
| `seed_rbac_core()` in `rbac.py` | Main seed function. Calls `_get_or_create_role` for each code in `SYSTEM_ROLE_FAMILIES`. Calls `_get_or_create_action_permission` for each entry in `ACTION_CODE_REGISTRY`. Creates `RolePermission` rows for family-level and action-level grants. | Aligned — no change needed |
| `_get_or_create_action_permission()` | Takes `(db, action_code, family)`. Checks existence by `Permission.code`. Creates if absent. Updates family/action_code if stale. Returns idempotent result. | Aligned |
| `_get_or_create_permission()` | Creates family-level `Permission` rows (VIEW/EXECUTE/APPROVE/CONFIGURE/ADMIN). | Aligned |
| `_get_or_create_role()` | Creates/retrieves `Role` rows for each system role code. | Aligned |
| `ACTION_CODE_REGISTRY` | 21 codes. Includes all P0-A-07B/C/D codes. Includes MMD-BE-08A code. | Runtime truth |
| `SYSTEM_ROLE_FAMILIES` | 11 roles. Families unchanged. | Role/family model |
| `RolePermission.UniqueConstraint` | `uq_role_permission_scope` on `(role_id, permission_id, scope_type, scope_value)` | DB-level duplicate prevention |
| Existing seed tests | `test_rbac_action_registry_alignment.py` — registry-level; no DB row tests existed | Gap filled by P0-A-08 |

---

## Permission / RolePermission Coverage

| Contract Item | Expected | Source of Truth | Test |
|---|---|---|---|
| `Permission` rows for action codes | 21 rows (one per `ACTION_CODE_REGISTRY` entry) | `ACTION_CODE_REGISTRY` | `test_seed_creates_permission_row_for_every_action_code` |
| `Permission.family` correct | Matches `ACTION_CODE_REGISTRY[code]` | `ACTION_CODE_REGISTRY` | `test_seed_permission_family_matches_registry` |
| `Permission.action_code` set | Equals action code string | `_get_or_create_action_permission` | `test_seed_permission_action_code_field_set` |
| No duplicate `Permission` rows | Exactly 1 per action code | `_get_or_create_*` idempotency | `test_seed_creates_exactly_one_permission_per_action_code` |
| P0-A-07B code seeded | `admin.downtime_reason.manage` → `ADMIN` | `ACTION_CODE_REGISTRY` | `test_seed_p0a07b_downtime_reason_manage_permission_exists` |
| P0-A-07C code seeded | `admin.security_event.read` → `ADMIN` | `ACTION_CODE_REGISTRY` | `test_seed_p0a07c_security_event_read_permission_exists` |
| P0-A-07D create code seeded | `admin.impersonation.create` → `ADMIN` | `ACTION_CODE_REGISTRY` | `test_seed_p0a07d_impersonation_create_permission_exists` |
| P0-A-07D revoke code seeded | `admin.impersonation.revoke` → `ADMIN` | `ACTION_CODE_REGISTRY` | `test_seed_p0a07d_impersonation_revoke_permission_exists` |
| All system roles created | 11 roles per `SYSTEM_ROLE_FAMILIES` | `SYSTEM_ROLE_FAMILIES` | `test_seed_creates_all_system_roles` |
| ADM ADMIN-family action RPs | All 8 ADMIN action codes | `SYSTEM_ROLE_FAMILIES["ADM"]` | `test_seed_adm_role_gets_all_admin_family_action_permissions` |
| OTS ADMIN-family action RPs | All 8 ADMIN action codes | `SYSTEM_ROLE_FAMILIES["OTS"]` | `test_seed_ots_role_gets_all_admin_family_action_permissions` |
| OPR EXECUTE-family action RPs | All 9 EXECUTE action codes | `SYSTEM_ROLE_FAMILIES["OPR"]` | `test_seed_opr_role_gets_all_execute_family_action_permissions` |
| QAL APPROVE-family action RPs | All 2 APPROVE action codes | `SYSTEM_ROLE_FAMILIES["QAL"]` | `test_seed_qal_role_gets_all_approve_family_action_permissions` |
| PMG APPROVE-family action RPs | All 2 APPROVE action codes | `SYSTEM_ROLE_FAMILIES["PMG"]` | `test_seed_pmg_role_gets_all_approve_family_action_permissions` |
| VIEW-only roles: 0 action RPs | QCI/EXE/PLN/INV have no action-level rows | VIEW has no action codes | `test_seed_view_only_roles_get_no_action_level_role_permissions` |
| OPR no ADMIN permissions | 0 ADMIN-family RPs for OPR | SoD invariant | `test_seed_opr_role_has_no_admin_action_permissions` |
| ADM no EXECUTE permissions | 0 EXECUTE-family RPs for ADM | SoD invariant | `test_seed_adm_role_has_no_execute_action_permissions` |
| Idempotent: no duplicate Permissions | Count unchanged on double run | `_get_or_create_*` | `test_seed_idempotent_no_duplicate_permission_rows` |
| Idempotent: no duplicate RolePermissions | Count unchanged on double run | `_get_or_create_*` + `UniqueConstraint` | `test_seed_idempotent_no_duplicate_role_permission_rows` |
| Idempotent: no duplicate Roles | Count unchanged on double run | `_get_or_create_role` | `test_seed_idempotent_no_duplicate_role_rows` |

---

## Files Inspected

- `docs/audit/p0-a-07e-rbac-action-registry-closeout-report.md`
- `docs/design/02_registry/action-code-registry.md`
- `backend/app/security/rbac.py` (full — `ACTION_CODE_REGISTRY`, `SYSTEM_ROLE_FAMILIES`, `seed_rbac_core`, all `_get_or_create_*` helpers)
- `backend/app/security/dependencies.py`
- `backend/app/models/rbac.py` (full — `Role`, `Permission`, `RolePermission`, `UserRole`, `RoleScope`, `Scope`, `UserRoleAssignment`)
- `backend/app/db/init_db.py` (seed call path, model imports)
- `backend/app/db/base.py`
- `backend/app/config/settings.py` (`auth_default_users_json` default)
- `backend/tests/test_access_service.py` (in-memory SQLite fixture pattern)
- `backend/tests/test_scope_rbac_foundation_alignment.py`
- `backend/tests/test_qa_foundation_authorization.py`
- `backend/tests/test_init_db_bootstrap_guard.py` (`_load_default_users` monkeypatch pattern)
- `backend/tests/test_rbac_action_registry_alignment.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_rbac_seed_alignment.py` | **Created** — 20 tests proving Permission/RolePermission seed correctness, SoD invariants, and idempotency |
| `backend/tests/test_rbac_action_registry_alignment.py` | **Updated** — added `admin.master_data.product_version.manage` to `_EXPECTED_ADMIN_MMD_CODES` (pre-existing drift fix; code already in registry and doc) |
| `.github/workflows/backend-ci.yml` | Added P0-A-08 step; updated CI summary text |
| `.github/workflows/pr-gate.yml` | Added `test_rbac_seed_alignment.py` and `test_impersonation_routes.py` (the latter was missing from P0-A-07D's pr-gate update) |

---

## Tests Added / Updated

### New: `backend/tests/test_rbac_seed_alignment.py` — 20 tests

| Test | Coverage |
|---|---|
| `test_seed_creates_permission_row_for_every_action_code` | All 21 action codes have Permission rows |
| `test_seed_permission_family_matches_registry` | Permission.family = ACTION_CODE_REGISTRY[code] for all 21 |
| `test_seed_permission_action_code_field_set` | Permission.action_code = code string for all 21 |
| `test_seed_creates_exactly_one_permission_per_action_code` | No duplicate Permission rows |
| `test_seed_p0a07b_downtime_reason_manage_permission_exists` | GAP-1 code: admin.downtime_reason.manage |
| `test_seed_p0a07c_security_event_read_permission_exists` | GAP-2 code: admin.security_event.read |
| `test_seed_p0a07d_impersonation_create_permission_exists` | GAP-3 code: admin.impersonation.create |
| `test_seed_p0a07d_impersonation_revoke_permission_exists` | GAP-3 code: admin.impersonation.revoke |
| `test_seed_creates_all_system_roles` | All 11 SYSTEM_ROLE_FAMILIES roles created |
| `test_seed_adm_role_gets_all_admin_family_action_permissions` | ADM → all ADMIN action RPs |
| `test_seed_ots_role_gets_all_admin_family_action_permissions` | OTS → all ADMIN action RPs |
| `test_seed_opr_role_gets_all_execute_family_action_permissions` | OPR → all EXECUTE action RPs |
| `test_seed_qal_role_gets_all_approve_family_action_permissions` | QAL → all APPROVE action RPs |
| `test_seed_pmg_role_gets_all_approve_family_action_permissions` | PMG → all APPROVE action RPs |
| `test_seed_view_only_roles_get_no_action_level_role_permissions` | QCI/EXE/PLN/INV have 0 action-level RPs |
| `test_seed_opr_role_has_no_admin_action_permissions` | SoD: OPR must not get ADMIN actions |
| `test_seed_adm_role_has_no_execute_action_permissions` | SoD: ADM must not get EXECUTE actions |
| `test_seed_idempotent_no_duplicate_permission_rows` | Double run: no duplicate Permission rows |
| `test_seed_idempotent_no_duplicate_role_permission_rows` | Double run: RolePermission count unchanged |
| `test_seed_idempotent_no_duplicate_role_rows` | Double run: no duplicate Role rows |

### Updated: `backend/tests/test_rbac_action_registry_alignment.py`

- Added `admin.master_data.product_version.manage` to `_EXPECTED_ADMIN_MMD_CODES`.
- Registry expected count: 20 → **21**.
- Change is a pure test data sync, not a behavior change.
- Code was already present in `rbac.py` and `action-code-registry.md` (added by MMD-BE-08A).

---

## CI Gate Changes

### `backend-ci.yml`

Added:
```yaml
# ── P0-A-08: RBAC seed alignment ─────────────────────────────────────
- name: P0-A-08 tests — RBAC role/permission DB seeding alignment
  shell: bash
  run: |
    cd backend
    python -m pytest -q \
      tests/test_rbac_seed_alignment.py \
      --tb=short
```

Updated CI summary text to mention `(08)`.

### `pr-gate.yml`

Added to targeted test list:
```
tests/test_impersonation_routes.py   (was missing from P0-A-07D's pr-gate update)
tests/test_rbac_seed_alignment.py
```

---

## Verification Commands Run

| Command | Expected | Classification |
|---|---|---|
| `pytest -q tests/test_rbac_seed_alignment.py` | 20 passed | PASS if all green |
| `pytest -q tests/test_rbac_action_registry_alignment.py tests/test_access_service.py tests/test_qa_foundation_authorization.py tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py` | 39 passed | PASS if all green |
| `pytest -q tests/test_downtime_reason_admin_routes.py tests/test_security_events_endpoint.py tests/test_admin_audit_security_events.py tests/test_impersonation_routes.py` | 17 passed | PASS if all green |
| `pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | 14 passed, 3 skipped | PASS_WITH_LOCAL_SKIPS |
| `alembic heads` | `0010 (head)` | PASS if single head |

---

## Results

| Command | Result | Classification |
|---|---|---|
| `test_rbac_seed_alignment.py` | **20 passed** | PASS |
| RBAC/auth regression (5 files) | **39 passed** (note: includes fix for pre-existing drift) | PASS |
| P0-A-07 route tests (4 files) | **17 passed** | PASS |
| Migration sanity (3 files) | **14 passed, 3 skipped** | PASS_WITH_LOCAL_SKIPS |
| `alembic heads` | **0010 (head)** | PASS |

**Total: 90 passed, 3 skipped, 0 failed.**

### Pre-existing drift noted and fixed

`test_action_code_registry_contains_exactly_canonical_set` was failing before my changes
because `admin.master_data.product_version.manage` was added to `rbac.py` and
`action-code-registry.md` by MMD-BE-08A (2026-05-03) but not to `_EXPECTED_ADMIN_MMD_CODES`.
This is classified as **FAIL_PREEXISTING** — it would have failed before P0-A-08 began.
Fixed by updating the expected set. Not a behavior change.

---

## Existing Gaps / Known Debts

| Item | Category | Notes |
|---|---|---|
| Live-DB skip tests | Environment gap | 3 tests require live Postgres; skip locally; CI Postgres service container covers |
| Admin UI for new action codes | Product scope | `admin.downtime_reason.manage`, `admin.security_event.read`, impersonation codes have no Admin UI consumer. Out of scope for P0-A series. |
| IEP CONFIGURE-family: no action codes | Registry gap | `IEP` has CONFIGURE in `SYSTEM_ROLE_FAMILIES` but no action code in `ACTION_CODE_REGISTRY` maps to CONFIGURE. IEP gets VIEW family-level row only. Intentional for now; add CONFIGURE action codes when IEP-specific governance slices run. |

---

## Scope Compliance

| Rule | Status |
|---|---|
| No production seed code changed | CONFIRMED — seed function untouched |
| No migrations added | CONFIRMED — `alembic heads` still `0010` |
| No route guards modified | CONFIRMED |
| No runtime auth evaluator changed | CONFIRMED |
| No frontend modified | CONFIRMED |
| No API endpoints added | CONFIRMED |
| No new roles created | CONFIRMED — only existing `SYSTEM_ROLE_FAMILIES` roles |
| No over-granting of roles | CONFIRMED — seed alignment follows `SYSTEM_ROLE_FAMILIES` matrix exactly |
| No MMD, Station Execution, Quality, Material changed | CONFIRMED |

---

## Risks

| Risk | Mitigation |
|---|---|
| Over-granting roles via seed | Seed follows `SYSTEM_ROLE_FAMILIES` matrix; tests explicitly verify OPR has no ADMIN, ADM has no EXECUTE |
| Seed idempotency failure | `_get_or_create_*` + existence check + DB `UniqueConstraint`; verified by 3 idempotency tests |
| Stale newly added action codes not seeded | Dynamic `ACTION_CODE_REGISTRY` iteration; `test_seed_creates_permission_row_for_every_action_code` fails if any code missing |
| SQLite behavior differences | SQLite FK enforcement disabled by default; RBAC tables use `String` FKs or internal integer FKs; tests isolate user-assignment seeding via monkeypatch |
| Registry doc diverging from runtime | Pre-existing: `test_action_code_registry_contains_exactly_canonical_set` (now updated) and `test_seed_creates_permission_row_for_every_action_code` both catch runtime-only drift |

---

## Recommended Next Slice

### P0-A-09 — IEP CONFIGURE Action Code Gap (if in scope)

`IEP` holds `{"VIEW", "CONFIGURE"}` in `SYSTEM_ROLE_FAMILIES` but no action code in
`ACTION_CODE_REGISTRY` maps to CONFIGURE. This means IEP's CONFIGURE family grant is
currently backed only by the family-level `Permission` row, not by any action-code-level
guard. If IEP-specific admin/configuration routes are planned (e.g., IE Process configuration),
a dedicated `admin.iep.*` or `configure.*` action code should be added.

**Alternative:** Continue with the next feature vertical (Quality, Material, MMD write
governance, or Station Execution hardening) depending on product roadmap priority.

---

## Stop Conditions Hit

None.

All mandatory files inspected. Seed function identified. Seed already aligned; Option A
selected. 20 new tests added and pass. Pre-existing test drift fixed. No production
code, migration, or runtime behavior changed. All verification commands run and reported.
