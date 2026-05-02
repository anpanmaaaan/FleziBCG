# Stop Condition Triggered

**Date:** 2025-07-30
**Task ID:** FE-P0A-04
**Task Name:** E2E Auth Refresh Retry Coverage

---

## Summary

FE-P0A-04 requires runtime E2E tests for the auth refresh-and-retry flow implemented by FE-P0A-02 and FE-P0A-03.

The task specifies Playwright as the preferred mechanism and prohibits adding new dependencies.

After inspecting the frontend project, the `@playwright/test` package (the Playwright test runner, which provides `test()`, `expect()`, `page.route()`, and the `playwright test` CLI) is **not installed**. Only the `playwright` browser automation library is present. These are distinct packages with distinct purposes.

Without `@playwright/test`, it is not possible to write `.spec.ts` E2E test files, configure a test runner, or use route interception in the manner the task requires — without adding a new dependency.

The task explicitly states: _"Do not add new testing dependency."_ and _"Do not add new E2E framework if Playwright already exists."_

Stop conditions are met. Implementation is not safe to continue.

---

## Mandatory Files Status

| File | Status |
|---|---|
| `.github/copilot-instructions.md` | ✓ Present — read |
| `.github/agent/AGENT.md` | ✓ Present — read |
| `docs/ai-skills/flezibcg-ai-brain-v6-auto-execution/SKILL.md` | ✓ Present — read |
| `docs/ai-skills/hard-mode-mom-v3/SKILL.md` | ✓ Present — read |
| `docs/audit/fe-p0a-02-auth-client-refresh-token-contract-report.md` | ✓ Present |
| `docs/audit/fe-p0a-03-request-retry-after-refresh-report.md` | ✓ Present |

All four mandatory files are present. The stop is not due to missing mandatory files.

---

## Source Evidence

### `frontend/package.json` — devDependencies

```json
"playwright": "^1.52.0"
```

`@playwright/test` is **not present**.

### `frontend/node_modules/`

```
node_modules/playwright/         ← browser automation library only
  index.d.ts                     ← exports from playwright-core only
  index.js
  lib/
  types/
```

`node_modules/@playwright/test/` — **does not exist**.

### Available test runner packages

None. No vitest, no jest, no @playwright/test, no testing-library, no mocha, no jasmine.

### Available test infrastructure

Only static Node.js smoke scripts:

- `frontend/scripts/auth-contract-smoke.mjs` — 14 static checks (FE-P0A-02)
- `frontend/scripts/auth-retry-smoke.mjs` — 14 static checks (FE-P0A-03)
- `frontend/scripts/route-smoke-check.mjs` — route invariant checks

### playwright package — what it provides

The `playwright` package at v1.52.0 is `playwright-core` re-exported. It provides:
- Browser launch API (`chromium.launch()`, `firefox.launch()`, etc.)
- Page navigation and automation primitives
- **No test runner** (`test()`, `expect()`, `describe()`, `beforeEach()`)
- **No route interception in test context** (`page.route()` exists but requires a `Page` object from a launched browser session; no fixtures/config/spec runner)
- **No `playwright test` CLI** (that comes from `@playwright/test`)

### Confirmed absent capabilities

| Capability | Required For | Present? |
|---|---|---|
| `test()` / `expect()` from `@playwright/test` | Writing `.spec.ts` files | NO |
| `page.route()` in test fixtures | Mocking backend endpoints | NO |
| `playwright.config.ts` support | Configuring test runner | NO |
| `npx playwright test` or equivalent | Running tests | NO |
| Vite test plugin | In-browser unit tests | NO |
| MSW (Mock Service Worker) | API mocking without backend | NO |

---

## Why Continuing Is Unsafe

1. **Adding `@playwright/test` is a new dependency.** The task explicitly prohibits it: _"Do not add new testing dependency."_ Proceeding anyway would violate task scope.

2. **Writing `.spec.ts` files without `@playwright/test` would produce broken/unrunnable tests.** Dead test files would give false confidence and pollute the codebase.

3. **The `playwright` library alone cannot run route interception in a test context** without either:
   - A full browser lifecycle managed by `@playwright/test` fixtures; or
   - A bespoke test harness (which would itself be a new dependency or new infrastructure).

4. **The project has no `playwright.config.*`**, no `e2e/` directory, and no prior pattern to follow for E2E tests. Adding these without the test runner would create orphaned configuration.

5. **No other runtime test harness exists** that could run the required tests without adding a dependency.

---

## Options

### Option A — Add `@playwright/test` as a devDependency (requires user approval)

**Action:** Add `@playwright/test@^1.52.0` to devDependencies (matching existing `playwright` version).

**Why safe:**
- Playwright browser automation is already listed — adding the test runner is the natural complement.
- `@playwright/test` is a pure devDependency; it does not affect production bundle.
- The two packages are designed to work together at the same version.

**Why requires approval:**
- Explicitly prohibited by current task instructions.
- User must consciously authorize the new dependency.

**Estimated effort if approved:** 1 slice — add `@playwright/test`, create `playwright.config.ts`, create `e2e/auth-refresh-retry.spec.ts` with 3-4 test cases, verify with `npm run test:e2e:auth`.

### Option B — Extend static smoke scripts to cover additional invariants

**Action:** Extend `auth-retry-smoke.mjs` and/or `auth-contract-smoke.mjs` with additional static source-code checks that cover the gaps not currently checked.

**Gaps coverable statically:**
- Verify `REFRESH_EXCLUDED_PATHS` includes all four auth endpoints
- Verify `refreshInFlight` is reset to `null` after use (`.finally(() => { refreshInFlight = null; })`)
- Verify `refreshHandler` result is awaited (not fire-and-forget)
- Verify `retried: true` is only set on the inner `request()` call
- Verify no direct `fetch()` call exists in the retry path (must go through `request()`)

**Limitation:** Static checks cannot prove actual HTTP request/response behavior at runtime. The runtime gap remains.

### Option C — Write a Node.js integration test script using `playwright` headless browser

**Action:** Create `scripts/auth-retry-integration.mjs` that:
1. Launches a Chromium browser via the `playwright` library directly (no test runner)
2. Starts a mock HTTP server using Node.js `http` module
3. Runs through the auth scenarios manually
4. Exits with code 0 on pass, 1 on fail

**Why risky:**
- Requires starting a dev server or building a minimal HTML fixture — non-trivial without the test runner
- No structured assertion library or test isolation
- Increases maintenance burden significantly
- Equivalent to writing a custom test runner — not aligned with project conventions
- Browsers may not be installed in this environment (requires `npx playwright install chromium`)

**Not recommended** unless Options A and B are both rejected.

---

## Recommended Decision

**Option A is strongly recommended.**

The `playwright` devDependency already signals the team's intent to use Playwright for testing. The `@playwright/test` test runner is the standard companion package at the same version. Without it, the `playwright` devDependency is unused (no Playwright tests can be written or run).

The prohibition on "new dependencies" in the task was intended to prevent adding unrelated or heavyweight frameworks (React Query, Zustand, MSW, vitest, jest). Adding `@playwright/test` at the same version as `playwright` is a targeted, minimal addition that completes the existing testing intent.

**If Option A is approved:**

1. `npm install --save-dev @playwright/test@^1.52.0` (matches existing playwright version)
2. Create `playwright.config.ts` with minimal config (baseURL, testDir, webServer for Vite dev server)
3. Create `e2e/auth-refresh-retry.spec.ts` with 3 mandatory + 1 optional test
4. Add `"test:e2e:auth": "playwright test e2e/auth-refresh-retry.spec.ts"` to package.json
5. Run `npx playwright install chromium` for browser binaries

**If Option B only:**

Extend smoke scripts. Document runtime gap as accepted. Close with a scope note in the FE-P0A-04 partial report.

---

## Stop Condition Classification

| Condition | Status |
|---|---|
| Any mandatory file missing | NOT TRIGGERED (all 4 mandatory files present) |
| FE-P0A-02 / FE-P0A-03 source changes missing | NOT TRIGGERED (both present and verified) |
| Playwright unavailable and no runtime test harness exists | **TRIGGERED** (`@playwright/test` absent; no test runner present) |
| Implementing E2E requires new framework dependency | **TRIGGERED** (`@playwright/test` required; prohibited by task) |
| All other stop conditions | NOT TRIGGERED |
