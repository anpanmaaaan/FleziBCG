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
