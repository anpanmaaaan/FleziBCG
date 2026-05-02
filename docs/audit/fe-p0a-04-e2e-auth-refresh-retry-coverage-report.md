# FE-P0A-04 — E2E Auth Refresh Retry Coverage

**Date:** 2025-07-30
**Task ID:** FE-P0A-04
**Depends on:** FE-P0A-02, FE-P0A-03
**Status:** PARTIAL — Stop condition triggered. Extended static coverage applied. Runtime E2E blocked pending dependency approval.

---

## Summary

FE-P0A-04 aimed to close the runtime E2E gap for the auth refresh-and-retry behavior implemented by FE-P0A-02 and FE-P0A-03.

A stop condition was triggered: `@playwright/test` (the Playwright test runner) is not installed. Only the `playwright` browser automation library is present. Adding `@playwright/test` would be a new test dependency, which the task prohibits.

**Actions taken within scope:**

- Hard Mode MOM v3 gate produced.
- 6 additional static invariant checks added to `auth-retry-smoke.mjs` (total: 20 checks, all PASS).
- Stop report created at `docs/audit/fe-p0a-04-e2e-auth-refresh-retry-coverage-stop-report.md` with 3 options and a recommendation.
- All existing FE-P0A-02 and FE-P0A-03 smoke checks still pass (14 + 20 = 34 total, 0 failures).

**Runtime E2E tests NOT added** — would require `@playwright/test` which is a new dependency.

---

## Routing

| Field | Value |
|---|---|
| Selected brain | Generic Brain (frontend auth QA) |
| Selected mode | QA Mode |
| Hard Mode MOM | v3 |
| Reason | Auth runtime behavior, refresh-token handling, session continuity, retry after token rotation, frontend/backend auth truth boundary |

---

## Hard Mode MOM v3 Gate

### Verdict

**`STOP_AND_REPORT`**

`@playwright/test` is not installed. The `playwright` devDependency provides browser automation APIs only — no test runner, no `test()`, no `expect()`, no `page.route()` fixtures, no `playwright test` CLI. Adding `@playwright/test` is a new test dependency, prohibited by task. No other runtime test harness exists.

### Stop Condition Classification

| Condition | Status |
|---|---|
| Playwright unavailable and no runtime test harness exists | **TRIGGERED** — `@playwright/test` absent |
| Implementing E2E requires new framework dependency | **TRIGGERED** — `@playwright/test` would be required |
| All mandatory files present | YES — not a stop cause |
| FE-P0A-02 / FE-P0A-03 source changes present | YES — not a stop cause |
| All other stop conditions | NOT TRIGGERED |

---

## Files Inspected

| File | Finding |
|---|---|
| `frontend/package.json` | `playwright: ^1.52.0` in devDependencies; `@playwright/test` absent; no `test:e2e` script |
| `frontend/node_modules/playwright/index.d.ts` | `export * from 'playwright-core'` — confirms browser automation only |
| `frontend/node_modules/@playwright/test/` | Does not exist |
| `frontend/playwright.config.*` | Does not exist |
| `frontend/e2e/` | Does not exist |
| `frontend/src/app/api/httpClient.ts` | FE-P0A-03 implementation confirmed: retry, exclusions, refreshInFlight |
| `frontend/src/app/auth/AuthContext.tsx` | FE-P0A-03 integration confirmed: setRefreshHandler + setUnauthorizedHandler wired |
| `frontend/scripts/auth-retry-smoke.mjs` | 14 existing checks — extended to 20 |
| `frontend/scripts/auth-contract-smoke.mjs` | 14 checks — no change needed |

---

## Files Changed

| File | Change |
|---|---|
| `frontend/scripts/auth-retry-smoke.mjs` | Added 6 extended static invariant checks (checks 15–20) |
| `docs/audit/fe-p0a-04-e2e-auth-refresh-retry-coverage-stop-report.md` | Stop report with source evidence, 3 options, recommendation |

---

## E2E Tests Added / Updated

**Runtime E2E tests: NOT ADDED** — `@playwright/test` required; prohibited.

### Extended Static Checks Added to `auth-retry-smoke.mjs`

These close the static portion of the runtime gap:

| Check | What it verifies |
|---|---|
| `test_refresh_in_flight_is_reset_after_completion` | `refreshInFlight = null` in `.finally()` — no stale promise leak |
| `test_refresh_result_is_awaited_not_fire_and_forget` | `await refreshInFlight` in 401 branch — result used before retry decision |
| `test_retry_guard_checks_retried_flag_and_excluded_path` | Both `!options.retried` AND `isExcludedFromRefresh` present in guard |
| `test_retry_path_does_not_call_fetch_directly` | Exactly 1 `fetch()` call in httpClient — retry uses `request()`, not `fetch()` |
| `test_excluded_path_check_normalizes_path` | `isExcludedFromRefresh` calls `normalizePath` — relative paths matched correctly |
| `test_logout_all_endpoint_is_excluded_from_refresh_retry` | `/v1/auth/logout-all` in `REFRESH_EXCLUDED_PATHS` |

**All 20 checks pass (0 failures).**

---

## Verification Commands Run

```
node scripts/auth-retry-smoke.mjs       → 20 passed, 0 failed
node scripts/auth-contract-smoke.mjs   → 14 passed, 0 failed
node scripts/route-smoke-check.mjs     → all PASS
node .\node_modules\eslint\bin\eslint.js scripts/auth-retry-smoke.mjs --max-warnings 0 → Exit: 0
```

No runtime `test:e2e:auth` command — not added (stop condition).

---

## Results

| Check | Result |
|---|---|
| Auth retry smoke — extended (20 checks) | **20/20 PASS** |
| Auth contract smoke — regression (14 checks) | **14/14 PASS** |
| Route smoke | **all PASS** |
| ESLint on smoke script | **Exit: 0** |
| Runtime E2E | **BLOCKED — @playwright/test not installed** |

---

## Existing Gaps / Known Technical Debts

| Gap | Severity | Resolution Path |
|---|---|---|
| **No runtime E2E test** — Auth refresh retry behavior is only verified statically. Actual browser execution, HTTP request/response flow, and localStorage persistence are not runtime-verified. | High | FE-P0A-04 can be resumed if `@playwright/test` is added (see stop report Option A) |
| **`playwright` devDependency is unused** — `playwright` is listed in devDependencies but cannot be used for testing without `@playwright/test`. The intent to test with Playwright is signaled but not completed. | Medium | Add `@playwright/test` matching the same version |
| **No Playwright browser binaries installed** — Even if `@playwright/test` is added, browsers must be installed via `npx playwright install` before tests can run. | Low | One-time setup step when Option A is approved |
| **No `playwright.config.ts`** — No test runner configuration exists; would need to be created. | Low | Single file, minimal config |
| **Static checks cannot detect runtime token rotation correctness** — If `refreshTokens()` had a bug that updated state but returned the wrong token in the HTTP context, static checks would not catch it. | Medium | Runtime E2E only |

---

## Scope Compliance

- Did NOT modify backend code or tests.
- Did NOT change frontend auth behavior.
- Did NOT add new dependency.
- Did NOT add production mock/fake auth logic.
- Did NOT touch MMD/Execution/Quality/Material/Integration screens.
- Did NOT derive permission truth in frontend.
- Extended smoke scripts only — all changes are in `scripts/` directory.

---

## Risks

| Risk | Assessment |
|---|---|
| Runtime auth retry bug not detected | **Present** — static checks validate structure but not runtime HTTP flow |
| `playwright` devDependency creates false confidence | **Present** — signals testing intent that cannot be fulfilled without `@playwright/test` |
| Future regression in excluded path list | **Mitigated** — static check `test_logout_all_endpoint_is_excluded_from_refresh_retry` added |

---

## Stop Conditions Hit

| Condition | Triggered |
|---|---|
| `@playwright/test` not installed — Playwright test runner unavailable | **YES** |
| Adding `@playwright/test` would be a new test dependency | **YES** |

Stop report: [docs/audit/fe-p0a-04-e2e-auth-refresh-retry-coverage-stop-report.md](../audit/fe-p0a-04-e2e-auth-refresh-retry-coverage-stop-report.md)

---

## Recommended Next Slice

**Approve `@playwright/test` addition and resume FE-P0A-04.**

If approved:

1. `npm install --save-dev @playwright/test@^1.52.0`
2. Create `frontend/playwright.config.ts` (minimal: baseURL, testDir, webServer using Vite)
3. Create `frontend/e2e/auth-refresh-retry.spec.ts` with:
   - `test_expired_access_token_refreshes_and_retries_original_request`
   - `test_refresh_failure_clears_auth_state`
   - `test_refresh_endpoint_401_does_not_trigger_recursive_refresh`
   - `test_parallel_401_requests_share_single_refresh` (optional)
4. Add `"test:e2e:auth": "playwright test e2e/auth-refresh-retry.spec.ts"` to package.json
5. `npx playwright install chromium`
6. Run `npm run test:e2e:auth` and verify all pass

This would complete the full FE-P0A-04 definition of done.
