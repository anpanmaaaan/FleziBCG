# P0-A-MIG-01 - Alembic Duplicate Revision 0004 Graph Repair Report

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: Hard Mode MOM v3
- Hard Mode MOM: v3 required (migration graph/invariant scope)
- Reason: Repair duplicate Alembic revision id 0004 and restore exactly one canonical linear head without expanding domain/API/frontend scope.

## User Requirement (Quoted)
Repair the Alembic migration graph so the repository has exactly one canonical linear migration head.

## Scope and Safety Decision
- In scope:
  - Alembic graph metadata repair for duplicate revision id 0004.
  - Baseline/migration gate assertions and CI summary text alignment.
  - Minimal test harness encoding fix required to execute mandatory migration suite on Windows cp932 locale.
- Out of scope:
  - Domain logic, API behavior, frontend/UI changes, auth model changes.
- Safety:
  - Optional live DB commands were not run because disposable safety was not confirmed for local DB target.
  - Observed local DB URL: postgresql+psycopg://mes:mes@localhost:5432/mes

## Graph State
### Before
- Duplicate revision id conflict existed for 0004.
- Alembic graph checks previously failed with overlapping revisions / multiple heads behavior.

### Repair Option Chosen
- Option A (rebase reason_codes migration to a new post-head revision id).
- Canonical replacement migration:
  - revision: 0010
  - down_revision: 0009
  - file: backend/alembic/versions/0010_reason_codes.py
- Legacy duplicate file status:
  - backend/alembic/versions/0004_reason_codes.py is absent.

### After
- Alembic heads reports exactly one head:
  - 0010 (head)

## Files Changed for This Repair Slice
- backend/alembic/versions/0010_reason_codes.py
- backend/tests/test_alembic_baseline.py
- .github/workflows/backend-ci.yml
- backend/tests/test_plant_hierarchy_orm_foundation.py

## Command Evidence
1) Alembic head verification
- Command:
  - cd backend
  - alembic heads
- Result:
  - 0010 (head)

2) Baseline migration test gate
- Command:
  - python -m pytest -q tests/test_alembic_baseline.py
- Result:
  - 6 passed, 1 skipped

3) Migration smoke + bootstrap guard
- Command:
  - python -m pytest -q tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py
- Result:
  - 8 passed, 2 skipped

4) Tenant lifecycle required trio
- Command:
  - python -m pytest -q tests/test_tenant_lifecycle_anchor.py tests/test_tenant_lifecycle_enforcement.py tests/test_tenant_seed_bootstrap.py
- Result:
  - 35 passed

5) Plant hierarchy required suite
- Initial run result:
  - Failed with UnicodeDecodeError in cp932 locale reading migration text.
- Minimal fix:
  - backend/tests/test_plant_hierarchy_orm_foundation.py updated to read migration file with encoding="utf-8".
- Re-run result:
  - 20 passed

6) Scope RBAC foundation alignment
- Command:
  - python -m pytest -q tests/test_scope_rbac_foundation_alignment.py
- Result:
  - 10 passed

7) Consolidated required suites re-check
- Command:
  - python -m pytest -q tests/test_alembic_baseline.py tests/test_qa_foundation_migration_smoke.py tests/test_init_db_bootstrap_guard.py tests/test_tenant_lifecycle_anchor.py tests/test_tenant_lifecycle_enforcement.py tests/test_tenant_seed_bootstrap.py tests/test_scope_rbac_foundation_alignment.py
- Result:
  - 59 passed, 3 skipped

## Hard Mode MOM v3 Evidence Summary
- Design Evidence Extract:
  - Invariant targeted: single canonical linear Alembic head.
- Event Map:
  - Not applicable (schema graph metadata repair only; no domain event flow altered).
- Invariant Map:
  - Migration revision IDs remain unique.
  - Head cardinality must equal 1.
  - Chain continuity preserved via down_revision linkage.
- State Transition Map:
  - Not applicable (no runtime domain state machine mutation).
- Test Matrix:
  - Alembic head check + required migration/tenant/scope suites executed.
- Verdict before coding:
  - Allow metadata-only graph repair and test-gate alignment.

## Residual Risks
- Local working tree may include unrelated environment bytecode changes under backend/.venv from test execution; these are not part of this repair logic and should be excluded from commits.
- Optional local live DB upgrade/current verification remains intentionally unexecuted due disposable safety ambiguity.

## Final Verdict
- Requirement satisfied.
- Repository migration graph now resolves to one canonical linear head: 0010.
