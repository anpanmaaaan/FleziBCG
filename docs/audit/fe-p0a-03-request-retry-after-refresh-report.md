# FE-P0A-03 — Request Retry After Refresh

**Date:** 2025-07-30
**Task ID:** FE-P0A-03
**Depends on:** FE-P0A-02 (auth client refresh token contract), P0-A-03B (backend auth wiring)
**Status:** COMPLETE

---

## Summary

Closes the runtime continuity gap left by FE-P0A-02.

Before this slice: when an API request received a 401, the frontend would fire `refreshTokens()` in a fire-and-forget callback but the original request was dropped. The user had to retry manually.

After this slice: the original request is automatically retried exactly once after successful token rotation. If rotation fails, auth state is cleared and the user is redirected to login via the existing path.

---

## Routing

| Field | Value |
|---|---|
| Selected brain | Generic Brain (frontend auth client — no MOM/MES execution logic) |
| Selected mode | Strict Mode (auth, token security, session continuity) |
| Hard Mode MOM | v3 |
| Reason | Task touches authentication runtime behavior, refresh-token client handling, session continuity, auth truth boundary, retry after token rotation, security-sensitive token persistence |

---

## Hard Mode MOM v3 Gate

### Verdict

**`ALLOW_FE_P0A03_REQUEST_RETRY_AFTER_REFRESH`**

All invariants provable without architecture rewrite. Shared in-flight promise is a safe, narrow deduplication mechanism. No new dependencies. No backend changes. No permission truth derivation.

### Design / Contract Evidence Extract

- FE-P0A-02: `httpClient.ts` 401 path called `onUnauthorized?.()` (fire-and-forget) then threw `HttpError`. Original request never retried.
- FE-P0A-02: `AuthContext.tsx` set `onUnauthorized` to `void refreshTokens()`. Refresh triggered but caller had already received the thrown error.
- `refreshTokens()`: `isRefreshingRef.current` reentrancy guard; clears auth state on failure; updates `getHttpContext()` on success so subsequent calls use the new token.
- Backend: `/auth/refresh` rotates token pair — old token cannot be reused.

### Current vs. New Frontend Auth Flow

**Before:**
```
API request → 401 → onUnauthorized?() (void, fire-and-forget)
                   → refresh triggered (may succeed)
                   → HttpError thrown to caller
                   → original request dropped
```

**After:**
```
API request → 401
  → excluded endpoint? → onUnauthorized?() → throw
  → already retried?   → onUnauthorized?() → throw
  → refreshHandler?
      → await refreshInFlight (shared, parallel-safe)
      → success → request(path, {...options, retried: true}) → return result
      → failure → auth state already cleared → throw
```

### Invariant Map

| Invariant | How enforced |
|---|---|
| Original request retried at most once | `options.retried = true` flag on retry; checked before attempting refresh |
| Refresh endpoint never retried | `REFRESH_EXCLUDED_PATHS` includes `/v1/auth/refresh` |
| Login endpoint never retried | `REFRESH_EXCLUDED_PATHS` includes `/v1/auth/login` |
| Logout endpoints never retried | `REFRESH_EXCLUDED_PATHS` includes `/v1/auth/logout`, `/v1/auth/logout-all` |
| New access token used for retried request | Retry calls `request()` → `buildHeaders()` → reads `getHttpContext()` (updated by `refreshTokens()` before returning `true`) |
| Old refresh token replaced after refresh | Existing: `setStoredRefreshToken(response.refresh_token)` in `refreshTokens()` |
| Refresh failure clears auth state | `clearLocalAuthState()` in `refreshTokens()` catch block |
| Non-retryable 401 clears auth state | `setUnauthorizedHandler(() => clearLocalAuthState())` |
| No infinite loop | `retried` flag + `isRefreshingRef.current` (second layer) |
| Parallel 401 deduplication | `refreshInFlight: Promise<boolean> \| null` — parallel 401s await same promise |
| Refresh token never logged | Static check passes on all new code |
| Persona is not auth truth | `RequireAuth.tsx` uses `isAuthenticated` only — unchanged |

---

## Files Inspected

| File | Purpose |
|---|---|
| `frontend/src/app/api/httpClient.ts` | HTTP client — pre-change 401 behavior |
| `frontend/src/app/auth/AuthContext.tsx` | Auth provider — current unauthorized handler |
| `frontend/src/app/api/authApi.ts` | Auth API wrappers |
| `frontend/src/app/api/index.ts` | API barrel exports |
| `frontend/src/app/auth/RequireAuth.tsx` | Route guard — verified unchanged |
| `frontend/scripts/auth-contract-smoke.mjs` | FE-P0A-02 invariant checks |
| `frontend/package.json` | Available scripts |
| `docs/audit/fe-p0a-02-auth-client-refresh-token-contract-report.md` | Prior slice report |

---

## Files Changed

| File | Change |
|---|---|
| `frontend/src/app/api/httpClient.ts` | Added `retried?: boolean` to `RequestOptions`; added `REFRESH_EXCLUDED_PATHS` constant + `isExcludedFromRefresh()` helper; added `refreshHandler` + `refreshInFlight` module vars; added `setRefreshHandler` export; restructured 401 handling to attempt refresh+retry before throwing |
| `frontend/src/app/api/index.ts` | Re-exported `setRefreshHandler` from httpClient |
| `frontend/src/app/auth/AuthContext.tsx` | Imported `setRefreshHandler`; changed `useEffect` handler to call both `setRefreshHandler(() => refreshTokens())` and `setUnauthorizedHandler(() => clearLocalAuthState())`; added `clearLocalAuthState` to effect deps |
| `frontend/scripts/auth-retry-smoke.mjs` | New static invariant smoke script (14 checks) |
| `frontend/package.json` | Added `check:auth:retry` script |

---

## Tests / Smoke Checks Added or Updated

### New: `frontend/scripts/auth-retry-smoke.mjs` — 14 checks, 0 failures

| Check | Result |
|---|---|
| `test_http_client_has_retry_after_refresh_hook` | PASS |
| `test_set_refresh_handler_exported_from_api_barrel` | PASS |
| `test_retry_marker_prevents_infinite_loop` | PASS |
| `test_original_request_retried_once_after_refresh_success` | PASS |
| `test_retried_request_uses_new_access_token` | PASS |
| `test_refresh_endpoint_is_excluded_from_refresh_retry` | PASS |
| `test_login_endpoint_is_excluded_from_refresh_retry` | PASS |
| `test_logout_endpoint_is_excluded_from_refresh_retry` | PASS |
| `test_parallel_401_uses_single_refresh_if_implemented` | PASS |
| `test_auth_context_wires_refresh_handler` | PASS |
| `test_auth_context_passes_refresh_tokens_to_handler` | PASS |
| `test_auth_context_wires_unauthorized_handler_for_non_retryable_401s` | PASS |
| `test_unauthorized_handler_clears_state_does_not_retry_refresh` | PASS |
| `test_refresh_token_is_never_logged_in_httpClient` | PASS |

### Existing: `frontend/scripts/auth-contract-smoke.mjs` — 14 checks, 0 failures (no regressions)

---

## Verification Commands Run

```
node scripts/auth-retry-smoke.mjs                    → 14 passed, 0 failed
node scripts/auth-contract-smoke.mjs                 → 14 passed, 0 failed
node .\node_modules\eslint\bin\eslint.js src/app/api/httpClient.ts src/app/api/index.ts src/app/auth/AuthContext.tsx --max-warnings 0 → Exit: 0
node .\node_modules\vite\bin\vite.js build            → ✓ 3408 modules transformed, built in 19.97s
node scripts/route-smoke-check.mjs                   → all PASS
```

`npm run lint` / `npm run build` produce PowerShell script execution policy errors in this environment — direct `node` invocations used (equivalent outcome).

---

## Results

| Check | Result |
|---|---|
| Auth retry smoke (14 checks) | PASS |
| Auth contract smoke — FE-P0A-02 regression (14 checks) | PASS |
| ESLint on changed files (0 warnings) | PASS |
| Vite production build | PASS |
| Route smoke check | PASS |

---

## Existing Gaps / Known Technical Debts

| Gap | Severity | Slice |
|---|---|---|
| **No E2E test coverage** — No Playwright E2E tests cover the actual 401→refresh→retry flow. Static smoke checks validate source structure, not runtime behavior. | Medium | Separate E2E slice |
| **No unit test framework** — Cannot write unit tests for `httpClient.ts` retry logic without vitest/jest. | Low | Separate test infrastructure slice |
| **`refreshInFlight` is a module singleton** — If multiple `AuthProvider` instances exist (e.g., in tests), the in-flight state is shared. In production there is exactly one `AuthProvider`. | Low | Non-issue in production; relevant only for test isolation |
| **AbortSignal not propagated on retry** — If the original request had `signal` set and it was aborted between original request and retry, the retry will still proceed. An aborted signal would cause the fetch to fail naturally. | Low | Edge case; acceptable |
| **localStorage-only token storage** — Refresh token in localStorage is accessible to any JS on the page (XSS risk). | Medium | Security hardening slice (requires backend cookie support) |
| **`/auth/me` retried on 401** — This is desirable (silent re-auth on bootstrap) but means the bootstrap `useEffect` may now make up to 2 calls to `/auth/me` on token expiry. | Low | Acceptable behavior; documented |

---

## Scope Compliance

- Does NOT modify backend code or tests.
- Does NOT change backend auth contract.
- Does NOT redesign auth architecture.
- Does NOT add new dependencies.
- Does NOT add new state management.
- Does NOT touch MMD/Execution/Quality/Material/Integration/AI screens.
- Does NOT derive permission truth in frontend.
- Works in a single vertical slice (httpClient retry + AuthContext wiring only).

---

## Risks

| Risk | Mitigation |
|---|---|
| `/auth/refresh` itself 401s → triggers another refresh | `/v1/auth/refresh` in `REFRESH_EXCLUDED_PATHS` — excluded at path level |
| Retry also 401s (token valid but insufficient permissions) | `options.retried = true` blocks second retry; `onUnauthorized()` clears state |
| Two parallel 401s each spawn a refresh → second invalidates first's token | `refreshInFlight` shared promise: second 401 awaits first refresh |
| AuthContext unmounts during async refresh | React state updates after unmount are a known React 17 warning, suppressed in React 18. No crash risk. |

---

## Recommended Next Slice

**FE-P0A-04 — Playwright E2E: Auth Flow Coverage**

Write Playwright E2E tests that cover:
1. Login → protected API call → verify token stored
2. Simulate expired access token → verify silent re-auth via refresh → verify original request completed
3. Simulate expired refresh token → verify redirect to login

This requires a test environment where the backend issues short-lived tokens or a mock server.

---

## Stop Conditions Hit

None. All mandatory files present. All invariants provable. No stop conditions triggered.
