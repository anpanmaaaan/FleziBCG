/**
 * FE-P0A-02: Auth Contract Smoke Check
 *
 * Validates that the frontend auth client source code complies with the
 * P0-A-03B strict refresh-token contract.
 *
 * These are static source-code invariant checks — not runtime tests.
 * A unit/integration test framework is not available in this project
 * (no vitest/jest/testing-library in package.json).
 *
 * All checks are PASS/FAIL with a final exit code.
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

const authApi = await readSource("app/api/authApi.ts");
const authContext = await readSource("app/auth/AuthContext.tsx");

if (!authApi) {
  console.error("ABORT: src/app/api/authApi.ts not found.");
  process.exit(2);
}
if (!authContext) {
  console.error("ABORT: src/app/auth/AuthContext.tsx not found.");
  process.exit(2);
}

// ─── 1. Login: LoginResponse has refresh_token field ─────────────────────────

if (/refresh_token\s*:\s*string/.test(authApi)) {
  pass("test_login_response_type_has_refresh_token");
} else {
  fail("test_login_response_type_has_refresh_token", "LoginResponse missing refresh_token field in authApi.ts");
}

// ─── 2. Login: handles missing refresh_token as a contract error ──────────────

if (/if\s*\(!response\.refresh_token\)/.test(authContext)) {
  pass("test_login_handles_missing_refresh_token_as_contract_error");
} else {
  fail("test_login_handles_missing_refresh_token_as_contract_error", "AuthContext.tsx login does not guard against missing refresh_token");
}

// ─── 3. Refresh: sends refresh_token in request body ─────────────────────────

if (/authApi\.refresh\(\s*\{/.test(authContext) && /refresh_token:\s*storedRefreshToken/.test(authContext)) {
  pass("test_refresh_sends_refresh_token_body");
} else {
  fail("test_refresh_sends_refresh_token_body", "AuthContext.tsx does not call authApi.refresh with refresh_token body");
}

// ─── 4. Refresh: POST /auth/refresh endpoint is wired ────────────────────────

if (/\/v1\/auth\/refresh/.test(authApi)) {
  pass("test_refresh_endpoint_is_wired_in_authApi");
} else {
  fail("test_refresh_endpoint_is_wired_in_authApi", "authApi.ts missing POST /v1/auth/refresh call");
}

// ─── 5. Refresh: replaces BOTH access and refresh tokens ─────────────────────

if (
  /setStoredToken\(response\.access_token\)/.test(authContext) &&
  /setStoredRefreshToken\(response\.refresh_token\)/.test(authContext)
) {
  pass("test_refresh_replaces_both_access_and_refresh_tokens");
} else {
  fail("test_refresh_replaces_both_access_and_refresh_tokens", "AuthContext.tsx does not atomically replace both tokens after refresh");
}

// ─── 6. Old refresh token not reused: guard clears state on null new token ───

if (/!response\.refresh_token/.test(authContext) && /clearLocalAuthState\(\)/.test(authContext)) {
  pass("test_refresh_does_not_reuse_old_token_if_rotation_fails");
} else {
  fail("test_refresh_does_not_reuse_old_token_if_rotation_fails", "AuthContext.tsx does not clear state when rotation returns null refresh_token");
}

// ─── 7. Refresh 401 clears auth state ────────────────────────────────────────

// refreshTokens calls clearLocalAuthState in the catch block
if (/clearLocalAuthState\(\)/.test(authContext)) {
  pass("test_refresh_401_clears_auth_state");
} else {
  fail("test_refresh_401_clears_auth_state", "AuthContext.tsx does not clear auth state on refresh failure");
}

// ─── 8. No infinite retry loop: isRefreshingRef guard present ────────────────

if (/isRefreshingRef\.current/.test(authContext)) {
  pass("test_refresh_failure_does_not_loop_infinitely");
} else {
  fail("test_refresh_failure_does_not_loop_infinitely", "AuthContext.tsx missing isRefreshingRef guard — infinite retry possible");
}

// ─── 9. Logout clears both access token AND refresh token ────────────────────

// clearLocalAuthState should call setStoredRefreshToken(null)
if (/setStoredRefreshToken\(null\)/.test(authContext)) {
  pass("test_logout_clears_access_and_refresh_tokens");
} else {
  fail("test_logout_clears_access_and_refresh_tokens", "AuthContext.tsx clearLocalAuthState does not clear refresh token");
}

// ─── 10. Refresh token storage key is distinct from access token key ─────────

if (/REFRESH_TOKEN_KEY\s*=\s*["']mes\.auth\.refresh_token["']/.test(authContext)) {
  pass("test_refresh_token_has_distinct_storage_key");
} else {
  fail("test_refresh_token_has_distinct_storage_key", "AuthContext.tsx missing REFRESH_TOKEN_KEY constant with correct value");
}

// ─── 11. Raw refresh token is never console.log'd ────────────────────────────

const refreshTokenLogPattern = /console\.(log|debug|warn|error)\s*\([^)]*refresh_token/;
if (!refreshTokenLogPattern.test(authContext) && !refreshTokenLogPattern.test(authApi)) {
  pass("test_refresh_token_is_never_logged");
} else {
  fail("test_refresh_token_is_never_logged", "Raw refresh_token value found in a console.log/debug/warn/error call");
}

// ─── 12. Legacy access-token-only refresh path is absent ─────────────────────

// Old pattern: /auth/refresh called with Authorization header only (no body)
// New pattern: always sends { refresh_token: ... } body
// Check that there is no refresh call that does NOT include a refresh_token body
const legacyPattern = /\/v1\/auth\/refresh.*method.*POST(?![\s\S]*body)/;
const hasLegacyRefresh = legacyPattern.test(authApi);
if (!hasLegacyRefresh) {
  pass("test_legacy_access_token_only_refresh_path_removed");
} else {
  fail("test_legacy_access_token_only_refresh_path_removed", "Legacy access-token-only refresh path still present in authApi.ts");
}

// ─── 13. RefreshRequest type defined in authApi ───────────────────────────────

if (/export interface RefreshRequest/.test(authApi)) {
  pass("test_RefreshRequest_type_exported");
} else {
  fail("test_RefreshRequest_type_exported", "authApi.ts missing exported RefreshRequest interface");
}

// ─── 14. Persona is not auth truth (RequireAuth uses isAuthenticated) ─────────

const requireAuth = await readSource("app/auth/RequireAuth.tsx");
if (requireAuth) {
  if (/isAuthenticated/.test(requireAuth) && !/persona|role_code|canAccess/.test(requireAuth)) {
    pass("test_persona_is_not_authorization_truth");
  } else {
    fail("test_persona_is_not_authorization_truth", "RequireAuth.tsx may be using persona/role_code as auth truth");
  }
} else {
  fail("test_persona_is_not_authorization_truth", "RequireAuth.tsx not found");
}

// ─── Report ───────────────────────────────────────────────────────────────────

const passed = results.filter((r) => r.status === "PASS").length;
const failed = results.filter((r) => r.status === "FAIL").length;

console.log("\n=== Auth Contract Smoke Check ===\n");
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
