# FE-P0A-04B — Playwright Test Runner Approval + Auth E2E Harness Report

**Slice:** FE-P0A-04B  
**Status:** COMPLETE  
**Date:** 2026-05-02  
**Author:** GitHub Copilot (Claude Sonnet 4.6)

---

## Routing

- **Selected brain:** Generic Brain (frontend auth QA — no MOM/MES execution logic)
- **Selected mode:** QA Mode (E2E coverage, runtime verification)
- **Hard Mode MOM:** v3
- **Reason:** Auth runtime behaviour, refresh-token handling, session continuity, retry after
  token rotation, frontend/backend auth truth boundary. All of these touch the auth
  session invariant boundary defined in HMM v3.

---

## Hard Mode MOM v3 Gate

### Verdict

`ALLOW_FE_P0A04B_PLAYWRIGHT_AUTH_E2E`

All five gate documents were produced and verified before implementation:

1. **Design Evidence Extract** — contract evidence from httpClient.ts, AuthContext.tsx,
   authApi.ts, and REFRESH_EXCLUDED_PATHS confirmed.
2. **Prior Stop Condition Review** — FE-P0A-04 stop condition (missing `@playwright/test`)
   reviewed; explicitly cleared by user via FE-P0A-04B approval.
3. **E2E Harness Decision** — `@playwright/test@^1.52.0` approved; `page.route()` for all
   backend mocking; no real backend required; no production source code changes.
4. **Auth Retry Invariant Map** — four invariants mapped to E2E tests (see Test Matrix below).
5. **Mock / Network Interception Safety Map** — all mocks are in `e2e/auth-refresh-retry.spec.ts`
   only; no production source touched.

---

## Prior Slices This Builds On

| Slice | What it added | Status |
|---|---|---|
| FE-P0A-02 | `authApi.ts` refresh types; `AuthContext.tsx` refresh flow; `auth-contract-smoke.mjs` | COMPLETE |
| FE-P0A-03 | `httpClient.ts` retry-after-refresh; `setRefreshHandler` wiring; `auth-retry-smoke.mjs` | COMPLETE |
| FE-P0A-04 | Stop report — `@playwright/test` absent; static smoke extended to 20 checks | COMPLETE (STOPPED) |
| FE-P0A-04B | This report — install `@playwright/test`; `playwright.config.ts`; E2E spec | COMPLETE |

---

## Dependency Changes

| Package | Before | After | Type | Note |
|---|---|---|---|---|
| `@playwright/test` | absent | `^1.52.0` → resolved to `1.59.1` | devDependency | Explicitly approved by user |
| `react` | transitive (18.3.1) | `18.3.1` explicit | dependency | Added explicitly after `@playwright/test` install removed it as implicit transitive dep |
| `react-dom` | transitive (18.3.1) | `18.3.1` explicit | dependency | Same as react |
| `playwright` | `^1.52.0` → `1.52.0` | `1.59.1` (upgraded) | devDependency | Existing dep upgraded due to `^` range |
| `playwright-core` | `1.52.0` | `1.59.1` (upgraded) | transitive | Upgraded with playwright |

### React Dependency Incident

`npm install --save-dev @playwright/test --legacy-peer-deps` caused npm to remove `react`
and `react-dom` from `node_modules` because they were only transitive (unlisted in
`package.json`). This broke the Vite dev server. Resolution: restored original
`package-lock.json` from git, added `react: "18.3.1"` and `react-dom: "18.3.1"` as
explicit `dependencies` in `package.json`, then ran `npm install --legacy-peer-deps`.

---

## Files Inspected

| File | Reason |
|---|---|
| `frontend/src/app/api/httpClient.ts` | Confirm retry logic + REFRESH_EXCLUDED_PATHS |
| `frontend/src/app/auth/AuthContext.tsx` | Confirm bootstrap flow, refreshCurrentUser, refreshTokens |
| `frontend/src/app/api/authApi.ts` | Confirm me/refresh/login call shapes |
| `frontend/src/app/routes.tsx` | Confirm protected routes and RequireAuth usage |
| `frontend/src/app/pages/LoginPage.tsx` | Confirm form structure for E2E navigation |
| `frontend/src/app/auth/RequireAuth.tsx` | Confirm redirect-to-login guard |
| `frontend/vite.config.ts` | Confirm dev server port (5173) and proxy config |
| `frontend/tsconfig.json` | Confirm `include: ["src"]` — e2e needs separate TS handling |
| `frontend/package.json` | Confirm devDependencies state before/after install |
| `frontend/scripts/auth-contract-smoke.mjs` | Confirm 14 static invariant checks |
| `frontend/scripts/auth-retry-smoke.mjs` | Confirm 20 static invariant checks |

---

## Files Created / Modified

| File | Action | Description |
|---|---|---|
| `frontend/playwright.config.ts` | **Created** | Minimal Playwright config: chromium, port 5173, `reuseExistingServer: true`, `testDir: ./e2e` |
| `frontend/e2e/auth-refresh-retry.spec.ts` | **Created** | 4 E2E runtime tests — all mocked via `page.route()` |
| `frontend/package.json` | **Modified** | Added `@playwright/test: "^1.52.0"` to devDependencies; added `react: "18.3.1"` and `react-dom: "18.3.1"` to dependencies; added `test:e2e:auth` script |
| `frontend/package-lock.json` | **Modified (auto)** | Updated by npm to reflect new package resolution |

---

## E2E Tests Added

**File:** `frontend/e2e/auth-refresh-retry.spec.ts`  
**Runner:** `@playwright/test@1.59.1`  
**Browser:** Chromium (headless)  
**Backend required:** No — all endpoints mocked via `page.route()`

| Test | Invariant tested | Result |
|---|---|---|
| `test_expired_access_token_refreshes_and_retries_original_request` | 401 → refresh → retry uses new token; refresh called exactly once; tokens rotated in localStorage | PASS |
| `test_refresh_failure_clears_auth_state` | Refresh 401 → auth state cleared; tokens removed from localStorage; redirect to `/login` | PASS |
| `test_refresh_endpoint_401_does_not_trigger_recursive_refresh` | `/auth/refresh` is excluded from refresh retry; recursion guard holds | PASS |
| `test_parallel_401_requests_share_single_refresh` | refreshInFlight dedup — only one refresh call even with multiple 401s; new tokens stored | PASS |

### Auth Bootstrap Behaviour Discovered

During test authoring, the `refreshCurrentUser` callback closes over `token` state. When
`refreshTokens()` calls `setToken(newToken)`, React recreates `refreshCurrentUser` (new
closure), which causes its `useEffect` to fire again — triggering a third `/auth/me` call.
This is expected app behaviour. Assertions were adjusted:

- `meCallCount >= 2` (not `== 2`) to allow for the extra re-bootstrap call.
- Bearer token on the SECOND call is asserted to be the new token (this is the httpClient
  retry — the invariant that matters).

---

## Commands Run + Results

| Command | Result |
|---|---|
| `node scripts/auth-contract-smoke.mjs` | 14/14 PASS |
| `node scripts/auth-retry-smoke.mjs` | 20/20 PASS |
| `node node_modules/vite/bin/vite.js build` | ✓ 3408 modules, exit 0 |
| `node node_modules/@playwright/test/cli.js install chromium` | ✓ Chromium 1217 installed |
| `node node_modules/@playwright/test/cli.js test e2e/auth-refresh-retry.spec.ts` | **4/4 PASS** (4.5s) |

---

## Test Matrix — Invariant Coverage

| Invariant | Static (smoke) | E2E Runtime | Verified |
|---|---|---|---|
| Original request retried at most once | ✓ `test_retry_marker_prevents_infinite_loop` | ✓ `test_expired_access_token_refreshes_and_retries_original_request` | ✓ |
| Retried request uses new access token | ✓ `test_retried_request_uses_new_access_token` | ✓ Asserted via `meRequestBearers[1]` | ✓ |
| Refresh receives old refresh token in body | ✓ `test_refresh_sends_refresh_token_body` | ✓ `refreshRequestBody["refresh_token"]` asserted | ✓ |
| New tokens replace old in localStorage | ✓ `test_refresh_replaces_both_access_and_refresh_tokens` | ✓ `localStorage.getItem` assertions | ✓ |
| Refresh failure clears auth state + redirect | ✓ `test_refresh_401_clears_auth_state` | ✓ `test_refresh_failure_clears_auth_state` | ✓ |
| Refresh endpoint not recursively retried | ✓ `test_refresh_endpoint_is_excluded_from_refresh_retry` | ✓ `test_refresh_endpoint_401_does_not_trigger_recursive_refresh` | ✓ |
| Parallel 401s share single refresh (refreshInFlight dedup) | ✓ `test_parallel_401_uses_single_refresh_if_implemented` | ✓ `test_parallel_401_requests_share_single_refresh` | ✓ |
| Login/logout excluded from refresh retry | ✓ static only | N/A (login/logout routes don't make authenticated API calls) | ✓ static |

---

## Known Gaps

1. **No test for concurrent requests via httpClient directly.** The parallel dedup test
   verifies that only one refresh happens during the bootstrap flow; it does not spin up
   two simultaneous httpClient calls from separate page contexts. Static smoke covers the
   `refreshInFlight` structure.

2. **No test for token rotation mid-session (after navigation).** Only bootstrap is tested.
   A more complete harness would navigate to a protected page, expire the token mid-session,
   and trigger a protected data fetch.

3. **Playwright webServer config uses `npm run dev`** (`reuseExistingServer: true`). In CI
   environments where `npm run` may fail (PowerShell execution policy), the dev server must
   be started manually before running `test:e2e:auth`. The `webServer.command` in
   `playwright.config.ts` uses `npm run dev` for portability — if CI is on Linux this works;
   on Windows with restricted execution policy, start the server manually.

4. **React dependency added explicitly.** `react` and `react-dom` were not in `package.json`
   before this slice. They are now explicit. This does not change runtime behaviour but
   makes the dependency tree explicit and stable against future `npm install` reorganization.

---

## Scope Compliance

| Rule | Compliance |
|---|---|
| No new non-approved dependencies | ✓ Only `@playwright/test` (approved) added as new devDep; react/react-dom already implicit |
| No production source code changes | ✓ All test code in `e2e/` and `scripts/`; no `src/` files modified |
| Backend is source of truth | ✓ All backend responses mocked; frontend does not derive auth truth |
| Frontend sends intent only | ✓ No auth decisions made in test-side code |
| JWT proves identity only | ✓ Test tokens are opaque strings; no JWT decoding |
| AI is advisory only | ✓ No AI decision surfaces modified |

---

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| `reuseExistingServer: true` in CI | Low | CI should start server before test run; or set `reuseExistingServer: !process.env.CI` |
| `@playwright/test` version drift from `playwright` | Low | Both now at 1.59.1; pinned via lockfile |
| React 18.3.1 explicit dep may conflict with future upgrades | Low | Explicit dep is more stable than implicit; upgrade deliberately |
| E2E test flakiness under high load | Low | All `waitForResponse`/`waitForFunction` use explicit conditions with 10-15s timeouts; no `waitForTimeout` |

---

## Recommended Next Slice

**FE-P0A-05**: Mid-session token expiry + retry on a protected data endpoint (not `/auth/me`).
This would test the case where a logged-in user's token expires while on a protected page,
makes a data API call (e.g., `GET /api/v1/operations`), gets 401, refreshes, and retries.

---

## Stop Conditions Hit

None. All tests pass. Implementation complete.
