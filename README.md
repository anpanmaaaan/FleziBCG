# FleziBCG

## API lifecycle (Phase 2 write flow)

Backend write-flow is event-driven via `ExecutionEvent`.

1. `POST /api/v1/operations/{operation_id}/start`
   - Body: `{ "operator_id"?: string, "started_at"?: ISO8601 }`
   - Action: append `OP_STARTED`, set operation status to `IN_PROGRESS`, set `actual_start`.
   - Guard: operation must exist, tenant match, status not `IN_PROGRESS`/`COMPLETED`.

2. `POST /api/v1/operations/{operation_id}/report-quantity`
   - Body: `{ "good_qty": number, "scrap_qty"?: number, "operator_id"?: string }`
   - Action: append `QTY_REPORTED`, increment `completed_qty`, `good_qty`, `scrap_qty`, status remains `IN_PROGRESS`.
   - Guard: operation exists, tenant match, status `IN_PROGRESS`, non-negative, `good_qty + scrap_qty > 0`.

3. `POST /api/v1/operations/{operation_id}/complete`
   - Body: `{ "operator_id"?: string }`
   - Action: append `OP_COMPLETED`, status `COMPLETED`, set `actual_end`.
   - Guard: operation exists, tenant match, status `IN_PROGRESS`.

### Notes

- `Operation` snapshot fields (`status`, `actual_start`, `actual_end`, `completed_qty`, `good_qty`, `scrap_qty`) are derived/projection fields, updated in service logic only.
- Source of truth remains `execution_events` append-only table.
- Frontend reads via `GET /api/v1/operations/{operation_id}` and list endpoints.
