# Frontend Coverage: Manufacturing Master Data (MMD) Shell Report

**Task:** FE-COVERAGE-01B — Add safe shell coverage for missing/partial Manufacturing Master Data screens  
**Date:** 2026-04-28  
**Status:** COMPLETE — All 5 Priority A shells delivered and verified

---

## Summary

Five new Manufacturing Master Data shell pages have been added to the frontend. All screens are SHELL phase with MOCK_FIXTURE data. No backend changes were made. All dangerous write/lifecycle actions are disabled (Lock icon + `cursor-not-allowed`). Backend MMD system remains source of truth.

---

## Screens Delivered

| Screen | Route | Phase | Data Source | Component |
|--------|-------|-------|-------------|-----------|
| BOM List | `/bom` | SHELL | MOCK_FIXTURE | `BomList.tsx` |
| BOM Detail | `/bom/:bomId` | SHELL | MOCK_FIXTURE | `BomDetail.tsx` |
| Routing Operation Detail | `/routes/:routeId/operations/:operationId` | SHELL | MOCK_FIXTURE | `RoutingOperationDetail.tsx` |
| Resource Requirement Mapping | `/resource-requirements` | SHELL | MOCK_FIXTURE | `ResourceRequirements.tsx` |
| Reason Code Management | `/reason-codes` | SHELL | MOCK_FIXTURE | `ReasonCodes.tsx` |

---

## Governance Compliance

### SHELL Phase Contract
- ✅ All pages display `MockWarningBanner` with `phase="SHELL"` and disclosure note
- ✅ All pages display `ScreenStatusBadge` with `phase="SHELL"`
- ✅ All pages display `BackendRequiredNotice` with MMD system note
- ✅ All write/lifecycle actions are disabled with Lock icon and `cursor-not-allowed`
- ✅ No API calls made — all data is inline MOCK_FIXTURE constants

### Actions Disabled (per screen)

**BOM List:** Create BOM, Import BOM  
**BOM Detail:** Edit BOM, Release BOM, Retire BOM, Add Component  
**Routing Operation Detail:** Edit Operation, Release  
**Resource Requirements:** Assign Resource, Edit (per row)  
**Reason Codes:** Create Reason Code, Edit (per row), Retire (per row)

---

## Infrastructure Updates

### `routes.tsx`
- Added 5 imports: `BomList`, `BomDetail`, `RoutingOperationDetail`, `ResourceRequirements`, `ReasonCodes`
- Added 5 route definitions:
  - `{ path: "bom", Component: BomList }`
  - `{ path: "bom/:bomId", Component: BomDetail }`
  - `{ path: "routes/:routeId/operations/:operationId", Component: RoutingOperationDetail }`
  - `{ path: "resource-requirements", Component: ResourceRequirements }`
  - `{ path: "reason-codes", Component: ReasonCodes }`

### `screenStatus.ts`
- Added 5 new SHELL entries: `bomList`, `bomDetail`, `routingOpDetail`, `resourceRequirements`, `reasonCodes`

### `components/Layout.tsx`
- Added icon imports: `FileText`, `Server`, `Tag`
- Added `getIconForPath()` entries for `/bom`, `/resource-requirements`, `/reason-codes`

### `persona/personaLanding.ts`
- **SUP menu:** Added BOM, Reason Codes
- **IEP menu:** Added BOM, Resource Requirements, Reason Codes
- **PMG menu:** Added BOM, Resource Requirements, Reason Codes
- Added `isRouteAllowedForPersona` guard entries for all 5 new routes

### `i18n/namespaces.ts`
- Added: `bomList`, `bomDetail`, `routingOpDetail`, `resourceReqs`, `reasonCodes`

### `i18n/registry/en.ts` + `i18n/registry/ja.ts`
- Added ~82 keys across 5 MMD namespaces (parity maintained)

---

## Verification Gates

| Gate | Result |
|------|--------|
| `npm run build` | ✅ PASS (built in ~7s) |
| `npm run lint` | ✅ PASS (0 errors) |
| `npm run check:routes` | ✅ PASS (0 FAIL) |
| `npm run lint:i18n:registry` | ✅ PASS (1092 keys, en/ja synchronized) |

---

## Invariants Maintained

- ❌ No backend changes
- ❌ No API files changed
- ❌ No auth/impersonation/persona behavior changed
- ❌ No existing PARTIAL screens downgraded (ProductList, ProductDetail, RouteList, RouteDetail remain PARTIAL + BACKEND_API)
- ❌ No execution state machine touched
- ❌ No real MMD mutations surfaced in UI
