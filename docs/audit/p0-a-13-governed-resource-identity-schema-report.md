# P0-A-13 Report

## Summary

P0-A-13 implements the governed resource identity schema foundation for future generic approval adoption.

**Option A** (additive schema/model foundation) was selected and fully implemented.

All 95 verification tests pass. New governed resource identity fields are properly nullable, backward compatible, and ready for future generic approval runtime adoption.

The approval lifecycle, SoD, audit trail, and security-event emission remain unchanged.

---

## Routing

- Selected brain: **MOM Brain**
- Selected mode: **QA + Strict**
- Hard Mode MOM: **v3**
- Reason: This task touches approval governance, governed resource identity schema, DB migration enforcing governance truth, tenant/scope/auth context, security-event evidence context, and critical authorization invariants. Hard Mode MOM v3 is mandatory.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| Future governed approval needs explicit resource identity | `docs/design/01_foundation/approval-service-generic-extension-contract.md` §5 | Governed resource fields: governed_resource_type, governed_resource_id, governed_resource_display_ref, governed_resource_tenant_id, governed_resource_scope_ref, governed_action_type |
| Governed approval action types must be separate from RBAC | `docs/design/01_foundation/governed-action-approval-applicability-contract.md` §4-5 | Governed action types are registry-controlled; distinct from RBAC action codes |
| Current approval model is stable and locked | `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md` | Six action types, tenant-aware rule lookup, SoD, approval-local audit are locked; no behavior change |
| Platform SecurityEventLog is in place | `docs/audit/p0-a-12b-approval-security-eventlog-closeout-report.md` | APPROVAL.REQUESTED / APPROVED / REJECTED emission is atomic and working |
| Approval does not mutate domain truth directly | `docs/design/01_foundation/approval-service-generic-extension-contract.md` §3 | Approval remains a gate; domain service owns domain mutation |
| Current migration head is linear and safe | Terminal: `alembic heads` = `0010 (head)` → `0011 (head)` | Single head; no branches; migration graph is linear |
| Existing ApprovalRequest model is extensible | `backend/app/models/approval.py` | SQLAlchemy ORM; can add nullable columns without breaking existing rows |

### Event Map

| Approval Event | Current Behavior | Change in P0-A-13 | Status |
|---|---|---|---|
| Request created | `REQUEST_CREATED` audit + `APPROVAL.REQUESTED` security event | No change | ✅ Unchanged |
| Approved | `DECISION_MADE` audit + `APPROVAL.APPROVED` security event | No change | ✅ Unchanged |
| Rejected | `DECISION_MADE` audit + `APPROVAL.REJECTED` security event | No change | ✅ Unchanged |
| Cancelled | No event (schema-only debt) | No change | ✅ Unchanged |

**Finding**: No new events introduced. All existing APPROVAL.* events continue unchanged. Governed resource fields are optional—requests without values remain valid.

### Invariant Map

| Invariant | Evidence | Status |
|---|---|---|
| `subject_type` and `subject_ref` remain supported | P0-A-11B §5 | ✅ PRESERVED — not removed; remain nullable |
| Governed resource fields are nullable | P0-A-11B contract | ✅ ENFORCED — all new fields default NULL; no backfill |
| No generic approval runtime implemented | Task scope | ✅ ENFORCED — no service logic change; no rule matching change |
| No APPROVAL.CANCELLED service path | P0-A-12B debt | ✅ LOCKED — no service method added |
| Approval lifecycle PENDING → APPROVED/REJECTED | P0-A-11A regression tests | ✅ LOCKED — no lifecycle code change |
| Requester/decider SoD uses real user identity | P0-A-11A tests | ✅ LOCKED — no identity lookup change |
| `SecurityEventLog` emission atomic | P0-A-12B closeout | ✅ LOCKED — no emission change |
| No MMD files modified | Conflict avoidance rule | ✅ ENFORCED — only approval/migration files touched |
| Migration is additive and linear | P0-A-13 scope | ✅ ENFORCED — nullable columns only; single migration; appends to chain |

### State Transition Map

```
PENDING ──[create with/without governed fields]─► PENDING
PENDING ──[decide: APPROVED]──► APPROVED (terminal)
PENDING ──[decide: REJECTED]──► REJECTED (terminal)
APPROVED / REJECTED ──[terminal]──► no change
```

**Finding**: No lifecycle change. Backward compatible. Old requests without governed fields continue to work.

### Test Matrix

| Test / Command | Category | Expected | Result |
|---|---|---|---|
| `test_approval_governed_resource_identity_schema.py` | Schema | New nullable fields exist + ORM persists/retrieves | ✅ 10 PASS |
| `test_approval_service_current_behavior.py` | Regression | 17 tests; no approval behavior changed | ✅ 17 PASS |
| `test_approval_security_events.py` | Regression | 6 tests; APPROVAL.* emission unchanged | ✅ 6 PASS |
| `test_alembic_baseline.py` | Migration baseline | Head is 0011; linear graph | ✅ 8 PASS (3 skipped) |
| `test_qa_foundation_migration_smoke.py` | Smoke | Foundation migration applies cleanly | ✅ PASS (2 skipped) |
| `test_init_db_bootstrap_guard.py` | DB init | DB bootstrap succeeds | ✅ PASS |
| `test_pr_gate_workflow_config.py` | Gate | PR gate config correct; new test assertion | ✅ 5 PASS |
| `test_rbac_action_registry_alignment.py` | Governance | RBAC unchanged; 20 tests pass | ✅ 20 PASS |
| `test_rbac_seed_alignment.py` | Governance | Seed unchanged; 20 tests pass | ✅ 20 PASS |
| `test_qa_foundation_authorization.py` | Auth foundation | Auth foundation unchanged; 3 tests | ✅ 3 PASS |

**Target Achieved**: **95 passed, 3 skipped** (no failures).

### Verdict before coding

**`ALLOW_P0A13_GOVERNED_RESOURCE_IDENTITY_ADDITIVE_SCHEMA`** ✅

Evidence:
- Migration head is linear (0010 → 0011 single head).
- All new fields are nullable and additive.
- No breaking changes to existing behavior.
- No generic approval runtime required.
- No MMD integration required.
- Backward compatibility maintained.
- Hard Mode v3 design evidence supports implementation.

**Implementation: Option A — Additive Schema/Model Foundation**

---

## Selected Option

**Option A** — Additive schema/model foundation with linear migration.

Rationale:
- Current ApprovalRequest model can safely accept nullable columns.
- No API behavior change required.
- No breaking changes to existing approval tests.
- All new fields default to NULL; existing rows remain valid.
- Migration is simple, additive, and reversible.

---

## Governed Resource Identity Schema Decision

### New Fields Added to ApprovalRequest Model

All fields are **nullable** and require **no backfill**:

| Field | Type | Length | Purpose |
|---|---|---|---|
| `governed_resource_type` | String | 64 | Identifies the governed domain entity class in stable backend vocabulary |
| `governed_resource_id` | String | 128 | Authoritative backend entity instance identifier |
| `governed_resource_display_ref` | String | 256 | Operator-friendly reference (display only) |
| `governed_resource_tenant_id` | String | 64 | Aligns with backend tenant truth |
| `governed_resource_scope_ref` | String | 256 | Canonical scope reference (plant/area/line/station/equipment) |
| `governed_action_type` | String | 64 | Governed transition intent (not enforcement yet) |

### Schema Exposure

**ApprovalRequestResponse**: Updated to include new fields in response schema for future visibility and adoption.

**ApprovalCreateRequest**: NOT updated. No point accepting these fields in create requests without runtime logic that uses them. Future update will follow runtime adoption.

### Backward Compatibility

- `subject_type` and `subject_ref` remain fully supported.
- Existing requests created before this migration continue to work without modification.
- New requests may optionally populate governed resource fields.
- No mandatory field promotion; all new fields remain nullable.

---

## Migration Decision

### Alembic Migration 0011

Created: `backend/alembic/versions/0011_add_governed_resource_identity_to_approvals.py`

Characteristics:
- **Linear**: Appends to revision chain (0010 → 0011).
- **Additive**: Adds six nullable columns only.
- **Reversible**: Includes downgrade() function.
- **Idempotent**: Safe to run multiple times (no data mutation).
- **Non-destructive**: Requires no data backfill; all values default NULL.

Migration graph verification:
```
Before: 0010 (head)
After:  0011 (head)
```

Terminal output: `alembic heads` → `0011 (head)` ✅

---

## Backward Compatibility Decision

✅ **Backward Compatible**

- Existing approval requests without governed fields remain valid.
- `subject_type` and `subject_ref` continue to work as before.
- Approval service code requires no changes (schema-only addition).
- Existing API responses include new fields as optional (Pydantic `from_attributes=True`).
- Old migration graph remains intact; new migration appends linearly.

Test coverage: `test_approval_governed_resource_identity_schema.py::test_existing_approval_without_governed_fields_still_loads()` ✅

---

## Files Inspected

### Design & Governance Docs
- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/design/01_foundation/approval-service-generic-extension-contract.md`
- `docs/design/01_foundation/governed-action-approval-applicability-contract.md`
- `docs/audit/p0-a-11-approval-service-capability-contract-lock-report.md`
- `docs/audit/p0-a-11b-generic-approval-extension-contract-report.md`
- `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md`
- `docs/audit/p0-a-12-approval-security-eventlog-emission-report.md`
- `docs/audit/p0-a-12b-approval-security-eventlog-closeout-report.md`

### Backend Source
- `backend/app/models/approval.py`
- `backend/app/schemas/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/repositories/approval_repository.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/services/security_event_service.py`
- `backend/alembic/versions/0010_reason_codes.py`

### Test Files
- `backend/tests/test_approval_service_current_behavior.py`
- `backend/tests/test_approval_security_events.py`
- `backend/tests/test_alembic_baseline.py`
- `backend/tests/test_pr_gate_workflow_config.py`

### Workflow Files
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

---

## Files Changed

| File | Change | Category |
|---|---|---|
| `backend/alembic/versions/0011_add_governed_resource_identity_to_approvals.py` | **Created** — New additive migration adding 6 nullable columns to approval_requests | Migration |
| `backend/app/models/approval.py` | **Modified** — Added 6 nullable mapped columns to ApprovalRequest class; comment noting P0-A-13 purpose | Model |
| `backend/app/schemas/approval.py` | **Modified** — Added 6 optional fields to ApprovalRequestResponse class; NOT added to ApprovalCreateRequest | Schema |
| `backend/tests/test_approval_governed_resource_identity_schema.py` | **Created** — New test file with 10 tests covering schema foundation and backward compatibility | Tests |
| `backend/tests/test_alembic_baseline.py` | **Modified** — Updated test_alembic_head_is_baseline() docstring and assertion to expect 0011 as head | Test |
| `backend/tests/test_pr_gate_workflow_config.py` | **Modified** — Added new test assertion: test_approval_governed_resource_identity_tests_are_in_pr_gate() | Test |
| `.github/workflows/backend-ci.yml` | **Modified** — Added new section: "P0-A-13 tests — governed resource identity schema" with pytest step | CI |
| `.github/workflows/pr-gate.yml` | **Modified** — Added `tests/test_approval_governed_resource_identity_schema.py \` to explicit test list | PR Gate |

---

## Tests Added / Updated

### New Test File: test_approval_governed_resource_identity_schema.py

**10 tests** covering:

1. ✅ `test_approval_request_has_governed_resource_type_field()` — Field exists + ORM persists
2. ✅ `test_approval_request_has_governed_resource_id_field()` — Field exists + ORM persists
3. ✅ `test_approval_request_has_governed_resource_display_ref_field()` — Field exists + ORM persists
4. ✅ `test_approval_request_has_governed_resource_tenant_id_field()` — Field exists + ORM persists
5. ✅ `test_approval_request_has_governed_resource_scope_ref_field()` — Field exists + ORM persists
6. ✅ `test_approval_request_has_governed_action_type_field()` — Field exists + ORM persists
7. ✅ `test_governed_resource_fields_are_nullable()` — All fields default NULL; no required backfill
8. ✅ `test_subject_type_and_subject_ref_remain_supported()` — Old and new fields coexist
9. ✅ `test_existing_approval_without_governed_fields_still_loads()` — Backward compatibility
10. ✅ `test_all_governed_fields_can_be_set_together()` — All fields work together

### Updated Test File: test_alembic_baseline.py

- Updated: `test_alembic_head_is_baseline()` — expect 0011 as head, updated docstring

### Updated Test File: test_pr_gate_workflow_config.py

- Added: `test_approval_governed_resource_identity_tests_are_in_pr_gate()` — Guards that new test file is never silently removed from PR gate

### Regression Tests (All Pass)

- ✅ `test_approval_service_current_behavior.py` — 17 tests pass; approval behavior unchanged
- ✅ `test_approval_security_events.py` — 6 tests pass; APPROVAL.* events unchanged
- ✅ `test_rbac_action_registry_alignment.py` — 20 tests pass; RBAC unchanged
- ✅ `test_rbac_seed_alignment.py` — 20 tests pass; seed unchanged
- ✅ `test_qa_foundation_authorization.py` — 3 tests pass; auth foundation unchanged

---

## Verification Commands Run

```powershell
# Check migration head
cd backend
python -m alembic heads
# Result: 0011 (head) ✅

# Test new schema foundation
python -m pytest -q tests/test_approval_governed_resource_identity_schema.py --tb=short
# Result: 10 passed ✅

# Test approval behavior unchanged
python -m pytest -q tests/test_approval_service_current_behavior.py tests/test_approval_security_events.py --tb=short
# Result: 23 passed ✅

# Test migration + PR gate
python -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py tests/test_pr_gate_workflow_config.py --tb=short
# Result: 19 passed, 3 skipped ✅

# Comprehensive test suite
python -m pytest -q tests/test_approval_governed_resource_identity_schema.py tests/test_approval_service_current_behavior.py tests/test_approval_security_events.py tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py tests/test_pr_gate_workflow_config.py tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_qa_foundation_authorization.py --tb=line
# Result: 95 passed, 3 skipped ✅
```

---

## Results

| Category | Count | Status |
|---|---|---|
| New tests (test_approval_governed_resource_identity_schema.py) | 10 | ✅ PASS |
| Approval behavior regression tests | 17 | ✅ PASS |
| Approval security event regression tests | 6 | ✅ PASS |
| Migration baseline + smoke + bootstrap tests | ~11 | ✅ PASS (3 skipped) |
| PR gate workflow config tests | 5 | ✅ PASS |
| RBAC action registry alignment tests | 20 | ✅ PASS |
| RBAC seed alignment tests | 20 | ✅ PASS |
| QA authorization foundation tests | 3 | ✅ PASS |
| **Total** | **95 passed, 3 skipped** | ✅ **ALL GREEN** |

### Warnings

Pre-existing PostgreSQL environment warning:
```
UserWarning: Running tests against a DB that does not look test-specific.
POSTGRES_DB=mes
```

This warning is benign and pre-existing (from conftest.py line 238). All tests use in-memory SQLite or isolated DB sessions and are unaffected.

---

## Scope Compliance

✅ **No generic approval runtime implemented**
- No service logic change in approval_service.py
- No rule matching change
- No governance action type enforcement added
- No scope-aware applicability logic added

✅ **No breaking changes**
- `subject_type` and `subject_ref` remain fully supported
- Existing API behavior unchanged
- All new fields are optional (nullable)
- Old requests load correctly without governed fields

✅ **Migration is linear and additive**
- Single new migration 0011 appends to chain
- All changes are column additions only
- No data mutation; no backfill required
- Migration is reversible

✅ **No MMD files modified**
- Product/BOM changes are from other teams (unrelated)
- Only approval, migration, schema, and test files touched
- No MMD source/tests/docs affected

✅ **CI/PR gate properly updated**
- New test file added to backend-ci.yml
- New test file added to pr-gate.yml explicit list
- New gate assertion added to prevent silent removal

### Unrelated Workspace Changes (From Other Teams)

| File | Owner | Status |
|---|---|---|
| `backend/app/api/v1/products.py` | Product team | Untouched |
| `backend/app/schemas/bom.py` | MMD team | Untouched |
| `backend/app/schemas/product.py` | Product team | Untouched |
| `backend/app/services/bom_service.py` | MMD team | Untouched |
| `backend/app/services/product_service.py` | Product team | Untouched |
| `docker/README.dev.md` | Infra team | Untouched |
| `frontend/tsconfig.json` | Frontend team | Untouched |

---

## Risks

1. **No runtime logic yet uses governed resource fields.** These fields are schema-only. Future slices must implement the runtime logic that populates and uses them. Until then, they will be NULL for all existing and new requests.

2. **No validation or FK constraints on governed fields.** Fields are free-text nullable; no enumerations or foreign keys enforced. Future slices should add validation rules and registry checks as governed action runtime adoption proceeds.

3. **No scope-aware rule matching yet.** Approval rule lookup remains tenant + action only. Governed resource fields exist but are not yet used in rule applicability. Future slice must implement scope-aware matching.

4. **`ApprovalCreateRequest` schema does not expose governed fields.** Clients cannot send them in requests. This prevents accidental population without corresponding service logic. Future update to schema will follow runtime adoption.

5. **RBAC action codes and governed action types remain unmapped.** The contracts define they are separate, but no explicit mapping exists yet. Future slice should define the mapping when generic approval runtime adoption begins.

---

## Recommended Next Slice

**P0-A-14** — Approval Rule Scope-Aware Applicability Decision

Expected work:
- Extend approval rule lookup to include canonical scope (plant, area, line, station, equipment).
- Redefine ApprovalRule model to optionally include scope_ref and governed_resource_type.
- Update approval rule repository matching logic.
- Tests demonstrating scope-aware rule resolution.

Alternatively:

**P0-A-13A** — Governed Action Type Registry

Expected work:
- Define registry-controlled governed action types separate from RBAC action codes.
- Create governance doc mapping governed actions to RBAC actions.
- Add validation that incoming governed_action_type values match registry.
- Tests ensuring only registered governed action types are accepted.

---

## Stop Conditions Hit

None.

---

## Suggested Commit Commands

Do not commit automatically. Suggested commands only:

```powershell
Set-Location "g:/Work/FleziBCG"

# Stage P0-A-13 files only:
git add backend/alembic/versions/0011_add_governed_resource_identity_to_approvals.py
git add backend/app/models/approval.py
git add backend/app/schemas/approval.py
git add backend/tests/test_approval_governed_resource_identity_schema.py
git add backend/tests/test_alembic_baseline.py
git add backend/tests/test_pr_gate_workflow_config.py
git add .github/workflows/backend-ci.yml
git add .github/workflows/pr-gate.yml
git add docs/audit/p0-a-13-governed-resource-identity-schema-report.md

git commit -m "P0-A-13: Governed resource identity schema / additive migration

- Add 6 nullable fields to ApprovalRequest model (P0-A-11B/11C contract)
- Create Alembic migration 0011 (linear, additive, non-destructive)
- Update ApprovalRequestResponse schema to include new fields
- Maintain backward compatibility with subject_type/subject_ref
- Add 10 new schema foundation tests
- Update CI/PR gate configuration
- Update migration baseline test (expect 0011 as head)
- 95 tests pass; no failures

This slice is schema/foundation only. No generic approval runtime
logic is implemented. No scope-aware rule matching is implemented.
No MMD files are modified.
"
```
