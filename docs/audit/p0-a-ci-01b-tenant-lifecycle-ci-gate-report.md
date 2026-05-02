# P0-A-CI-01B Report
## Tenant Lifecycle Anchor Tests — Backend CI Gate Patch

**Slice:** P0-A-CI-01B  
**Date:** 2026-05-02  
**Status:** COMPLETE  
**Verdict:** `ALLOW_P0A_CI01B_TENANT_TEST_CI_GATE_PATCH` → IMPLEMENTED

---

## Summary

Patched `backend-ci.yml` and `pr-gate.yml` to include `tests/test_tenant_lifecycle_anchor.py` in the P0-A foundation test gate. Also corrected the stale `"Alembic head: linear chain to 0005"` summary line in `backend-ci.yml` to `0006`. `test_pr_gate_workflow_config.py` required no changes. 33 tests pass locally, 3 skips (expected — no local Postgres).

---

## Routing

```
Selected brain: MOM Brain
Selected mode: Strict
Hard Mode MOM: v3 — CI gate, Alembic migration gate, tenant lifecycle foundation,
               schema drift prevention
Reason: CI gate hardening for a tenant lifecycle boundary anchor. Gaps here allow
        P0-A foundation drift to go undetected in future PRs.
```

---

## Hard Mode MOM v3 Gate

### Design / Baseline Evidence Extract

| Evidence | Source | Finding |
|---|---|---|
| P0-A-02A added `test_tenant_lifecycle_anchor.py` (16 tests) | P0-A-02A report | Tests exist; must be added to CI |
| P0-A-02A added migration `0006` | P0-A-02A report | Alembic head is now `0006` |
| P0-A-CI-01 built `backend-ci.yml` before `0006` existed | CI-01 report | Tenant test step absent from CI |
| `backend-ci.yml` summary line: `"Alembic head: linear chain to 0005"` | `backend-ci.yml` line 201 | Stale — must update to `0006` |
| `pr-gate.yml` targeted test list: no `test_tenant_lifecycle_anchor.py` | `pr-gate.yml` | Must add |
| `test_pr_gate_workflow_config.py`: only asserts import check + HMM skill paths | `test_pr_gate_workflow_config.py` | No test-list assertions — no change needed |
| CI Postgres service present: `postgres:16`, credentials `flezibcg_ci` | `backend-ci.yml` | Live DB tests will run in CI |

### Current CI Gate Map

| Workflow | Current P0-A Test Coverage | Missing Tenant Test? | Action |
|---|---|---|---|
| `backend-ci.yml` | 14 test files in 7 steps | YES | Add step; fix summary line |
| `pr-gate.yml` | 18 test files (hardcoded list) | YES | Add to list |
| `test_pr_gate_workflow_config.py` | Validates import check + HMM paths | N/A | No change needed |

### Tenant Test Inclusion Map

| File | Should Include? | Current State | Action |
|---|---|---|---|
| `.github/workflows/backend-ci.yml` | YES | Missing | Added new step |
| `.github/workflows/pr-gate.yml` | YES | Missing | Added to targeted list |
| `backend/tests/test_pr_gate_workflow_config.py` | N/A — no test-list assertions | Unchanged | None |

### Live Postgres Skip Policy Decision

| Policy Area | Decision |
|---|---|
| Local skip policy | Live Postgres tests may skip if no local disposable Postgres available |
| CI no-skip expectation | `backend-ci.yml` provides `postgres:16` service — live DB tests MUST NOT skip in CI |
| Local skips in this run | 3 skips — all `db_engine` fixture skips (Postgres unavailable locally) |
| Local skips acceptable? | YES — expected for local dev without Docker Postgres |
| CI Postgres env var | `DATABASE_URL: postgresql+psycopg://flezibcg_ci:flezibcg_ci@localhost:5432/flezibcg_test` at job level |

### Risk / Stop Condition Map

| Risk | Mitigation |
|---|---|
| Accidentally weakening CI | Added test step; did not remove any existing step |
| Duplicate test list drift | Tenant test added to both `backend-ci.yml` and `pr-gate.yml` — now in sync |
| Local DB unavailable | Skips documented; CI has Postgres service |
| CI DB env mismatch | `DATABASE_URL` matches `settings.py` `database_url` field |
| Known broad-suite station queue failure | Not touched — `test_station_queue_session_aware_migration.py` still excluded |

### Verdict before coding

`ALLOW_P0A_CI01B_TENANT_TEST_CI_GATE_PATCH`

---

## Files Inspected

- `.github/copilot-instructions.md`
- `.github/agent/AGENT.md`
- `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md`
- `docs/ai-skills/hard-mode-mom-v3/SKILL.md`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/pr-gate.yml`
- `backend/tests/test_pr_gate_workflow_config.py`
- `backend/tests/test_tenant_lifecycle_anchor.py`
- `backend/tests/test_alembic_baseline.py`

---

## Files Changed

| File | Change |
|---|---|
| `.github/workflows/backend-ci.yml` | Added step `P0-A tests — tenant lifecycle anchor`; fixed stale summary line `0005` → `0006` |
| `.github/workflows/pr-gate.yml` | Added `tests/test_tenant_lifecycle_anchor.py` to hardcoded targeted test list |

No backend app code, migration, model, or frontend files changed.

---

## CI Gate Update

### `backend-ci.yml` — new step added (between plant hierarchy and security events)

```yaml
# ── P0-A Foundation tests: tenant lifecycle anchor ──────────────────────────
- name: P0-A tests — tenant lifecycle anchor
  shell: bash
  run: |
    cd backend
    python -m pytest -q \
      tests/test_tenant_lifecycle_anchor.py \
      --tb=short
```

### `pr-gate.yml` — added line to targeted list

```
tests/test_tenant_lifecycle_anchor.py
```

### Summary line corrected

```
Alembic head: linear chain to 0006
```

---

## Live Postgres Skip Policy

- **Local:** 3 skips (`test_alembic_upgrade_head_live` + 2 DB-health-check based skips) — acceptable; Postgres not running locally
- **CI:** `backend-ci.yml` provides `postgres:16` service container with `DATABASE_URL` at job level — live Postgres steps will NOT skip in CI
- **`test_tenant_lifecycle_anchor.py`:** No live-DB skips — all 16 tests use SQLite or AST; will pass in CI without Postgres

---

## Verification Commands Run

```bash
cd backend
python -m pytest tests/test_tenant_lifecycle_anchor.py \
  tests/test_pr_gate_workflow_config.py \
  tests/test_alembic_baseline.py \
  tests/test_qa_foundation_migration_smoke.py \
  tests/test_init_db_bootstrap_guard.py \
  -q --tb=short
```

---

## Results

| Suite | Passed | Skipped | Failed |
|---|---|---|---|
| `test_tenant_lifecycle_anchor.py` + `test_pr_gate_workflow_config.py` + `test_alembic_baseline.py` + `test_qa_foundation_migration_smoke.py` + `test_init_db_bootstrap_guard.py` | **33** | **3** | **0** |

Skips = `test_alembic_upgrade_head_live` (live Postgres unavailable locally) + 2 related skips — expected.

---

## Existing Gaps / Known Debts

| Gap | Status |
|---|---|
| `test_station_queue_session_aware_migration.py` pre-existing failure | Excluded from P0-A gate; still needs isolated fix |
| `backend-ci.yml` only runs on `backend/**` path filter — adding a test not under `backend/**` would not trigger CI | N/A — `test_tenant_lifecycle_anchor.py` is under `backend/tests/` |

---

## Scope Compliance

| Requirement | Status |
|---|---|
| Tenant lifecycle test added to `backend-ci.yml` | ✓ |
| Tenant lifecycle test added to `pr-gate.yml` | ✓ |
| `test_pr_gate_workflow_config.py` unchanged | ✓ (no test-list assertions) |
| No backend app code changed | ✓ |
| No migrations changed | ✓ |
| No frontend changed | ✓ |
| No new secrets/credentials | ✓ |
| Stale summary line corrected | ✓ |
| Report created | ✓ |

---

## Recommended Next Slice

**P0-A-02B** — Tenant lifecycle enforcement in auth/session (or deferred to P1), OR  
**P0-A-06A** — Tenant CRUD Admin API (if in product scope).

---

## Stop Conditions Hit

None.
