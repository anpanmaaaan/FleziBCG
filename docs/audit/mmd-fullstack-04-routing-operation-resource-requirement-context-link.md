# MMD-FULLSTACK-04 — Routing Operation to Resource Requirements Context Link Report

## History

| Date       | Version | Change                                                                                       |
|------------|--------:|----------------------------------------------------------------------------------------------|
| 2026-05-02 |    v1.0 | Added read-only contextual navigation from Routing Operation Detail to Resource Requirements. |

---

## 1. Scope

Narrow frontend read-navigation slice for Manufacturing Master Data / Product Definition.

Added a contextual link from the Routing Operation Detail screen (`/routes/:routeId/operations/:operationId`) to the Resource Requirements read view (`/resource-requirements?routeId=:routeId&operationId=:operationId`), and added a corresponding "clear filter" escape link on the Resource Requirements page.

No backend source, no database migration, no write action, no new route was created.

---

## 2. Baseline Evidence Used

| Report                                                          | Status         |
|-----------------------------------------------------------------|----------------|
| `docs/audit/mmd-audit-00-fullstack-source-alignment.md`         | Confirmed present |
| `docs/audit/mmd-fullstack-01-routing-operation-contract-alignment.md` | Confirmed present |
| `docs/audit/mmd-fullstack-02-routing-operation-detail-read-integration.md` | Confirmed present |
| `docs/audit/mmd-fullstack-03-resource-requirements-read-integration.md` | Confirmed present |

MMD-FULLSTACK-03 source state confirmed:
- `ResourceRequirements.tsx`: Phase `PARTIAL/BACKEND_API`, already uses `useSearchParams` with `routeId`/`operationId` handling.
- `RoutingOperationDetail.tsx`: Phase `PARTIAL/BACKEND_API`, reads `routeId`/`operationId` from `useParams`.
- `routingApi.ts`: includes `listResourceRequirements(routingId, operationId)` helper and `ResourceRequirementItemFromAPI` type.
- `screenStatus.ts`: `resourceRequirements` marked `PARTIAL/BACKEND_API`.

---

## 3. Navigation Contract

| Source Screen                             | Target Screen             | Context Params                            | Decision               |
|-------------------------------------------|---------------------------|-------------------------------------------|------------------------|
| `/routes/:routeId/operations/:operationId` | `/resource-requirements` | `?routeId=:routeId&operationId=:operationId` | Safe read navigation; no authorization implied |

The link uses `encodeURIComponent` on both params to prevent URL injection.

---

## 4. Query Param Behavior

| Param          | Source                      | Consumer                | Behavior                                                    |
|----------------|-----------------------------|-------------------------|-------------------------------------------------------------|
| `routeId`      | `useParams` in ROD page     | `useSearchParams` in RR page | Filters load to single routing                         |
| `operationId`  | `useParams` in ROD page     | `useSearchParams` in RR page | Filters load to single operation within routing        |
| (absent)       | —                           | RR page                 | Falls through to global all-routings load mode              |
| `operationId` without `routeId` | — | RR page           | Guard triggers; shows `resourceReqs.error.invalidFilter`    |
| invalid IDs    | —                           | RR page                 | Operation not found in API response → empty table, no crash |

Clear-filter link: visible in RR scope banner whenever `routeId` or `operationId` are present. Links to `/resource-requirements` (no params). i18n key: `resourceReqs.action.clearFilter`.

---

## 5. Files Changed

| File                                                  | Change                                                                  |
|-------------------------------------------------------|-------------------------------------------------------------------------|
| `frontend/src/app/pages/RoutingOperationDetail.tsx`   | Added contextual `<Link>` to Resource Requirements in Resources section |
| `frontend/src/app/pages/ResourceRequirements.tsx`     | Added `Link` import; added clear-filter link in scope banner            |
| `frontend/src/app/i18n/registry/en.ts`                | Added `routingOpDetail.action.viewResourceReqs`, `resourceReqs.action.clearFilter` |
| `frontend/src/app/i18n/registry/ja.ts`                | Added same two keys in Japanese                                         |

---

## 6. Frontend Changes

### RoutingOperationDetail.tsx

Added a `<Link>` inside the Resources section footer row (alongside the existing italic note):

```tsx
{routeId && operationId && (
  <Link
    to={`/resource-requirements?routeId=${encodeURIComponent(routeId)}&operationId=${encodeURIComponent(operationId)}`}
    className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium shrink-0"
  >
    {t("routingOpDetail.action.viewResourceReqs")}
  </Link>
)}
```

The link is conditional: only rendered when both `routeId` and `operationId` are available from `useParams`. The link is a plain read navigation link — no POST, no mutation, no authorization claim.

### ResourceRequirements.tsx

- Added `Link` import from `react-router`.
- Refactored the scope info banner to a flex row with a conditional "Clear filter" link:

```tsx
<div className="flex items-center justify-between gap-4">
  <span><strong>{t("resourceReqs.scope.label")}:</strong> {scopeText}</span>
  {(routeId || operationId) && (
    <Link to="/resource-requirements" className="text-xs text-blue-600 hover:text-blue-800 font-medium shrink-0">
      {t("resourceReqs.action.clearFilter")}
    </Link>
  )}
</div>
```

Existing load modes (filtered by routing+operation, filtered by routing only, global) remain unchanged.

### i18n Keys Added (en.ts / ja.ts)

| Key                                      | en                             | ja                           |
|------------------------------------------|--------------------------------|------------------------------|
| `routingOpDetail.action.viewResourceReqs` | View Resource Requirements    | リソース要件を表示             |
| `resourceReqs.action.clearFilter`        | Clear filter                   | フィルターをクリア             |

Total key count after: **1702** (parity PASS, en.ts = ja.ts).

---

## 7. Backend Verification / Changes

**Backend not modified.** No backend source files, no migration files, no schema changes were made in this slice.

Backend regression inspection: `tests/test_resource_requirement_api.py` and `tests/test_routing_foundation_api.py` — no backend source changed; targeted backend tests not required for this FE navigation-only slice. Tests were passing at MMD-FULLSTACK-03 baseline (10 passed).

---

## 8. Screen Status Decision

No screen status change required. Both pages remain `PARTIAL/BACKEND_API` as established in MMD-FULLSTACK-03. This slice adds UX navigation only; it does not change functional completeness.

---

## 9. Boundary Guardrails

| Invariant                                             | Enforcement                                                |
|-------------------------------------------------------|------------------------------------------------------------|
| Link is read-navigation only                          | `<Link>` component, no POST/PUT/DELETE                     |
| Resource Requirements page remains read-only          | All write action buttons remain `disabled` with lock icon  |
| Backend is not modified                               | No BE files touched                                        |
| Query params do not grant authorization               | Server-side auth unchanged; JWT not affected               |
| Routing Operation is MMD definition, not exec state   | Link label is "View Resource Requirements", not "Execute"  |
| Frontend must not invent Quality truth                | No quality-related rendering added                         |
| No mock data reintroduced                             | Load paths remain API-backed                               |
| No screen status overclaim                            | Pages remain `PARTIAL`                                     |

---

## 10. Tests / Verification Commands

| Gate                | Command                                                          | Result     |
|---------------------|------------------------------------------------------------------|------------|
| TypeScript (IDE)    | VS Code language server                                          | PASS — no errors |
| i18n parity         | `node scripts/check_i18n_registry_parity.mjs`                    | PASS — 1702 keys, en.ts = ja.ts |
| Route smoke         | `node scripts/route-smoke-check.mjs`                             | PASS — all gates |
| Vite build          | `node node_modules/vite/bin/vite.js build`                       | PASS — built in ~8s |
| ESLint (changed)    | `node node_modules/eslint/bin/eslint.js src/app/pages/RoutingOperationDetail.tsx src/app/pages/ResourceRequirements.tsx` | PASS — no output = no errors |
| Backend (baseline)  | Not re-run; backend not modified; MMD-FULLSTACK-03 baseline was 10 passed | Inspection-only |

---

## 11. Remaining Risks / Deferred Items

| Item                                               | Reason Deferred                                 |
|----------------------------------------------------|-------------------------------------------------|
| Resource Requirement create/edit/delete UI         | Out of scope — requires backend MMD governance workflow |
| Work Center entity                                 | Out of scope                                    |
| Quality checkpoint linkage                         | Out of scope                                    |
| "Back to Operation" link in RR page                | Not requested; clear-filter link covers the escape path |
| Required skill / skill level on routing operation  | Out of scope                                    |

---

## 12. Final Verdict

**COMPLETE.** MMD-FULLSTACK-04 objectives satisfied:

- Routing Operation Detail has a contextual link to Resource Requirements.
- Link includes `routeId` and `operationId` query params (URL-encoded).
- Resource Requirements page already consumed query params (MMD-FULLSTACK-03); clear-filter escape added.
- Default Resource Requirements behavior unchanged when no params present.
- Invalid query params do not crash the page (empty table, existing guard).
- No mock data reintroduced.
- No write actions enabled.
- No backend source modified.
- No migration modified.
- All frontend verification gates PASS.
- Report created.
