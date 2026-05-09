# QC P0-F Require-Recheck Hold Gate Implementation Report

## Scope implemented

Implemented the correction slice for `REQUIRE_RECHECK` quality disposition behavior:

- `REQUIRE_RECHECK` no longer releases the active quality hold
- execution progression gate remains active after recheck is requested
- backend emits a recheck projection event instead of a release event for this path

Out of scope in this slice:

- frontend disposition UX updates
- measurement submit payload cleanup
- new hold lifecycle tables or richer reinspection workflow modeling

## Design-aligned behavior

Aligned to quality interaction contracts:

- quality affects execution through gates and allowed-actions
- recheck is distinct from hold release
- backend remains source of truth for whether execution may continue

Implemented disposition behavior:

- `REQUIRE_RECHECK` =>
  - `quality_status = QC_PENDING`
  - `hold_status = ACTIVE`
  - `review_status = DECISION_PENDING`
  - emit `disposition_decision_recorded`
  - emit `qc_recheck_requested`
  - do not emit `qc_hold_released`
- release-like dispositions continue to release the hold as before.

## Code changes

- Updated disposition branching in:
  - `backend/app/services/quality_service.py`
- Added regression coverage for:
  - active-hold preservation after `REQUIRE_RECHECK`
  - resume-block preservation after `REQUIRE_RECHECK`
  - files:
    - `backend/tests/test_quality_measurement_service.py`
    - `backend/tests/test_quality_hold_execution_gating.py`
- Updated API behavior baseline:
  - `docs/design/05_application/api-catalog-current-baseline.md`

## Verification

Focused regression slice passed on isolated test DB:

```bash
cd backend
DATABASE_URL='postgresql+psycopg://mes:mes@localhost:5432/mes_test' \
PYTHONPATH=/workspaces/FleziBCG/backend \
/workspaces/FleziBCG/.venv/bin/python -m pytest -q \
  tests/test_quality_measurement_service.py \
  tests/test_quality_hold_execution_gating.py
```

Result: `22 passed`.

## Next slice

1. Tighten the public measurement API contract so client threshold fields are no longer authoritative request inputs.
2. Align the frontend measurement screen to that narrowed contract.
3. Decide whether partial submission should remain allowed or be validated against required item completeness.