# FE-P0A-02 — Auth Client Refresh Token Contract Update

**Date:** 2025-07-30
**Task ID:** FE-P0A-02
**Depends on:** P0-A-03A (refresh token foundation), P0-A-03B (backend auth wiring)
**Status:** COMPLETE

---

## Routing

| Field | Value |
|---|---|
| Selected brain | flezibcg-ai-brain-v6-auto-execution |
| Selected mode | AUTO_IMPL |
| Hard Mode MOM | v3 |
| Reason | UI task touches auth execution state (token storage, unauthorized handler, logout flow); frontend never derives auth truth, only handles token lifecycle as a side-effect of backend responses. |

---

## HMM v3 Gate

### Design Evidence Extract

- P0-A-03B backend contract: `POST /auth/login` returns `refresh_token: str | None`, `POST /auth/refresh` accepts `{ refresh_token: str }` body and returns rotated pair.
- Token storage: localStorage — `mes.auth.token` (access), `mes.auth.refresh_token` (new, refresh).
- Auth truth: server only. JWT proves identity, authorization is server-side. Frontend sends intent.
- Existing 401 handler: `setUnauthorizedHandler(() => void logout())` → replaced with `void refreshTokens()`.

### Event Map

| Event | Handler |
|---|---|
| Successful login | Store both tokens; hydrate currentUser |
| 401 from any API call | Fire refreshTokens(); if succeeds, caller retries on next navigation; if fails, clearLocalAuthState() |
| Successful refresh | Rotate both tokens in localStorage; update httpContextProvider |
| Refresh fails (any error or null token) | clearLocalAuthState() → user sees login screen |
| Logout | Revoke session via backend; clearLocalAuthState() removes both tokens |

### Invariant Map

| Invariant | How enforced |
|---|---|
| Refresh token never exposed to console | Static check `test_refresh_token_is_never_logged` |
| Access and refresh tokens are always rotated together | `test_refresh_replaces_both_access_and_refresh_tokens` |
| Old refresh token is never reused if rotation response is null | Guard in `refreshTokens()`: `if (!response.refresh_token) { clearLocalAuthState(); return false; }` |
| Infinite refresh loop not possible | `isRefreshingRef.current` reentrancy guard |
| Persona is not auth truth | `RequireAuth.tsx` uses `isAuthenticated` only |
| Frontend never fabricates token state | All tokens come from backend `LoginResponse` / `RefreshResponse` |

### State Transition Map

```
UNINITIALIZED
  ↓ (token in localStorage?)
  ├─ YES → INITIALIZING → refreshCurrentUser → AUTHENTICATED
  └─ NO  → UNAUTHENTICATED

UNAUTHENTICATED
  ↓ login(username, password)
  ├─ success → AUTHENTICATED
  └─ backend error → UNAUTHENTICATED (error propagated to caller)

AUTHENTICATED
  ↓ 401 from API call
  ├─ refreshTokens()
  │   ├─ success → AUTHENTICATED (new tokens stored; original request not retried)
  │   └─ failure → UNAUTHENTICATED (clearLocalAuthState)
  ↓ logout()
  └─ UNAUTHENTICATED

NOTE: Request retry after token refresh is NOT implemented in this slice.
      The original failed request is dropped; the user remains on the current
      page with fresh tokens. Retry-after-refresh is a follow-up slice.
```

### Test Matrix

| Test | Type | Result |
|---|---|---|
| test_login_response_type_has_refresh_token | Static | PASS |
| test_login_handles_missing_refresh_token_as_contract_error | Static | PASS |
| test_refresh_sends_refresh_token_body | Static | PASS |
| test_refresh_endpoint_is_wired_in_authApi | Static | PASS |
| test_refresh_replaces_both_access_and_refresh_tokens | Static | PASS |
| test_refresh_does_not_reuse_old_token_if_rotation_fails | Static | PASS |
| test_refresh_401_clears_auth_state | Static | PASS |
| test_refresh_failure_does_not_loop_infinitely | Static | PASS |
| test_logout_clears_access_and_refresh_tokens | Static | PASS |
| test_refresh_token_has_distinct_storage_key | Static | PASS |
| test_refresh_token_is_never_logged | Static | PASS |
| test_legacy_access_token_only_refresh_path_removed | Static | PASS |
| test_RefreshRequest_type_exported | Static | PASS |
| test_persona_is_not_authorization_truth | Static | PASS |

### Verdict

`ALLOW_FE_P0A02_AUTH_CLIENT_UPDATE`

All invariants provable. No fabrication of auth state. No derivation of authorization. Backend is source of truth. Risk: see Known Gaps.

---

## Backward Compatibility Decision

**Option A (strict)** was selected: login throws if `refresh_token` is absent from backend response.

This is a **non-negotiable contract assertion**. The backend (P0-A-03B) guarantees refresh_token is returned on every successful login. If a future backend regression returns `null`, the frontend will fast-fail at login time with a visible error rather than silently degrading to a non-refreshable session.

**Not selected:** Option B (graceful fallback to logout-on-401) — rejected because it allows silent regressions to persist until users encounter 401 errors mid-session.

---

## Files Inspected

| File | Purpose |
|---|---|
| `frontend/src/app/api/authApi.ts` | Auth API call wrappers — pre-change state |
| `frontend/src/app/auth/AuthContext.tsx` | Auth provider — pre-change state |
| `frontend/src/app/api/httpClient.ts` | HTTP client with 401 hook — unchanged |
| `frontend/src/app/auth/RequireAuth.tsx` | Route guard — verified unchanged |
| `frontend/src/app/auth/index.ts` | Auth barrel export — verified |
| `frontend/package.json` | Scripts inventory |
| `backend/app/api/v1/auth.py` | Backend contract source of truth |
| `backend/app/schemas/auth.py` | LoginResponse / RefreshRequest schemas |

---

## Files Changed

| File | Change |
|---|---|
| `frontend/src/app/api/authApi.ts` | Added `refresh_token` to `LoginResponse`; added `RefreshRequest`, `RefreshResponse` interfaces; added `authApi.refresh()` method |
| `frontend/src/app/auth/AuthContext.tsx` | Added `REFRESH_TOKEN_KEY`, `getStoredRefreshToken()`, `setStoredRefreshToken()`; updated `login()` to store refresh token and guard missing token; updated `clearLocalAuthState()` to clear refresh token; added `refreshTokens()` callback; changed `setUnauthorizedHandler` to call `refreshTokens` instead of `logout`; extended `AuthContextValue` with `refreshTokens`; updated `useMemo` value and deps |
| `frontend/scripts/auth-contract-smoke.mjs` | New static smoke script (14 invariant checks) |
| `frontend/package.json` | Added `check:auth:contract` script |

---

## Tests Added / Updated

### New: `frontend/scripts/auth-contract-smoke.mjs`

Static source-code invariant checks. 14 checks, 0 failures.

**Note on test framework absence:** No unit test framework (vitest/jest/testing-library) is present in `package.json`. Only Playwright (`^1.52.0`) is available, and no E2E test suite exists. Static smoke checks are the available verification mechanism for this codebase.

---

## Verification Commands Run

```
node scripts/auth-contract-smoke.mjs          → 14 passed, 0 failed
node .\node_modules\eslint\bin\eslint.js src/app/api/authApi.ts src/app/auth/AuthContext.tsx --max-warnings 0 → Exit: 0
node scripts/route-smoke-check.mjs            → All PASS
node .\node_modules\vite\bin\vite.js build    → ✓ 3408 modules transformed, built in 7.14s
```

`npm run lint` / `npm run build` produce PowerShell script execution policy errors in this environment — direct `node` invocations used instead (equivalent outcome).

---

## Results

| Check | Result |
|---|---|
| Auth contract smoke (14 checks) | PASS |
| ESLint on changed files (0 warnings) | PASS |
| Vite production build | PASS |
| Route smoke check | PASS |

---

## Existing Gaps / Known Technical Debts

| Gap | Severity | Slice |
|---|---|---|
| **No request retry after token refresh** — On 401, `refreshTokens()` is fired but the original failed request is dropped. The user retains fresh tokens but the in-flight action silently fails. The user must manually retry. | Medium | FE-P0A-03 or dedicated retry slice |
| **Fire-and-forget 401 handler** — `setUnauthorizedHandler` returns void; no mechanism to notify the original call site that refresh succeeded or failed. | Low | Blocked by httpClient architecture; requires interceptor refactor |
| **No E2E test coverage** — No Playwright E2E tests cover login, token refresh, or logout flows. | Medium | Separate E2E slice |
| **No unit test framework** — `authApi.ts` and `AuthContext.tsx` cannot be unit-tested without vitest or jest. | Low | Separate test infrastructure slice |
| **localStorage-only token storage** — Refresh token stored in localStorage is accessible to any JS on the page (XSS risk). Httponly cookie storage would be more secure. | Medium | Security hardening slice (requires backend cookie support) |
| **refreshCurrentUser called on every navigation** — Not introduced here, but existing behavior. | Low | Performance optimization |

---

## Scope Compliance

- Does NOT invent product scope.
- Works in a single vertical slice (auth client contract update only).
- Does NOT modify httpClient.ts retry logic (deferred).
- Does NOT touch any execution, quality, material, or ERP code.
- All auth truth remains on the backend.

---

## Risks

| Risk | Mitigation |
|---|---|
| Login throws if backend returns `null` refresh_token (strict Option A) | P0-A-03B guarantees non-null on success. Backend has test coverage for this contract. |
| Token refresh called concurrently (e.g., two parallel 401 responses) | `isRefreshingRef.current` reentrancy guard returns `false` immediately on second call. |
| Stale `currentUser` in refreshTokens closure | `currentUser` is a dependency of `refreshTokens` callback. React will recreate the callback when user changes. |

---

## Recommended Next Slice

**FE-P0A-03 — Request Retry After Token Refresh**

Wire an interceptor pattern so that when `refreshTokens()` succeeds after a 401, the original failed request is automatically retried. This requires modifying `httpClient.ts` to queue pending requests during refresh rather than using a fire-and-forget callback.

---

## Stop Conditions Hit

- All 14 auth contract invariants pass.
- ESLint: 0 warnings on changed files.
- Production build: clean.
- Route smoke: no regressions.
- Scope: auth client only. No execution/quality/material/tenant code touched.
