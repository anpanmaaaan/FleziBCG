# QC P0-G Measurement Submit Contract Implementation Report

## Scope implemented

Implemented the public-contract cleanup for Quality Lite measurement submission:

- backend request schema now accepts only operator-observed measurement facts
- threshold override fields are rejected by the request contract
- frontend measurement page submits only `item_code` and `measured_value`
- backend requirement limits remain visible in the UI as read-only context

Out of scope in this slice:

- required-item completeness enforcement
- route/navigation changes
- broader QC page redesign outside Measurement Entry

## Design-aligned behavior

Aligned to quality and frontend boundary rules:

- backend decides quality truth
- operator submits observed values only
- frontend displays backend-owned limits but does not authoritatively send them back

## Code changes

- Narrowed backend request models and forbade extra fields:
  - `backend/app/schemas/quality.py`
- Updated quality service tests to the narrowed request shape and added contract rejection coverage:
  - `backend/tests/test_quality_measurement_service.py`
- Narrowed frontend measurement request type:
  - `frontend/src/app/api/qualityApi.ts`
- Updated Measurement Entry to:
  - build submit payload from `item_code` + `measured_value` only
  - render backend limits as read-only display values
  - lock template item-code rows against ad hoc edits when backend requirements are loaded
  - file: `frontend/src/app/pages/MeasurementEntry.tsx`
- Updated API baseline documentation:
  - `docs/design/05_application/api-catalog-current-baseline.md`

## Verification

Backend regression slice passed:

```bash
cd backend
DATABASE_URL='postgresql+psycopg://mes:mes@localhost:5432/mes_test' \
PYTHONPATH=/workspaces/FleziBCG/backend \
/workspaces/FleziBCG/.venv/bin/python -m pytest -q \
  tests/test_quality_measurement_service.py \
  tests/test_quality_hold_execution_gating.py
```

Result: `23 passed`.

Frontend validation passed:

```bash
cd frontend
npm run build
npm run lint
```

Result: build PASS, lint PASS.

## Next slice

1. Decide whether partial measurement submission is allowed or whether all required template items must be present.
2. If completeness is required, enforce it in backend validation first.
3. Then align the measurement page UX to incomplete-row guidance instead of backend rejection after submit.