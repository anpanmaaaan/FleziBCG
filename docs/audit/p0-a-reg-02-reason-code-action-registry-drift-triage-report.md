# P0-A-REG-02 Report — Reason Code Action Registry Drift Triage / Governance Alignment

| Field    | Value                                                                |
|----------|----------------------------------------------------------------------|
| Slice    | P0-A-REG-02                                                          |
| Date     | 2026-05-04                                                           |
| Author   | AI Brain (Hard Mode MOM v3)                                          |
| Status   | CLOSED — GOVERNANCE ALIGNMENT COMPLETE                               |
| Depends  | P0-A-15A, MMD-BE-10A                                                 |

---

## Summary

P0-A-REG-02 triages and resolves the RBAC registry validation failure discovered during P0-A-15A verification.

The drift was: `admin.master_data.reason_code.manage` existed in the runtime `ACTION_CODE_REGISTRY` and in the canonical `action-code-registry.md` governance doc, but was absent from the expected canonical set used in `test_rbac_action_registry_alignment.py`.

Evidence from three independent sources confirmed this is **Option B**: the code was intentionally added by the MMD team under slice **MMD-BE-10A** as a prerequisite for the future Reason Code write API (MMD-BE-13). The only stale artifact was the test expected set.

**Option B** was selected. No MMD runtime source was modified. One line added to `_EXPECTED_ADMIN_MMD_CODES` with attribution comment. All 40 RBAC alignment tests now pass.

---

## Routing

| Field          | Value |
|----------------|-------|
| Selected brain | MOM Brain |
| Selected mode  | QA + Strict |
| Hard Mode MOM  | v3 |
| Reason         | Touches RBAC action registry truth, MMD governance boundary, CI/PR gate correctness, critical authorization invariant |

---

## Hard Mode MOM v3 Gate

| Gate Artifact           | Status |
|-------------------------|--------|
| Design Evidence Extract | ✅ Complete |
| Event Map               | ✅ Complete — no runtime events |
| Invariant Map           | ✅ Complete — 4 invariants verified |
| State Transition Map    | ✅ N/A — no state transition |
| Test Matrix             | ✅ Complete |
| Verdict                 | ✅ ALLOW_P0A_REG02_REASON_CODE_ACTION_REGISTRY_GOVERNANCE_ALIGNMENT |

---

## Selected Option

**Option B — Minimal non-MMD governance alignment**

Criteria met:
1. `admin.master_data.reason_code.manage` is intentionally present in runtime `ACTION_CODE_REGISTRY` — confirmed by MMD-BE-10A audit report.
2. It matches current MMD/Reason Code governance direction — confirmed by `action-code-registry.md` entry and `reason-code-write-governance-contract.md`.
3. Failure is only stale `_EXPECTED_ADMIN_MMD_CODES` in the shared alignment test.
4. Changes limited to governance test only — no MMD runtime touched.

---

## Drift Evidence Map

| Artifact | Status | Evidence |
|----------|--------|---------|
| `admin.master_data.reason_code.manage` in `backend/app/security/rbac.py` | ✅ Present — intentional | MMD-BE-10A, commit `44756c4f`, line 63 |
| `admin.master_data.reason_code.manage` in `docs/design/02_registry/action-code-registry.md` | ✅ Present — intentional | Line 73: "Create, update, release, or retire a Reason Code definition (when write APIs are enabled by MMD-BE-13)" |
| `docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md` | ✅ Present — full audit | Status: COMPLETE; objective: register code as prereq for MMD-BE-13; no write API added |
| `backend/tests/test_mmd_rbac_action_codes.py` | ✅ Present — MMD team added | 7 tests covering `admin.master_data.reason_code.manage` (created by MMD team in same commit) |
| `_EXPECTED_ADMIN_MMD_CODES` in `test_rbac_action_registry_alignment.py` | ❌ STALE — missing entry | Only 5 MMD codes; `reason_code.manage` absent; caused `test_action_code_registry_contains_exactly_canonical_set` to fail |

---

## Runtime Registry vs Canonical Registry

| Source | Contains `admin.master_data.reason_code.manage` | Status |
|--------|------------------------------------------------|--------|
| `backend/app/security/rbac.py` (runtime) | ✅ Yes | Correct — intentional |
| `docs/design/02_registry/action-code-registry.md` (governance doc) | ✅ Yes | Correct — added by MMD-BE-10A |
| `test_rbac_action_registry_alignment.py` `_EXPECTED_ADMIN_MMD_CODES` (test) | ❌ No (before fix) | **Stale** — fixed by P0-A-REG-02 |

**Root cause**: The shared governance alignment test was not updated when MMD-BE-10A registered the code. The MMD team updated the runtime, the governance doc, and their own domain test (`test_mmd_rbac_action_codes.py`), but did not update the shared cross-domain alignment test.

---

## Test Failure Classification

| Classification | Value |
|---------------|-------|
| Failure type | **Stale test expectation** (not a runtime registry accident) |
| Severity | Low — test gap only; runtime and doc are consistent |
| Ownership | Governance alignment test is shared infrastructure; drift triage is a governance slice responsibility |
| Fix type | Add `admin.master_data.reason_code.manage` to `_EXPECTED_ADMIN_MMD_CODES` with attribution comment |
| Precedent | Identical to P0-A-REG-01 (BOM code drift) |

---

## Ownership Decision

| Party | Responsibility |
|-------|---------------|
| MMD team | Intentionally added `admin.master_data.reason_code.manage` under MMD-BE-10A; correctly updated runtime, governance doc, and domain test; did not update shared governance alignment test |
| P0-A-REG-02 (this slice) | Update shared `_EXPECTED_ADMIN_MMD_CODES` in `test_rbac_action_registry_alignment.py` with attribution comment |
| Neither party | No MMD runtime source changes; no approval runtime changes |

---

## Files Inspected

| File | Purpose |
|------|---------|
| `docs/audit/p0-a-15a-approval-rule-scope-applicability-schema-report.md` | Identified pre-existing failure; confirmed P0-A-15A did not introduce it |
| `backend/tests/test_rbac_action_registry_alignment.py` | Stale `_EXPECTED_ADMIN_MMD_CODES` — the failing test |
| `backend/app/security/rbac.py` | Runtime `ACTION_CODE_REGISTRY` — `admin.master_data.reason_code.manage` confirmed at line 63 |
| `docs/design/02_registry/action-code-registry.md` | Governance doc — entry confirmed at line 73 |
| `docs/audit/mmd-be-10a-reason-code-action-code-registry-patch.md` | Full MMD-BE-10A audit report — intent and verification documented |
| `backend/tests/test_mmd_rbac_action_codes.py` | MMD domain test for `reason_code.manage` — confirms intentional addition |
| `docs/audit/mmd-be-00-subdomain-evidence-contract-lock-report.md` | Reason Code subdomain baseline — confirmed read-only API; write deferred to MMD-BE-13 |
| `docs/audit/p0-a-reg-01-bom-action-registry-drift-triage-report.md` | Precedent report — identical pattern; Option B applied |
| `backend/tests/test_rbac_seed_alignment.py` | Confirmed fully dynamic — no update needed |

---

## Files Changed

| File | Change | Notes |
|------|--------|-------|
| `backend/tests/test_rbac_action_registry_alignment.py` | Modified | Added `"admin.master_data.reason_code.manage"` to `_EXPECTED_ADMIN_MMD_CODES` with MMD-BE-10A attribution comment |
| `docs/audit/p0-a-reg-02-reason-code-action-registry-drift-triage-report.md` | Created | This report |

**No MMD runtime source changed. No migrations. No APIs. No frontend.**

---

## Verification Commands Run

| Command | Result |
|---------|--------|
| `git log --oneline` | Confirmed commit `44756c4f fix(mmd): add Reason Code manage action code` and `fe85b956 docs(mmd): define Reason Code write governance` |
| `git show 44756c4f --stat` | Confirmed 4 files changed: `rbac.py`, `test_mmd_rbac_action_codes.py`, `mmd-be-10a-...-patch.md`, `action-code-registry.md` |
| `pytest tests/test_rbac_action_registry_alignment.py tests/test_rbac_seed_alignment.py` (after fix) | **40 passed** ✅ |
| `pytest tests/test_approval_rule_scope_applicability_schema.py tests/test_approval_service_current_behavior.py tests/test_approval_security_events.py tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py tests/test_pr_gate_workflow_config.py tests/test_qa_foundation_authorization.py tests/test_scope_rbac_foundation_alignment.py` | **68 passed, 3 skipped** ✅ |

---

## Results

| Metric | Value |
|--------|-------|
| Previously failing tests | 1 (`test_action_code_registry_contains_exactly_canonical_set`) |
| RBAC alignment tests after fix | **40 passed, 0 failed** |
| Full verification suite | **68 passed, 3 skipped (live DB), 0 failed** |
| MMD runtime files changed | 0 |
| New migrations | 0 |
| New APIs | 0 |

---

## Scope Compliance

| Requirement | Status |
|-------------|--------|
| No MMD runtime source modified | ✅ Compliant |
| No Reason Code write behavior added | ✅ Compliant |
| No migrations added | ✅ Compliant |
| No API endpoints added | ✅ Compliant |
| No approval runtime changed | ✅ Compliant |
| No ACTION_CODE_REGISTRY changed | ✅ Compliant (only test expected set updated) |
| Failing test resolved without weakening | ✅ Compliant — expected set expanded, not narrowed |
| Evidence unambiguous before Option B applied | ✅ Confirmed — 3 independent sources |

---

## Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Future MMD action code additions skip updating shared alignment test again | Medium | The attribution comment pattern in `_EXPECTED_ADMIN_MMD_CODES` makes intent visible; CI will catch future drift |
| `test_mmd_rbac_action_codes.py` and `test_rbac_action_registry_alignment.py` may drift independently | Low | Both test the same code; shared test is the authoritative cross-domain gate |

---

## Recommended Next Slice

No immediate follow-up required from this triage. The registry is now consistent across runtime, governance doc, and alignment test.

Future: When MMD-BE-13 (Reason Code write API) is implemented, no action is needed for the registry — the code is already registered and aligned.

---

## Stop Conditions Hit

None.

| Condition | Result |
|-----------|--------|
| Ownership of `admin.master_data.reason_code.manage` unclear | ❌ Not triggered — fully documented under MMD-BE-10A |
| Runtime registry and canonical docs conflict | ❌ Not triggered — both consistent |
| Fixing requires touching MMD runtime source | ❌ Not triggered — only test expected set updated |
| Test alignment would hide accidental runtime action | ❌ Not triggered — action is intentional and documented |
| Workspace contamination prevents safe path-isolated work | ❌ Not triggered — clear diff boundary |
