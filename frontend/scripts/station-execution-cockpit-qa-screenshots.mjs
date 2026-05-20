/**
 * Station Execution Cockpit QA Screenshot Harness — FE-SE-COCKPIT-HERO-10
 *
 * Captures /station?operationId=<id> in the Mode B operator cockpit while
 * an operation is IN_PROGRESS, to demonstrate that the AllowedActionZone is
 * driven by backend `allowed_actions` (not by frontend status branching).
 *
 * Mocked API state:
 *   - /v1/auth/me                                   → returns operator
 *   - /v1/station/queue                             → 1 item, ownership=mine, has_open_session=true
 *   - /v1/station/sessions/current?station_id=...   → open session
 *   - /v1/station/operations/:id/detail             → IN_PROGRESS, qty 100/30,
 *                                                     allowed_actions=
 *                                                       [report_production, pause_execution,
 *                                                        start_downtime, complete_execution]
 *
 * Expected primary CTA: "Report Qty" (report_production wins precedence
 * because remainingQty=70 > 0).
 *
 * Output: docs/audit/fe-se-cockpit-hero-10/
 *
 * Visual QA only. Mocked API data. Does NOT prove backend truth, authorization,
 * E2E flow, or pilot golden-path coverage.
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
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "fe-se-cockpit-hero-10");

const VIEWPORT = { name: "desktop", width: 1440, height: 900 };

const OPERATION_ID = 42;
const STATION_ID = "STATION_01";
const SESSION_ID = "sess-qa-002";

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

const MOCK_SESSION_CURRENT = {
  session: {
    session_id: SESSION_ID,
    station_id: STATION_ID,
    status: "open",
    operator_user_id: "opr-001",
    equipment_id: "EQP-001",
    opened_at: "2026-05-12T08:00:00Z",
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
      operation_name: "Mix component A",
      wo_code: "WO-100",
      product_code: "PRD-001",
      product_name: "Widget A",
      sequence: 10,
      status: "IN_PROGRESS",
      closure_status: "OPEN",
      planned_start: "2026-05-12T07:30:00Z",
      planned_end: "2026-05-12T10:30:00Z",
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
  planned_start: "2026-05-12T07:30:00Z",
  planned_end: "2026-05-12T10:30:00Z",
  downtime_open: false,
  // Backend-truth: what the operator can do right now.
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

    // Silent fallback for any other call.
    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
}

async function assertPrimaryReportQty(page, label) {
  const primary = page.locator('[data-action-role="primary"]');
  await primary.waitFor({ state: "visible", timeout: 10000 });
  const dataAction = await primary.getAttribute("data-action");
  if (dataAction !== "report_production") {
    throw new Error(
      `[${label}]: primary CTA data-action='${dataAction}' but expected 'report_production' ` +
        `(allowed_actions includes report_production AND remainingQty=70 > 0).`,
    );
  }
  const text = (await primary.textContent())?.trim() ?? "";
  if (!/report/i.test(text)) {
    throw new Error(`[${label}]: primary CTA text '${text}' did not match /report/i`);
  }
  console.log(`PASS [${label}]: primary CTA = report_production ("${text}")`);
}

async function assertNoPartialBadge(page, label) {
  const partial = await page.$("[aria-label='Screen status: PARTIAL']");
  if (partial) {
    throw new Error(`[${label}]: PARTIAL badge still visible — MockWarningBanner not removed`);
  }
  console.log(`PASS [${label}]: no PARTIAL badge`);
}

async function assertConnectedBadge(page, label) {
  const badge = await page.$("[aria-label='Screen status: CONNECTED']");
  if (!badge) {
    throw new Error(`[${label}]: CONNECTED badge not found`);
  }
  console.log(`PASS [${label}]: CONNECTED badge visible`);
}

async function assertSecondaryActionsPresent(page, label) {
  const secondaries = page.locator('[data-action-role="secondary"]');
  const count = await secondaries.count();
  if (count < 3) {
    throw new Error(
      `[${label}]: expected >=3 secondary actions ` +
        `(complete_execution, pause_execution, start_downtime); got ${count}.`,
    );
  }
  const ids = [];
  for (let i = 0; i < count; i++) {
    ids.push(await secondaries.nth(i).getAttribute("data-action"));
  }
  const expected = ["complete_execution", "pause_execution", "start_downtime"];
  for (const want of expected) {
    if (!ids.includes(want)) {
      throw new Error(
        `[${label}]: secondary action '${want}' missing. Got: ${JSON.stringify(ids)}`,
      );
    }
  }
  console.log(`PASS [${label}]: secondary actions = ${JSON.stringify(ids)}`);
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
    console.log("Starting FE-SE-COCKPIT-HERO-10 cockpit QA screenshot run");
    console.log(
      "Visual QA only: mocked API. Does NOT prove backend truth, authorization, or E2E.",
    );

    const context = await browser.newContext({ viewport: { width: VIEWPORT.width, height: VIEWPORT.height } });
    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-cockpit-token");
    }, TOKEN_KEY);

    const page = await context.newPage();
    page.on("console", (msg) => console.log(`[page.${msg.type()}] ${msg.text()}`));
    page.on("pageerror", (err) => console.log(`[page.error] ${err.message}`));
    page.on("requestfailed", (req) => console.log(`[page.requestfailed] ${req.url()} ${req.failure()?.errorText}`));
    await installMocks(page, devServerUrl);

    // Land on root to set auth, then jump straight to the cockpit by operationId.
    await page.goto(devServerUrl, { waitUntil: "domcontentloaded", timeout: 30000 });
    console.log(`[harness] after root goto, url=${page.url()}`);
    await page.goto(`${devServerUrl}/station?operationId=${OPERATION_ID}`, {
      waitUntil: "networkidle",
      timeout: 30000,
    });
    console.log(`[harness] after station goto, url=${page.url()}`);
    try {
      await page.waitForSelector('[data-testid="allowed-action-zone"]', { timeout: 15000 });
      console.log("[harness] allowed-action-zone visible");
    } catch (err) {
      console.log(`[harness] allowed-action-zone NOT visible after 15s: ${err.message}`);
      const empty = await page.$('[data-testid="allowed-action-zone-empty"]');
      console.log(`[harness] empty banner present? ${empty ? "yes" : "no"}`);
      const fallbackPath = path.join(OUTPUT_DIR, `cockpit-DEBUG-${VIEWPORT.name}-${VIEWPORT.width}x${VIEWPORT.height}.png`);
      await page.screenshot({ path: fallbackPath, fullPage: true });
      console.log(`[harness] saved debug screenshot: ${path.relative(REPO_ROOT, fallbackPath)}`);
      throw err;
    }
    await page.waitForTimeout(400);

    const label = `in-progress/${VIEWPORT.name}`;
    await assertConnectedBadge(page, label);
    await assertNoPartialBadge(page, label);
    await assertPrimaryReportQty(page, label);
    await assertSecondaryActionsPresent(page, label);

    // Visibility gate: action zone must be in the viewport and rendered with
    // non-zero area. Just being in the DOM is not enough for review evidence.
    const zone = page.locator('[data-testid="allowed-action-zone"]');
    await zone.scrollIntoViewIfNeeded();
    await page.waitForTimeout(150);
    const zoneBox = await zone.boundingBox();
    if (!zoneBox || zoneBox.width < 200 || zoneBox.height < 80) {
      throw new Error(
        `[${label}]: allowed-action-zone box too small to be visibly rendered ` +
          `(box=${JSON.stringify(zoneBox)}). Expected width>=200 and height>=80.`,
      );
    }
    const primary = page.locator('[data-action-role="primary"]');
    const primaryBox = await primary.boundingBox();
    if (!primaryBox || primaryBox.height < 40) {
      throw new Error(
        `[${label}]: primary CTA not visibly rendered (box=${JSON.stringify(primaryBox)}).`,
      );
    }
    const inViewport = await primary.evaluate((el) => {
      const r = el.getBoundingClientRect();
      return (
        r.top >= 0 &&
        r.left >= 0 &&
        r.bottom <= window.innerHeight &&
        r.right <= window.innerWidth
      );
    });
    if (!inViewport) {
      throw new Error(`[${label}]: primary CTA is outside viewport bounds; layout fails the right-side action zone requirement.`);
    }
    console.log(
      `PASS [${label}]: action zone visibly rendered ` +
        `(zone=${Math.round(zoneBox.width)}x${Math.round(zoneBox.height)} at ` +
        `${Math.round(zoneBox.x)},${Math.round(zoneBox.y)}; primary in viewport).`,
    );

    // Full-page screenshot for full layout context.
    const outputFile = path.join(
      OUTPUT_DIR,
      `cockpit-in-progress-${VIEWPORT.name}-${VIEWPORT.width}x${VIEWPORT.height}.png`,
    );
    await page.screenshot({ path: outputFile, fullPage: true });
    console.log(`Saved: ${path.relative(REPO_ROOT, outputFile)}`);

    // Viewport-only screenshot proving the action zone is above the fold.
    const aboveFoldFile = path.join(
      OUTPUT_DIR,
      `cockpit-in-progress-${VIEWPORT.name}-${VIEWPORT.width}x${VIEWPORT.height}-viewport.png`,
    );
    await page.screenshot({ path: aboveFoldFile, fullPage: false });
    console.log(`Saved: ${path.relative(REPO_ROOT, aboveFoldFile)}`);

    // Tight crop of the action zone itself.
    const zoneFile = path.join(
      OUTPUT_DIR,
      `cockpit-in-progress-${VIEWPORT.name}-${VIEWPORT.width}x${VIEWPORT.height}-action-zone.png`,
    );
    await zone.screenshot({ path: zoneFile });
    console.log(`Saved: ${path.relative(REPO_ROOT, zoneFile)}`);

    await context.close();
    console.log("Completed FE-SE-COCKPIT-HERO-10 cockpit QA screenshot capture");
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
