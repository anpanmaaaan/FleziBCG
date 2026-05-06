# FE-HEADER-02 — Header Cleanup / TopBar Retirement + Header Metadata Contract

**Date:** 2026-05-06  
**Slice:** FE-HEADER-02  
**Status:** COMPLETE

---

## Routing
- **Selected brain:** Generic Brain
- **Selected mode:** Strict
- **Hard Mode MOM:** OFF — no execution, auth, IAM, projections, or backend touched
- **Reason:** Narrow frontend cleanup — verify and retire dead component, remove barrel reference.

---

## Source Inputs Read

| File | Purpose |
|---|---|
| `.github/copilot-instructions.md` | Entry rules |
| `.github/agent/AGENT.md` | Behavioral guidelines |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | Brain/mode selection |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | MOM v3 gate |
| `.github/copilot-instructions-design-md-addendum.md` | FE/UI addendum |
| `frontend/src/app/components/AppHeader.tsx` | New header component |
| `frontend/src/app/components/Layout.tsx` | App shell |
| `frontend/src/app/components/TopBar.tsx` | Retired component |
| `frontend/src/app/components/index.ts` | Barrel exports |
| `frontend/src/app/i18n/registry/en.ts` | EN i18n registry |
| `frontend/src/app/i18n/registry/ja.ts` | JA i18n registry |
| `frontend/src/app/i18n/namespaces.ts` | Namespace union type |
| `frontend/e2e/header-operational-context.spec.ts` | Focused header e2e spec |

---

## TopBar Usage Evidence

Full grep across `frontend/src/**/*.{ts,tsx}` for `TopBar`:

| Location | Match | Runtime consumer? |
|---|---|---|
| `components/index.ts` line 15 | `export { TopBar } from "./TopBar"` | No — barrel only |
| `components/TopBar.tsx` lines 9–484 | component definition | Not imported anywhere |
| `i18n/registry/en.ts` lines 980–988 | `topBar.*` keys | **YES — AppHeader.tsx reuses them** |
| `i18n/registry/ja.ts` lines 970–978 | `topBar.*` keys | **YES — AppHeader.tsx reuses them** |
| `i18n/namespaces.ts` line 29 | `topBar: "topBar"` | **YES — required for AppHeader.tsx key types** |
| `e2e/` | none | No tests reference TopBar component |

Grep for `import.*TopBar|from.*TopBar` across all frontend source returned exactly **1 match**: the barrel export line in `index.ts`. No component, page, or test imports the `TopBar` component.

**Verdict:** `TopBar.tsx` is confirmed dead code. Safe to delete.

**Note on `topBar.*` i18n keys:** `AppHeader.tsx` reuses `topBar.menu.*` keys (profile, settings, helpSupport, logoutAll, logout, signingOut) for its user dropdown menu. These keys must be retained in both registries and the `topBar` namespace must remain in `namespaces.ts`. Key retirement is out of scope for this slice (no broad i18n refactor).

---

## Cleanup Decision

**Action taken:** Delete `TopBar.tsx` + remove barrel re-export.

**Metadata extraction decision:** `AppHeader.tsx` derives domain label via a 2-line `useMemo` calling `getGroupIdForPath` and `NAV_GROUPS.find`. No extraction to a separate helper file is warranted — the logic is minimal, co-located, and readable. Creating a helper file for 2 lines would violate AGENT.md simplicity rules.

---

## Files Changed

| File | Change |
|---|---|
| `frontend/src/app/components/TopBar.tsx` | **DELETED** — confirmed zero runtime consumers |
| `frontend/src/app/components/index.ts` | Removed `export { TopBar } from "./TopBar"` (line 15) |

### Files NOT changed (confirmed)

- `frontend/src/app/routes.tsx` — unchanged
- `frontend/src/app/navigation/navigationGroups.ts` — unchanged
- `frontend/src/app/components/Layout.tsx` — unchanged
- `frontend/src/app/components/AppHeader.tsx` — unchanged
- `frontend/src/app/persona/personaLanding.ts` — unchanged
- `frontend/src/app/i18n/registry/en.ts` — unchanged
- `frontend/src/app/i18n/registry/ja.ts` — unchanged
- `frontend/src/app/i18n/namespaces.ts` — unchanged (note: `topBar` namespace retained; `appHeader` was added in FE-HEADER-01 fix)
- All backend files — untouched

---

## Route / Sidebar / Auth Non-Change Confirmation

- `check:routes` result: PASS (all route assertions pass, identical to pre-change run)
- No navigation group file modified
- No auth/persona/session file modified
- No route registry file modified

---

## Header Metadata Contract

`AppHeader.tsx` derives display metadata as follows:

```typescript
const domainLabel = useMemo(() => {
  const groupId = getGroupIdForPath(location.pathname);
  return NAV_GROUPS.find((group) => group.id === groupId)?.label
    ?? t("appHeader.domain.unknown");
}, [location.pathname, t]);

const statusPhase = getScreenStatusMatchByRoute(location.pathname)?.entry.phase ?? "UNKNOWN";
```

- Domain label: read from `NAV_GROUPS` via `getGroupIdForPath` — no hardcoding.
- Screen status phase: read from `screenStatus.ts` registry — no hardcoding.
- All user-facing strings: routed through `t(...)`.
- No backend/API dependency introduced.
- No local mock truth introduced.

---

## MOM Safety Check

| Concern | Status |
|---|---|
| Backend truth respected | YES — no backend calls added or faked |
| Permission truth respected | YES — no authorization logic touched |
| Execution state truth respected | YES — no execution state consumed or derived |
| Quality truth respected | YES — no quality pass/fail logic touched |
| Integration/ERP truth respected | YES — no ERP/posting logic touched |
| AI/Digital Twin truth respected | YES — no AI/DT logic touched |

---

## i18n Check

- Pre-change: `en.ts` and `ja.ts` synchronized at **1857 keys** ✓
- Post-change: `en.ts` and `ja.ts` synchronized at **1857 keys** ✓
- `topBar.*` keys (8 keys): retained — actively used by `AppHeader.tsx`
- `appHeader.*` keys (10 keys): retained — used by `AppHeader.tsx`
- No new keys added or removed in this slice

---

## RouteStatusBanner Preservation Check

`RouteStatusBanner` is rendered in `Layout.tsx` below the header outlet, independent of `AppHeader`. The `TopBar` deletion does not touch `Layout.tsx` — `RouteStatusBanner` placement is unchanged and verified by build passing.

---

## Responsive / Accessibility Check

No changes to `AppHeader.tsx` in this slice. Mobile drawer behavior, `aria-expanded`, `aria-controls`, and focus return logic are all unmodified. Playwright mobile drawer test (test 1) confirms focus return behavior still works.

---

## Tests / Verification

### Pre-change baseline

| Command | Result |
|---|---|
| `npm run lint` | PASS (0 errors) |
| `npm run build` | PASS (3409 modules, 9.31s, CSS: 142.17 kB) |
| `npm run check:routes` | PASS |
| `npm run lint:i18n:registry` | PASS (1857 keys) |

### Post-change

| Command | Result |
|---|---|
| `npm run lint` | PASS (0 errors) |
| `npm run build` | PASS (3409 modules, 9.41s, CSS: 141.82 kB — TopBar styles removed) |
| `npm run check:routes` | PASS (identical results) |
| `npm run lint:i18n:registry` | PASS (1857 keys — no change) |
| `playwright test e2e/header-operational-context.spec.ts --project=chromium` | **2/2 PASS** |

CSS bundle shrinkage (142.17 kB → 141.82 kB gzip: 22.75 kB → 22.70 kB) confirms TopBar Tailwind classes removed from output.

---

## Known Limitations

1. **`topBar.*` key namespace retained:** `AppHeader.tsx` reuses the old `topBar.menu.*` keys for its user dropdown. A future slice could migrate these to `appHeader.menu.*` and clean up the `topBar` namespace, but this requires careful key migration and registry sync — out of scope for FE-HEADER-02.

2. **`topBar` namespace entry remains in `namespaces.ts`:** Required because `AppHeader.tsx` calls `t("topBar.menu.*")`. Remove only after key migration.

3. **No `npm run lint:i18n` (hardcode check) run:** Script existence was not verified in this slice. No new user-visible strings were added in FE-HEADER-02, so the risk of new hardcode violations is zero.

---

## Next Recommended Slice

**FE-HEADER-03 — TopBar i18n Key Migration**

Scope: Migrate `topBar.menu.*` keys used by `AppHeader.tsx` to `appHeader.menu.*`, remove the 8 `topBar.*` keys from both registries, remove `topBar` namespace from `namespaces.ts` (while preserving `topBar` in `I18N_NAMESPACES` only if other consumers remain — verify first).

Pre-condition: Verify no other component uses any `topBar.*` key after this migration.

---

## Commit Guidance

```
feat(fe): FE-HEADER-02 — retire TopBar.tsx, remove barrel re-export

- Delete frontend/src/app/components/TopBar.tsx (confirmed zero runtime consumers)
- Remove export { TopBar } from components/index.ts barrel
- topBar.* i18n keys retained: reused by AppHeader.tsx menu items

Verification: lint PASS, build PASS (CSS -0.35 kB), routes PASS,
i18n 1857 keys PASS, Playwright 2/2 PASS
```
