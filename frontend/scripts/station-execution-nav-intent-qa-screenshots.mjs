/**
 * Station Execution Navigation Intent QA Harness — FE-SE-NAV-INTENT-11
 *
 * Verifies that /station respects the Navigation Intent And Explicit Selection
 * Gate: the default landing must NOT auto-select the first queue item, must
 * NOT inject an operationId into the URL, and must NOT render the cockpit /
 * AllowedActionZone. Deep links and explicit user gestures must still work.
 *
 * Three scenarios:
 *   A. default /station with queue items
 *      - URL has NO operationId
 *      - AllowedActionZone is NOT visible
 *      - queue selection surface is visible with at least one queue card
 *   B. explicit deep link /station?operationId=42
 *      - operation detail loads
 *      - AllowedActionZone IS visible
 *   C. explicit click on first queue row from scenario A
 *      - URL gains operationId
 *      - AllowedActionZone becomes visible
 *
 * Output: docs/audit/fe-se-nav-intent-11/
 *
 * Visual QA only. Mocked API data. Does NOT prove backend truth,
 * authorization, E2E flow, or pilot golden-path coverage.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import http from "node:http";

import { chromium } from "playwright";

const TOKEN_KEY = "mes.auth.token";

async function resolveDevServerUrl() {
  const argPort = process.argv[2];
  if (argPort) return `http://localhost:${argPort}`;
  for (const port of [5173, 5174]) {
    const reachable = await new Promise((resolve) => {
      const req = http.get(`http://localhost:${port}/`, (res) => {
        res.resume();
        resolve(true);
      });
      req.setTimeout(1500, () => {
        req.destroy();
        resolve(false);
      });
      req.on("error", () => resolve(false));
    });
    if (reachable) return `http://localhost:${port}`;
  }
  return null;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "fe-se-nav-intent-11");

const VIEWPORT = { name: "desktop", width: 1440, height: 900 };

const OPERATION_ID = 42;
const STATION_ID = "STATION_01";
const SESSION_ID = "sess-qa-nav-11";

const MOCK_USER = {
  user_id: "opr-001",
  username: "operator",
  role_code: "OPR",
  tenant_id: "default",
};

const MOCK_DASHBOARD_SUMMARY = {
  context: { date: "2026-05-20", shift: "DAY" },
  workOrders: { total: 5, inProgress: 2, completed: 3, blocked: 0 },
  operations: { total: 12, running: 3, paused: 0, completed: 8, blocked: 1 },
  alerts: { total: 0, critical: 0, warning: 0 },
};

const MOCK_SESSION_CURRENT = {
  session: {
    session_id: SESSION_ID,
    station_id: STATION_ID,
    status: "open",
    operator_user_id: "opr-001",
    equipment_id: "EQP-001",
    opened_at: "2026-05-20T08:00:00Z",
    closed_at: null,
  },
};

const MOCK_QUEUE = {
  station_id: STATION_ID,
  station_scope_value: "ST-01",
  station_scope_type: "station",
  items: [
    {
      operation_id: OPERATION_ID,
      operation_code: "OP-042",
      operation_number: "OP-042",
      operation_name: "Mix component A",
      name: "Mix component A",
      wo_code: "WO-100",
      product_code: "PRD-001",
      product_name: "Widget A",
      sequence: 10,
      status: "IN_PROGRESS",
      closure_status: "OPEN",
      planned_start: "2026-05-20T07:30:00Z",
      planned_end: "2026-05-20T10:30:00Z",
      quantity: 100,
      completed_qty: 30,
      good_qty: 28,
      scrap_qty: 2,
      uom_code: "EA",
      station_id: STATION_ID,
      station_code: "ST-01",
      station_name: "Mix Station 01",
      ownership: {
        owner_state: "mine",
        has_open_session: true,
        session_id: SESSION_ID,
        operator_user_id: "opr-001",
      },
    },
    {
      operation_id: 43,
      operation_code: "OP-043",
      operation_number: "OP-043",
      operation_name: "Mix component B",
      name: "Mix component B",
      wo_code: "WO-100",
      product_code: "PRD-002",
      product_name: "Widget B",
      sequence: 20,
      status: "PLANNED",
      closure_status: "OPEN",
      planned_start: "2026-05-20T10:30:00Z",
      planned_end: "2026-05-20T12:00:00Z",
      quantity: 50,
      completed_qty: 0,
      good_qty: 0,
      scrap_qty: 0,
      uom_code: "EA",
      station_id: STATION_ID,
      station_code: "ST-01",
      station_name: "Mix Station 01",
      ownership: {
        owner_state: "none",
        has_open_session: false,
        session_id: null,
        operator_user_id: null,
      },
    },
  ],
};

const MOCK_OPERATION_DETAIL = {
  id: OPERATION_ID,
  code: "OP-042",
  name: "Mix component A",
  wo_id: 100,
  wo_code: "WO-100",
  status: "IN_PROGRESS",
  closure_status: "OPEN",
  product_code: "PRD-001",
  product_name: "Widget A",
  uom_code: "EA",
  quantity: 100,
  completed_qty: 30,
  good_qty: 28,
  scrap_qty: 2,
  sequence: 10,
  station_id: STATION_ID,
  station_code: "ST-01",
  station_name: "Mix Station 01",
  planned_start: "2026-05-20T07:30:00Z",
  planned_end: "2026-05-20T10:30:00Z",
  downtime_open: false,
  allowed_actions: [
    "report_production",
    "pause_execution",
    "start_downtime",
    "complete_execution",
  ],
  routing_operation_code: "RO-042",
};

async function installMocks(page, devServerUrl) {
  await page.route(`${devServerUrl}/api/**`, async (route) => {
    const request = route.request();
    const url = request.url();
    const method = request.method();
    const json = (body, status = 200) => {
      console.log(`[mock] ${method} ${url} -> ${status}`);
      return route.fulfill({
        status,
        contentType: "application/json",
        body: JSON.stringify(body),
      });
    };

    if (url.includes("/v1/auth/me") && method === "GET") return json(MOCK_USER);
    if (url.includes("/v1/auth/logout") && method === "POST")
      return json({ status: "ok", revoked_session_id: "qa-session" });

    if (url.includes("/v1/dashboard/summary") && method === "GET") return json(MOCK_DASHBOARD_SUMMARY);
    if (url.includes("/v1/dashboard/health") && method === "GET") return json({ status: "ok" });

    if (url.includes(`/v1/station/queue/${OPERATION_ID}/detail`) && method === "GET")
      return json(MOCK_OPERATION_DETAIL);
    if (url.includes("/v1/station/queue") && method === "GET") return json(MOCK_QUEUE);
    if (url.includes("/v1/station/sessions/current") && method === "GET") return json(MOCK_SESSION_CURRENT);
    if (url.includes(`/v1/station/operations/${OPERATION_ID}/detail`) && method === "GET")
      return json(MOCK_OPERATION_DETAIL);

    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
}

function urlHasOperationId(currentUrl) {
  const u = new URL(currentUrl);
  return u.searchParams.has("operationId");
}

async function assertCockpitNotVisible(page, label) {
  const zone = await page.$('[data-testid="allowed-action-zone"]');
  if (zone) {
    throw new Error(
      `[${label}]: AllowedActionZone unexpectedly visible on landing. ` +
        `Landing must remain queue/selection mode until explicit selection.`,
    );
  }
  console.log(`PASS [${label}]: AllowedActionZone NOT rendered (queue/selection mode).`);
}

async function assertCockpitVisible(page, label) {
  await page.waitForSelector('[data-testid="allowed-action-zone"]', { timeout: 15000 });
  console.log(`PASS [${label}]: AllowedActionZone visible.`);
}

async function assertNoOperationIdInUrl(page, label) {
  if (urlHasOperationId(page.url())) {
    throw new Error(
      `[${label}]: URL '${page.url()}' contains operationId; initial landing must not ` +
        `inject an entity id from the first queue item.`,
    );
  }
  console.log(`PASS [${label}]: URL has no operationId (${page.url()}).`);
}

async function assertOperationIdInUrl(page, label, expectedId) {
  const u = new URL(page.url());
  const actual = u.searchParams.get("operationId");
  if (String(actual) !== String(expectedId)) {
    throw new Error(
      `[${label}]: URL operationId=${actual} but expected ${expectedId}. URL=${page.url()}`,
    );
  }
  console.log(`PASS [${label}]: URL operationId=${expectedId}.`);
}

async function assertQueueRendered(page, label) {
  const card = page.locator('button:has-text("Mix component A")').first();
  await card.waitFor({ state: "visible", timeout: 10000 });
  console.log(`PASS [${label}]: queue selection surface rendered (queue card visible).`);
  return card;
}

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
  try {
    console.log("Starting FE-SE-NAV-INTENT-11 navigation intent QA harness");
    console.log("Visual QA only: mocked API. Does NOT prove backend truth or E2E.");

    const context = await browser.newContext({
      viewport: { width: VIEWPORT.width, height: VIEWPORT.height },
    });
    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-nav-intent-token");
    }, TOKEN_KEY);

    const page = await context.newPage();
    page.on("console", (msg) => console.log(`[page.${msg.type()}] ${msg.text()}`));
    page.on("pageerror", (err) => console.log(`[page.error] ${err.message}`));
    page.on("requestfailed", (req) =>
      console.log(`[page.requestfailed] ${req.url()} ${req.failure()?.errorText}`),
    );
    await installMocks(page, devServerUrl);

    // ── Scenario A: default /station landing ────────────────────────────────
    await page.goto(devServerUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.goto(`${devServerUrl}/station`, { waitUntil: "networkidle", timeout: 30000 });
    // Give the page a beat to settle in case any auto-select code paths
    // would have run.
    await page.waitForTimeout(800);

    const labelA = "A/landing-default";
    await assertQueueRendered(page, labelA);
    await assertNoOperationIdInUrl(page, labelA);
    await assertCockpitNotVisible(page, labelA);

    const screenshotA = path.join(OUTPUT_DIR, "A-station-landing-no-autoselect.png");
    await page.screenshot({ path: screenshotA, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, screenshotA)}`);

    // ── Scenario B: explicit deep link ─────────────────────────────────────
    await page.goto(`${devServerUrl}/station?operationId=${OPERATION_ID}`, {
      waitUntil: "networkidle",
      timeout: 30000,
    });
    const labelB = "B/deep-link";
    await assertCockpitVisible(page, labelB);
    await assertOperationIdInUrl(page, labelB, OPERATION_ID);
    const screenshotB = path.join(OUTPUT_DIR, "B-station-deep-link-cockpit.png");
    await page.screenshot({ path: screenshotB, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, screenshotB)}`);

    // ── Scenario C: explicit queue row selection from landing ──────────────
    await page.goto(`${devServerUrl}/station`, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(500);
    const labelC = "C/explicit-selection";
    await assertNoOperationIdInUrl(page, `${labelC}/pre-click`);
    await assertCockpitNotVisible(page, `${labelC}/pre-click`);

    const card = await assertQueueRendered(page, `${labelC}/pre-click`);
    await card.click();
    await page.waitForSelector('[data-testid="allowed-action-zone"]', { timeout: 15000 });
    await assertOperationIdInUrl(page, `${labelC}/post-click`, OPERATION_ID);
    await assertCockpitVisible(page, `${labelC}/post-click`);
    const screenshotC = path.join(OUTPUT_DIR, "C-station-explicit-selection-cockpit.png");
    await page.screenshot({ path: screenshotC, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, screenshotC)}`);

    await context.close();
    console.log("Completed FE-SE-NAV-INTENT-11 navigation intent QA harness");
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  if (message.includes("ERR_CONNECTION_REFUSED")) {
    console.error("FAIL: dev server not reachable. Start with: npm run dev");
  } else {
    console.error(`FAIL: ${message}`);
  }
  process.exitCode = 1;
});
