# P0-A-15C Report

## Summary

P0-A-15C bridges optional governed context into `ApprovalCreateRequest` schema and `create_approval_request` service. `ApprovalRequest` already had all 6 nullable governed fields from P0-A-13. This slice allows callers to populate those fields at creation time, enabling the P0-A-15B scope-aware matching to work end-to-end.

All 13 bridge tests (T-CB-01 through T-CB-10, including two negative tests for T-CB-04 and T-CB-05) pass. All existing approval, RBAC, and scope foundation tests remain green (131 passed, 3 skipped across full suite).

No migration was added. No model was modified. No registry enforcement was introduced. VALID_ACTION_TYPES is unchanged.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** Strict
- **Hard Mode MOM:** v3 ON
- **Reason:** Task touches approval governance, governed resource identity, tenant/scope authorization foundation, SecurityEventLog payload context, and critical authorization invariant.

---

## Hard Mode MOM v3 Gate

**Design Evidence Extract:**

| Evidence | Source |
|---|---|
| `ApprovalRequest` has 6 nullable governed fields from P0-A-13 migration 0011 | `backend/app/models/approval.py` |
| `ApprovalRequestResponse` already exposes all 6 governed fields | `backend/app/schemas/approval.py` (response schema) |
| `ApprovalCreateRequest` had NO governed context fields before this slice | `backend/app/schemas/approval.py` (create schema) |
| `create_approval_request` did not map governed context before this slice | `backend/app/services/approval_service.py` |
| P0-A-15B decision-time matching reads `governed_resource_scope_ref`, `governed_resource_type`, `governed_action_type` from persisted `ApprovalRequest` | `backend/app/services/approval_service.py` L179-184 |
| `APPROVAL.REQUESTED` detail: `action_type= requester_role= subject_type= subject_ref=` | `backend/app/services/approval_service.py` |
| P0-A-15B scope-aware matching fully operational | P0-A-15B-01 closeout report |

**Event Map:**

| Event | Change |
|---|---|
| `APPROVAL.REQUESTED` | Detail optionally appended with governed context if provided; structure unchanged |
| `APPROVAL.APPROVED` | Unchanged |
| `APPROVAL.REJECTED` | Unchanged |
| `APPROVAL.CANCELLED` | Not implemented (schema-only debt) |
| New event types | None |

**Invariant Map:**

| Invariant | Test |
|---|---|
| Legacy create without governed context remains valid | T-CB-01 |
| Governed context fields are optional (default=None) | T-CB-01, T-CB-07 |
| Governed context persisted if provided | T-CB-02 |
| Response schema exposes persisted governed context | T-CB-03 |
| `APPROVAL.REQUESTED` includes governed context if provided | T-CB-04 |
| Decision-time matching uses persisted governed context end-to-end | T-CB-05 |
| `subject_type`/`subject_ref` unchanged | T-CB-06 |
| No governed action registry enforcement | T-CB-07 |
| `VALID_ACTION_TYPES` unchanged | T-CB-08 |
| No `APPROVAL.CANCELLED` service path | T-CB-09 |
| Existing behavior suite green | T-CB-10 |
| No migration added | ✓ |
| SoD invariant (requester ≠ decider) unchanged | ✓ |

**State Transition Map:** No lifecycle change. PENDING → APPROVED/REJECTED (terminal). CANCELLED schema-only debt, no service path.

**Verdict:** `ALLOW_P0A15C_APPROVAL_CREATE_REQUEST_GOVERNED_CONTEXT_BRIDGE`

---

## Selected Option

**Option A — Optional create request bridge only.**

`ApprovalCreateRequest` safely adds 6 optional fields. `ApprovalRequest` model already has those fields from P0-A-13. Service maps fields at construction time. No API break. All existing tests remain green.

---

## Create Request Bridge Decision

Added 6 optional fields to `ApprovalCreateRequest`:
- `governed_resource_type: str | None = Field(default=None, max_length=128)`
- `governed_resource_id: str | None = Field(default=None, max_length=256)`
- `governed_resource_display_ref: str | None = Field(default=None, max_length=256)`
- `governed_resource_tenant_id: str | None = Field(default=None, max_length=64)`
- `governed_resource_scope_ref: str | None = Field(default=None, max_length=256)`
- `governed_action_type: str | None = Field(default=None, max_length=128)`

Updated `create_approval_request` to map all 6 fields to `ApprovalRequest` at ORM construction time.

---

## Backward Compatibility Decision

All 6 new fields default to `None`. Existing callers that do not provide them receive identical behavior: governed fields are `None` on the persisted request, and scope-aware matching falls back to legacy wildcard rules per P0-A-15B scoring algorithm.

---

## SecurityEventLog Payload Decision

`APPROVAL.REQUESTED` detail string is extended conditionally. If any of `governed_resource_type`, `governed_resource_scope_ref`, or `governed_action_type` is non-None, the detail string appends:

```
governed_resource_type=<value> governed_resource_scope_ref=<value> governed_action_type=<value>
```

If none are provided, the detail string is unchanged from the pre-P0-A-15C format.

---

## End-to-End Matching Decision

P0-A-15B matching is now fully activated end-to-end:
1. Caller provides governed context in `ApprovalCreateRequest`
2. Bridge persists governed context to `ApprovalRequest` (this slice)
3. `decide_approval_request` reads governed context from `ApprovalRequest` (P0-A-15B)
4. `get_approver_role_codes` uses scope-aware scoring to select applicable rules (P0-A-15B)

---

## Tests Added / Updated

### New file: `backend/tests/test_approval_create_governed_context_bridge.py`

| Test | ID | Status |
|---|---|---|
| `test_legacy_create_without_governed_context_succeeds` | T-CB-01 | PASS |
| `test_create_with_governed_context_persists_all_fields` | T-CB-02 | PASS |
| `test_response_schema_exposes_governed_context_fields` | T-CB-03 | PASS |
| `test_approval_requested_event_includes_governed_context_when_provided` | T-CB-04 | PASS |
| `test_approval_requested_event_without_governed_context_is_clean` | T-CB-04 (negative) | PASS |
| `test_end_to_end_scope_aware_matching_with_persisted_governed_context` | T-CB-05 | PASS |
| `test_end_to_end_scope_aware_matching_rejects_wrong_role` | T-CB-05 (negative) | PASS |
| `test_subject_type_and_subject_ref_remain_present_and_correct` | T-CB-06 | PASS |
| `test_arbitrary_governed_action_type_is_accepted_without_registry_enforcement` | T-CB-07 | PASS |
| `test_valid_action_types_unchanged` | T-CB-08 | PASS |
| `test_unknown_action_type_raises_value_error` | T-CB-08 (negative) | PASS |
| `test_no_cancel_approval_request_function_exists` | T-CB-09 | PASS |
| `test_existing_approval_service_create_behavior_is_unaffected` | T-CB-10 | PASS |

**Total new tests: 13**

### Updated: `backend/tests/test_pr_gate_workflow_config.py`

Added `test_approval_create_governed_context_bridge_tests_are_in_pr_gate`.

---

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `.github/copilot-instructions-hard-mode-mom-v3-addendum.md`
- `backend/app/schemas/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/models/approval.py`
- `backend/app/api/v1/approvals.py`
- `backend/tests/test_approval_security_events.py`
- `backend/tests/test_approval_rule_scope_aware_matching.py`
- `backend/tests/test_approval_governed_resource_identity_schema.py`
- `backend/tests/test_approval_service_current_behavior.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/pr-gate.yml`
- `.github/workflows/backend-ci.yml`
- `docs/audit/p0-a-15b-01-approval-rule-scope-aware-matching-closeout-report.md` (via session summary)

---

## Files Changed

| File | Change |
|---|---|
| `backend/app/schemas/approval.py` | Added 6 optional governed context fields to `ApprovalCreateRequest` |
| `backend/app/services/approval_service.py` | `create_approval_request` maps governed context to ORM; `APPROVAL.REQUESTED` detail extended |
| `backend/tests/test_approval_create_governed_context_bridge.py` | NEW — T-CB-01..T-CB-10 (13 tests) |
| `backend/tests/test_pr_gate_workflow_config.py` | Added P0-A-15C guard test |
| `.github/workflows/pr-gate.yml` | Added `test_approval_create_governed_context_bridge.py` |
| `.github/workflows/backend-ci.yml` | Added P0-A-15C step |

---

## Verification Commands Run

```
git status --short
cd backend
python -m pytest -q tests/test_approval_create_governed_context_bridge.py
python -m pytest -q tests/test_approval_rule_scope_aware_matching.py tests/test_approval_rule_scope_applicability_schema.py tests/test_approval_service_current_behavior.py tests/test_approval_governed_resource_identity_schema.py tests/test_approval_security_events.py tests/test_pr_gate_workflow_config.py
python -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_scope_rbac_foundation_alignment.py tests/test_qa_foundation_authorization.py
python -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
```

---

## Results

| Command | Result |
|---|---|
| `git status --short` | PASS — only P0-A-15C files modified + unrelated pre-existing changes |
| `test_approval_create_governed_context_bridge.py` | PASS — 13 passed, 1 warning |
| approval regression suite (6 test files) | PASS — 65 passed, 1 warning |
| RBAC/scope suite (4 test files) | PASS — 53 passed, 1 warning |
| alembic/smoke suite (3 test files) | PASS — 14 passed, 3 skipped, 1 warning |
| **Combined** | **145 passed, 3 skipped, 0 failed** |

Warning is benign: `conftest.py:234 UserWarning: Running tests against a DB that does not look test-specific. POSTGRES_DB=mes` — SQLite in-memory tests are unaffected.

---

## Scope Compliance

| Rule | Status |
|---|---|
| No migration added | ✓ |
| `ApprovalRequest` model not modified | ✓ |
| `ApprovalRule` schema fields not modified | ✓ |
| Repository matching precedence not changed | ✓ |
| No runtime governed action registry implemented | ✓ |
| `governed_action_type` not globally enforced | ✓ |
| `VALID_ACTION_TYPES` unchanged | ✓ |
| `MASTER_DATA` action type not added | ✓ |
| `APPROVAL.CANCELLED` not implemented | ✓ |
| No new approval endpoints | ✓ |
| No frontend/Admin UI added | ✓ |
| No MMD files touched | ✓ |
| No route guards changed | ✓ |
| `ACTION_CODE_REGISTRY` not changed | ✓ |
| No tests weakened | ✓ |

---

## Risks

- None identified. All new fields are optional and additive. SoD invariant and decision-time matching logic are unchanged. The detail string extension is append-only and backward-compatible.

---

## Recommended Next Slice

**P0-A-15D** (suggested): End-to-end integration test for the full approval lifecycle with governed context — from HTTP `POST /approvals` (API layer) through service, repository matching, and decision, using the FastAPI test client. This would validate the HTTP layer accepts the new optional fields without regression.

Alternatively: Begin the first domain-specific caller slice that populates governed context when requesting approvals for QC operations.

---

## Stop Conditions Hit

None.
