# QC P0 Merge Readiness Checklist

## Verdict

GO for the QC P0 slice, with scope control.

Condition:
- Merge only the QC-scoped files listed below (or review any extra files explicitly as out-of-slice).

## Must-review files

### Backend domain truth

- backend/app/services/quality_service.py
- backend/app/schemas/quality.py
- backend/app/repositories/quality_repository.py
- backend/app/api/v1/quality.py
- backend/app/models/quality.py

### Backend schema and tests

- backend/alembic/versions/0015_quality_measurement_foundation.py
- backend/alembic/versions/0016_quality_disposition_decisions.py
- backend/tests/test_quality_measurement_service.py
- backend/tests/test_quality_hold_execution_gating.py

### Frontend contract alignment

- frontend/src/app/api/qualityApi.ts
- frontend/src/app/pages/MeasurementEntry.tsx
- frontend/src/app/pages/QualityHolds.tsx
- frontend/src/app/i18n/registry/en.ts
- frontend/src/app/i18n/registry/ja.ts
- frontend/e2e/quality-measurement-completeness.spec.ts

### Frontend test stability and setup

- frontend/e2e/header-operational-context.spec.ts
- frontend/README.md

### Design and implementation evidence

- docs/design/05_application/api-catalog-current-baseline.md
- docs/implementation/qc-p0-quality-slice-pr-summary.md
- docs/implementation/qc-p0-a-initial-measurement-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-a-initial-measurement-implementation-report.md
- docs/implementation/qc-p0-b-disposition-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-b-disposition-implementation-report.md
- docs/implementation/qc-p0-c-execution-gating-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-c-execution-gating-implementation-report.md
- docs/implementation/qc-p0-d-accepted-good-release-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-d-accepted-good-release-implementation-report.md
- docs/implementation/qc-p0-e-backend-owned-measurement-evaluation-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-e-backend-owned-measurement-evaluation-implementation-report.md
- docs/implementation/qc-p0-f-require-recheck-hold-gate-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-f-require-recheck-hold-gate-implementation-report.md
- docs/implementation/qc-p0-g-measurement-submit-contract-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-g-measurement-submit-contract-implementation-report.md
- docs/implementation/qc-p0-h-required-measurement-completeness-hard-mode-mom-v3-gate.md
- docs/implementation/qc-p0-h-required-measurement-completeness-implementation-report.md

## Gate checks

1. Backend truth gate
- Pass if pass/fail is derived from backend requirement metadata, not client threshold payload.

2. Recheck gate integrity
- Pass if `REQUIRE_RECHECK` keeps quality hold active and execution remains blocked.

3. Submit contract gate
- Pass if submit accepts only operator-observed facts and rejects threshold extras.

4. Completeness gate
- Pass if submit rejects missing required template item codes.

5. FE intent-only gate
- Pass if UI only sends intent payload and never computes backend truth outcomes.

## Verification evidence (latest)

1. Backend targeted tests
- `tests/test_quality_measurement_service.py`
- `tests/test_quality_hold_execution_gating.py`
- Result: pass (24 passed as reported in implementation report).

2. Frontend static checks
- `npm run lint`
- `npm run build`
- Result: pass.

3. Frontend E2E
- `npx playwright test e2e/quality-measurement-completeness.spec.ts`
- `npx playwright test`
- Result: pass (full suite 7 passed).

## Merge blocker checklist

- [ ] No out-of-scope backend execution or IAM behavior changes hidden in the same commit set.
- [ ] Alembic migration order and upgrade path validated in target environment.
- [ ] Quality API router registration confirmed in backend routing table.
- [ ] QA reviewer signs off on strict completeness policy (no draft submission path).
- [ ] Frontend reviewers confirm visible-only E2E selector pattern where duplicated hidden nodes exist.

## Recommendation

Proceed with merge once the blocker checklist is marked complete and PR scope is explicitly constrained to the files above.
