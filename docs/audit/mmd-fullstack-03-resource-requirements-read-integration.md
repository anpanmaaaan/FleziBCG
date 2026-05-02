# MMD-FULLSTACK-03 — Resource Requirements FE Read Integration

## Routing
- Selected brain: flezibcg-ai-brain-v6-auto-execution
- Selected mode: autonomous implementation (read-only vertical slice)
- Hard Mode MOM: v3 ON for MMD contract/read-integration boundary discipline
- Reason: Slice touches governed MMD read contracts (routing/operation/resource requirement linkage), FE source-of-truth representation, and invariant-preserving UI behavior without introducing write paths.

## Scope
- Implement FE read integration for /resource-requirements using existing backend read APIs only.
- Keep mutation controls disabled (no create/update/delete from FE).
- Do not add/modify backend endpoints, migrations, or contracts.

## Design Evidence Extract
- FE target page exists and is shell/mock: frontend/src/app/pages/ResourceRequirements.tsx.
- Backend read path exists under routings API:
  - GET /v1/routings
  - GET /v1/routings/{routing_id}
  - GET /v1/routings/{routing_id}/operations/{operation_id}/resource-requirements
- Backend schema contract for resource requirement exists in backend/app/schemas/resource_requirement.py.
- Backend route coverage exists in:
  - backend/tests/test_resource_requirement_api.py
  - backend/tests/test_resource_requirement_service.py
  - backend/tests/test_routing_foundation_api.py

## Read Integration Contract Map
- Existing FE API reused:
  - routingApi.listRoutings()
  - routingApi.getRouting(routingId)
- Existing backend read endpoint integrated via FE API extension:
  - routingApi.listResourceRequirements(routingId, operationId)
- FE page loading modes:
  - Global: load all routings, then read requirements per operation.
  - Routing-scoped: ?routeId=... (or ?routingId=...), load all operation requirements for that routing.
  - Routing+operation-scoped: ?routeId=...&operationId=..., load only that operation requirements.
  - Invalid filter guard: operationId without routeId shows deterministic error message.

## Resource Requirement API Contract
- Response fields used from backend contract:
  - requirement_id
  - routing_id
  - operation_id
  - required_resource_type
  - required_capability_code
  - quantity_required
  - notes
  - metadata_json
- FE derived fields (display only):
  - operation_code / operation_name / routing_code from routing + operation context
  - status from routing.lifecycle_status (context status badge)

## Invariant Map
- Backend remains source of truth:
  - FE performs read-only aggregation from backend APIs.
- Authorization remains server-side:
  - FE only consumes already-protected endpoints.
- No execution/auth/state derivation in FE:
  - No lifecycle transitions or write commands added.
- No fabricated write behavior:
  - Assign/Edit controls remain disabled and labeled backend-governed.

## FE/BE Alignment Map
- frontend/src/app/api/routingApi.ts:
  - Added typed resource requirement read contract and nested list endpoint method.
- frontend/src/app/pages/ResourceRequirements.tsx:
  - Replaced inline mock fixture with async backend read loader.
  - Added scoped query behavior and deterministic invalid-filter guard.
  - Updated table columns to backend-backed values (resource type, capability, quantity, notes, lifecycle status context).
- frontend/src/app/screenStatus.ts:
  - Updated /resource-requirements from SHELL/MOCK_FIXTURE to PARTIAL/BACKEND_API.
- frontend/src/app/i18n/registry/en.ts and frontend/src/app/i18n/registry/ja.ts:
  - Added read-integration messages and new column/scope/error/footer keys.

## Test Matrix
- FE static verification:
  - i18n registry parity
  - route smoke / coverage
  - build
  - lint
- BE targeted regression:
  - tests/test_resource_requirement_api.py
  - tests/test_resource_requirement_service.py
  - tests/test_routing_foundation_api.py

## Verdict Before Coding
- Safe path exists and is contract-aligned.
- Proceed with FE-only read integration using existing backend APIs.
- No backend contract or migration changes required.

## Implementation Summary
- Integrated /resource-requirements with backend read APIs via routingApi.
- Preserved strict read-only UX (all mutation buttons disabled).
- Added scoped query support for deterministic contextual reads:
  - routeId/routingId
  - operationId
- Replaced shell-only scope messaging with read-integration scope messaging.
- Updated status registry classification to PARTIAL/BACKEND_API.

## Verification
Frontend commands requested in task:
1) node scripts/check-i18n-registry.cjs
2) node scripts/check-route-parity.mjs
3) node scripts/check-screen-status.mjs
4) vite build
5) eslint

Workspace reality:
- Scripts (1)-(3) above are not present under frontend/scripts in this repo.
- Equivalent available checks were executed:
  - G:\nodejs\node.exe scripts/check_i18n_registry_parity.mjs
    - PASS: en.ts and ja.ts key-synchronized
  - G:\nodejs\node.exe scripts/route-smoke-check.mjs
    - PASS summary with 0 failures; includes screenStatus coverage alignment
  - G:\nodejs\node.exe node_modules/vite/bin/vite.js build
    - PASS
  - G:\nodejs\node.exe node_modules/eslint/bin/eslint.js .
    - PASS (no output)

Backend command executed:
- g:/Work/FleziBCG/.venv/Scripts/python.exe -m pytest -q tests/test_resource_requirement_api.py tests/test_resource_requirement_service.py tests/test_routing_foundation_api.py
- Result: 10 passed in 2.18s

## Final Verdict
- MMD-FULLSTACK-03 completed as a safe, read-only FE integration slice.
- /resource-requirements now reads existing backend contracts.
- No backend write path, contract mutation, or scope expansion introduced.
