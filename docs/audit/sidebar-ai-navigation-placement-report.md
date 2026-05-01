# AI Navigation Placement Decision Report

## History
| Date | Version | Change |
|---|---:|---|
| 2026-05-01 | v1.0 | FE-NAV-03: Reviewed and finalized AI screen placement under Reporting & Analytics. Removed separate `ai-intelligence` navigation group. |

---

## Routing

- **Selected brain:** FleziBCG AI Brain Enterprise v4
- **Selected mode:** FE Navigation IA — Safe Placement
- **Hard Mode MOM:** Read and boundary-checked; no Hard Mode contract intervention required.
- **Reason:** Navigation grouping is a presentation-layer, display-only change. No backend, execution, auth, persona semantics, routes, or operational logic were changed.

---

## 1. Scope

FE-NAV-03 reviews and finalizes the sidebar/navigation placement of AI screens added in FE-COVERAGE-01F.

Decision applied: AI screens are moved from the separate `AI Intelligence` group into `Reporting & Analytics`.

`Digital Twin` and `Compliance` remain as separate groups — no change.

---

## 2. Source Files Inspected

| File | Status |
|---|---|
| `frontend/src/app/navigation/navigationGroups.ts` | Read + modified |
| `frontend/src/app/components/Layout.tsx` | Read — verified `reporting-analytics` icon registered |
| `frontend/src/app/persona/personaLanding.ts` | Read — no group ID references; safe |
| `frontend/src/app/routes.tsx` | Read — no group ID references; routes unchanged |
| `frontend/src/app/screenStatus.ts` | Read — no group ID references; screen status unchanged |
| `docs/audit/frontend-coverage-ai-twin-compliance-report.md` | Read — FE-COVERAGE-01F baseline |
| `docs/audit/frontend-screen-coverage-matrix.md` | Read — current coverage state |

---

## 3. Precondition Check

| Check | Result | Notes |
|---|---|---|
| `git status --short` — no conflict markers | PASS | Unrelated: station-execution screenshots (8), tsconfig.json |
| Navigation group file readable | PASS | |
| Route file readable | PASS | |
| `ai-intelligence` group ID referenced outside navigationGroups.ts | PASS — NO REFERENCES | Only defined in navigationGroups.ts; safe to remove |
| `reporting-analytics` icon registered in Layout.tsx | PASS | `BarChart3` icon registered at line 193 |
| FE-COVERAGE-01F report present | PASS | `docs/audit/frontend-coverage-ai-twin-compliance-report.md` |
| FE-NAV-01 / FE-NAV-01B reports present | PASS | `docs/audit/sidebar-domain-navigation-ia-report.md`, `docs/audit/sidebar-quick-search-report.md` |
| Baseline build | PASS | Built in ~7.6s |
| Baseline lint | PASS | 0 errors |
| Baseline check:routes | PASS | 78 routes, 0 fail |
| Baseline lint:i18n:registry | PASS | 1692 keys, en/ja parity |

---

## 4. Product Decision

### Decision Applied

**AI screens are placed under Reporting & Analytics.**

No separate `AI Intelligence` group remains.

### Rationale

| Principle | Implication |
|---|---|
| Deterministic reporting first | AI must not appear as an independent operational module; it supplements reporting |
| AI is advisory only | AI insights sit naturally adjacent to OEE / downtime / shift reports |
| MVP information architecture | Fewer top-level groups reduces cognitive load; AI advisory ≠ operational control authority |
| FleziBCG product principle | "Deterministic reporting first. AI is advisory only. AI must not appear as an operational control authority." |

### Alternative Considered (Not Applied)

`AI Intelligence` as a separate top-level group. Rejected for MVP because:
- It implies AI has equal operational standing to Production, Quality, Integration.
- In current state (all shells, no backend connection), it would be a misleading top-level domain.
- Reporting & Analytics is the natural home for advisory intelligence in MOM/MES products at this maturity level.

---

## 5. Navigation IA Before

```
Reporting & Analytics
  /performance/oee-deep-dive
  /reports/downtime
  /reports/production-performance
  /reports/quality-performance
  /reports/shift
  /reports/material-wip
  /reports/integration-status

AI & Intelligence   ← separate group
  /ai/insights
  /ai/shift-summary
  /ai/anomaly-detection
  /ai/bottleneck-explanation
  /ai/natural-language-insight

Digital Twin
  /digital-twin
  /digital-twin/state-graph
  /digital-twin/what-if

Compliance
  /compliance/record-package
  /compliance/e-signature
  /compliance/electronic-batch-record
```

---

## 6. Navigation IA After

```
Reporting & Analytics
  /performance/oee-deep-dive
  /reports/downtime
  /reports/production-performance
  /reports/quality-performance
  /reports/shift
  /reports/material-wip
  /reports/integration-status
  /ai/insights                      ← AI screens merged here
  /ai/shift-summary
  /ai/anomaly-detection
  /ai/bottleneck-explanation
  /ai/natural-language-insight

Digital Twin                        ← unchanged
  /digital-twin
  /digital-twin/state-graph
  /digital-twin/what-if

Compliance                          ← unchanged
  /compliance/record-package
  /compliance/e-signature
  /compliance/electronic-batch-record
```

No `AI & Intelligence` group remains.

---

## 7. Navigation Placement Summary

| Area | Before | After | Decision |
|---|---|---|---|
| AI screens | `AI & Intelligence` group | `Reporting & Analytics` | Merged — advisory intelligence belongs with reporting |
| Digital Twin screens | `Digital Twin` group | `Digital Twin` group | Kept separate — distinct architectural domain |
| Compliance screens | `Compliance` group | `Compliance` group | Kept separate — distinct regulatory domain |

---

## 8. AI Advisory Boundary Review

| Boundary | Status |
|---|---|
| AI screens still labeled Advisory Only / Demo Advisory | ✓ Unchanged |
| AI screen content not modified | ✓ |
| AI routes not changed | ✓ |
| AI page status badges not changed (SHELL / MOCK_FIXTURE) | ✓ |
| No AI backend connection introduced | ✓ |
| No AI recommendation truth introduced | ✓ |
| Dangerous AI actions remain disabled | ✓ |
| Moving to Reporting & Analytics does NOT grant AI operational authority | ✓ — group is display-only |

Navigation group membership is a **presentation-layer attribute only**. Moving `/ai/*` routes into `reporting-analytics` group does not grant those screens any new authority, data access, or operational meaning.

---

## 9. Digital Twin / Compliance Placement Review

| Group | Decision | Rationale |
|---|---|---|
| Digital Twin | Kept separate | Digital Twin is an architectural simulation domain — distinct from analytics reporting |
| Compliance | Kept separate | Compliance/e-sign/eBR is a regulatory domain — distinct from operational reporting |

Both groups have their legal / boundary disclaimers unchanged.

---

## 10. Persona / Authorization Safety Review

| Check | Result | Notes |
|---|---|---|
| Route paths unchanged | PASS | No route added, removed, or renamed |
| Persona route guards unchanged | PASS | `isRouteAllowedForPersona` in personaLanding.ts not touched |
| `ai-intelligence` group ID referenced in personaLanding.ts | PASS — NO REFERENCES | Group IDs are not used in persona logic |
| Sidebar grouping is display-only | PASS | `getGroupIdForPath()` used only for UI rendering |
| Backend authorization remains source of truth | PASS | navigationGroups.ts is a presentation utility only |
| Auth behavior unchanged | PASS | |
| Impersonation behavior unchanged | PASS | |
| `allowed_actions` logic unchanged | PASS | |

---

## 11. Search / Route Smoke Review

| Check | Result |
|---|---|
| `check:routes` passes after change | PASS — 78 routes, 0 fail |
| Route count unchanged | PASS — 78 before, 78 after |
| No route path changes | PASS |
| `getGroupIdForPath("/ai/insights")` → `reporting-analytics` | ✓ (new behavior; was `ai-intelligence`) |
| Sidebar search: `/ai` prefix routes now open `Reporting & Analytics` | ✓ |
| AI routes remain searchable via sidebar quick search | ✓ (search matches on route path prefix, not group) |

---

## 12. i18n Review

| Check | Result | Notes |
|---|---|---|
| navigationGroups.ts uses hardcoded labels (no i18n keys) | PASS | No i18n changes required |
| "AI & Intelligence" was never an i18n key | PASS | Hardcoded in group `label` field only |
| `lint:i18n:registry` passes after change | PASS — 1692 keys, en/ja parity | Unchanged |
| Unused i18n keys from AI group | NONE | No i18n keys existed for the group label |

No i18n churn. No keys added or removed.

---

## 13. Files Changed

| File | Change |
|---|---|
| `frontend/src/app/navigation/navigationGroups.ts` | Added `/ai` to `reporting-analytics.routePrefixes`; removed `ai-intelligence` group entirely |

**Total files modified: 1**

---

## 14. Verification Results

| Command | Before | After |
|---|---|---|
| `npm run build` | PASS | PASS |
| `npm run lint` | PASS | PASS |
| `npm run check:routes` | PASS — 78 routes, 0 fail | PASS — 78 routes, 0 fail |
| `npm run lint:i18n:registry` | PASS — 1692 keys | PASS — 1692 keys |

---

## 15. Deferred Issues

None. The move was clean and required no deferred items.

---

## 16. Final Verdict

**FE-NAV-03: COMPLETE — ALL ACCEPTANCE CRITERIA MET**

- ✓ AI screens placed under Reporting & Analytics
- ✓ No separate `AI Intelligence` group remains
- ✓ Digital Twin remains a separate group
- ✓ Compliance remains a separate group
- ✓ No route added, removed, or renamed
- ✓ No route path changed
- ✓ No auth / persona / impersonation behavior changed
- ✓ No AI behavior changed (screens still SHELL / DEMO / Advisory Only)
- ✓ No Digital Twin behavior changed
- ✓ No Compliance/e-sign/eBR behavior changed
- ✓ Sidebar search still works for AI screens
- ✓ Active AI route opens Reporting & Analytics group (not a phantom group)
- ✓ Route smoke passes — 78 routes, 0 fail
- ✓ Build, lint, route check, i18n registry all PASS
- ✓ 1 file changed (navigationGroups.ts only)
- ✓ Documentation report created

---

## 17. Recommended Next Slice

| ID | Description | Priority |
|---|---|---|
| FE-NAV-04 | Review Planning & Scheduling group — `/scheduling` and future planning screens (APSScheduling, DispatchQueue) | Medium |
| FE-NAV-05 | Review whether Integration group should merge with Reporting & Analytics or stay separate as backends come online | Low |
| FE-QA-ROUTES-02 | Add persona-access smoke checks for `/ai/*`, `/digital-twin/*`, `/compliance/*` routes | Medium |
| FE-COVERAGE-02 | Connect AI Insights Dashboard to real backend AI advisory API when available | Future |
