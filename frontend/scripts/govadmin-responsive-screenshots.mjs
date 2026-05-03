/**
 * FE-GOVADMIN-02 — Governance/Admin Responsive Visual QA Screenshot Harness
 *
 * Captures all 9 governance/admin routes at 4 viewports.
 * Uses mock auth token only — no backend mutations performed.
 * QA only: screenshots do not represent backend truth.
 *
 * Usage:
 *   node scripts/govadmin-responsive-screenshots.mjs
 *
 * Requires dev server running at http://localhost:5173
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const DEV_SERVER_URL = "http://localhost:5173";
const TOKEN_KEY = "mes.auth.token";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "fe-govadmin-02-runtime-qa");

const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "laptop", width: 1180, height: 820 },
  { name: "tablet", width: 820, height: 1180 },
  { name: "mobile", width: 430, height: 932 },
];

const ROUTES = [
  { slug: "users", path: "/users" },
  { slug: "roles", path: "/roles" },
  { slug: "action-registry", path: "/action-registry" },
  { slug: "scope-assignments", path: "/scope-assignments" },
  { slug: "sessions", path: "/sessions" },
  { slug: "audit-log", path: "/audit-log" },
  { slug: "security-events", path: "/security-events" },
  { slug: "tenant-settings", path: "/tenant-settings" },
  { slug: "plant-hierarchy", path: "/plant-hierarchy" },
];

/** Mock auth token payload — UI QA only, not backend truth */
const MOCK_USER = {
  user_id: "adm-001",
  username: "qa_reviewer",
  role_code: "ADM",
  tenant_id: "default",
};

function screenshotPath(slug, viewport) {
  return path.join(OUTPUT_DIR, `${slug}-${viewport.name}.png`);
}

async function installQaMocks(page) {
  await page.route(`${DEV_SERVER_URL}/api/**`, async (route) => {
    const request = route.request();
    const url = request.url();

    const json = (body, status = 200) =>
      route.fulfill({
        status,
        contentType: "application/json",
        body: JSON.stringify(body),
      });

    if (url.includes("/v1/auth/me")) {
      return json(MOCK_USER);
    }

    // Allow all other requests to pass through (governance pages use mock data)
    return route.continue();
  });
}

async function captureRoute(browser, route) {
  const results = [];

  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });

    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-govadmin-token");
    }, TOKEN_KEY);

    const page = await context.newPage();
    await installQaMocks(page);

    try {
      // Navigate to root first (handles auth redirect)
      await page.goto(DEV_SERVER_URL, { waitUntil: "domcontentloaded", timeout: 20000 });

      // Navigate to target route
      await page.goto(`${DEV_SERVER_URL}${route.path}`, {
        waitUntil: "networkidle",
        timeout: 20000,
      });

      // Wait for content to be visible
      await page.waitForSelector("h1, [class*='GovernancePageShell'], main, body", { timeout: 10000 });

      // Brief settle time for any animations
      await page.waitForTimeout(300);

      const outputFile = screenshotPath(route.slug, viewport);
      await page.screenshot({ path: outputFile, fullPage: true });

      const relPath = path.relative(REPO_ROOT, outputFile);
      console.log(`  ✓ ${relPath}`);
      results.push({ viewport: viewport.name, status: "ok", file: relPath });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`  ✗ ${route.slug} @ ${viewport.name}: ${msg}`);
      results.push({ viewport: viewport.name, status: "error", error: msg });
    } finally {
      await context.close();
    }
  }

  return results;
}

async function main() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const allResults = {};

  try {
    console.log("FE-GOVADMIN-02 — Governance/Admin Responsive Screenshot QA");
    console.log(`Output: ${OUTPUT_DIR}`);
    console.log(`Routes: ${ROUTES.length}, Viewports: ${VIEWPORTS.length}`);
    console.log("---");

    for (const route of ROUTES) {
      console.log(`\n${route.slug} (${route.path})`);
      allResults[route.slug] = await captureRoute(browser, route);
    }

    console.log("\n--- Summary ---");
    let totalOk = 0;
    let totalErr = 0;
    for (const [slug, results] of Object.entries(allResults)) {
      const ok = results.filter((r) => r.status === "ok").length;
      const err = results.filter((r) => r.status === "error").length;
      totalOk += ok;
      totalErr += err;
      console.log(`  ${slug}: ${ok} ok, ${err} errors`);
    }
    console.log(`\nTotal: ${totalOk} screenshots captured, ${totalErr} errors`);

    // Write results JSON for report
    const resultFile = path.join(OUTPUT_DIR, "results.json");
    await fs.writeFile(resultFile, JSON.stringify(allResults, null, 2));
    console.log(`\nResults saved to: ${path.relative(REPO_ROOT, resultFile)}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);

  if (message.includes("ERR_CONNECTION_REFUSED") || message.includes("net::ERR_CONNECTION_REFUSED")) {
    console.error("FAIL: dev server is not reachable at http://localhost:5173. Start the frontend dev server first.");
  } else {
    console.error(`FAIL: screenshot harness crashed: ${message}`);
  }

  process.exitCode = 1;
});
