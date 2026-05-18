# Agent Report - FE-TS-BASELINE-01

**Date:** 2026-05-18
**Branch:** codex/station-execution-pilot-stack
**Task:** Restore frontend typecheck baseline — fix 4 pre-existing `tsc --noEmit` errors. Final hygiene correction: remove unused `type ScreenPhase` import from RouteStatusBanner.tsx.

---

## Routing

- Selected brain: FleziBCG Frontend
- Selected mode: Typecheck baseline cleanup (no UI redesign)
- Hard Mode MOM: kept from parent slice (EquipmentBinding and OperatorIdentification touch station/operator/equipment setup screens)
- Selected skills read: copilot-instructions.md (entry rule), latest-agent-report.md (context)
- Coverage class: frontend
- Hard Mode kept from parent slice: yes
- Reason: Two of the four error files (EquipmentBinding.tsx, OperatorIdentification.tsx) belong to governed station/session workflow screens. All changes are type-only with zero runtime behavior impact.

---

## Task / Slice

Fix all 4 baseline `tsc --noEmit` errors so future frontend slices can use typecheck as a clean gate.

Known errors fixed:

1. `src/app/components/RouteStatusBanner.tsx(39,72)` — `Property 'notes' does not exist` on `UNKNOWN_STATUS` fallback (inferred type missing `notes?`).
2. `src/app/pages/EquipmentBinding.tsx(40,19)` — `string` passed to `t()` where `I18nSemanticKey` required (`fallbackKey: string`).
3. `src/app/pages/OperatorIdentification.tsx(44,19)` — same pattern (`fallbackKey: string`).
4. `src/app/pages/ProductDetail.tsx(14,8)` — `BomItemFromAPI` imported from `@/app/api` but not re-exported from `index.ts`.

---

## Changed in This Slice

### 1. `frontend/src/app/components/RouteStatusBanner.tsx`

Root cause: `UNKNOWN_STATUS` was inferred as `{ routePattern: string; phase: ScreenPhase; dataSource: "NONE" }` — a type without `notes?`. When used as `statusEntry`, TypeScript computed a union that lacked `notes`.

Fix: Added `ScreenStatusEntry` type annotation to `UNKNOWN_STATUS`. Since `ScreenStatusEntry` has `notes?: string` (optional), the constant satisfies the interface and the union collapses to `ScreenStatusEntry`. Also imported `type ScreenStatusEntry` from `@/app/screenStatus`. Removed the now-redundant `as ScreenPhase` and `as const` casts. Runtime behavior: identical.

Hygiene correction (final pass): Removed the now-unused `type ScreenPhase` import. After the UNKNOWN_STATUS fix, `ScreenPhase` was no longer referenced anywhere in this file. Removing it eliminates a dead import with no runtime impact.

### 2. `frontend/src/app/pages/EquipmentBinding.tsx`

Root cause: `presentBindError(error: unknown, fallbackKey: string)` — `fallbackKey` typed as `string` but `t()` requires `I18nSemanticKey`.

Fix: Changed `fallbackKey: string` to `fallbackKey: I18nSemanticKey`. Added `type I18nSemanticKey` to the existing `@/app/i18n` import. All call sites pass literal i18n keys which satisfy `I18nSemanticKey`. No callers changed. Runtime behavior: identical.

### 3. `frontend/src/app/pages/OperatorIdentification.tsx`

Root cause: Same pattern — `presentIdentifyError(error: unknown, fallbackKey: string)`.

Fix: Changed `fallbackKey: string` to `fallbackKey: I18nSemanticKey`. Added `type I18nSemanticKey` to the existing `@/app/i18n` import. Runtime behavior: identical.

### 4. `frontend/src/app/api/index.ts`

Root cause: `BomItemFromAPI` is defined and exported in `productApi.ts` but was missing from the barrel re-export in `index.ts`. `ProductDetail.tsx` imports from `@/app/api` (the barrel), so the import failed type-checking.

Fix: Added `BomItemFromAPI` to the `export type { ... } from "./productApi"` block. Placed alphabetically between `BomCreateRequest` and `BomItemCreateRequest`. Runtime behavior: type-only export, no runtime impact.

---

## Existing/Parent Changes Observed

All prior slice files (StationSession.tsx, StationEntryPanel.tsx, station-session-setup-qa-screenshots.mjs, docs/agent-reports/latest-agent-report.md) were committed in `5c2d4786 fix(frontend): harden station session setup flow`. They no longer appear in the working tree.

`docs/audit/station-session-setup-qa/` is gitignored (added by `a48b1833`).

---

## Files Intended for Commit

- `frontend/src/app/api/index.ts`
- `frontend/src/app/components/RouteStatusBanner.tsx`
- `frontend/src/app/pages/EquipmentBinding.tsx`
- `frontend/src/app/pages/OperatorIdentification.tsx`
- `docs/agent-reports/latest-agent-report.md`

NOT for commit:
- `docs/audit/station-session-setup-qa/` (gitignored generated artifacts)

---

## Generated Artifact Paths

None generated in this slice.

---

## git status --short Summary

```
 M docs/agent-reports/latest-agent-report.md         -> IN SCOPE
 M frontend/src/app/api/index.ts                     -> IN SCOPE
 M frontend/src/app/components/RouteStatusBanner.tsx -> IN SCOPE
 M frontend/src/app/pages/EquipmentBinding.tsx        -> IN SCOPE
 M frontend/src/app/pages/OperatorIdentification.tsx  -> IN SCOPE
```

No out-of-scope dirty files. No unrelated staged files.

---

## Commands Run and Results

| Command | Exit | Result |
|---------|------|--------|
| `tsc --noEmit` | **0 (PASS)** | Clean — 0 errors (was: exit 2, 4 errors) |
| `npm run lint:i18n` | 0 | PASS: 2592 keys, en/ja synchronized |
| `npm run check:routes` | 0 | PASS 24 / FAIL 0, 79/80 covered |
| `git diff --check` | 0 | PASS: no whitespace issues |

---

## tsc Honest Report

**Exit code: 0 (PASS) — tsc --noEmit is now clean.**

All 4 previously known baseline errors eliminated:

| File | Prior error | Fix applied |
|------|-------------|-------------|
| `RouteStatusBanner.tsx(39,72)` | `notes` not on union type | `ScreenStatusEntry` annotation on `UNKNOWN_STATUS` |
| `EquipmentBinding.tsx(40,19)` | `string` not assignable to `I18nSemanticKey` | `fallbackKey: I18nSemanticKey` |
| `OperatorIdentification.tsx(44,19)` | same | same |
| `ProductDetail.tsx(14,8)` | `BomItemFromAPI` not exported from `@/app/api` | added to `index.ts` barrel |

Zero new errors introduced.

---

## Verification Notes

- All 4 fixes are type-only. No JavaScript runtime behavior changed.
- `BomItemFromAPI` was already fully defined and exported from `productApi.ts`; only the barrel was missing it.
- `ScreenStatusEntry.notes` is `?: string` (optional) so `UNKNOWN_STATUS` satisfies the interface without adding the field.
- `I18nSemanticKey` callers all pass string literals that are valid i18n keys — confirmed from call site inspection.
- Station Session behavior, readiness guards, and screenshot harness from prior slice are unchanged and committed.
- Hygiene correction verified: `type ScreenPhase` removed from RouteStatusBanner.tsx import; tsc still exits 0 confirming the import was genuinely unused.

---

## Limitations / Not Covered

- No E2E tests for the fixed screens (EquipmentBinding, OperatorIdentification, RouteStatusBanner, ProductDetail).
- This slice does not address any remaining eslint warnings (not requested).
- `strict: false` is still in `tsconfig.json` — stricter checking may reveal additional latent issues in a future slice.

---

## Known Environment Caveats

- Vite auto-increments port (5173→5174); harness handles this automatically.
- Terminal tool sometimes hangs on sync Start-Process -Wait; use async mode for long operations.

---

## Hard Mode MOM v3

**Kept from parent slice: yes.**

EquipmentBinding.tsx and OperatorIdentification.tsx are station/session/operator/equipment setup screens. Per Hard Mode MOM v3 policy, work touching these files carries v3 forward. Both fixes are purely type annotations with zero runtime behavior change. Coverage class is **frontend** (type-only, no backend mutation, no execution state change, no auth impact).

---

## Next Plan

1. Consider enabling `strict: true` in `tsconfig.json` incrementally to surface remaining latent type issues (separate slice).
2. FE-SE-SESSION-CLOSE-01: Verify CloseSessionPanel commandError display surfaces close failures correctly.
3. FE-SE-SESSION-E2E-01: Playwright E2E for queue navigation readiness gate (requires live backend).