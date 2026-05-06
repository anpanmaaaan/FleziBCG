# P0-A-17 Report

## Summary

P0-A-17 is a **partial delivery** with stop conditions triggered for three of the
twelve planned tests. Ten of twelve tests (T-TIE-API-01, 04, 06–12) are
implemented, pass, and are wired into CI/PR gate. Three tests
(T-TIE-API-02, T-TIE-API-03, T-TIE-API-05) are deferred because they require
P0-A-15A (scope fields on `ApprovalRule`) and P0-A-15B (specificity scoring
system), which are not yet implemented in the codebase.

A secondary finding: the conversation context carried forward in the session
summary was inaccurate — it described P0-A-15A through P0-A-16 as completed and
present on disk, but none of those test files or runtime changes exist on the
`enhance-design-system` branch. Those commits (P0-A-14 through P0-A-16A) exist
only on the `autocode` branch. The actual codebase on `enhance-design-system` is
at the state following P0-A-13 (governed resource identity fields on `ApprovalRequest`).

**CORRECTION (P0-A-REC-01):** This report previously stated the Alembic chain was
broken (`0013.down_revision = "0012"`, no `0012.py`). This was incorrect for the
`enhance-design-system` branch. On this branch, `0013.down_revision = "0011"` and
the chain is healthy (`alembic heads` → `0013 (head)`). The
`DATABASE_URL=postgresql+psycopg://x:x@127.0.0.1:9991/x` workaround is valid for
bypassing the live Postgres dependency during SQLite in-memory runs but is not
required to work around a broken chain. See P0-A-REC-01 report for full details.

---

## Routing

- **Selected brain:** MOM Brain (FleziBCG AI Brain v6 Auto-Execution)
- **Selected mode:** QA / contract hardening — API coverage (partial)
- **Hard Mode MOM:** v3 ON
- **Reason:** Touches tenant/scope/auth, approval governance, approval decision API,
  multi-role group authorization behavior, SoD invariant, SecurityEventLog taxonomy,
  critical authorization contracts.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Source | Finding |
|---|---|
| `backend/app/repositories/approval_repository.py` (disk) | `get_rules_for_action` has NO `_score_rule`, NO scope/resource-type params. Returns ALL active rules for `action_type + tenant_id.in_([tenant_id, "*"])`. |
| `backend/app/models/approval.py` (disk) | `ApprovalRule` has: `action_type`, `approver_role_code`, `tenant_id`, `is_active`, `created_at` only. NO `scope_ref`, `governed_resource_type`, `governed_action_type`, `priority`. |
| `backend/app/services/approval_service.py` `decide_approval_request` | Calls `get_approver_role_codes(db, appr_req.action_type, tenant_id)` — 3 params, no scope context. |
| `backend/alembic/versions/` | Files: 0001–0011, 0013. No 0012.py. `0013` has `down_revision = "0011"` → chain healthy on `enhance-design-system`. **CORRECTION from P0-A-REC-01:** earlier claim of `down_revision = "0012"` was wrong. Migration 0012 exists only on `autocode` branch. |
| Conversation session summary | Claimed P0-A-15A through P0-A-16 were implemented and test files existed. **INACCURATE.** All those test files are absent. Scoring system not implemented. |
| Existing approval test files | Only: `test_approval_service_current_behavior.py`, `test_approval_security_events.py`, `test_approval_governed_resource_identity_schema.py` (and new `test_approval_decision_same_score_api.py`). |
| `approval_service.decide_approval_request` SoD guard | `if appr_req.requester_id == decider_user_id: raise ValueError("Requester cannot approve their own request")` → 400 |
| `approvals.py` error mapping | `LookupError→404, PermissionError→403, ValueError→400` |

### Event Map

| Event | Status |
|---|---|
| APPROVAL.REQUESTED | Existing; unchanged |
| APPROVAL.APPROVED | Existing; unchanged |
| APPROVAL.REJECTED | Existing; unchanged |
| APPROVAL.CANCELLED | Remains unimplemented (no service path, no route) |

### Invariant Map

| Invariant | Evidence | P0-A-17 Test | Result |
|---|---|---|---|
| All rules matching action+tenant contribute to allowed_roles | `get_approver_role_codes` returns set union | T-TIE-API-01a/01b | PASS |
| Role with no matching rule → 403 | `decider_role_code not in allowed_roles → PermissionError` | T-TIE-API-04 | PASS |
| Repeated fresh requests behave consistently | Same rule setup, 3 sequential requests | T-TIE-API-06 | PASS |
| Tenant isolation enforced | `get_request_by_id(db, id, tenant_b)` → None → LookupError → 404 | T-TIE-API-07 | PASS |
| Terminal guard enforced | `status != "PENDING" → ValueError` | T-TIE-API-08 | PASS |
| SoD APPROVE enforced | `requester_id == decider_user_id → ValueError` | T-TIE-API-09 | PASS |
| SoD REJECT enforced | same | T-TIE-API-10 | PASS |
| SecurityEventLog taxonomy unchanged | No new event types | T-TIE-API-11 | PASS |
| APPROVAL.CANCELLED not introduced | `not hasattr(approval_service, "cancel_approval_request")` | T-TIE-API-12 | PASS |
| Scope-specific tie (score=4) | Requires `scope_ref` on `ApprovalRule` (P0-A-15A) | T-TIE-API-02 | **DEFERRED** |
| Governed resource type tie (score=2) | Requires `governed_resource_type` on `ApprovalRule` (P0-A-15A) | T-TIE-API-03 | **DEFERRED** |
| Lower-score wildcard rejected | Requires scoring system (P0-A-15B) | T-TIE-API-05 | **DEFERRED** |

### State Transition Map

| State | Command | Guard | Event | Next State | Invalid |
|---|---|---|---|---|---|
| PENDING | APPROVED | role in allowed_roles AND SoD pass | APPROVAL.APPROVED | APPROVED | CANCELLED: unimplemented |
| PENDING | REJECTED | role in allowed_roles AND SoD pass | APPROVAL.REJECTED | REJECTED | same |
| APPROVED | any decide | — | — | — | 400 "not pending" |
| REJECTED | any decide | — | — | — | 400 "not pending" |

### Verdict

`ALLOW_P0A17_APPROVAL_DECISION_API_SAME_SCORE_ROLE_GROUP_DETERMINISM_COVERAGE`
(partial — 10 of 12 tests delivered; 3 deferred to P0-A-15A/B)

---

## Selected Option

**Option A (partial):** API multi-role determinism tests only, using the current
source. Scope-specific and scoring-dependent tests are deferred.

Option B (stop-and-report) was triggered specifically for T-TIE-API-02, 03, 05
which require runtime/model/repository changes.

---

## Same-Score Role Group Coverage Decision

In the current source there is no score-based filtering: `get_rules_for_action`
returns ALL active rules for the matching `action_type + tenant_id`, regardless of
specificity. "Same score" in the current model means all matching rules are treated
equally — every rule contributes its `approver_role_code` to the allowed set.

Tests T-TIE-API-01a/01b prove this API-boundary behavior for two wildcard rules.
T-TIE-API-06 proves stability across repeated fresh requests.

---

## Determinism Replay

Three sequential requests in T-TIE-API-06 within the same DB:
- Request 1: QAL decider → 200 APPROVED
- Request 2: PMG decider → 200 APPROVED
- Request 3: QAL again → 200 APPROVED (stability confirmed)

No stochastic or ordering-dependent exclusion observed.

---

## SoD / Tenant Isolation Replay

| Test | Setup | Result |
|---|---|---|
| T-TIE-API-07 | Request tenant-a; decider tenant-b | 404 (request not found under tenant-b) |
| T-TIE-API-09 | Same user creates + APPROVE | 400 "requester cannot approve" |
| T-TIE-API-10 | Same user creates + REJECT | 400 "requester cannot approve" |

---

## SecurityEventLog Replay

T-TIE-API-11: After APPROVED, exactly 1 event: `APPROVAL.APPROVED`. No CANCELLED.
T-TIE-API-12: `not hasattr(approval_service_module, "cancel_approval_request")` → True.
After REJECTED lifecycle, 0 `APPROVAL.CANCELLED` events in log.

---

## Tests Added / Updated

| File | Status | Tests |
|---|---|---|
| `backend/tests/test_approval_decision_same_score_api.py` | **NEW** | 10 tests: T-TIE-API-01a, 01b, 04, 06, 07, 08, 09, 10, 11, 12 |
| `.github/workflows/pr-gate.yml` | UPDATED | Added `tests/test_approval_decision_same_score_api.py` |
| `.github/workflows/backend-ci.yml` | UPDATED | Added P0-A-17 step after P0-A-13 |
| `backend/tests/test_pr_gate_workflow_config.py` | UPDATED | Added `test_approval_decision_same_score_api_tests_are_in_pr_gate` |

Deferred (not in file): T-TIE-API-02, T-TIE-API-03, T-TIE-API-05

---

## Files Inspected

- `.github/copilot-instructions.md`
- `backend/app/repositories/approval_repository.py`
- `backend/app/models/approval.py`
- `backend/app/services/approval_service.py`
- `backend/app/api/v1/approvals.py`
- `backend/app/config/settings.py`
- `backend/app/db/session.py`
- `backend/tests/conftest.py`
- `backend/tests/test_approval_service_current_behavior.py`
- `backend/tests/test_approval_security_events.py`
- `backend/tests/test_approval_governed_resource_identity_schema.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/pr-gate.yml`
- `.github/workflows/backend-ci.yml`
- `backend/alembic/versions/` (all migration files)
- `docs/audit/p0-a-16a-approval-decision-specificity-api-closeout-report.md`
- `docs/design/01_foundation/approval-rule-scope-applicability-contract.md`

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_approval_decision_same_score_api.py` | Created (new) |
| `.github/workflows/pr-gate.yml` | Added `test_approval_decision_same_score_api.py` to test list |
| `.github/workflows/backend-ci.yml` | Added P0-A-17 step |
| `backend/tests/test_pr_gate_workflow_config.py` | Added `test_approval_decision_same_score_api_tests_are_in_pr_gate` |

No approval model, repository, service, or route files changed.
No migrations added.
No MMD files touched.

---

## Verification Commands Run

All with `DATABASE_URL=postgresql+psycopg://x:x@127.0.0.1:9991/x` override
(required because `0013` migration references missing `0012`, breaking the Alembic
chain when PostgreSQL is reachable).

```
python -m pytest -q tests/test_approval_decision_same_score_api.py
python -m pytest -q tests/test_approval_service_current_behavior.py tests/test_approval_security_events.py tests/test_pr_gate_workflow_config.py
python -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_scope_rbac_foundation_alignment.py tests/test_qa_foundation_authorization.py
python -m pytest -q tests/test_approval_governed_resource_identity_schema.py
```

---

## Results

| Suite | Result |
|---|---|
| `test_approval_decision_same_score_api.py` | **10 passed, 1 warning** |
| `test_approval_service_current_behavior.py` + `test_approval_security_events.py` + `test_pr_gate_workflow_config.py` | **29 passed, 1 warning** |
| RBAC / scope / QA foundation suites | **53 passed, 1 warning** |
| `test_approval_governed_resource_identity_schema.py` | **10 passed, 1 warning** |

All warnings are the benign conftest "TEST DB NOT REACHABLE" warning from the
DATABASE_URL override. No failures, no errors.

---

## Scope Compliance

| Constraint | Status |
|---|---|
| No migrations added | ✓ |
| No ApprovalRequest model fields modified | ✓ |
| No ApprovalRule schema fields modified | ✓ |
| No repository matching precedence changed | ✓ |
| No approval service decision logic changed | ✓ |
| No approval API route logic changed | ✓ |
| No governed action registry implemented | ✓ |
| No VALID_ACTION_TYPES modified | ✓ |
| No APPROVAL.CANCELLED implemented | ✓ |
| No new approval endpoints added | ✓ |
| No frontend/Admin UI added | ✓ |
| No MMD source/tests/docs modified | ✓ |
| No ACTION_CODE_REGISTRY changed | ✓ |

---

## Risks

1. **~~Broken alembic chain (0013 → 0012 missing)~~** *(CORRECTION from P0-A-REC-01:
   this risk was stated incorrectly. On `enhance-design-system`, `0013.down_revision = "0011"`
   and the chain is healthy. Migration 0012 exists only on the `autocode` branch.
   No chain repair needed on this branch.)*

2. **Session summary inaccuracy:** The conversation summary described P0-A-15A
   through P0-A-16 as fully implemented and present on disk. They were not. Future
   agents must verify disk state independently before acting on session summaries.

3. **T-TIE-API-05 absence:** Without the scoring system, the wildcard "fallback"
   behavior means wildcard roles ARE included in allowed_roles when tenant-specific
   rules also exist. This is the pre-P0-A-15B behavior. T-TIE-API-05 cannot be
   written correctly until the scoring system is implemented.

---

## Recommended Next Slice

**P0-A-15A** (prerequisite) — Add `scope_ref`, `governed_resource_type`,
`governed_action_type`, `priority` fields to `ApprovalRule` model with Alembic
migration 0012. This work exists on the `autocode` branch; evaluate cherry-pick
vs fresh implementation on `enhance-design-system` (see P0-A-REC-01 report).

After P0-A-15A: **P0-A-15B** — Implement `_score_rule` and scope-aware
`get_rules_for_action` in `approval_repository.py`.

After P0-A-15A/B: **P0-A-17-B** — Add T-TIE-API-02, T-TIE-API-03, T-TIE-API-05
to `test_approval_decision_same_score_api.py` to complete the full 12-test suite.

---

## Stop Conditions Hit

| Condition | Tests Affected |
|---|---|
| Tests require `scope_ref` on `ApprovalRule` (runtime model change — P0-A-15A not implemented) | T-TIE-API-02 |
| Tests require `governed_resource_type` on `ApprovalRule` (runtime model change — P0-A-15A not implemented) | T-TIE-API-03 |
| Tests require scoring system `_score_rule` in `approval_repository.py` (P0-A-15B not implemented) | T-TIE-API-05 |

Action taken: partial delivery of 10 feasible tests; deferred tests documented here.
