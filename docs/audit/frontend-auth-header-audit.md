# Frontend Auth Header Audit

Date: 2026-04-05
Scope: frontend API plumbing only (no backend code changes)

## 1) Summary

This audit verified that protected backend calls use the shared authenticated HTTP path in frontend.

- Total findings: 4
- Type A (protected, must include Authorization): 2
- Type B (public/external/infra intentional): 2
- Type C (unknown): 0
- Findings fixed: 2/2 (Type A)

Result: protected call paths in audited files now flow through `httpClient.request()` which injects `Authorization: Bearer <token>` from AuthContext context provider.

## 2) Findings List

### F-01
- File: frontend/src/app/pages/OperationList.tsx
- Lines (before fix): 141-147, 165-171
- Type: A (protected)
- What was wrong:
  - Direct `fetch('/api/v1/production-orders/...')` and `fetch('/api/v1/production-orders')` bypassed shared `httpClient`.
  - Could send requests without Authorization header depending on call path.

### F-02
- File: frontend/src/app/pages/ProductionOrderList.tsx
- Lines (before fix): 223-229
- Type: A (protected)
- What was wrong:
  - Direct `fetch('/api/v1/production-orders')` bypassed shared `httpClient`.
  - Could send requests without Authorization header.

### F-03
- File: frontend/src/app/api/httpClient.ts
- Lines: 99-104
- Type: B (intentional infra)
- Notes:
  - This is the official shared transport itself.
  - `fetch()` here is expected; headers are prepared centrally by `buildHeaders()`.

### F-04
- File: frontend/src/utils/supabase.ts
- Lines: 17-24
- Type: B (intentional external service)
- Notes:
  - Calls Supabase function endpoint with Supabase anon token, not MES backend `/api/v1` protected endpoints.
  - Not part of MES bearer-session auth path.

## 3) Fixes Applied

### Fix A: unify production-order requests behind shared authenticated API client

- Added new wrapper: frontend/src/app/api/productionOrderApi.ts
  - `list()` -> `request('/v1/production-orders')`
  - `get(orderId)` -> `request('/v1/production-orders/{id}')`

- Updated frontend/src/app/pages/OperationList.tsx
  - Replaced direct `fetch` calls with `productionOrderApi.list()` and `productionOrderApi.get()`.
  - Current references after fix:
    - import/wrapper usage lines 11-16
    - `loadProductionOrder` lines 119-121
    - list call line 138

- Updated frontend/src/app/pages/ProductionOrderList.tsx
  - Replaced direct `fetch` call with `productionOrderApi.list()`.
  - Current reference after fix: line 224.

### Fix B: optional DEV diagnostic for Authorization attachment

- Updated frontend/src/app/api/httpClient.ts
  - Added DEV-only debug gate:
    - `import.meta.env.DEV && VITE_HTTP_DEBUG_AUTH === '1'`
  - Logs whether Authorization header is attached, without printing token.
  - Relevant lines:
    - gate: 29-31
    - debug log: 89-96

### Fix C: automated smoke check script (no new dependencies)

- Added frontend/scripts/auth-header-smoke-check.mjs
  - Imports `request` and `setHttpContextProvider` from `httpClient.ts`
  - Mocks `fetch`
  - Asserts:
    - `Authorization: Bearer smoke-token`
    - `X-Tenant-ID: default`

## 4) Verification Results

### 4.1 Build
- Command: `cd frontend && npm run build`
- Result: PASS

### 4.2 Automated smoke check (code-level)
- Command: `cd frontend && node --experimental-strip-types scripts/auth-header-smoke-check.mjs`
- Result: PASS
- Output: `PASS: httpClient attaches Authorization and tenant headers when token context is present.`

### 4.3 Protected endpoint call path proof in code
- `/work-orders` path now loads production-order data through `productionOrderApi` -> `httpClient.request()`.
- `/production-orders` path now loads through `productionOrderApi` -> `httpClient.request()`.
- Existing API modules for `/operations` and route/monitor flows already use `request()` from shared `httpClient`.

### 4.4 Manual network verification (browser)
- Target scenarios:
  - SUP -> `/work-orders`
  - SUP -> `/routes`
  - SUP -> `/operations`
- Expected in DevTools Network:
  - `Authorization: Bearer <token>` present
  - No `{"detail":"Authentication required"}` due to missing header
- Note:
  - Browser DevTools steps are manual and must be executed in runtime UI session.

## 5) Non-regression

- No backend files modified by this audit.
- Persona/menu policy logic was not altered.
- Existing login/logout flow remains unchanged.
