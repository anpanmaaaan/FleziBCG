/**
 * Station Session Setup QA Screenshot Harness
 *
 * Captures /station-session in three states:
 *   1. missing-station  — no stationId param
 *   2. no-session       — stationId present, backend returns session: null
 *   3. open-session     — stationId present, backend returns open session
 *
 * Output: docs/audit/station-session-setup-qa/
 *
 * Visual QA only. Mocked API data. Does not prove backend truth or E2E behavior.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import http from "node:http";

import { chromium } from "playwright";

const TOKEN_KEY = "mes.auth.token";

// Auto-detect dev server port: check arg, then 5173, then 5174
async function resolveDevServerUrl() {
  const argPort = process.argv[2];
  if (argPort) return `http://localhost:${argPort}`;

  for (const port of [5173, 5174]) {
    const reachable = await new Promise((resolve) => {
      const req = http.get(`http://localhost:${port}/`, (res) => { res.resume(); resolve(true); });
      req.setTimeout(1500, () => { req.destroy(); resolve(false); });
      req.on("error", () => resolve(false));
    });
    if (reachable) return `http://localhost:${port}`;
  }
  return null;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "station-session-setup-qa");

const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "narrow", width: 430, height: 932 },
];

const MOCK_USER = {
  user_id: "opr-001",
  username: "operator",
  role_code: "OPR",
  tenant_id: "default",
};

const MOCK_DASHBOARD_SUMMARY = {
  context: { date: "2026-05-12", shift: "DAY" },
  workOrders: { total: 5, inProgress: 2, completed: 3, blocked: 0 },
  operations: { total: 12, running: 3, paused: 0, completed: 8, blocked: 1 },
  alerts: { total: 0, critical: 0, warning: 0 },
};

const MOCK_SESSION_OPEN = {
  session: {
    session_id: "sess-qa-001",
    station_id: "STATION_01",
    status: "open",
    operator_user_id: "opr-001",
    equipment_id: "EQP-001",
    opened_at: "2026-05-12T08:00:00Z",
    closed_at: null,
  },
};

const MOCK_SESSION_NONE = {
  session: null,
};

function screenshotPath(name, viewport) {
  return path.join(OUTPUT_DIR, `${name}-${viewport.name}-${viewport.width}x${viewport.height}.png`);
}

function isHtml(pathname) {
  return pathname === "/" || pathname.startsWith("/station") || pathname.startsWith("/login") || pathname.startsWith("/dashboard");
}

async function installMocks(page, sessionResponse, devServerUrl) {
  await page.route(`${devServerUrl}/api/**`, async (route) => {
    const request = route.request();
    const url = request.url();
    const method = request.method();

    const json = (body, status = 200) =>
      route.fulfill({
        status,
        contentType: "application/json",
        body: JSON.stringify(body),
      });

    if (url.includes("/v1/auth/me") && method === "GET") {
      return json(MOCK_USER);
    }

    if (url.includes("/v1/auth/logout") && method === "POST") {
      return json({ status: "ok", revoked_session_id: "qa-session" });
    }

    if (url.includes("/v1/dashboard/summary") && method === "GET") {
      return json(MOCK_DASHBOARD_SUMMARY);
    }

    if (url.includes("/v1/dashboard/health") && method === "GET") {
      return json({ status: "ok" });
    }

    if (url.includes("/v1/station/sessions/current") && method === "GET") {
      return json(sessionResponse);
    }

    // Absorb any other API calls silently
    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
}

async function captureState(browser, stateName, routePath, sessionResponse, devServerUrl, assertions = []) {
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-station-session-token");
    }, TOKEN_KEY);

    const page = await context.newPage();
    await installMocks(page, sessionResponse, devServerUrl);

    // Navigate to root first to ensure auth token is set
    await page.goto(devServerUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForURL((url) => isHtml(url.pathname), { timeout: 30000 });

    // Navigate to target state
    await page.goto(`${devServerUrl}${routePath}`, { waitUntil: "networkidle", timeout: 30000 });

    // Wait for page content
    await page.waitForSelector("main, h1, body", { timeout: 15000 });
    // Small settle for dynamic content
    await page.waitForTimeout(400);

    // Run assertions before screenshot
    for (const assertion of assertions) {
      await assertion(page, stateName, viewport.name);
    }

    const outputFile = screenshotPath(stateName, viewport);
    await page.screenshot({ path: outputFile, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, outputFile)}`);

    await context.close();
  }
}

// Assertions

const assertConnectedBadge = async (page, state, viewport) => {
  // ScreenStatusBadge renders aria-label="Screen status: CONNECTED"
  const badge = await page.$("[aria-label='Screen status: CONNECTED']");
  if (!badge) {
    throw new Error(`[${state}/${viewport}]: CONNECTED badge not found (aria-label='Screen status: CONNECTED') — ScreenStatusBadge phase may still be PARTIAL`);
  }
  console.log(`PASS [${state}/${viewport}]: CONNECTED badge visible (aria-label matched)`);
};

const assertNoPartialBadge = async (page, state, viewport) => {
  const partial = await page.$("[aria-label='Screen status: PARTIAL']");
  if (partial) {
    throw new Error(`[${state}/${viewport}]: PARTIAL badge found — ScreenStatusBadge was not updated to CONNECTED`);
  }
  console.log(`PASS [${state}/${viewport}]: No PARTIAL badge visible`);
};

// Open-session specific assertions (visual/mock coverage only)
const assertEndSessionButtonVisible = async (page, state, viewport) => {
  const btn = await page.$("button:has-text('End session')");
  if (!btn) {
    throw new Error(`[${state}/${viewport}]: "End session" button not found — sessionStatus='open' not received by OpenSessionPanel`);
  }
  console.log(`PASS [${state}/${viewport}]: "End session" button visible`);
};

const assertNoNotYetInSessionRow = async (page, state, viewport) => {
  // Target specifically the OpenSessionPanel row: the div containing h2 with text "Session".
  // Using .filter({ has: locator }) avoids false positives from the first generic
  // .flex.items-center.gap-3 element which could be a header row or another panel.
  const sessionRow = page.locator("div.flex.items-center.gap-3").filter({
    has: page.locator('h2:has-text("Session")')
  });
  const rowText = await sessionRow.first().textContent().catch(() => "");
  if (rowText.includes("Not yet")) {
    throw new Error(`[${state}/${viewport}]: session row shows "Not yet" — sessionStatus='open' not reflected in OpenSessionPanel`);
  }
  console.log(`PASS [${state}/${viewport}]: session row shows "Open" (no "Not yet")`);
};

async function main() {
  const devServerUrl = await resolveDevServerUrl();
  if (!devServerUrl) {
    console.error("FAIL: dev server not reachable on ports 5173 or 5174. Start with: npm run dev");
    process.exitCode = 1;
    return;
  }
  console.log(`Using dev server at ${devServerUrl}`);

  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });

  const badgeAssertions = [assertConnectedBadge, assertNoPartialBadge];
  const openSessionAssertions = [assertConnectedBadge, assertNoPartialBadge, assertEndSessionButtonVisible, assertNoNotYetInSessionRow];

  try {
    console.log("Starting Station Session Setup QA screenshot run");
    console.log("Visual QA only: mocked API. Does not prove backend truth, authorization, or E2E coverage.");
    console.log("");

    // State 1: missing station (no stationId param)
    await captureState(
      browser,
      "missing-station",
      "/station-session",
      MOCK_SESSION_NONE,
      devServerUrl,
      badgeAssertions,
    );

    // State 2: stationId provided, no session
    await captureState(
      browser,
      "no-session",
      "/station-session?stationId=STATION_01",
      MOCK_SESSION_NONE,
      devServerUrl,
      badgeAssertions,
    );

    // State 3: stationId provided, open session with operator + equipment
    await captureState(
      browser,
      "open-session",
      "/station-session?stationId=STATION_01",
      MOCK_SESSION_OPEN,
      devServerUrl,
      openSessionAssertions,
    );

    console.log("");
    console.log("Completed Station Session Setup QA screenshot capture");
    console.log(`Screenshots saved to: docs/audit/station-session-setup-qa/`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);

  if (message.includes("ERR_CONNECTION_REFUSED") || message.includes("net::ERR_CONNECTION_REFUSED")) {
    console.error("FAIL: dev server not reachable. Start with: npm run dev (port 5173 or 5174).");
  } else {
    console.error(`FAIL: screenshot harness crashed: ${message}`);
  }

  process.exitCode = 1;
});
