# QC Feature Handoff Report (2026-05-08)

## Purpose

Handoff snapshot for the current Quality (QC) feature state after station-execution-first completion and the latest QC admin/UI cleanup.

## Current QC baseline

- Backend is source of truth for quality outcomes, hold lifecycle, and quality-to-execution gating.
- Measurement submit contract accepts operator-observed facts only (`item_code`, `measured_value`).
- Required-measurement completeness is enforced server-side.
- `REQUIRE_RECHECK` does not clear active hold and does not unblock execution progression.
- Gate definition create currently supports `gate_type=PRE_ACCEPTANCE` only.

## Live API surface (quality)

- `GET /api/v1/quality/operations/{operation_id}/requirements`
- `GET /api/v1/quality/gates/definitions`
- `POST /api/v1/quality/gates/definitions`
- `POST /api/v1/quality/gates/instances/open`
- `POST /api/v1/quality/measurements`
- `GET /api/v1/quality/holds`
- `GET /api/v1/quality/deviations`
- `POST /api/v1/quality/holds/{hold_id}/deviations`
- `POST /api/v1/quality/deviations/{deviation_request_id}/resolve`
- `GET /api/v1/quality/nonconformances`
- `POST /api/v1/quality/nonconformances`
- `POST /api/v1/quality/reviews/{review_id}/disposition`

## Frontend status

Connected quality pages in active use:

- `frontend/src/app/pages/MeasurementEntry.tsx`
- `frontend/src/app/pages/QualityHolds.tsx`
- `frontend/src/app/pages/QCCheckpoints.tsx`
- `frontend/src/app/pages/DefectManagement.tsx`

Latest alignment changes included:

- QC checkpoints create form now sends `gate_type=PRE_ACCEPTANCE`.
- EN/JA i18n includes pre-acceptance gate-type label.
- Legacy backend note banners on QC checkpoints/defects pages were removed from rendered page body.

## Documentation sync completed in this handoff

Updated:

- `docs/design/06_application_backend/quality-lite-api.md`
- `docs/design/05_application/api-catalog-current-baseline.md`
- `docs/implementation/qc-p0-quality-slice-pr-summary.md`
- `docs/implementation/quality-pr-documentation-sync-checklist.md`

Created:

- `docs/implementation/qc-feature-handoff-report-2026-05-08.md`

## Validation references

Recent validation evidence already captured in prior implementation artifacts:

- backend targeted tests for quality measurement and hold/execution gating
- frontend lint/build/i18n parity checks
- regression fix for unsupported `gate_type='MEASUREMENT'` now aligned to backend enum

## Known constraints and next-owner notes

- If backend expands `QualityGateTypeEnum`, update all of: backend schema validation, service guard, frontend create form options, and EN/JA labels in same PR.
- Keep quality docs synchronized with route-level contracts whenever adding/deprecating quality endpoints.
- Preserve backend-owned truth boundaries: frontend captures intent only.
