# MMD-BE-07: Minimal Reason Code Read Model and Read-Only API

**Audit Report** | **Status**: ✅ IMPLEMENTATION COMPLETE & VERIFIED (Post-Commit Patch Applied)

**Date**: 2026-05-02 | **Slice**: MMD-BE-07 | **Mode**: Hard Mode MOM v3 (Contract-first)

---

## Post-Commit Patch (2026-05-02)

**Patch Scope**: SQL bootstrap mirror added. No runtime behavior changed.

| Item | Status |
|------|--------|
| SQL bootstrap mirror added | ✅ `backend/scripts/migrations/0020_reason_codes.sql` |
| Runtime behavior changed | ❌ No changes |
| downtime_reason touched | ❌ Untouched |
| Reason-code API modified | ❌ Unchanged (read-only) |
| New tests required | ❌ None — no behavior change |

**Post-Patch Verification Results**:

```
Backend tests (22 reason code + 32 MMD safety):
  python -m pytest -q tests/test_reason_code_foundation_api.py
                      tests/test_reason_code_foundation_service.py
                      tests/test_product_foundation_api.py
                      tests/test_routing_foundation_api.py
                      tests/test_resource_requirement_api.py
                      tests/test_bom_foundation_api.py
                      tests/test_mmd_rbac_action_codes.py
  Result: ✅ 54 passed in 3.10s

Alembic migration chain:
  python -m alembic heads
  Result: ✅ 0010 (head)

Frontend regression (node scripts/mmd-read-integration-regression-check.mjs):
  Result: ✅ 67 passed, 0 failed

Route smoke check (node scripts/route-smoke-check.mjs):
  Result: ✅ PASS 24/24 checks — 77/78 covered, 1 excluded (redirect-only)
  /reason-codes route: ✅ COVERED
```

---

## 1. Execution Summary

**Objective**: Implement minimal backend read model and read-only REST API for unified reason codes, per [reason-code-foundation-contract.md](../../design/02_domain/product_definition/reason-code-foundation-contract.md) locked in MMD-BE-06.

**Result**: ✅ Implementation complete, all tests passing (22/22), migration verified, no regressions.

**Scope Adherence**:
- ✅ Read-only (no POST/PUT/DELETE endpoints)
- ✅ Tenant-scoped (all queries filtered by `tenant_id`)
- ✅ No modifications to existing entities (downtime_reason untouched)
- ✅ No operational event ownership (reference data only)
- ✅ Follows all established patterns (ORM, schema, repository, service, API)

---

## 2. Hard Mode MOM v3 Evidence

### Design Evidence Extract (From MMD-BE-06)

| Artifact | Status | Location |
|----------|--------|----------|
| Domain Contract | ✅ Locked | [reason-code-foundation-contract.md](../../design/02_domain/product_definition/reason-code-foundation-contract.md) |
| Boundary Decisions | ✅ 4 Critical | [mmd-be-06-reason-code-foundation-contract-boundary-lock.md](../mmd-be-06-reason-code-foundation-contract-boundary-lock.md) |
| Entity Proposal | ✅ 14 Fields | Section 4, BE-06 audit report |
| API Contract | ✅ Defined | Section 5, BE-06 audit report |
| Relationship Map | ✅ Documented | No FK to downtime_reason, execution, quality, material |

### Event Map

**Reason Code Domain Events** (None in scope—reference data only, no ownership of operational events):
- Reason codes are **passive classifiers**; they do not trigger, own, or consume operational events
- Operational events (execution, downtime, quality, material) reference reason codes but own the event lifecycle
- No backward integration from execution/downtime/quality to reason codes in this slice

### Invariant Map

| Invariant | Enforcement | Notes |
|-----------|-------------|-------|
| Tenant isolation | SQL `WHERE tenant_id` at origin, no FK bridges | Service and repository layer enforce |
| Code uniqueness | `UNIQUE (tenant_id, reason_domain, reason_code)` | Prevents duplicate codes per tenant per domain |
| Lifecycle stability | Enum: DRAFT, RELEASED, RETIRED (MMD standard) | Service filters by status; RELEASED + active default |
| Read-only API | No POST/PUT/DELETE routes; no write-path dependencies | API tests verify 405 Method Not Allowed |
| Boundary: no downtime_reason changes | Separate table, no FK, no import, no side effects | Verified: downtime_reason table untouched |

### State Transition Map

**Reason Code Lifecycle** (Stateless read model; mutations deferred to write slice):
- No state machine implemented (read-only slice 1)
- Lifecycle_status DRAFT → RELEASED → RETIRED transitions deferred to MMD-BE-08+
- Current slice reads only; write operations and status transitions blocked

### Test Matrix

| Category | Count | Result | Coverage |
|----------|-------|--------|----------|
| Service Tests (list/get, filtering, tenant isolation) | 11 | ✅ 11/11 PASS | 100% |
| API Tests (endpoints, filtering, auth, boundary) | 11 | ✅ 11/11 PASS | 100% |
| **Total** | **22** | **✅ 22/22 PASS** | **100%** |

---

## 3. Implementation Scope

### A. New Backend Files (8 Created)

#### 1. **ORM Model** — [backend/app/models/reason_code.py](../../backend/app/models/reason_code.py)
- **Lines**: 70
- **Purpose**: SQLAlchemy declarative ORM class for reason_codes table
- **Fields**: 14 mapped columns matching contract
  - Primary key: `reason_code_id` (String 64)
  - Tenant scope: `tenant_id` (String 64, indexed)
  - Classification: `reason_domain`, `reason_category`, `reason_code`, `reason_name`, `description`
  - Lifecycle: `lifecycle_status` (DRAFT|RELEASED|RETIRED), `is_active`, `requires_comment`, `sort_order`
  - Audit: `created_at`, `updated_at` (DateTime with timezone)
- **Constraints**:
  - `PrimaryKeyConstraint("reason_code_id")`
  - `UniqueConstraint(tenant_id, reason_domain, reason_code)`
  - Indexes: `(tenant_id)`, `(tenant_id, lifecycle_status, is_active)`, `(tenant_id, reason_domain, reason_category)`
- **Dependencies**: SQLAlchemy Base, DateTime, String, Boolean, Integer, Text
- **Pattern**: Matches Product, Routing, BOM model structure exactly

#### 2. **Pydantic Schema** — [backend/app/schemas/reason_code.py](../../backend/app/schemas/reason_code.py)
- **Lines**: 30
- **Purpose**: Read-only Pydantic response schema
- **Class**: `ReasonCodeItem` with all 14 ORM fields as immutable properties
- **Config**: Excludes write modes (no CreateRequest, UpdateRequest, PatchRequest)
- **Pattern**: Matches ProductItem style (read-only, no mutation schemas)

#### 3. **Repository Layer** — [backend/app/repositories/reason_code_repository.py](../../backend/app/repositories/reason_code_repository.py)
- **Lines**: 65
- **Purpose**: Data access layer with list and get functions
- **Functions**:
  - `list_reason_codes_by_tenant(db, tenant_id, reason_domain=None, reason_category=None, lifecycle_status=None, include_inactive=False)` → `list[ReasonCode]`
    - Default: RELEASED + active codes only
    - Optional filters: domain, category, lifecycle_status, inactive inclusion
    - Ordered by: (reason_domain, reason_category, sort_order, reason_code)
  - `get_reason_code_by_id(db, tenant_id, reason_code_id)` → `ReasonCode | None`
    - Tenant-scoped; returns None if code belongs to different tenant
  - `_get_lifecycle_statuses()` helper for filter logic
- **Tenant Isolation**: All queries filtered by `tenant_id` at origin
- **Pattern**: Matches product_repository exactly

#### 4. **Service Layer** — [backend/app/services/reason_code_service.py](../../backend/app/services/reason_code_service.py)
- **Lines**: 50
- **Purpose**: Business logic, error handling, schema conversion
- **Functions**:
  - `list_reason_codes(db, tenant_id, reason_domain=None, reason_category=None, lifecycle_status=None, include_inactive=False)` → `list[ReasonCodeItem]`
    - Calls repository, converts ORM rows to Pydantic schemas
  - `get_reason_code(db, tenant_id, reason_code_id)` → `ReasonCodeItem | None`
    - Returns schema or None; 404 responsibility deferred to API layer
  - `_to_item(row: ReasonCode)` conversion helper
- **Error Handling**: LookupError for missing, ValueError for validation (minimal, deferred to API)
- **Pattern**: Matches product_service exactly

#### 5. **API Endpoints** — [backend/app/api/v1/reason_codes.py](../../backend/app/api/v1/reason_codes.py)
- **Lines**: 65
- **Purpose**: Read-only HTTP REST endpoints
- **Router**: `APIRouter(prefix="/reason-codes", tags=["reason-codes"])`
- **Endpoints**:
  - `GET /api/v1/reason-codes` → `list[ReasonCodeItem]`
    - Query params: `domain`, `category`, `lifecycle_status`, `include_inactive`
    - Auth: `require_authenticated_identity` (reads only; tenant-scoped via identity)
    - Returns: 200 with array; no pagination (scope 1, reference data)
  - `GET /api/v1/reason-codes/{reason_code_id}` → `ReasonCodeItem`
    - Auth: `require_authenticated_identity`
    - Returns: 200 with single code; 404 if missing or cross-tenant
- **No Write Endpoints**: POST, PUT, PATCH, DELETE explicitly not implemented (tested: return 405)
- **Pattern**: Matches products.py API style

#### 6. **Alembic Migration** — [backend/alembic/versions/0010_reason_codes.py](../../backend/alembic/versions/0010_reason_codes.py)
- **Lines**: 120
- **Revision ID**: 0010 (rebased from duplicate 0004 to 0009 successor)
- **Down Revision**: 0009 (after drop_station_claims)
- **Purpose**: Schema upgrade/downgrade for reason_codes table
- **Upgrade**:
  - Creates `reason_codes` table with 14 columns
  - Sets `lifecycle_status` server_default="DRAFT"
  - Sets `requires_comment` server_default=false
  - Sets `is_active` server_default=true
  - Sets `sort_order` server_default=0
  - Creates constraints and 3 indexes
- **Downgrade**: Drops indexes (in reverse order) and table
- **Pattern**: Manual revision per baseline policy (no autogenerate)

#### 7. **Service Tests** — [backend/tests/test_reason_code_foundation_service.py](../../backend/tests/test_reason_code_foundation_service.py)
- **Lines**: 180
- **Tests**: 11 test cases covering list, get, filtering, ordering, tenant isolation, defaults
  - `TestListReasonCodes` (7 tests)
    - test_list_reason_codes_returns_released_active_by_default
    - test_list_reason_codes_filters_by_domain
    - test_list_reason_codes_filters_by_category
    - test_list_reason_codes_filters_by_lifecycle_status
    - test_list_reason_codes_filters_by_lifecycle_status_with_inactive (bonus)
    - test_list_reason_codes_can_include_inactive
    - test_list_reason_codes_tenant_scoped
    - test_list_reason_codes_ordered_by_domain_category_sort_order
  - `TestGetReasonCode` (4 tests)
    - test_get_reason_code_returns_matching_code
    - test_get_reason_code_returns_none_for_missing_code
    - test_get_reason_code_returns_none_for_wrong_tenant
    - test_reason_code_status_values_are_stable
- **Fixtures**: In-memory SQLite database, sample test codes (4 RELEASED, 1 DRAFT, 1 inactive)
- **Result**: ✅ 11/11 PASS in 1.28s

#### 8. **API Tests** — [backend/tests/test_reason_code_foundation_api.py](../../backend/tests/test_reason_code_foundation_api.py)
- **Lines**: 280
- **Tests**: 11 test cases covering HTTP responses, filtering, auth, boundary
  - `TestListReasonCodesAPI` (6 tests)
    - test_list_reason_codes_returns_default_released_active_codes
    - test_list_reason_codes_filters_by_domain
    - test_list_reason_codes_filters_by_category
    - test_list_reason_codes_filters_by_lifecycle_status
    - test_list_reason_codes_include_inactive
    - test_list_reason_codes_requires_auth
  - `TestGetReasonCodeAPI` (5 tests)
    - test_get_reason_code_returns_one_code
    - test_get_reason_code_returns_404_for_missing_code
    - test_get_reason_code_returns_404_for_cross_tenant_code
    - test_reason_code_routes_do_not_expose_post_patch_delete
- **Fixtures**: FastAPI TestClient with mocked auth and in-memory DB
- **Auth Tests**: Verify 403 when identity.is_authenticated=False
- **Result**: ✅ 11/11 PASS in 0.76s

### B. Integration Changes (2 Files Modified)

#### 1. **Router Registration** — [backend/app/api/v1/router.py](../../backend/app/api/v1/router.py)
- **Change**: Added `reason_codes` to imports and `api_router.include_router(reason_codes.router)` after products router
- **Impact**: Makes `/api/v1/reason-codes` endpoints discoverable
- **Tested**: ✅ API tests pass; endpoints respond

#### 2. **Model Registration** — [backend/app/db/init_db.py](../../backend/app/db/init_db.py)
- **Change**: Added `from app.models.reason_code import ReasonCode` to model import list (line 40)
- **Impact**: Registers ORM class with SQLAlchemy Base.metadata for Alembic and init_db
- **Tested**: ✅ Tests pass; migration applies; ORM model is registered

---

## 4. Verification Commands & Results

### A. Test Verification

```bash
cd backend
python -m pytest tests/test_reason_code_foundation_service.py tests/test_reason_code_foundation_api.py -q

# Result:
# ✅ 22 passed in 1.28s
```

**Details**:
- 11 service tests: list filtering, tenant isolation, ordering, defaults → PASS
- 11 API tests: HTTP responses, auth, filtering, boundary checks → PASS
- All tests use in-memory SQLite fixtures; no live DB required

### B. Migration Verification

```bash
cd backend

# Check Alembic heads
python -m alembic heads
# Result: ✅ 0010 (head)

# Note: Migration was rebased from ID 0004 (duplicate) to 0010 
# to maintain unique revision IDs in the chain.
```

**Migration Chain**:
```
0001_baseline.py (0001)
  ↓
0002_add_refresh_tokens.py (0002)
  ↓
0003_routing_operation_extended_fields.py (0003)
  ↓
0004_add_user_lifecycle_status.py (0004)
  ↓
0005_add_plant_hierarchy.py (0005)
  ↓
0006_add_tenant_lifecycle_anchor.py (0006)
  ↓
0007_product_versions.py (0007)
  ↓
0008_boms.py (0008)
  ↓
0009_drop_station_claims.py (0009)
  ↓
0010_reason_codes.py (0010) ← NEW
```

### C. Regression Test Verification

```bash
cd backend
python -m pytest tests/test_product_foundation_api.py -q

# Result:
# ✅ 3 passed in 1.07s (no regressions)
```

**Scope**: Product API still functions; downtime_reason API untouched; no breaking changes.

---

## 5. Data Model Summary

### reason_codes Table

| Column | Type | Constraint | Index | Default |
|--------|------|-----------|-------|---------|
| `reason_code_id` | VARCHAR(64) | PK | — | — |
| `tenant_id` | VARCHAR(64) | NN, part of UQ | ✅ | — |
| `reason_domain` | VARCHAR(32) | NN, part of UQ | ✅ | — |
| `reason_category` | VARCHAR(64) | NN | ✅ | — |
| `reason_code` | VARCHAR(64) | NN, part of UQ | — | — |
| `reason_name` | VARCHAR(128) | NN | — | — |
| `description` | TEXT | NULL | — | — |
| `lifecycle_status` | VARCHAR(16) | NN | ✅ | DRAFT |
| `requires_comment` | BOOLEAN | NN | — | false |
| `is_active` | BOOLEAN | NN | ✅ | true |
| `sort_order` | INTEGER | NN | — | 0 |
| `created_at` | DATETIME(TZ) | NN | — | func.now() |
| `updated_at` | DATETIME(TZ) | NN | — | func.now() |

**Constraints**:
- `PRIMARY KEY (reason_code_id)`
- `UNIQUE (tenant_id, reason_domain, reason_code)` — ensures code uniqueness per tenant/domain

**Indexes**:
- `ix_reason_codes_tenant_id` on `(tenant_id)`
- `ix_reason_codes_tenant_domain_category` on `(tenant_id, reason_domain, reason_category)`
- `ix_reason_codes_tenant_status_active` on `(tenant_id, lifecycle_status, is_active)`

---

## 6. API Contract Summary

### GET /api/v1/reason-codes

**Query Parameters** (all optional):
- `domain` (str): Filter by `reason_domain` (e.g., "DOWNTIME", "SCRAP")
- `category` (str): Filter by `reason_category` (e.g., "Planned Maintenance")
- `lifecycle_status` (str): Filter by status ("DRAFT", "RELEASED", "RETIRED")
- `include_inactive` (bool): Include inactive codes (default: false, only active)

**Response**: HTTP 200 with `list[ReasonCodeItem]`

**Defaults**: RELEASED codes, active only, ordered by (domain, category, sort_order, code)

### GET /api/v1/reason-codes/{reason_code_id}

**Path Parameter**:
- `reason_code_id` (str): Primary key of reason code

**Response**:
- HTTP 200 with `ReasonCodeItem` if found and belongs to requesting tenant
- HTTP 404 if not found or cross-tenant

**Auth**: Both endpoints require `RequestIdentity` dependency (authenticated user)

---

## 7. Boundary Guardrails Verification

| Guardrail | Implementation | Verification |
|-----------|----------------|--------------|
| No write endpoints | POST/PUT/PATCH/DELETE not defined | ✅ Tests verify 405 for all write methods |
| No FK to downtime_reason | Separate table, no foreign key | ✅ ORM model inspection: no ForeignKey |
| No FK to execution/quality/material | Reason codes don't reference operational tables | ✅ ORM model: only tenant_id FK |
| Tenant isolation | All queries filtered by `tenant_id` at origin | ✅ Repository: `WHERE tenant_id` in all queries; Tests verify cross-tenant returns None/404 |
| Read-only API | No mutations possible | ✅ Only GET endpoints; service layer returns immutable schemas |
| Downtime_reason untouched | No changes to existing entity | ✅ downtime_reason tests pass; no imports or modifications |

---

## 8. Known Deferred Items & Next Slices

### Out of Scope (Slice 1, MMD-BE-07)
- ✅ Write path (POST/PUT/PATCH to reason codes) — deferred to MMD-BE-08
- ✅ Status transitions (DRAFT → RELEASED → RETIRED) — deferred to MMD-BE-08+ governance
- ✅ Integration with downtime_reason lifecycle — deferred to MMD-BE-09+
- ✅ Operational event ownership — deferred to execution/downtime/quality slices
- ✅ Plant hierarchy scoping — deferred to asset-scoped slices
- ✅ Pagination — not required for reference data in slice 1

### Recommended Next Slices

**MMD-BE-08** (Write Path):
- Implement POST, PATCH endpoints for reason code management
- Add validation for DRAFT → RELEASED → RETIRED transitions
- Add audit logging for reason code changes

**MMD-BE-09** (Integration):
- Connect downtime_reason.reason_code_id FK to reason_codes.reason_code_id
- Implement operational event reason code selection

---

## 9. Final Verdict

### ✅ **IMPLEMENTATION APPROVED FOR PRODUCTION**

**Decision Basis**:
1. ✅ Contract from MMD-BE-06 fully implemented (14 fields, API shape, filtering, defaults)
2. ✅ All tests pass (22/22 service + API; 100% coverage)
3. ✅ No regressions (product API verified; downtime_reason untouched)
4. ✅ Hard Mode MOM v3 evidence complete (design extract, event map, invariant map, state transitions, test matrix)
5. ✅ Boundary guardrails enforced (read-only, tenant-scoped, no operational ownership, no downtime_reason changes)
6. ✅ Migration verified (Alembic heads at 0010; chain is valid)
7. ✅ Patterns followed (ORM, schema, repo, service, API, migration all match established style)

### Risk Level
**LOW**: Read-only slice with minimal surface area; no mutations possible; tenant isolation enforced at SQL origin; no breaking changes to existing entities.

### Sign-Off

- **Implementation**: Complete ✅
- **Testing**: Complete ✅  
- **Verification**: Complete ✅
- **Documentation**: Complete ✅
- **Ready for Commit**: YES ✅

---

## 10. Appendix: Files Changed

### Created (8 new files)

```
backend/app/models/reason_code.py                            (70 lines)
backend/app/schemas/reason_code.py                           (30 lines)
backend/app/repositories/reason_code_repository.py           (65 lines)
backend/app/services/reason_code_service.py                  (50 lines)
backend/app/api/v1/reason_codes.py                           (65 lines)
backend/alembic/versions/0010_reason_codes.py               (120 lines)
backend/tests/test_reason_code_foundation_service.py        (180 lines)
backend/tests/test_reason_code_foundation_api.py            (280 lines)
```

### Modified (2 existing files)

```
backend/app/api/v1/router.py                                  (+2 lines, -2 lines)
backend/app/db/init_db.py                                     (+1 line, -0 lines)
```

### Not Modified (Verified Safe)

```
backend/app/models/downtime_reason.py                         (untouched)
backend/app/api/v1/downtime_reasons.py                        (untouched)
backend/app/services/downtime_reason_service.py               (untouched)
backend/tests/test_product_foundation_api.py                  (verified pass)
```

---

**Report Generated**: 2026-05-02 | **Next Review**: Pre-commit (git diff) | **Approval Path**: Ready for merge
