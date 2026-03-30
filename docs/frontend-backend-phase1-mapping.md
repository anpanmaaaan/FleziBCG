# Frontend to Backend Phase 1 Mapping

This document maps the current Phase 1 frontend screens in `frontend/` to the backend skeleton implemented in `backend/`.

## Summary

Relevant frontend screens:
- `Home` (/)
- `ProductionOrderList` (/production-orders)
- `OperationList` (/production-order/:orderId)
- `OperationExecutionOverview` (/operation/:woId)
- `OperationExecutionDetail` (/operation-detail/:operationId)
- `StationExecution` (/station-execution)
- `QCCheckpoints` (/quality)

All of these screens currently rely on mock data and have no real backend wiring yet.

---

## 1. Home

- Frontend component: `frontend/src/app/pages/Home.tsx`
- Route: `/`
- Screen purpose: execution tracking landing page with production queue, production line/station status, and alerts.

### Related backend endpoint(s)
- `GET /api/v1/dashboard`
- `GET /api/v1/production-orders`

### Main request params
- none currently defined in frontend

### Expected response schema
- Dashboard summary should include counts and high-level metrics for production orders, work orders, operations, and current line/station health.
- Production order list should include queue items with IDs, release dates, status, progress, and route.

### Backend-derived fields
- total counts and KPIs
- queue order status
- production line status and station status
- progress values for orders and lines

### User intent only fields
- none for Home in the current mock implementation; Home is read-only in Phase 1

### Current gap or mismatch
- Home currently uses `queueOrders`, `productionLines`, and `defectAlerts` from local mock data.
- The backend skeleton only provides aggregate counts via `/dashboard`; it does not yet expose line/station status or queue details.

### Recommended next backend endpoint if missing
- extend `/api/v1/dashboard` to include queue orders and production line/station summaries
- optionally add `/api/v1/production-orders?scope=queue` or `/api/v1/queue`

---

## 2. ProductionOrderList

- Frontend component: `frontend/src/app/pages/ProductionOrderList.tsx`
- Route: `/production-orders`
- Screen purpose: production order table with search, filtering, and column management.

### Related backend endpoint(s)
- `GET /api/v1/production-orders`

### Main request params
- none currently used, but frontend supports search/filter by production order, serial number, route ID.

### Expected response schema
- production order summary list
- fields expected by UI:
  - `id`
  - `serialNumber`
  - `lotId`
  - `routeId`
  - `customer`
  - `priority`
  - `machineNumber`
  - `quantity`
  - `plannedStartDate`
  - `plannedCompletionDate`
  - `actualStartDate`
  - `actualCompletionDate`
  - `releasedDate`
  - `assignee`
  - `department`
  - `status`
  - `progress`
  - `materialCode`
  - `productName`

### Backend-derived fields
- `status`
- `progress`
- planned/actual dates
- route and machine assignment
- quantity and order identifiers

### User intent only fields
- column visibility settings are local UI state only
- search values are UI filters only

### Current gap or mismatch
- backend schema `ProductionOrderSummary` is minimal and currently misses many UI fields such as `serialNumber`, `releasedDate`, `assignee`, `productName`, and `progress`.
- frontend is built around `productionOrders` mock objects, not API responses.

### Recommended next backend endpoint if missing
- `GET /api/v1/production-orders` with a richer summary shape that matches `productionOrders` mock fields

---

## 3. OperationList

- Frontend component: `frontend/src/app/pages/OperationList.tsx`
- Route: `/production-order/:orderId`
- Screen purpose: work order execution status list for a selected production order.

### Related backend endpoint(s)
- `GET /api/v1/production-orders/{order_id}`
- `GET /api/v1/work-orders/{wo_id}/operations`

### Main request params
- `orderId` path parameter for production order

### Expected response schema
- production order detail containing work orders
- work order summary fields expected by UI:
  - `id`
  - `work_order_number`
  - `status`
  - `planned_start`
  - `planned_end`
  - `actual_start`
  - `estimated_completion`
  - `overall_progress`
  - `completed_operations`
  - `current_operation`
  - `delay_minutes`
  - `operations_count`

### Backend-derived fields
- work order status
- overall progress
- planned/actual dates
- count of completed operations
- delay and timing status

### User intent only fields
- UI filtering and search criteria

### Current gap or mismatch
- current backend detail schema is minimal and does not expose `estimated_completion`, `current_operation`, or delay metadata.
- `ProductionOrderDetail` currently returns only a list of work orders with placeholder `overall_progress`.

### Recommended next backend endpoint if missing
- `GET /api/v1/production-orders/{order_id}` should return work order summaries with progress and timing metadata
- potentially `GET /api/v1/production-orders/{order_id}/work-orders` if the UI needs separate fetch

---

## 4. OperationExecutionOverview

- Frontend component: `frontend/src/app/pages/OperationExecutionOverview.tsx`
- Route: `/operation/:woId`
- Screen purpose: operation execution Gantt overview for a work order, with clickable operations.

### Related backend endpoint(s)
- `GET /api/v1/work-orders/{wo_id}/operations`

### Main request params
- `woId` path parameter for work order ID

### Expected response schema
- list of operations with timeline and status details
- fields expected by UI:
  - `id`
  - `sequence`
  - `name`
  - `workstation`
  - `operatorName`
  - `status`
  - `planned_start`
  - `planned_end`
  - `actual_start`
  - `actual_end`
  - `currentTime`
  - `delayMinutes`
  - `qcRequired`
  - `progress`

### Backend-derived fields
- operation status
- planned and actual timing
- current progress
- QC requirement flag
- delay and on-time/late status

### User intent only fields
- click on operation bar to navigate to detail

### Current gap or mismatch
- current backend operation list schema only provides basic fields and does not include time tracking or `currentTime`/`delayMinutes`.
- `status` values in frontend include `Not Started` and `Running`, while backend uses `Pending` / `In Progress` / `Completed`.

### Recommended next backend endpoint if missing
- enrich `GET /api/v1/work-orders/{wo_id}/operations` with operation schedule and live execution fields

---

## 5. OperationExecutionDetail

- Frontend component: `frontend/src/app/pages/OperationExecutionDetail.tsx`
- Route: `/operation-detail/:operationId`
- Screen purpose: detailed view of a single operation with overview, quality, materials, timeline, and documents tabs.

### Related backend endpoint(s)
- `GET /api/v1/operations/{operation_id}`
- `POST /api/v1/operations/{operation_id}/start`

### Main request params
- `operationId` path parameter
- `OperationStartRequest` body for start action:
  - `operator_id`
  - `started_at`

### Expected response schema
- operation detail fields expected by UI:
  - `id`
  - `operation_number`
  - `name`
  - `sequence`
  - `description`
  - `work_order_id`
  - `work_order_number`
  - `production_order_id`
  - `production_order_number`
  - `status`
  - `productionLine`
  - `workstation`
  - `work_center`
  - `machineId`
  - `machineName`
  - `operatorId`
  - `operatorName`
  - `planned_start`
  - `planned_end`
  - `actual_start`
  - `actual_end`
  - `estimatedCompletion`
  - `quantity`
  - `completed_qty`
  - `good_qty`
  - `scrap_qty`
  - `progress`
  - `qcRequired`
  - `qcStatus`
  - `timing`
  - `delayMinutes`
  - `blockReason`
  - `timeline` events
  - `materials`
  - `qc_checkpoints`

### Backend-derived fields
- operation status and timing
- actual start/end timestamps
- progress / completed quantities
- quality pass/fail state
- timeline event history

### User intent only fields
- operation start request payload
- progress of the currently selected tab is UI-only until backed by real data

### Current gap or mismatch
- `OperationDetail` schema in backend is too narrow: it lacks `description`, `operatorName`, `estimatedCompletion`, `timing`, `delayMinutes`, and rich tab data structures.
- frontend uses mock arrays for QC checkpoints, materials, and timeline events, which are not represented in the current backend skeleton.

### Recommended next backend endpoint if missing
- `GET /api/v1/operations/{operation_id}` should return richer operation detail including event-derived timing and QC status
- add `POST /api/v1/operations/{operation_id}/report-quantity`
- add `POST /api/v1/operations/{operation_id}/complete`
- add QC-related endpoints later if needed

---

## 6. StationExecution

- Frontend component: `frontend/src/app/pages/StationExecution.tsx`
- Route: `/station-execution`
- Screen purpose: station-level execution workflow with operator login, serial scan, execution session control, QC entry, and part consumption.

### Related backend endpoint(s)
- `POST /api/v1/operations/{operation_id}/start`
- `GET /api/v1/work-orders/{wo_id}/operations`
- future endpoints for quantity reporting and completion

### Main request params
- none currently in route; the page is driven by scanned serial and operator state
- expected future params could include:
  - `operation_id`
  - `wo_id`
  - `operator_id`
  - `serial_number`

### Expected response schema
- work order / operation assignment data to load the next active operation
- station session metadata
- QC checkpoints for the operation
- part list consumption details

### Backend-derived fields
- operation metadata
- authorized operator / operator assignment
- execution session state and start time
- QC pass/fail result evaluation

### User intent only fields
- operator login inputs
- serial scan input
- QC value entry and part consumption actions
- session control buttons

### Current gap or mismatch
- StationExecution is currently entirely local mock state.
- The backend skeleton only includes start operation intent; it does not include session or work order resolution by serial number.

### Recommended next backend endpoint if missing
- `POST /api/v1/operations/{operation_id}/start`
- `POST /api/v1/operations/{operation_id}/report-quantity`
- `POST /api/v1/operations/{operation_id}/complete`
- `GET /api/v1/work-orders/{wo_id}/operations` to load station tasks
- later, QC measurement endpoints

---

## 7. QCCheckpoints

- Frontend component: `frontend/src/app/pages/QCCheckpoints.tsx`
- Route: `/quality`
- Screen purpose: QC checkpoint catalog, search/filter, and checkpoint status overview.

### Related backend endpoint(s)
- none currently in Phase 1 skeleton

### Main request params
- none currently

### Expected response schema
- list of QC checkpoints with fields:
  - `id`
  - `checkpoint_name`
  - `station_id`
  - `station_name`
  - `operation_id`
  - `qc_type`
  - `parameter`
  - `specification`
  - `lower_limit`
  - `upper_limit`
  - `unit`
  - `frequency`
  - `mandatory`
  - `status`

### Backend-derived fields
- checkpoint status
- active/inactive state

### User intent only fields
- filter and search inputs
- actions for add/edit/delete (UI-only placeholders)

### Current gap or mismatch
- the current backend skeleton does not include QC endpoints or checkpoint models.
- QCCheckpoints is fully mock-based and will require a dedicated QC domain when Phase 1 expands.

### Recommended next backend endpoint if missing
- `GET /api/v1/qc/checkpoints`
- `POST /api/v1/qc/measurements`
- `GET /api/v1/operations/{operation_id}/qc`

---

## Overall frontend observations

1. **Frontend pages currently relying on mock data**
   - `Home`
   - `ProductionOrderList`
   - `OperationList`
   - `OperationExecutionOverview`
   - `OperationExecutionDetail`
   - `StationExecution`
   - `QCCheckpoints`

2. **Where frontend currently derives status/progress**
   - `Home` computes line and queue statuses locally from `productionLines` and `queueOrders` mock data.
   - `ProductionOrderList` reads `status` and `progress` from `productionOrders` mock rows.
   - `OperationList` computes `overallProgress` and filters work orders from static mock objects.
   - `OperationExecutionOverview` computes operation counts, completed/in-progress counts, and overall progress from `mockOperationSequence`.
   - `OperationExecutionDetail` uses mock operation fields and derives QC counts, material status, and timeline display from static arrays.
   - `StationExecution` updates execution state, QC results, and part consumption entirely in local component state.
   - `QCCheckpoints` filters and displays checkpoint status from `mockCheckpoints`.

3. **Backend response shapes likely needing adjustment**
   - `ProductionOrderSummary` should be expanded to include `serialNumber`, `releasedDate`, `routeId`, `status`, `progress`, `plannedCompletionDate`, and UI-specific labels like `assignee` and `department`.
   - `ProductionOrderDetail` should include richer work order metadata and derived `overall_progress`/`delay_minutes` values.
   - `OperationListItem` should include scheduling fields such as `workstation`, `productionLine`, `timing`, and `remainingTime` or `delayMinutes`.
   - `OperationDetail` should include `description`, `operatorName`, `estimatedCompletion`, `timing`, `qcStatus`, and potentially a nested timeline/materials structure.
   - `dashboard` payload should likely be extended beyond simple counts to support the Home screen's queue and production line summaries.

---

## Recommended integration priorities

1. wire `ProductionOrderList` to `GET /api/v1/production-orders` first with a fuller summary shape
2. wire `OperationList` and production order detail to `GET /api/v1/production-orders/{order_id}`
3. wire `OperationExecutionOverview` to `GET /api/v1/work-orders/{wo_id}/operations`
4. wire `OperationExecutionDetail` to `GET /api/v1/operations/{operation_id}` and `POST /api/v1/operations/{operation_id}/start`
5. expand `Home` dashboard payload to include queue and line metrics
6. build station/session endpoints for `StationExecution`
7. add QC endpoints after the core execution flow is stable
