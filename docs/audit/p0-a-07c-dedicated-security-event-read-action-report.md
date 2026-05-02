# P0-A-07C Report

## Summary

Resolved GAP-2 from P0-A-07A. Introduced a dedicated `admin.security_event.read`
action code for the security event read route, replacing the semantically incorrect
`admin.user.manage` guard in `security_events.py`. Registry updated. Tests updated.
All verification commands pass.

---

## Routing
- Selected brain: MOM Brain
- Selected mode: Backend implementation + RBAC/action registry hardening + audit/security authorization semantic correction + route guard contract alignment + QA/regression
- Hard Mode MOM: v3
- Reason: Touches route-level authorization guard behavior, RBAC action registry, admin/audit security boundary, and security event read governance domain.

---

## Hard Mode MOM v3 Gate

### Design Evidence Extract
| Doc | Evidence |
|---|---|
| P0-A-07A report (GAP-2) | `security_events.py` uses `admin.user.manage` — semantic mismatch identified; fix deferred to P0-A-07C |
| P0-A-07B report | GAP-1 resolved; 19 codes in registry; `_EXPECTED_ADMIN_CONFIG_CODES` pattern established |
| `docs/design/02_registry/action-code-registry.md` | Naming convention: `admin.<entity>.<verb>`, ADMIN family for admin-restricted operations |
| `backend/app/security/rbac.py ACTION_CODE_REGISTRY` | 19 entries pre-change; no `admin.security_event.read` |
| `backend/app/api/v1/security_events.py` | GET `/security-events` guarded by `require_action("admin.user.manage")` |
| `backend/tests/test_security_events_endpoint.py` | `_override_admin_dependency` pattern — auto-discovers dependency; survives rename |
| `backend/tests/test_admin_audit_security_events.py` | Pure service-layer tests; unaffected |

### Current Security Event Authorization Map
| Route / Area | Before | After | Decision |
|---|---|---|---|
| GET `/security-events` | `admin.user.manage` | `admin.security_event.read` | Replaced — semantic mismatch (IAM code for audit read) |

### Verdict
**`ALLOW_P0A07C_DEDICATED_SECURITY_EVENT_READ_ACTION`**

---

## Action Code Naming Decision

**Option A — `admin.security_event.read`**

- Convention: `admin.<entity>.<verb>` — matches all existing admin codes
- Entity: `security_event` — aligns with source file name and schema
- Verb: `read` — semantically precise (read operation, not mutation)
- Family: `ADMIN` — security events are admin-restricted; this is an intentional exception to the general "reads use `require_authenticated_identity`" rule
- Option B (`security.events.read`) rejected: no `security.*` domain prefix exists in registry

---

## Compatibility Policy

**Policy A — Strict semantic cutover**

- Pre-production system; no production grants to migrate
- `_override_admin_dependency` test pattern dynamically discovers new dependency — no test restructure needed
- No dual-allow fallback introduced

---

## Action Code Decision

| Field | Value |
|---|---|
| Action Code | `admin.security_event.read` |
| Family | `ADMIN` |
| Description | Read security/audit event log entries (admin-restricted) |
| Registry section | "Audit / Security Governance" |

---

## Files Inspected

- `docs/audit/p0-a-07a-rbac-action-registry-semantic-alignment-report.md`
- `docs/audit/p0-a-07b-dedicated-downtime-reason-admin-action-report.md`
- `docs/design/02_registry/action-code-registry.md`
- `backend/app/security/rbac.py`
- `backend/app/api/v1/security_events.py`
- `backend/tests/test_rbac_action_registry_alignment.py`
- `backend/tests/test_security_events_endpoint.py`
- `backend/tests/test_admin_audit_security_events.py`

---

## Files Changed

### `backend/app/security/rbac.py`
Added new audit/security governance section to `ACTION_CODE_REGISTRY`:

```python
# Audit / security governance action codes — admin-restricted access to
# security and audit event logs. Read-only but requires ADMIN family.
"admin.security_event.read": "ADMIN",
```

Total action codes: **20** (was 19).

### `backend/app/api/v1/security_events.py`

| Route | Before | After |
|---|---|---|
| `GET /security-events` | `admin.user.manage` | `admin.security_event.read` |

### `docs/design/02_registry/action-code-registry.md`
Added new "Audit / Security Governance" section:

| Action Code | Family | Description |
|---|---|---|
| `admin.security_event.read` | ADMIN | Read security/audit event log entries (admin-restricted) |

Added history entry for P0-A-07C.

### `backend/tests/test_rbac_action_registry_alignment.py`
- Updated module docstring: GAP-2 marked as RESOLVED in P0-A-07C
- Added `_EXPECTED_ADMIN_AUDIT_CODES = frozenset({"admin.security_event.read"})`
- Added `_EXPECTED_ADMIN_AUDIT_CODES` to `_ALL_EXPECTED_CODES` union
- Added `test_all_canonical_admin_audit_codes_in_registry` — positive registry completeness test
- Updated `test_admin_codes_map_to_admin_family` — includes audit codes in admin family check
- Replaced `test_known_gap_security_events_uses_admin_user_manage` (GAP-2 lock) with `test_known_gap_security_events_resolved_uses_dedicated_action_code` (resolved-gap positive assertion)

Total tests in file: **19** (was 18).

---

## Tests Added / Updated

| Test | File | Change |
|---|---|---|
| `test_all_canonical_admin_audit_codes_in_registry` | test_rbac_action_registry_alignment.py | New — positive completeness test |
| `test_admin_codes_map_to_admin_family` | test_rbac_action_registry_alignment.py | Updated — includes audit codes |
| `test_known_gap_security_events_resolved_uses_dedicated_action_code` | test_rbac_action_registry_alignment.py | Replaced GAP-2 lock test |
| `test_action_code_registry_contains_exactly_canonical_set` | test_rbac_action_registry_alignment.py | Now passes with 20 codes |

---

## Verification Commands Run

```
python -m pytest -q tests/test_rbac_action_registry_alignment.py
python -m pytest -q tests/test_security_events_endpoint.py tests/test_admin_audit_security_events.py
python -m pytest -q tests/test_security_event_service.py tests/test_access_service.py tests/test_qa_foundation_authorization.py tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py
python -m pytest -q tests/test_downtime_reason_admin_routes.py tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
```

---

## Results

| Command | Result |
|---|---|
| `pytest -q tests/test_rbac_action_registry_alignment.py` | **19 passed** |
| `pytest -q tests/test_security_events_endpoint.py tests/test_admin_audit_security_events.py` | **5 passed** |
| `pytest -q tests/test_security_event_service.py tests/test_access_service.py tests/test_qa_foundation_authorization.py tests/test_scope_rbac_foundation_alignment.py tests/test_pr_gate_workflow_config.py` | **21 passed** |
| `pytest -q tests/test_downtime_reason_admin_routes.py tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py` | **16 passed, 3 skipped** |

All pre-existing tests pass. No regressions. 3 skipped = live Postgres tests not available locally (expected).

---

## Remaining Known Gaps

| GAP | Description | Status |
|---|---|---|
| GAP-1 | `downtime_reasons.py` used `admin.user.manage` for downtime admin mutations | **RESOLVED** (P0-A-07B) |
| GAP-2 | `security_events.py` used `admin.user.manage` for admin-restricted audit read | **RESOLVED** (P0-A-07C) |
| GAP-3 | `impersonations.py` uses `require_authenticated_identity` instead of `require_action` | Open — deferred |

---

## Registry Summary (Post P0-A-07C)

| Domain | Count | Codes |
|---|---|---|
| Execution | 9 | `execution.{start,complete,report_quantity,pause,resume,start_downtime,end_downtime,close,reopen}` |
| Approval | 2 | `approval.{create,decide}` |
| IAM / Platform Admin | 3 | `admin.{impersonation.create,impersonation.revoke,user.manage}` |
| MMD | 3 | `admin.master_data.{product,routing,resource_requirement}.manage` |
| Configuration Admin | 1 | `admin.downtime_reason.manage` |
| Audit / Security Governance | 1 | `admin.security_event.read` |
| **Total** | **20** | |

---

## Scope Compliance

| Rule | Status |
|---|---|
| No migration added | ✓ |
| No frontend change | ✓ |
| No Admin UI added | ✓ |
| No broad RBAC rewrite | ✓ |
| GAP-3 impersonation behavior unchanged | ✓ |
| No API path/schema/response changes | ✓ |
| No tenant/scope enforcement change | ✓ |
| No MMD/Execution/Quality change | ✓ |

---

## Risks

| Risk | Status |
|---|---|
| Existing roles miss new action | Pre-production — no production grants; not a risk |
| Broad RBAC rewrite triggered | Not triggered — 1 code added, 1 guard changed |
| Registry/source drift | All 3 locations (rbac.py, doc, tests) updated atomically |
| GAP-3 accidentally fixed | Not touched — impersonations.py unchanged |

---

## Recommended Next Slice

**P0-A-07D (or separate GAP-3 slice):** Resolve GAP-3 — wire `admin.impersonation.create` and `admin.impersonation.revoke` as route-level guards in `impersonations.py` (currently these codes exist in the registry but routes delegate to service layer). Requires evidence that service-layer checks are sufficient or that route-level gating is needed.

Alternatively: proceed to next foundation hardening slice as defined by the P0-A roadmap.

---

## Stop Conditions Hit

None.
