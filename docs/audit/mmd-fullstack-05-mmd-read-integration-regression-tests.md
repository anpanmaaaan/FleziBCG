# MMD-FULLSTACK-05: MMD Read Integration Regression Tests — Audit Report

**Slice:** MMD-FULLSTACK-05  
**Type:** QA / Contract Hardening — static regression script, no runtime changes  
**Date:** 2025-07-30  
**Branch:** autocode  
**Hard Mode MOM:** v3 ON (boundary/contract discipline for MMD read truth)

---

## Summary

Creates `frontend/scripts/mmd-read-integration-regression-check.mjs` — a static source-code
invariant regression script that locks the MMD read integration baseline established by
MMD-FULLSTACK-01 through 04 and frozen in MMD-READ-BASELINE-01.

No runtime source was modified. Only a new script file and a `package.json` entry were added.

---

## Routing

- **Selected brain:** MOM Brain
- **Selected mode:** QA / Contract Hardening
- **Hard Mode MOM:** v3 ON
- **Reason:** Locks MMD manufacturing definition read truth. Guards against domain boundary
  violations, mock reversion, rejected field reintroduction, and screen status regression.

---

## Pre-Coding Evidence

### Baseline Evidence Extract

| Evidence Item | Status |
|---|---|
| MMD-BE-01 committed (`26bfda5f`) | ✅ Confirmed |
| MMD-FULLSTACK-01 through 04 committed | ✅ Confirmed (HEAD `e819368f`) |
| `routingApi.ts` has `setup_time`, `run_time_per_unit`, `work_center_code` | ✅ Confirmed |
| `routingApi.ts` has `ResourceRequirementItemFromAPI` + `listResourceRequirements()` | ✅ Confirmed |
| `RoutingOperationDetail.tsx` uses `useParams`, `routingApi.getRouting`, `encodeURIComponent`, `/resource-requirements` link | ✅ Confirmed |
| `ResourceRequirements.tsx` uses `useSearchParams`, `listResourceRequirements`, clear-filter link | ✅ Confirmed |
| `screenStatus.ts`: `routingOpDetail` = PARTIAL/BACKEND_API; `resourceRequirements` = PARTIAL/BACKEND_API | ✅ Confirmed |
| `routes.tsx` has all 9 MMD routes | ✅ Confirmed |
| `en.ts`/`ja.ts`: `viewResourceReqs` and `clearFilter` keys present | ✅ Confirmed (1702 keys, parity) |

### Invariant Map

| Invariant | Enforcement |
|---|---|
| MMD read screens stay read-only | Assert write-action buttons remain disabled on RR page |
| `qc_checkpoint_count` belongs to Quality domain | Assert absent from `routingApi.ts` and ROD page |
| `work_center_code` is canonical; bare `work_center` is rejected | Regex `\bwork_center\b(?!_code)` NOT present |
| `required_skill` / `required_skill_level` belong to ResourceRequirement domain | Assert absent from ROD and API type |
| Backend is source of truth; no mock primary data | Assert no `const mock[…] = [` in RR page |
| Screen status not regressed | Assert PARTIAL + BACKEND_API for both screens |

### Stop Conditions Check

- MMD-BE-01 committed ✅ — no stop condition triggered
- MMD-FULLSTACK-04 committed ✅ — no stop condition triggered

**Verdict:** PROCEED — all evidence present, all stop conditions cleared.

---

## File Change Plan

| File | Change |
|---|---|
| `frontend/scripts/mmd-read-integration-regression-check.mjs` | CREATED — 47-check regression script |
| `frontend/package.json` | MODIFIED — added `"check:mmd:read"` script |

---

## Check Coverage

The script covers 6 check groups, 47 individual assertions:

| Group | Checks | Description |
|---|---|---|
| A. Routing API contract lock | 9 | Extended fields present; RR type/helper present; rejected fields absent |
| B. Routing Operation Detail contract lock | 13 | Backend read active; `work_center_code` correct; link to RR present with params + `encodeURIComponent`; rejected fields absent |
| C. Resource Requirements read integration lock | 6 | Backend read active; query params consumed; clear-filter present; no inline mock array; write actions remain disabled |
| D. Screen status lock | 2 | Both screens remain PARTIAL/BACKEND_API |
| E. Route registry lock | 9 | All 9 MMD routes present in `routes.tsx` |
| F. i18n keys lock | 8 | MMD-FULLSTACK-03 and 04 keys present in `en.ts` and `ja.ts` |

---

## Verification Gates

| Gate | Command | Result |
|---|---|---|
| MMD regression script | `node scripts/mmd-read-integration-regression-check.mjs` | ✅ 47/47 PASS |
| i18n parity | `node scripts/check_i18n_registry_parity.mjs` | ✅ PASS — 1702 keys |
| Route smoke | `node scripts/route-smoke-check.mjs` | ✅ 24/24 PASS |
| Vite build | `node node_modules/vite/bin/vite.js build` | ✅ built in 6.77s |
| ESLint | `node node_modules/eslint/bin/eslint.js src/ --ext .ts,.tsx` | ✅ PASS (no output) |
| Backend targeted | `pytest -q test_routing_operation_extended_fields.py test_resource_requirement_api.py test_resource_requirement_service.py` | ✅ 17 passed in 1.73s |

---

## Slice Closure

MMD-FULLSTACK-05 is complete.

The regression script is deterministic, exits non-zero on failure, and is registered as
`npm run check:mmd:read` in `package.json`. It can be run at any point to verify the MMD
read integration baseline has not regressed.

### MMD Read Track — Running Status

| Slice | Status |
|---|---|
| MMD-AUDIT-00 | ✅ Complete |
| MMD-FULLSTACK-01: FE/BE contract alignment | ✅ Committed |
| MMD-FULLSTACK-02: ROD read integration | ✅ Committed |
| MMD-FULLSTACK-03: RR read integration | ✅ Committed |
| MMD-FULLSTACK-04: Context link ROD→RR | ✅ Committed |
| MMD-BE-01: Extended fields + Alembic 0003 | ✅ Committed (`26bfda5f`) |
| MMD-READ-BASELINE-01: Freeze handoff report | ✅ Committed (`e819368f`) |
| **MMD-FULLSTACK-05: Regression script** | **✅ Complete** |
