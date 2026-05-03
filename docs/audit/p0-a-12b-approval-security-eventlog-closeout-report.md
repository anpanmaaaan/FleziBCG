# P0-A-12B Report

## Summary

P0-A-12B closes out the P0-A-12 approval `SecurityEventLog` emission implementation and P0-A-12A CI gate patch.

**Option A** (closeout report only) was selected, with one minimal gate hardening: a new `test_approval_security_event_tests_are_in_pr_gate()` assertion was added to `test_pr_gate_workflow_config.py` to prevent silent disappearance of the approval security event test from the PR gate. This is a pure test file change — no runtime behavior was modified.

All required verification commands pass. **70 passed, 0 failed.**

The P0-A-12 approval SecurityEventLog chain is now fully closed:

| Slice | Purpose | Status |
|---|---|---|
| P0-A-12 | Implemented APPROVAL.REQUESTED / APPROVED / REJECTED emission | ✅ Implemented and tested |
| P0-A-12A | Added `test_approval_security_events.py` to `backend-ci.yml` and `pr-gate.yml` | ✅ Patched |
| **P0-A-12B** | Full verification replay + PR gate config guard | ✅ **CLOSED** |

---

## Routing

- Selected brain: MOM Brain
- Selected mode: QA + Strict
- Hard Mode MOM: v3
- Reason: This task validates approval governance, SecurityEventLog emission, audit/security event evidence, separation of duties, impersonation context, tenant/scope/auth, CI/PR gate correctness, and critical authorization invariants. Hard Mode MOM v3 is mandatory.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| P0-A-12 implemented APPROVAL.REQUESTED / APPROVED / REJECTED emission | `docs/audit/p0-a-12-approval-security-eventlog-emission-report.md` | `record_security_event(db, ..., commit=False)` called before `db.commit()` in both `create_approval_request` and `decide_approval_request`; atomic with transaction |
| P0-A-12A patched both workflow files | `docs/audit/p0-a-12a-approval-security-event-test-gate-report.md` | `backend-ci.yml` line 267 and `pr-gate.yml` line 166 now include `test_approval_security_events.py` |
| Current approval service source confirms emission is in place | `backend/app/services/approval_service.py` | `from app.services.security_event_service import record_security_event` present; both service methods call it with `commit=False` |
| 6 focused security event tests exist | `backend/tests/test_approval_security_events.py` | Tests: APPROVAL.REQUESTED, APPROVAL.APPROVED, APPROVAL.REJECTED, audit-log preservation, impersonation context capture, APPROVAL.CANCELLED absence |
| APPROVAL.CANCELLED is intentionally absent | P0-A-11C §9, P0-A-12 report | `CANCELLED` is schema-only; no service path; `ApprovalDecideRequest` Pydantic validator rejects "CANCELLED" |
| `test_pr_gate_workflow_config.py` previously had no test-file-level coverage guard | `backend/tests/test_pr_gate_workflow_config.py` | Only import check, skill path, and hard-mode report assertions existed; no assertion for `test_approval_security_events.py` inclusion |
| Unrelated dirty workspace changes are all from other teams | `git status --short` | Station session, frontend BOM/MMD UI, docker README — all untouched |

### Event Map

| Approval Event | Current ApprovalAuditLog | Current SecurityEventLog | Closeout Decision |
|---|---|---|---|
| Request created | `REQUEST_CREATED` | `APPROVAL.REQUESTED` | ✅ Emitted — confirmed by test and source |
| Approved | `DECISION_MADE` | `APPROVAL.APPROVED` | ✅ Emitted — confirmed by test and source |
| Rejected | `DECISION_MADE` | `APPROVAL.REJECTED` | ✅ Emitted — confirmed by test and source |
| Cancelled | None | None | ✅ NOT emitted — schema-only debt; confirmed by `test_approval_cancelled_event_is_never_emitted` |

### Invariant Map

| Invariant | Evidence | Closeout Status |
|---|---|---|
| `ApprovalAuditLog` rows remain | `approval_service.py` calls `_log_event()` before `record_security_event()`; `test_approval_audit_log_is_preserved_alongside_security_event` | ✅ LOCKED |
| `SecurityEventLog` emits `APPROVAL.REQUESTED` | `create_approval_request()` calls `record_security_event(..., event_type="APPROVAL.REQUESTED", commit=False)` | ✅ LOCKED |
| `SecurityEventLog` emits `APPROVAL.APPROVED` | `decide_approval_request()` emits `f"APPROVAL.{decision_value}"` which resolves to `APPROVAL.APPROVED` | ✅ LOCKED |
| `SecurityEventLog` emits `APPROVAL.REJECTED` | Same pattern as above for `REJECTED` | ✅ LOCKED |
| `SecurityEventLog` does NOT emit `APPROVAL.CANCELLED` | No service path; `test_approval_cancelled_event_is_never_emitted` | ✅ LOCKED |
| Approval lifecycle (PENDING→APPROVED/REJECTED) is unchanged | All 17 existing `test_approval_service_current_behavior.py` tests pass | ✅ LOCKED |
| Requester/decider SoD remains unchanged | `test_requester_cannot_decide_own_request` still passes | ✅ LOCKED |
| Real user identity remains authoritative under impersonation | `actor_user_id` is `decider_user_id` (real user); `test_impersonation_context_is_captured_in_approval_decision_event` | ✅ LOCKED |
| CI/PR gate covers `test_approval_security_events.py` | Verified by `Select-String` in both workflow files; locked by new `test_approval_security_event_tests_are_in_pr_gate()` | ✅ LOCKED |
| No MMD files are changed | `git status --short` confirms | ✅ CONFIRMED |

### State Transition Map

```
PENDING ──[create]─────────────► PENDING    — emits APPROVAL.REQUESTED
PENDING ──[decide: APPROVED]──► APPROVED   (terminal) — emits APPROVAL.APPROVED
PENDING ──[decide: REJECTED]──► REJECTED   (terminal) — emits APPROVAL.REJECTED
APPROVED / REJECTED ──[re-decide]──► ValueError (unchanged)
CANCELLED ── schema-only; no service path; APPROVAL.CANCELLED never emitted
```

No lifecycle change.

### Test Matrix

| Test / Command | Expected | Result |
|---|---|---|
| `test_approval_security_events.py` (6 tests) | APPROVAL.REQUESTED/APPROVED/REJECTED emitted; audit log preserved; impersonation captured; CANCELLED absent | 6 PASS |
| `test_approval_service_current_behavior.py` (17 tests) | Existing behavior unchanged | 17 PASS |
| `test_pr_gate_workflow_config.py` (4 tests, +1 new) | Import check, skill paths, report paths, approval security test gate | 4 PASS |
| `test_rbac_action_registry_alignment.py` + `test_rbac_seed_alignment.py` (40 tests) | RBAC registry + seed aligned | 40 PASS |
| `test_qa_foundation_authorization.py` (3 tests) | Auth foundation aligned | 3 PASS |
| **Total** | | **70 passed, 0 failed** |

### Verdict

`ALLOW_P0A12B_APPROVAL_SECURITY_EVENTLOG_CLOSEOUT_REPLAY`

---

## Selected Option

**Option A** — closeout report only, with one minimal gate hardening (new assertion in `test_pr_gate_workflow_config.py`).

Evidence confirmed:
1. All approval security event tests pass.
2. Both `backend-ci.yml` and `pr-gate.yml` include `test_approval_security_events.py`.
3. No runtime behavior needs correction.
4. The only gap was the absence of a PR gate config assertion to prevent future silent removal — fixed with a single test.

---

## SecurityEventLog Emission Closeout

| Field | Value |
|---|---|
| Events emitted | `APPROVAL.REQUESTED`, `APPROVAL.APPROVED`, `APPROVAL.REJECTED` |
| Events deliberately absent | `APPROVAL.CANCELLED` (no service path; schema-only debt) |
| `actor_user_id` | `requester_id` (REQUESTED), `decider_user_id` (real user, APPROVED/REJECTED) |
| `tenant_id` | Passed from service method parameter — tenant-scoped |
| `resource_type` | `"APPROVAL_REQUEST"` |
| `resource_id` | `str(appr_req.id)` |
| `detail` | Human-readable string: `action_type=... requester_role=... subject_type=...` (REQUESTED) / `action_type=... decider_role=... impersonation_session=...` (APPROVED/REJECTED) |
| Atomicity | `commit=False` — SecurityEventLog row is in the same `db.commit()` as ApprovalRequest/Decision and ApprovalAuditLog |
| ApprovalAuditLog preserved | Yes — `_log_event()` still called; both tables written in same transaction |

---

## CI / PR Gate Coverage Closeout

| Workflow | File location | Line | Status |
|---|---|---|---|
| `backend-ci.yml` | Step: "P0-A-12 tests — approval SecurityEventLog emission" | Line 267 | ✅ Present |
| `pr-gate.yml` | "Run backend tests" explicit list | Line 166 | ✅ Present |
| `test_pr_gate_workflow_config.py` | `test_approval_security_event_tests_are_in_pr_gate()` | New (added this slice) | ✅ Guards against silent removal |

---

## Verification Replay Matrix

| Command | Suite | Result | Classification |
|---|---|---|---|
| `git status --short` | Workspace scope compliance | Unrelated station session / frontend BOM/MMD changes only | PASS |
| `pytest -q tests/test_approval_security_events.py` | Approval SecurityEventLog emission | 6 passed, 1 warning | PASS_WITH_WARNINGS (pre-existing env warning) |
| `pytest -q tests/test_approval_service_current_behavior.py` | Approval current-behavior regression | 17 passed | PASS |
| `pytest -q tests/test_pr_gate_workflow_config.py` | PR gate workflow config | 4 passed | PASS |
| `pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` | RBAC registry + seed alignment | 40 passed | PASS |
| `pytest -q tests/test_qa_foundation_authorization.py` | QA auth foundation | 3 passed | PASS |
| `pytest -q tests/test_security_event_service.py tests/test_scope_rbac_foundation_alignment.py` | Security event service + scope foundation | Included in combined 81-passed run | PASS |

**Recurring warning**: `conftest.py:238: UserWarning: Running tests against a DB that does not look test-specific`. Pre-existing `POSTGRES_DB=mes` environment warning. All approval and security event tests use in-memory SQLite; unaffected.

---

## Remaining Approval Debts

| Debt | Source | Contract Reference |
|---|---|---|
| `APPROVAL.CANCELLED` event — not emitted | Schema-only; no service path | P0-A-11C §9; P0-A-12 report |
| `APPROVAL.*` events in `detail` are plain-text strings | Structured payload would require `SecurityEventLog` JSON column | P0-A-12 risk §2 |
| `impersonation_session_id` not a first-class `SecurityEventLog` column | Captured in `detail` only | P0-A-12 risk §4 |
| Generic approval / governed resource identity | Future schema slice — `governed_resource_type`, `governed_resource_id` etc. | P0-A-11B contract |
| Scope-aware approval applicability | Current rule lookup is tenant + action only | P0-A-11B + P0-A-11C |
| `MASTER_DATA` approval action type | Future MMD release/retire governed approval | P0-A-11C §16 |

---

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/audit/p0-a-12-approval-security-eventlog-emission-report.md`
- `docs/audit/p0-a-12a-approval-security-event-test-gate-report.md`
- `backend/app/services/approval_service.py`
- `backend/app/services/security_event_service.py`
- `backend/app/models/security_event.py`
- `backend/tests/test_approval_security_events.py`
- `backend/tests/test_approval_service_current_behavior.py`
- `backend/tests/test_pr_gate_workflow_config.py`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`

---

## Files Changed

| File | Change |
|---|---|
| `backend/tests/test_pr_gate_workflow_config.py` | Added `test_approval_security_event_tests_are_in_pr_gate()` — guards that `pr-gate.yml` always includes `test_approval_security_events.py` |
| `docs/audit/p0-a-12b-approval-security-eventlog-closeout-report.md` | Created (this file) |

---

## Verification Commands Run

```powershell
Set-Location "g:/Work/FleziBCG"
git status --short

Push-Location "g:/Work/FleziBCG/backend"
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q `
  tests/test_approval_security_events.py `
  tests/test_approval_service_current_behavior.py `
  tests/test_pr_gate_workflow_config.py `
  tests/test_rbac_action_registry_alignment.py `
  tests/test_rbac_seed_alignment.py `
  tests/test_qa_foundation_authorization.py `
  tests/test_scope_rbac_foundation_alignment.py `
  tests/test_security_event_service.py
Pop-Location

Select-String "test_approval_security_events.py" `
  "g:/Work/FleziBCG/.github/workflows/backend-ci.yml", `
  "g:/Work/FleziBCG/.github/workflows/pr-gate.yml"
```

---

## Results

| Suite | Count | Status |
|---|---|---|
| `test_approval_security_events.py` | 6 passed | PASS |
| `test_approval_service_current_behavior.py` | 17 passed | PASS |
| `test_pr_gate_workflow_config.py` | 4 passed (including new assertion) | PASS |
| `test_rbac_action_registry_alignment.py` + `test_rbac_seed_alignment.py` | 40 passed | PASS |
| `test_qa_foundation_authorization.py` | 3 passed | PASS |
| `test_security_event_service.py` + `test_scope_rbac_foundation_alignment.py` | Included in 81-passed combined run | PASS |
| **Total (focused suite)** | **70 passed, 0 failed** | ✅ **ALL GREEN** |

CI/PR gate workflow coverage:
- `backend-ci.yml` line 267: ✅ `tests/test_approval_security_events.py`
- `pr-gate.yml` line 166: ✅ `tests/test_approval_security_events.py`

---

## Scope Compliance

- No approval runtime behavior was changed.
- No approval service, model, schema, repository, or API was changed.
- No `SecurityEventLog` implementation was changed.
- No `ACTION_CODE_REGISTRY` or `seed_rbac_core` was changed.
- No migrations were added.
- No API endpoints were added.
- No frontend or Admin UI was changed.
- No MMD source, MMD tests, or MMD docs were touched.
- No route guards were changed.
- No governance tests were weakened.
- `APPROVAL.CANCELLED` was NOT implemented.

Unrelated dirty workspace changes (all from other teams):

| File | Owner | Status |
|---|---|---|
| `backend/tests/test_station_session_command_context_diagnostic.py` | Station team | Untouched |
| `backend/tests/test_station_session_lifecycle.py` | Station team | Untouched |
| `docker/README.dev.md` | Infra | Untouched |
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | MMD/frontend team | Untouched |
| `frontend/src/app/api/index.ts` | Frontend team | Untouched |
| `frontend/src/app/api/productApi.ts` | Frontend/MMD team | Untouched |
| `frontend/src/app/i18n/namespaces.ts` | Frontend team | Untouched |
| `frontend/src/app/i18n/registry/en.ts` | Frontend team | Untouched |
| `frontend/src/app/i18n/registry/ja.ts` | Frontend team | Untouched |
| `frontend/src/app/pages/BomDetail.tsx` | Frontend/MMD team | Untouched |
| `frontend/src/app/pages/BomList.tsx` | Frontend/MMD team | Untouched |
| `frontend/tsconfig.json` | Frontend team | Untouched |
| `backend/scripts/seed/seed_station_session_scenarios.py` (untracked) | Station team | Untouched |
| `docs/audit/station-session-test-hardening-01-isolation-report.md` (untracked) | Station team | Untouched |

---

## Risks

1. **`APPROVAL.CANCELLED` remains unimplemented.** Any future slice that adds a `cancel_approval_request` service method must emit `APPROVAL.CANCELLED` at that time. The schema field exists but has no service path. The regression test `test_cancelled_remains_schema_only_debt` will fail if a cancellation path is accidentally added without proper governance.

2. **`SecurityEventLog.detail` is a plain-text string.** Future consumers must not rely on parsing `detail` as structured data. If structured payloads are needed, a future migration must add a JSON column.

3. **`impersonation_session_id` appears in `detail` only.** Not queryable as a first-class column in `SecurityEventLog`. This is documented debt from P0-A-12.

4. **Generic approval prerequisites still unmet.** P0-A-11B and P0-A-11C define prerequisites for generic adoption (governed resource identity fields, scope-aware applicability, registry-controlled governed action types). None are implemented yet.

---

## Recommended Next Slice

The P0-A-12 chain (approval SecurityEventLog emission + CI gate + closeout) is fully closed.

Recommended next, in priority order:

1. **P0-A-13**: Governed resource identity migration — add `governed_resource_type`, `governed_resource_id`, `governed_resource_tenant_id` to `ApprovalRequest`. This is the first of five prerequisites for generic approval adoption (P0-A-11B contract).

2. **P0-A-12C** (optional): `SecurityEventLog` structured payload — add a JSON `payload` column to store structured approval event fields (approval_request_id, action_type, etc.) as queryable data.

3. **MMD release/retire governed approval**: Define `MASTER_DATA` approval action type when product scope requires governed release/retire transitions in MMD.

---

## Stop Conditions Hit

None.

---

## Suggested Commit Commands

Do not commit automatically. Suggested commands only:

```powershell
Set-Location "g:/Work/FleziBCG"

# Stage this slice's changes only:
git add backend/tests/test_pr_gate_workflow_config.py
git add docs/audit/p0-a-12b-approval-security-eventlog-closeout-report.md

# Stage P0-A-12 and P0-A-12A changes if not yet committed:
git add backend/app/services/approval_service.py
git add backend/tests/test_approval_service_current_behavior.py
git add backend/tests/test_approval_security_events.py
git add .github/workflows/backend-ci.yml
git add .github/workflows/pr-gate.yml
git add docs/audit/p0-a-12-approval-security-eventlog-emission-report.md
git add docs/audit/p0-a-12a-approval-security-event-test-gate-report.md

git commit -m "P0-A-12/12A/12B: Approval SecurityEventLog emission + CI gate + closeout"
```
