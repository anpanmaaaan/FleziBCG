# QC P0-D Accepted-Good Release Implementation Report

## Scope implemented

Implemented backend-derived quantity effect semantics for Quality Lite:

- in-spec measurement (`QC_PASSED`) releases accepted-good quantity effect
- out-of-spec measurement (`QC_HOLD`) defers accepted-good release as held-pending quantity effect
- disposition decision now returns and emits quantity effect based on disposition code

This slice keeps quantity effects as backend-derived outputs of quality commands/events. It does not yet redesign execution-core quantity projection storage.

## Design-aligned behavior

Aligned to quality contracts:

- accepted good may differ from reported good when QC gate exists
- accepted-good derivation may be deferred until QC pass or disposition
- accepted-good release is backend-authoritative, not frontend-derived

Implemented disposition quantity effects:

- `RELEASE_QC_HOLD` => `accepted_good_release_qty = reported_good_qty`, `held_pending_good_qty = 0`
- `ACCEPT_WITH_DEVIATION` => `accepted_good_release_qty = reported_good_qty`, `held_pending_good_qty = 0`
- `REQUIRE_RECHECK` => `accepted_good_release_qty = 0`, `held_pending_good_qty = reported_good_qty`
- `CONFIRM_SCRAP` => `accepted_good_release_qty = 0`, `held_pending_good_qty = 0`

## Code changes

- Added response fields:
  - `accepted_good_release_qty`
  - `held_pending_good_qty`
  - file: backend/app/schemas/quality.py
- Added quantity effect derivation in service and applied it to:
  - submit path response and events
  - disposition path response and events
  - file: backend/app/services/quality_service.py
- Added regression tests for pass/hold/disposition quantity effects:
  - file: backend/tests/test_quality_measurement_service.py

## Events updated

- `qc_result_recorded` payload now includes:
  - `reported_good_qty`
  - `accepted_good_release_qty`
  - `held_pending_good_qty`
- `qc_hold_applied` payload now includes:
  - `held_pending_good_qty`
- `disposition_decision_recorded` payload now includes:
  - `reported_good_qty`
  - `accepted_good_release_qty`
  - `held_pending_good_qty`

## Verification

```bash
cd backend
DATABASE_URL='postgresql+psycopg://mes:mes@localhost:5432/mes_test' \
PYTHONPATH=/workspaces/FleziBCG/backend \
/workspaces/FleziBCG/.venv/bin/python -m pytest -q \
  tests/test_quality_measurement_service.py \
  tests/test_quality_hold_execution_gating.py
```

Result: `16 passed`.

## Follow-up

1. decide whether to materialize accepted-good projection fields on execution read model/entity.
2. define quantity effect for `CONFIRM_SCRAP` if explicit scrap-transfer semantics are needed.
3. expose quantity effect fields in FE quality hold/review screens.