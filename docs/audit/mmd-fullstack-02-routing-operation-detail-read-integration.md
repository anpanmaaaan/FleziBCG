# MMD-FULLSTACK-02 Routing Operation Detail API Read Integration

## Routing
- Selected brain: MOM Brain
- Selected mode: Autonomous Implementation (Read-only FE slice)
- Hard Mode MOM: v3 ON for MMD contract/read-integration boundary discipline.
- Reason: This slice connects Routing Operation Detail to the existing backend read contract for manufacturing master data. It remains read-only and does not touch execution commands, quality truth, material/backflush, tenant/auth, migrations, or backend write paths.

## Pre-Coding Evidence

### Design Evidence Extract
- Existing backend read API already returns routing with operations list: GET /v1/routings/{routing_id}.
- Existing frontend client already exposes routingApi.getRouting(routingId).
- Existing operation fields required by this slice are already present in FE contract: operation_id, operation_code, operation_name, sequence_no, standard_cycle_time, required_resource_type, setup_time, run_time_per_unit, work_center_code.
- Current RoutingOperationDetail page was shell/mock and needed conversion to backend read.

### Read Integration Contract Map
- Request path: /v1/routings/{routeId}
- FE caller: routingApi.getRouting(routeId)
- Response contract used:
  - routing_id, routing_code, routing_name, lifecycle_status
  - operations[] containing operation fields above
- No new endpoint required.

### Operation Lookup Contract
- Route params used: routeId and operationId.
- Lookup rule: operation.operation_id === operationId.
- Not found conditions:
  - routeId or operationId missing
  - backend returns 404 for routing
  - routing exists but no operation matches operationId

### Invariant Map
- Read-only only: no create/update/release operations added.
- Backend remains source of truth for execution eligibility and resource applicability.
- Frontend does not derive authorization or execution truth.
- No schema, migration, or backend write-path changes.

### FE/BE Alignment Map
- FE API type source: frontend/src/app/api/routingApi.ts
- BE response source: backend/app/schemas/routing.py and backend/app/api/v1/routings.py
- Alignment status: direct mapping, no adapter transformation required for this slice.

### Test Matrix
- Frontend build: required
- Frontend lint: required
- Frontend i18n registry parity: required
- Frontend route smoke: required
- Backend routing read contract pytest set: required

### Verdict Before Coding
- ALLOW_IMPLEMENTATION

## Implementation Summary
- Replaced mock fixture data path in RoutingOperationDetail with live read integration using routeId and operationId.
- Added loading, error, and not-found states for operation detail read flow.
- Kept mutation buttons disabled and backend-required notices intact.
- Updated screen status registry classification from SHELL/MOCK_FIXTURE to PARTIAL/BACKEND_API for routing operation detail route.

## Files Changed
- frontend/src/app/pages/RoutingOperationDetail.tsx
- frontend/src/app/screenStatus.ts

## Verification

### Frontend
- Command set:
  - npm.cmd run build
  - npm.cmd run lint
  - npm.cmd run lint:i18n:registry
  - npm.cmd run check:routes
- Result:
  - build: pass
  - lint: pass
  - i18n registry parity: pass (1691 keys synchronized)
  - route smoke: pass (24 pass, 0 fail; 77/78 covered, 1 redirect excluded)

Note: PowerShell execution policy blocked npm.ps1, so npm.cmd was used.

### Backend
- Command:
  - g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest tests/test_routing_foundation_api.py tests/test_routing_operation_extended_fields.py tests/test_routing_foundation_service.py -q
- Result:
  - 18 passed in 1.69s

## Scope Guard Confirmation
- No backend code changes.
- No new API endpoints.
- No migration or table changes.
- No additions in out-of-scope domains (BOM/Product Version/Reason Codes/Resource Requirement execution logic).

## Final Verdict
- MMD-FULLSTACK-02 complete for read integration scope.