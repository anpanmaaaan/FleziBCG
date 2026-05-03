# P0-A-12 Report

## Summary

P0-A-12 implements the minimal platform `SecurityEventLog` emission hook for current approval request creation and decision actions.

**Option B** was selected. Evidence confirmed a narrow safe path: `record_security_event(db, ..., commit=False)` can be called directly within the existing `create_approval_request` and `decide_approval_request` service methods, using the same SQLAlchemy session, before the existing `db.commit()`. All three events are emitted atomically with the approval request/decision and `ApprovalAuditLog` in a single transaction.

**No schema change. No API change. No lifecycle change. No migration. No MMD files touched.**

New events emitted:
- `APPROVAL.REQUESTED` — on approval request creation
- `APPROVAL.APPROVED` — on approval decision APPROVED
- `APPROVAL.REJECTED` — on approval decision REJECTED

`APPROVAL.CANCELLED` is NOT emitted (no service path; schema-only debt per P0-A-11C §9).

Existing `ApprovalAuditLog` rows (`REQUEST_CREATED`, `DECISION_MADE`) are fully preserved.

**Total verified: 23 new + existing approval tests passed + 46 RBAC/auth tests = 69 passed, 0 failed.**

---

## Routing

- Selected brain: MOM Brain
- Selected mode: QA + Strict + Backend Implementation
- Hard Mode MOM: v3
- Reason: This task touches approval governance, audit/security event evidence, separation of duties, impersonation context, tenant/scope/auth, role/action/scope assignment, security-event taxonomy, and critical authorization invariants. Hard Mode MOM v3 is mandatory.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| P0-A-11D confirmed approval governance chain closed | `docs/audit/p0-a-11d-approval-governance-contract-closeout-report.md` | All suites green; approval current behavior locked; remaining debt: SecurityEventLog emission |
| P0-A-11C defined APPROVAL.* taxonomy | `docs/design/01_foundation/governed-action-approval-applicability-contract.md` §10 | `APPROVAL.REQUESTED`, `APPROVAL.APPROVED`, `APPROVAL.REJECTED` defined; `APPROVAL.CANCELLED` only if cancellation implemented |
| P0-A-11A locked current approval behavior | `backend/tests/test_approval_service_current_behavior.py` | 17 regression tests; none asserted "no SecurityEventLog" but `_make_session()` did not create `security_event_logs` table |
| Approval service already has `db` Session in scope | `backend/app/services/approval_service.py` | `create_approval_request(db, ...)` and `decide_approval_request(db, ...)` already receive the session |
| `record_security_event(db, ..., commit=False)` is a narrow safe call | `backend/app/services/security_event_service.py` | Takes `db Session`, `commit=False` only adds to session without committing — atomic with existing `db.commit()` |
| `SecurityEventLog` model requires no schema change | `backend/app/models/security_event.py` | Fields: `tenant_id`, `actor_user_id`, `event_type`, `resource_type`, `resource_id`, `detail` (Text) — all mappable from approval context |
| No circular import risk | Source analysis | `security_event_service.py` imports only `models.security_event` and `repositories.security_event_repository`; neither imports `approval_service` |
| Impersonation context available | `decide_approval_request(db, ..., impersonation_session_id=...)` | `impersonation_session_id` is already passed to the decision function; captured in `detail` field of security event |
| APPROVAL.CANCELLED has no service path | `backend/app/services/approval_service.py`, `backend/app/schemas/approval.py` | No `cancel_approval_request` function; `ApprovalDecideRequest` rejects "CANCELLED" via Pydantic validator |

### Event Map

| Approval Event | Current ApprovalAuditLog | Current SecurityEventLog | Target SecurityEventLog | Decision |
|---|---|---|---|---|
| Request created | `REQUEST_CREATED` | None | `APPROVAL.REQUESTED` | **Implemented** |
| Approved | `DECISION_MADE` | None | `APPROVAL.APPROVED` | **Implemented** |
| Rejected | `DECISION_MADE` | None | `APPROVAL.REJECTED` | **Implemented** |
| Cancelled | None | None | `APPROVAL.CANCELLED` | **NOT implemented** — schema-only debt, no service path |

### Invariant Map

| Invariant | Evidence | Test |
|---|---|---|
| `ApprovalAuditLog` rows remain after SecurityEventLog emission is added. | Both `_log_event()` and `record_security_event()` are called before `db.commit()`; neither removes the other. | `test_approval_audit_log_is_preserved_alongside_security_event` |
| SecurityEventLog emission does not change approval lifecycle. | `record_security_event(..., commit=False)` only adds a row; it does not modify `ApprovalRequest.status` or `ApprovalDecision`. | All 17 existing regression tests still pass |
| Requester/decider SoD remains unchanged. | `decide_approval_request` SoD check precedes SecurityEventLog emission; emission does not alter the check. | `test_requester_cannot_decide_own_request` still passes |
| Real user identity remains authoritative under impersonation. | `actor_user_id` in SecurityEventLog is set to `decider_user_id` (real user ID); impersonation context captured in `detail`. | `test_impersonation_context_is_captured_in_approval_decision_event` |
| `APPROVAL.CANCELLED` is never emitted. | No service path exists; `ApprovalDecideRequest` rejects "CANCELLED". | `test_approval_cancelled_event_is_never_emitted` |
| No MMD files are changed. | `git status --short` confirmed | Verified — no MMD source in diff |
| No schema/API/frontend changes are made. | Source diff | No migration, no new API endpoint, no frontend change |

### State Transition Map

```
PENDING ──[decide: APPROVED]──► APPROVED  (terminal)  — emits APPROVAL.APPROVED
PENDING ──[decide: REJECTED]──► REJECTED  (terminal)  — emits APPROVAL.REJECTED
PENDING ──[create]────────────► PENDING               — emits APPROVAL.REQUESTED
APPROVED / REJECTED ──[re-decide]──► ValueError (unchanged)
CANCELLED ──────────────────────────── schema-only; no service path; never emitted
```

No lifecycle change. State machine is identical to P0-A-11A baseline.

### Test Matrix

| Test / Command | Expected | Result |
|---|---|---|
| `test_create_request_emits_approval_requested_security_event` | SecurityEventLog row with event_type=APPROVAL.REQUESTED | PASS |
| `test_decide_approved_emits_approval_approved_security_event` | SecurityEventLog row with event_type=APPROVAL.APPROVED | PASS |
| `test_decide_rejected_emits_approval_rejected_security_event` | SecurityEventLog row with event_type=APPROVAL.REJECTED | PASS |
| `test_approval_audit_log_is_preserved_alongside_security_event` | Both REQUEST_CREATED/DECISION_MADE and APPROVAL.*/APPROVAL.* rows present | PASS |
| `test_impersonation_context_is_captured_in_approval_decision_event` | actor_user_id=real user; impersonation_session_id in detail | PASS |
| `test_approval_cancelled_event_is_never_emitted` | No APPROVAL.CANCELLED row | PASS |
| All 17 `test_approval_service_current_behavior.py` tests | Unchanged behavior, ApprovalAuditLog still present | 17 PASS |
| `test_rbac_action_registry_alignment.py` + `test_rbac_seed_alignment.py` (40) | Registry aligned | 40 PASS |
| `test_qa_foundation_authorization.py` + `test_pr_gate_workflow_config.py` (6) | Auth + PR gate | 6 PASS |

### Verdict

`ALLOW_P0A12_MINIMAL_APPROVAL_SECURITY_EVENTLOG_HOOK`

---

## Selected Option

**Option B — Minimal runtime emission hook + tests.**

Evidence confirmed narrow safe path:
1. `record_security_event(db, ..., commit=False)` requires only the existing `db` Session.
2. No circular import between `approval_service.py` and `security_event_service.py`.
3. `SecurityEventLog` model maps fully from existing approval context without schema change.
4. Emission is atomic with the approval transaction (single `db.commit()` covers all rows).
5. Existing P0-A-11A regression tests required only `SecurityEventLog.__table__.create(bind=engine)` in `_make_session()` to accommodate the new table in the in-memory SQLite session.

---

## SecurityEventLog Readiness Decision

**READY — minimal hook implemented.**

| Readiness Check | Assessment |
|---|---|
| Approval service has `db` Session in scope | ✅ Yes |
| `record_security_event` callable with same `db` | ✅ Yes — `commit=False` |
| No circular import | ✅ Yes |
| No schema change needed | ✅ Yes — `SecurityEventLog` has `detail: Text` for extra fields |
| Impersonation context capturable without schema change | ✅ Yes — captured in `detail` |
| APPROVAL.CANCELLED safely blocked | ✅ Yes — no service path; Pydantic validator rejects "CANCELLED" decision |
| Existing regression tests fixable without behavior change | ✅ Yes — only `SecurityEventLog.__table__.create` added to test fixture |
| No MMD files touched | ✅ Yes |

---

## Event Taxonomy Decision

| Event | Emitted | `actor_user_id` | `resource_type` | `resource_id` | `detail` |
|---|---|---|---|---|---|
| `APPROVAL.REQUESTED` | ✅ Yes | `requester_id` | `APPROVAL_REQUEST` | `str(appr_req.id)` | `action_type=... requester_role=... subject_type=... subject_ref=...` |
| `APPROVAL.APPROVED` | ✅ Yes | `decider_user_id` (real) | `APPROVAL_REQUEST` | `str(appr_req.id)` | `action_type=... decider_role=... impersonation_session=...` |
| `APPROVAL.REJECTED` | ✅ Yes | `decider_user_id` (real) | `APPROVAL_REQUEST` | `str(appr_req.id)` | `action_type=... decider_role=... impersonation_session=...` |
| `APPROVAL.CANCELLED` | ❌ Not implemented | — | — | — | No service path |

---

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `docs/audit/p0-a-11d-approval-governance-contract-closeout-report.md`
- `docs/audit/p0-a-11c-governed-action-approval-applicability-decision-report.md`
- `docs/design/01_foundation/governed-action-approval-applicability-contract.md`
- `docs/design/01_foundation/approval-service-generic-extension-contract.md`
- `backend/app/services/approval_service.py`
- `backend/app/services/security_event_service.py`
- `backend/app/repositories/security_event_repository.py`
- `backend/app/models/approval.py`
- `backend/app/models/security_event.py`
- `backend/app/schemas/approval.py`
- `backend/tests/test_approval_service_current_behavior.py`

---

## Files Changed

| File | Change |
|---|---|
| `backend/app/services/approval_service.py` | Added `from app.services.security_event_service import record_security_event`; added `record_security_event(..., commit=False)` calls in `create_approval_request` and `decide_approval_request` before `db.commit()` |
| `backend/tests/test_approval_service_current_behavior.py` | Added `from app.models.security_event import SecurityEventLog` import; added `SecurityEventLog.__table__.create(bind=engine)` to `_make_session()` |
| `backend/tests/test_approval_security_events.py` | Created — 6 tests covering APPROVAL.REQUESTED, APPROVAL.APPROVED, APPROVAL.REJECTED emission, ApprovalAuditLog preservation, impersonation context capture, APPROVAL.CANCELLED absence |
| `docs/audit/p0-a-12-approval-security-eventlog-emission-report.md` | Created (this file) |

---

## Tests Added / Updated

### New: `backend/tests/test_approval_security_events.py` (6 tests)

| Test | Verifies |
|---|---|
| `test_create_request_emits_approval_requested_security_event` | APPROVAL.REQUESTED emitted; correct tenant_id, actor_user_id, resource_type, resource_id, action_type in detail |
| `test_decide_approved_emits_approval_approved_security_event` | APPROVAL.APPROVED emitted; actor_user_id=decider; resource_id=request id; action_type + role in detail |
| `test_decide_rejected_emits_approval_rejected_security_event` | APPROVAL.REJECTED emitted; correct fields |
| `test_approval_audit_log_is_preserved_alongside_security_event` | Both ApprovalAuditLog (REQUEST_CREATED, DECISION_MADE) AND SecurityEventLog (APPROVAL.REQUESTED, APPROVAL.APPROVED) present |
| `test_impersonation_context_is_captured_in_approval_decision_event` | actor_user_id=real user; impersonation_session_id appears in detail field |
| `test_approval_cancelled_event_is_never_emitted` | No APPROVAL.CANCELLED row after full approve lifecycle |

### Updated: `backend/tests/test_approval_service_current_behavior.py`

| Change | Reason |
|---|---|
| Added `from app.models.security_event import SecurityEventLog` | Import needed for table creation |
| Added `SecurityEventLog.__table__.create(bind=engine)` to `_make_session()` | `record_security_event` now adds a row to `security_event_logs` during approval operations; the table must exist in the in-memory test DB |

No existing tests were removed or weakened.

---

## Verification Commands Run

```powershell
Set-Location "g:/Work/FleziBCG"
git status --short

Push-Location "g:/Work/FleziBCG/backend"
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q tests/test_approval_security_events.py tests/test_approval_service_current_behavior.py
& "g:/Work/FleziBCG/.venv/Scripts/python.exe" -m pytest -q tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py tests/test_qa_foundation_authorization.py tests/test_pr_gate_workflow_config.py
Pop-Location
```

---

## Results

| Suite | Count | Status |
|---|---|---|
| `test_approval_security_events.py` (new) | 6 passed | PASS |
| `test_approval_service_current_behavior.py` (existing) | 17 passed | PASS |
| `test_rbac_action_registry_alignment.py` + `test_rbac_seed_alignment.py` | 40 passed | PASS |
| `test_qa_foundation_authorization.py` + `test_pr_gate_workflow_config.py` | 6 passed | PASS |
| **Total** | **69 passed, 0 failed** | ✅ **ALL GREEN** |

Recurring warning: `conftest.py:238: UserWarning: Running tests against a DB that does not look test-specific`. Pre-existing environment warning from `POSTGRES_DB=mes`. All approval and security event tests use in-memory SQLite; unaffected.

---

## Scope Compliance

- No approval lifecycle behavior was changed.
- No approval model, schema, repository, or API was changed.
- No DB migration was added.
- No API endpoints were added.
- No RBAC action codes were added or changed.
- No `ACTION_CODE_REGISTRY` entries were changed.
- No `seed_rbac_core` or `seed_approval_rules` were changed.
- No frontend or Admin UI was changed.
- No MMD runtime source, MMD tests, or MMD docs were touched.
- `APPROVAL.CANCELLED` was NOT implemented.
- No route guards were changed.
- No governance tests were weakened.

Changes from this slice in `git status --short`:

| File | Owner | Status |
|---|---|---|
| `backend/app/services/approval_service.py` | **This slice** | Modified — minimal SecurityEventLog emission hook |
| `backend/tests/test_approval_service_current_behavior.py` | **This slice** | Modified — `_make_session()` fixture + SecurityEventLog import |
| `backend/tests/test_approval_security_events.py` (untracked) | **This slice** | New test file |
| `backend/tests/test_station_session_command_context_diagnostic.py` | Station team | Untouched |
| `backend/tests/test_station_session_lifecycle.py` | Station team | Untouched |
| `docker/README.dev.md` | Infra | Untouched |
| `frontend/src/app/i18n/namespaces.ts` | Frontend team | Untouched |
| `frontend/tsconfig.json` | Frontend team | Untouched |
| `docs/audit/mmd-be-12a-bom-write-boundary-guardrail.md` (untracked) | MMD team | Untouched |

---

## Risks

1. **`SecurityEventLog` emission failure would roll back the approval transaction.** Since emission is `commit=False` and part of the same `db.commit()`, a DB failure on the `security_event_logs` table (e.g., table missing in production migration drift) would roll back the entire approval. This is the correct atomicity behavior — partial audit records are worse than a failed write.

2. **`detail` is a plain text string.** Future consumers of the SecurityEventLog for approval events should not parse `detail` as structured data. If structured payloads are needed, a future slice should add a JSON column to `SecurityEventLog` or introduce a typed event schema — out of scope for this slice.

3. **`actor_user_id` on `APPROVAL.REQUESTED` is the requester, not the approver.** This is correct per the taxonomy decision (P0-A-11C §10: "who acted" = the person who submitted the request). Future readers must understand that `APPROVAL.APPROVED` / `APPROVAL.REJECTED` has the decider as actor.

4. **Platform `SecurityEventLog` does not currently store `impersonation_session_id` as a first-class column.** The impersonation context appears in `detail` as a string. If this needs to be queryable, a future migration could add the column — out of scope.

5. **`APPROVAL.CANCELLED` remains unimplemented.** If a future slice adds a `cancel_approval_request` service method, it must emit `APPROVAL.CANCELLED` at that time.

---

## Recommended Next Slice

### P0-A-13 (suggested): Approval SecurityEventLog query baseline
- Add a test verifying that `get_security_events(..., event_type="APPROVAL.REQUESTED")` returns the correct rows (testing the existing query path with approval events).
- Optional: Add an API endpoint to surface approval-specific security events if product scope requires it.

### Or: MMD Release/Retire governed approval
- Define `MASTER_DATA` approval action type.
- Define scope-aware applicability rule.
- Wire approval rule for the governed resource type.
- This requires the future contracts defined in P0-A-11B and P0-A-11C.

### Or: Governed resource identity migration
- Add `governed_resource_type`, `governed_resource_id`, `governed_resource_tenant_id` to `ApprovalRequest` as a new migration slice.
- This is a prerequisite for full generic approval adoption per P0-A-11B.

---

## Stop Conditions Hit

None.
