# Sidebar Quick Search — Audit Report

**Task:** FE-NAV-01B — Sidebar Quick Search / Screen Switcher
**Date:** 2025-07-27
**Status:** PASS — all gates green

---

## Objective

Add a lightweight quick-search input inside the expanded sidebar that filters persona-visible navigation items by label, route path, or group label. No new dependencies. No auth/route/backend changes. No outside-persona route exposure.

---

## Files Changed

| File | Change |
|------|--------|
| `frontend/src/app/navigation/navigationGroups.ts` | Added `filterNavigationGroups(sections, query)` export |
| `frontend/src/app/i18n/registry/en.ts` | Added 4 `navigation.search.*` keys (EN) |
| `frontend/src/app/i18n/registry/ja.ts` | Added 4 `navigation.search.*` keys (JA) |
| `frontend/src/app/components/SidebarSearch.tsx` | Created — controlled search input component |
| `frontend/src/app/components/Layout.tsx` | Imported Search icon, filterNavigationGroups, SidebarSearch; added navSearch state; clears on route change; renders SidebarSearch in expanded desktop + mobile drawer; search mode expands all matched groups; empty state shown when no match |

---

## Behaviour Spec

- Search input is visible only in **expanded** desktop sidebar and **mobile drawer**. Hidden in icon-only compact mode.
- Filtering is **persona-scoped**: operates on items already returned by `getMenuItemsForPersona()`. Does not expose routes outside the persona.
- Filtering matches against: item `label`, item `to` (route path), or group `label`.
- When a group label matches the query, **all items in that group** are shown.
- When searching, **all matched groups are expanded** (toggle state is bypassed in search mode).
- Empty state (magnifier icon + "No screens match" text) shown when query yields zero sections.
- Search is **cleared automatically** on navigation (`useEffect` on `location.pathname`).
- `Escape` key clears the search input (handled in `SidebarSearch.tsx`).
- Search input is accessible: `<label htmlFor>` with `.sr-only`, `aria-label` on clear button, focus ring, `role="search"` via native `type="search"`.

---

## i18n Keys Added

### en.ts
```
"navigation.search.placeholder": "Search screens…"
"navigation.search.ariaLabel": "Search navigation screens"
"navigation.search.noResults": "No screens match"
"navigation.search.clear": "Clear search"
```

### ja.ts
```
"navigation.search.placeholder": "画面を検索…"
"navigation.search.ariaLabel": "ナビゲーション画面を検索"
"navigation.search.noResults": "該当する画面はありません"
"navigation.search.clear": "検索をクリア"
```

---

## Verification Results

| Check | Result |
|-------|--------|
| `npm run build` | ✅ PASS — 6.98s, 0 errors (chunk size warning is pre-existing) |
| `npm run lint` | ✅ PASS — 0 errors, 0 warnings |
| `npm run check:routes` | ✅ PASS — 24/24 routes |
| `npm run lint:i18n:registry` | ✅ PASS — en.ts and ja.ts synchronized (1321 keys) |

---

## Safety Notes

- Backend is not affected. This is purely a frontend presentational feature.
- Authorization is not affected. `filterNavigationGroups` only receives items already permitted by persona.
- No new npm dependencies introduced.
- `filterNavigationGroups` is a pure function (no side effects). Existing navigation group structure (`NAV_GROUPS`, `groupMenuItems`) is unchanged.
- Route definitions in `routes.tsx` are unchanged.
- `personaLanding.ts` is unchanged.
