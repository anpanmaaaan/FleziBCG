import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright configuration — FleziBCG frontend.
 *
 * Chromium only for this slice.
 * The Vite dev server is started automatically if not already running.
 *
 * Test files live under ./e2e/
 *
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: "./e2e",

  // Stop after first failure in CI; run all in development.
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: "list",

  // Global timeout per test (30 s). Adjusted conservatively for auth flows.
  timeout: 30_000,

  use: {
    // Base URL for the Vite dev server.
    baseURL: "http://localhost:5173",

    // Collect trace on first retry only.
    trace: "on-first-retry",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
