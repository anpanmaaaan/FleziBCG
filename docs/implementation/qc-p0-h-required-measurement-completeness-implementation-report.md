# QC P0-H Required Measurement Completeness Implementation Report

## Scope implemented

Implemented strict completeness policy for QC measurement submission:

- backend now rejects submit payloads that do not include all required template item codes
- rejection path returns `REQUIRED_MEASUREMENTS_MISSING:<codes>` and writes no quality events
- frontend Measurement Entry aligns submit affordance and messaging with strict completeness

Out of scope in this slice:

- reinspection workflow expansion
- additional DB schema for measurement draft staging
- route/menu/access surface changes

## Design-aligned behavior

Aligned to quality truth and UI safety:

- backend remains source of quality truth
- operator still records observed values only
- strict policy is enforced server-side and mirrored in frontend guidance

## Code changes

- Service enforcement:
  - `backend/app/services/quality_service.py`
  - required template item coverage check in `submit_qc_measurement()`
- Backend regression coverage:
  - `backend/tests/test_quality_measurement_service.py`
  - added missing-required rejection test
  - updated existing submit tests to include full required measurement set
- Frontend alignment:
  - `frontend/src/app/pages/MeasurementEntry.tsx`
  - strict completeness submit gating + localized state/error guidance
  - `frontend/src/app/i18n/registry/en.ts`
  - `frontend/src/app/i18n/registry/ja.ts`
- API behavior docs:
  - `docs/design/05_application/api-catalog-current-baseline.md`

## Verification

Backend focused regression:

```bash
cd backend
DATABASE_URL='postgresql+psycopg://mes:mes@localhost:5432/mes_test' \
PYTHONPATH=/workspaces/FleziBCG/backend \
/workspaces/FleziBCG/.venv/bin/python -m pytest -q \
  tests/test_quality_measurement_service.py \
  tests/test_quality_hold_execution_gating.py
```

Result: `24 passed`.

Frontend verification:

```bash
cd frontend
npm run build
npm run lint
npx playwright install-deps chromium
npx playwright test e2e/quality-measurement-completeness.spec.ts
```

Result: build PASS, lint PASS, targeted Playwright regression PASS.

Additional FE verification after selector stabilization:

```bash
cd frontend
npx playwright test
```

Result: full frontend Playwright suite PASS (7 passed).

## Next slice

1. If product later needs draft/partial capture, introduce a separate draft measurement command/read model instead of weakening strict submit.
2. Expand FE regression from targeted spec to broader quality measurement E2E coverage.