/**
 * FE-P0A-03: Auth Retry Smoke Check
 *
 * Validates that the frontend httpClient and AuthContext source code implement
 * the retry-after-refresh invariants required by FE-P0A-03.
 *
 * These are static source-code invariant checks — not runtime tests.
 * No unit test framework is available (no vitest/jest/testing-library).
 *
 * All checks are PASS/FAIL with a final non-zero exit code on any failure.
 */

import fs from "node:fs/promises";
import path from "node:path";

const FRONTEND_ROOT = process.cwd();
const SRC = path.join(FRONTEND_ROOT, "src");

const results = [];

function pass(name) {
  results.push({ name, status: "PASS" });
}

function fail(name, reason) {
  results.push({ name, status: "FAIL", reason });
}

async function readSource(relPath) {
  const fullPath = path.join(SRC, relPath);
  try {
    return await fs.readFile(fullPath, "utf8");
  } catch {
    return null;
  }
}

// ─── Load source files ───────────────────────────────────────────────────────

const httpClient = await readSource("app/api/httpClient.ts");
const authContext = await readSource("app/auth/AuthContext.tsx");
const apiIndex = await readSource("app/api/index.ts");

if (!httpClient) { console.error("ABORT: src/app/api/httpClient.ts not found."); process.exit(2); }
if (!authContext) { console.error("ABORT: src/app/auth/AuthContext.tsx not found."); process.exit(2); }
if (!apiIndex)   { console.error("ABORT: src/app/api/index.ts not found.");        process.exit(2); }

// ─── 1. httpClient exports setRefreshHandler ─────────────────────────────────

if (/export const setRefreshHandler/.test(httpClient)) {
  pass("test_http_client_has_retry_after_refresh_hook");
} else {
  fail("test_http_client_has_retry_after_refresh_hook", "httpClient.ts does not export setRefreshHandler");
}

// ─── 2. setRefreshHandler is re-exported from the api barrel ─────────────────

if (/setRefreshHandler/.test(apiIndex)) {
  pass("test_set_refresh_handler_exported_from_api_barrel");
} else {
  fail("test_set_refresh_handler_exported_from_api_barrel", "src/app/api/index.ts does not re-export setRefreshHandler");
}

// ─── 3. RequestOptions has retried flag (loop guard) ─────────────────────────

if (/retried\s*\?/.test(httpClient)) {
  pass("test_retry_marker_prevents_infinite_loop");
} else {
  fail("test_retry_marker_prevents_infinite_loop", "RequestOptions in httpClient.ts is missing the retried? flag");
}

// ─── 4. Retry path re-calls request() with retried: true ─────────────────────

if (/return request<T>\(path,\s*\{\s*\.\.\.options,\s*retried:\s*true\s*\}\)/.test(httpClient)) {
  pass("test_original_request_retried_once_after_refresh_success");
} else {
  fail("test_original_request_retried_once_after_refresh_success", "httpClient.ts does not retry request with { ...options, retried: true }");
}

// ─── 5. Retried request uses new access token (re-runs buildHeaders via request()) ──

// The retry calls request() which calls buildHeaders() which reads from getHttpContext.
// AuthContext already updates getHttpContext inside refreshTokens() before returning true.
// Evidence: retry calls request<T>(path, { ...options, retried: true }) not fetch() directly.
if (/return request<T>\(path,/.test(httpClient) && /buildHeaders/.test(httpClient)) {
  pass("test_retried_request_uses_new_access_token");
} else {
  fail("test_retried_request_uses_new_access_token", "Retry path does not re-run buildHeaders (must call request(), not fetch() directly)");
}

// ─── 6. Refresh endpoint excluded from refresh retry ─────────────────────────

if (/\/v1\/auth\/refresh/.test(httpClient) && /REFRESH_EXCLUDED_PATHS/.test(httpClient)) {
  pass("test_refresh_endpoint_is_excluded_from_refresh_retry");
} else {
  fail("test_refresh_endpoint_is_excluded_from_refresh_retry", "httpClient.ts REFRESH_EXCLUDED_PATHS missing /v1/auth/refresh");
}

// ─── 7. Login endpoint excluded from refresh retry ───────────────────────────

if (/\/v1\/auth\/login/.test(httpClient) && /REFRESH_EXCLUDED_PATHS/.test(httpClient)) {
  pass("test_login_endpoint_is_excluded_from_refresh_retry");
} else {
  fail("test_login_endpoint_is_excluded_from_refresh_retry", "httpClient.ts REFRESH_EXCLUDED_PATHS missing /v1/auth/login");
}

// ─── 8. Logout endpoints excluded from refresh retry ─────────────────────────

if (/\/v1\/auth\/logout/.test(httpClient) && /REFRESH_EXCLUDED_PATHS/.test(httpClient)) {
  pass("test_logout_endpoint_is_excluded_from_refresh_retry");
} else {
  fail("test_logout_endpoint_is_excluded_from_refresh_retry", "httpClient.ts REFRESH_EXCLUDED_PATHS missing /v1/auth/logout");
}

// ─── 9. Parallel 401 protection: shared refreshInFlight promise ──────────────

if (/refreshInFlight/.test(httpClient)) {
  pass("test_parallel_401_uses_single_refresh_if_implemented");
} else {
  fail("test_parallel_401_uses_single_refresh_if_implemented", "httpClient.ts missing refreshInFlight deduplication variable");
}

// ─── 10. AuthContext wires setRefreshHandler ─────────────────────────────────

if (/setRefreshHandler/.test(authContext)) {
  pass("test_auth_context_wires_refresh_handler");
} else {
  fail("test_auth_context_wires_refresh_handler", "AuthContext.tsx does not call setRefreshHandler");
}

// ─── 11. AuthContext passes refreshTokens to setRefreshHandler ───────────────

if (/setRefreshHandler\s*\(\s*\(\)\s*=>\s*refreshTokens\(\)/.test(authContext)) {
  pass("test_auth_context_passes_refresh_tokens_to_handler");
} else {
  fail("test_auth_context_passes_refresh_tokens_to_handler", "AuthContext.tsx does not pass refreshTokens to setRefreshHandler");
}

// ─── 12. AuthContext still wires setUnauthorizedHandler for non-retryable 401s ─

if (/setUnauthorizedHandler/.test(authContext)) {
  pass("test_auth_context_wires_unauthorized_handler_for_non_retryable_401s");
} else {
  fail("test_auth_context_wires_unauthorized_handler_for_non_retryable_401s", "AuthContext.tsx does not call setUnauthorizedHandler");
}

// ─── 13. Unauthorized handler calls clearLocalAuthState (not refreshTokens) ──

// The setUnauthorizedHandler in AuthContext should NOT call refreshTokens — that
// would create a second refresh attempt on already-retried failures.
// Check that the unauthorized handler body is clearLocalAuthState, not refreshTokens.
const unauthorizedHandlerBlock = authContext.match(/setUnauthorizedHandler\s*\(\s*\(\)\s*=>\s*\{([^}]+)\}/);
if (unauthorizedHandlerBlock) {
  const body = unauthorizedHandlerBlock[1];
  if (/clearLocalAuthState/.test(body) && !/refreshTokens/.test(body)) {
    pass("test_unauthorized_handler_clears_state_does_not_retry_refresh");
  } else {
    fail("test_unauthorized_handler_clears_state_does_not_retry_refresh", "setUnauthorizedHandler body should call clearLocalAuthState, not refreshTokens");
  }
} else {
  // Arrow body style without braces — less likely but still check for absence of refreshTokens in nearby context
  if (/setUnauthorizedHandler/.test(authContext) && !/setUnauthorizedHandler.*refreshTokens/.test(authContext)) {
    pass("test_unauthorized_handler_clears_state_does_not_retry_refresh");
  } else {
    fail("test_unauthorized_handler_clears_state_does_not_retry_refresh", "Cannot verify unauthorized handler body — check AuthContext.tsx manually");
  }
}

// ─── 14. Refresh token is never console.log'd in httpClient ──────────────────

const logInHttpClient = /console\.(log|debug|warn|error)\s*\([^)]*refresh_token/.test(httpClient);
if (!logInHttpClient) {
  pass("test_refresh_token_is_never_logged_in_httpClient");
} else {
  fail("test_refresh_token_is_never_logged_in_httpClient", "Raw refresh_token found in a console.log/debug/warn/error in httpClient.ts");
}

// ─── FE-P0A-04: Extended static invariants (runtime gap mitigations) ─────────
//
// These checks close the static portion of the runtime gap identified in the
// FE-P0A-04 stop report. They verify structural guarantees that runtime E2E
// tests would also verify, but at the source-code level only.
// A runtime gap remains (see fe-p0a-04 stop report for options).

// ─── 15. refreshInFlight is reset to null after use (.finally) ───────────────

if (/refreshInFlight\s*=\s*null/.test(httpClient) && /\.finally\(/.test(httpClient)) {
  pass("test_refresh_in_flight_is_reset_after_completion");
} else {
  fail("test_refresh_in_flight_is_reset_after_completion", "httpClient.ts refreshInFlight is not reset to null in a .finally() block");
}

// ─── 16. refreshHandler result is awaited (not fire-and-forget) ──────────────

// Check that refresh in the 401 branch awaits the result
if (/await refreshInFlight/.test(httpClient)) {
  pass("test_refresh_result_is_awaited_not_fire_and_forget");
} else {
  fail("test_refresh_result_is_awaited_not_fire_and_forget", "httpClient.ts 401 branch does not await refreshInFlight — refresh is fire-and-forget");
}

// ─── 17. Retry guard checks BOTH retried flag AND excluded path ───────────────

// The condition must be: !options.retried AND !isExcludedFromRefresh AND refreshHandler
if (/!options\.retried/.test(httpClient) && /isExcludedFromRefresh/.test(httpClient)) {
  pass("test_retry_guard_checks_retried_flag_and_excluded_path");
} else {
  fail("test_retry_guard_checks_retried_flag_and_excluded_path", "httpClient.ts 401 branch does not check both !options.retried and isExcludedFromRefresh");
}

// ─── 18. No direct fetch() call in retry path ────────────────────────────────

// Retry must call request() (not fetch()) so buildHeaders re-runs with new token.
// Count fetch() calls — should be exactly one (the main request, not in retry).
const fetchCallCount = (httpClient.match(/\bfetch\s*\(/g) || []).length;
if (fetchCallCount === 1) {
  pass("test_retry_path_does_not_call_fetch_directly");
} else if (fetchCallCount === 0) {
  fail("test_retry_path_does_not_call_fetch_directly", "No fetch() call found in httpClient.ts — unexpected");
} else {
  fail("test_retry_path_does_not_call_fetch_directly", `Multiple fetch() calls found (${fetchCallCount}) — retry may be calling fetch() directly instead of request()`);
}

// ─── 19. isExcludedFromRefresh normalizes path (uses normalizePath) ───────────

if (/normalizePath/.test(httpClient) && /isExcludedFromRefresh/.test(httpClient)) {
  // Check that isExcludedFromRefresh uses normalizePath
  const funcBody = httpClient.match(/function isExcludedFromRefresh[\s\S]*?\}/)?.[0] ?? "";
  if (/normalizePath/.test(funcBody)) {
    pass("test_excluded_path_check_normalizes_path");
  } else {
    fail("test_excluded_path_check_normalizes_path", "isExcludedFromRefresh does not call normalizePath — path comparison may fail for relative paths");
  }
} else {
  fail("test_excluded_path_check_normalizes_path", "httpClient.ts missing normalizePath usage in exclusion check");
}

// ─── 20. logout-all is also excluded ─────────────────────────────────────────

if (/\/v1\/auth\/logout-all/.test(httpClient)) {
  pass("test_logout_all_endpoint_is_excluded_from_refresh_retry");
} else {
  fail("test_logout_all_endpoint_is_excluded_from_refresh_retry", "httpClient.ts REFRESH_EXCLUDED_PATHS missing /v1/auth/logout-all");
}

// ─── Report ───────────────────────────────────────────────────────────────────

const passed = results.filter((r) => r.status === "PASS").length;
const failed = results.filter((r) => r.status === "FAIL").length;

console.log("\n=== Auth Retry Smoke Check (FE-P0A-03) ===\n");
for (const r of results) {
  if (r.status === "PASS") {
    console.log(`  ✓ ${r.name}`);
  } else {
    console.log(`  ✗ ${r.name}`);
    console.log(`    REASON: ${r.reason}`);
  }
}

console.log(`\n${passed} passed, ${failed} failed\n`);

if (failed > 0) {
  process.exit(1);
}
