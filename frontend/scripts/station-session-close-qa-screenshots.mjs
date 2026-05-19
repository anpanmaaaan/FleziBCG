/**
 * Station Session Close QA Screenshot Harness
 *
 * Captures /station-session close-session failure state:
 *   1. no-session-open — no active session, operator can open a station session
 *   2. close-session-failure — session open, close API returns STATION_SESSION_ACTIVE_EXECUTION (409)
 *      - Clicks "Close Session" to open confirm dialog
 *      - Clicks confirm button to attempt close
 *      - Waits for commandError banner to appear in CloseSessionPanel
 *   3. close-session-confirm — session open, close confirm dialog shown (no submit yet)
 *
 * Output: docs/audit/station-session-close-qa/
 *
 * Visual QA only. Mocked API data. Does not prove backend truth or E2E behavior.
 * Screenshots are generated review evidence and are not intended for commit.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

import http from "node:http";

import { chromium } from "playwright";

const TOKEN_KEY = "mes.auth.token";

async function isReachable(url) {
  return new Promise((resolve) => {
    const req = http.get(`${url}/`, (res) => { res.resume(); resolve(true); });
    req.setTimeout(1500, () => { req.destroy(); resolve(false); });
    req.on("error", () => resolve(false));
  });
}

// Auto-detect dev server port: check arg, then 5173, then 5174.
async function resolveDevServerUrl() {
  const argPort = process.argv[2];
  if (argPort) {
    const explicitUrl = `http://localhost:${argPort}`;
    return (await isReachable(explicitUrl)) ? explicitUrl : null;
  }

  for (const port of [5173, 5174]) {
    const url = `http://localhost:${port}`;
    if (await isReachable(url)) return url;
  }
  return null;
}

async function waitForDevServer(url, timeoutMs = 30000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await isReachable(url)) return true;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return false;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const FRONTEND_ROOT = path.resolve(__dirname, "..");
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "station-session-close-qa");

async function resolveOrStartDevServer() {
  const existingUrl = await resolveDevServerUrl();
  if (existingUrl) {
    return { devServerUrl: existingUrl, devServerProcess: null };
  }

  const viteBin = path.join(FRONTEND_ROOT, "node_modules", "vite", "bin", "vite.js");
  const devServerProcess = spawn(process.execPath, [viteBin, "--host", "127.0.0.1"], {
    cwd: FRONTEND_ROOT,
    stdio: "ignore",
    windowsHide: true,
  });

  const devServerUrl = "http://localhost:5173";
  if (await waitForDevServer(devServerUrl)) {
    return { devServerUrl, devServerProcess };
  }

  devServerProcess.kill();
  throw new Error("dev server not reachable and auto-start did not become ready on port 5173");
}

async function stopDevServer(devServerProcess) {
  if (!devServerProcess || devServerProcess.exitCode !== null) {
    return;
  }

  await new Promise((resolve) => {
    const timeout = setTimeout(resolve, 3000);
    devServerProcess.once("exit", () => {
      clearTimeout(timeout);
      resolve();
    });
    devServerProcess.kill();
  });
}

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
  context: { date: "2026-05-18", shift: "DAY" },
  workOrders: { total: 3, inProgress: 1, completed: 2, blocked: 0 },
  operations: { total: 6, running: 1, paused: 0, completed: 4, blocked: 1 },
  alerts: { total: 0, critical: 0, warning: 0 },
};

const MOCK_SESSION_OPEN = {
  session: {
    session_id: "sess-qa-close-001",
    station_id: "STATION_01",
    status: "OPEN",
    operator_user_id: "opr-001",
    equipment_id: "EQP-001",
    opened_at: "2026-05-18T08:00:00Z",
    closed_at: null,
  },
};

const MOCK_SESSION_NONE = {
  session: null,
};

const MOCK_OPENED_SESSION = {
  session_id: "sess-qa-open-001",
  tenant_id: "default",
  station_id: "STATION_01",
  status: "OPEN",
  operator_user_id: "opr-001",
  equipment_id: null,
  opened_at: "2026-05-18T08:05:00Z",
  closed_at: null,
};

/** Backend error response for STATION_SESSION_ACTIVE_EXECUTION */
const CLOSE_FAILURE_RESPONSE = {
  code: "STATION_SESSION_ACTIVE_EXECUTION",
  detail: "STATION_SESSION_ACTIVE_EXECUTION",
};

function screenshotPath(name, viewport) {
  return path.join(OUTPUT_DIR, `${name}-${viewport.name}-${viewport.width}x${viewport.height}.png`);
}

function isHtml(pathname) {
  return pathname === "/" || pathname.startsWith("/station") || pathname.startsWith("/login") || pathname.startsWith("/dashboard");
}

/**
 * Install API mocks. closeSessionShouldFail controls whether POST .../close returns 409.
 */
async function installMocks(page, sessionResponse, devServerUrl, { closeSessionShouldFail = false } = {}) {
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

    if (url.match(/\/v1\/station\/sessions$/) && method === "POST") {
      return json(MOCK_OPENED_SESSION);
    }

    // Mock close session endpoint
    if (url.match(/\/v1\/station\/sessions\/[^/]+\/close$/) && method === "POST") {
      if (closeSessionShouldFail) {
        return json(CLOSE_FAILURE_RESPONSE, 409);
      }
      // Successful close: return session with status=closed
      return json({
        ...sessionResponse.session,
        status: "CLOSED",
        closed_at: "2026-05-18T09:00:00Z",
      });
    }

    // Absorb any other API calls silently
    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
}

// --- Assertions ---

const assertConnectedBadge = async (page, state, viewport) => {
  const badge = await page.$("[aria-label='Screen status: CONNECTED']");
  if (!badge) {
    throw new Error(`[${state}/${viewport}]: CONNECTED badge not found`);
  }
  console.log(`PASS [${state}/${viewport}]: CONNECTED badge visible`);
};

const assertCloseSessionPanelVisible = async (page, state, viewport) => {
  // CloseSessionPanel renders h2 with endSession.title = "End Session / Handoff"
  const heading = await page.$("h2");
  let found = false;
  const headings = await page.$$("h2");
  for (const h of headings) {
    const text = await h.textContent();
    if (text && text.includes("End Session")) {
      found = true;
      break;
    }
  }
  if (!found) {
    throw new Error(`[${state}/${viewport}]: CloseSessionPanel "End Session / Handoff" heading not found`);
  }
  console.log(`PASS [${state}/${viewport}]: CloseSessionPanel heading visible`);
};

const assertCloseSessionErrorBannerVisible = async (page, state, viewport) => {
  // commandError banner has role="alert" and contains "Session close blocked"
  const alert = await page.$("[role='alert']");
  if (!alert) {
    throw new Error(`[${state}/${viewport}]: No [role="alert"] found — commandError banner not rendered in CloseSessionPanel`);
  }
  const alertText = await alert.textContent();
  if (!alertText || !alertText.includes("Session close blocked")) {
    throw new Error(
      `[${state}/${viewport}]: Alert text does not contain "Session close blocked". Got: "${alertText?.slice(0, 100)}"`
    );
  }
  console.log(`PASS [${state}/${viewport}]: commandError banner visible with "Session close blocked" text`);
};

const assertCloseConfirmButtonsVisible = async (page, state, viewport) => {
  // After showCloseConfirm=true: "Close Session" and "Cancel" buttons visible
  const cancelBtn = await page.$("button:has-text('Cancel')");
  if (!cancelBtn) {
    throw new Error(`[${state}/${viewport}]: "Cancel" button not found — close confirm dialog not shown`);
  }
  console.log(`PASS [${state}/${viewport}]: Close confirm buttons visible (Cancel button found)`);
};

const assertOpenSessionActionVisible = async (page, state, viewport) => {
  const openBtn = page.getByRole("button", { name: "Open session" }).first();
  await openBtn.waitFor({ state: "visible", timeout: 10000 });
  if (!(await openBtn.isEnabled())) {
    throw new Error(`[${state}/${viewport}]: "Open session" button is visible but disabled`);
  }
  console.log(`PASS [${state}/${viewport}]: Open session action visible and enabled`);
};

const assertOpenedSessionVisible = async (page, state, viewport) => {
  const sessionText = await page.getByText("#sess-qa-open-001").first();
  await sessionText.waitFor({ state: "visible", timeout: 10000 });
  const closePanelHeading = await page.getByRole("heading", { name: /End Session/i }).first();
  await closePanelHeading.waitFor({ state: "visible", timeout: 10000 });
  console.log(`PASS [${state}/${viewport}]: Opened session and close handoff panel visible`);
};

// --- State capture functions ---

async function captureCloseFailureState(browser, devServerUrl) {
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-station-session-close-token");
    }, TOKEN_KEY);

    const page = await context.newPage();

    // First install mocks with closeSessionShouldFail=true
    await installMocks(page, MOCK_SESSION_OPEN, devServerUrl, { closeSessionShouldFail: true });

    // Navigate to root first to ensure auth token is set
    await page.goto(devServerUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForURL((url) => isHtml(url.pathname), { timeout: 30000 });

    // Navigate to station-session with open session
    await page.goto(`${devServerUrl}/station-session?stationId=STATION_01`, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForSelector("main, h1, body", { timeout: 15000 });
    await page.waitForTimeout(500);

    // Click "Close Session" button (the red outlined one — before confirm is shown)
    // This is the bottom button in CloseSessionPanel: stationSession.action.closeSession = "Close Session"
    const closeBtn = page.getByRole("button", { name: "Close Session" }).first();
    await closeBtn.waitFor({ state: "visible", timeout: 10000 });
    await closeBtn.click();
    await page.waitForTimeout(300);

    // Now confirm buttons should be visible: "Close Session" + "Cancel"
    // Click the confirm "Close Session" button to trigger the actual API call
    const confirmCloseBtn = page.getByRole("button", { name: "Close Session" }).first();
    await confirmCloseBtn.waitFor({ state: "visible", timeout: 5000 });
    await confirmCloseBtn.click();

    // Wait for commandError banner to appear
    await page.waitForSelector("[role='alert']", { timeout: 10000 });
    await page.waitForTimeout(400);

    // Run assertions
    const state = "close-session-failure";
    for (const assertion of [
      assertConnectedBadge,
      assertCloseSessionPanelVisible,
      assertCloseSessionErrorBannerVisible,
      assertCloseConfirmButtonsVisible,
    ]) {
      await assertion(page, state, viewport.name);
    }

    const outputFile = screenshotPath(state, viewport);
    await page.screenshot({ path: outputFile, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, outputFile)}`);

    await context.close();
  }
}

async function captureNoSessionOpenState(browser, devServerUrl) {
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-station-session-close-token");
    }, TOKEN_KEY);

    const page = await context.newPage();
    await installMocks(page, MOCK_SESSION_NONE, devServerUrl);

    await page.goto(devServerUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForURL((url) => isHtml(url.pathname), { timeout: 30000 });

    await page.goto(`${devServerUrl}/station-session?stationId=STATION_01`, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForSelector("main, h1, body", { timeout: 15000 });
    await page.waitForTimeout(500);

    const state = "no-session-open";
    await assertConnectedBadge(page, state, viewport.name);
    await assertOpenSessionActionVisible(page, state, viewport.name);

    await page.getByRole("button", { name: "Open session" }).first().click();
    await assertOpenedSessionVisible(page, state, viewport.name);

    const outputFile = screenshotPath(state, viewport);
    await page.screenshot({ path: outputFile, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, outputFile)}`);

    await context.close();
  }
}

async function captureCloseConfirmState(browser, devServerUrl) {
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-station-session-close-token");
    }, TOKEN_KEY);

    const page = await context.newPage();
    await installMocks(page, MOCK_SESSION_OPEN, devServerUrl);

    await page.goto(devServerUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForURL((url) => isHtml(url.pathname), { timeout: 30000 });

    await page.goto(`${devServerUrl}/station-session?stationId=STATION_01`, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForSelector("main, h1, body", { timeout: 15000 });
    await page.waitForTimeout(500);

    // Click "Close Session" to show the confirm dialog
    const closeBtn = page.getByRole("button", { name: "Close Session" }).first();
    await closeBtn.waitFor({ state: "visible", timeout: 10000 });
    await closeBtn.click();
    await page.waitForTimeout(400);

    const state = "close-session-confirm";
    for (const assertion of [
      assertConnectedBadge,
      assertCloseSessionPanelVisible,
      assertCloseConfirmButtonsVisible,
    ]) {
      await assertion(page, state, viewport.name);
    }

    const outputFile = screenshotPath(state, viewport);
    await page.screenshot({ path: outputFile, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, outputFile)}`);

    await context.close();
  }
}

async function main() {
  const { devServerUrl, devServerProcess } = await resolveOrStartDevServer();
  console.log(`Using dev server at ${devServerUrl}`);

  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  let browser = null;

  try {
    browser = await chromium.launch({ headless: true });
    console.log("Starting Station Session Close QA screenshot run");
    console.log("Visual QA only: mocked API. Does not prove backend truth, authorization, or E2E coverage.");
    console.log("");

    // State 1: no active session can open a session
    await captureNoSessionOpenState(browser, devServerUrl);

    // State 2: close confirm dialog (before submit)
    await captureCloseConfirmState(browser, devServerUrl);

    // State 3: close failure (after submit, STATION_SESSION_ACTIVE_EXECUTION error)
    await captureCloseFailureState(browser, devServerUrl);

    console.log("");
    console.log("Completed Station Session Close QA screenshot capture");
    console.log(`Screenshots saved to: docs/audit/station-session-close-qa/`);
  } finally {
    if (browser) {
      await browser.close();
    }
    await stopDevServer(devServerProcess);
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
