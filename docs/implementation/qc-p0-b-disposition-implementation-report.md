# QC P0-B Disposition Implementation Report

## Scope implemented

Implemented the next Quality Lite backend slice for authorized hold resolution:

- quality disposition decision persistence
- QAL-owned disposition command path by default
- hold review completion and hold release projection updates
- disposition event and security-event audit trail

Out of scope in this slice:

- accepted-good quantity release effects
- execution allowed-action gating changes from QC hold
- approval-request workflow bridge for disposition decisions
- frontend integration of disposition actions

## Code changes

### Backend model and migration

- Added `quality_disposition_decisions`
- Files:
  - backend/app/models/quality.py
  - backend/alembic/versions/0016_quality_disposition_decisions.py
  - backend/app/db/init_db.py

### Backend repository/service

- Added hold lookup, measurement-record lookup, and disposition-decision persistence
- Added `record_quality_disposition()` in quality service
- Default authorization rule in this slice: only `QAL` may decide disposition
- Disposition code mapping in this slice:
  - `RELEASE_QC_HOLD` -> `QC_PASSED`
  - `ACCEPT_WITH_DEVIATION` -> `QC_PASSED`
  - `REQUIRE_RECHECK` -> `QC_PENDING`
  - `CONFIRM_SCRAP` -> `QC_FAILED`

### Backend API

- Added route:
  - `POST /api/v1/quality/reviews/{review_id}/disposition`
- Existing read route retained:
  - `GET /api/v1/quality/holds`

### Events and audit

- Added execution-event intents:
  - `disposition_decision_recorded`
  - `qc_hold_released`
- Added security event:
  - `QUALITY.DISPOSITION_RECORDED`

### Tests

- Extended backend QC tests in:
  - backend/tests/test_quality_measurement_service.py
- Covered scenarios:
  - QAL can disposition an active hold
  - PMG is rejected by default
  - tenant isolation on hold decision
  - duplicate disposition on released hold is rejected

## Verification status

Targeted QC suite passed on isolated test DB:

```bash
cd backend
DATABASE_URL='postgresql+psycopg://mes:mes@localhost:5432/mes_test' \
PYTHONPATH=/workspaces/FleziBCG/backend \
/workspaces/FleziBCG/.venv/bin/python -m pytest -q tests/test_quality_measurement_service.py
```

Result: `8 passed`.

## Notes

- This slice resolves the review/disposition path and hold release state only.
- Quantity release and execution gating remain separate follow-up slices.