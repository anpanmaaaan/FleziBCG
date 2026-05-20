/**
 * Station Execution Interrupted Mode QA Harness — FE-SE-INTERRUPTED-MODE-11
 * (hardened by FE-SE-INTERRUPTED-MODE-11-CORRECTION: asserts visible operator
 * guidance text and visible reporting-disabled reason text in addition to
 * severity, primary action, allowed/forbidden actions, and reporting testid)
 *
 * Verifies that the Mode B operator cockpit responds correctly to interrupted
 * states (PAUSED / BLOCKED / downtime_open):
 *
 *   1. PAUSED without downtime open
 *      - andon banner visible with severity=warning
 *      - primary action data-action = resume_execution
 *      - reporting input section data-testid = report-input-disabled
 *      - no forbidden action visible (only ids in backend allowed_actions)
 *   2. BLOCKED with downtime open
 *      - andon banner visible with severity=danger
 *      - primary action data-action = end_downtime
 *      - reporting input section data-testid = report-input-disabled
 *   3. PAUSED with downtime open (paused-with-downtime-open)
 *      - andon banner visible with severity=danger
 *      - primary action data-action = end_downtime
 *      - reporting input section data-testid = report-input-disabled
 *
 * Also re-asserts the FE-SE-NAV-INTENT-11 invariant: scenarios that drive the
 * cockpit do so via explicit deep link `?operationId=42`, not via implicit
 * first-item selection.
 *
 * Coverage: desktop (1440x900) and tablet (834x1112) viewports for the PAUSED
 * scenario (layout uses xl: column at 1280px+, so a narrower viewport proves
 * the andon banner still sits above the fold).
 *
 * Output: docs/audit/fe-se-interrupted-mode-11/
 *
 * Visual QA only. Mocked API data. Does NOT prove backend truth,
 * authorization, E2E flow, or pilot golden-path coverage. Backend still owns
 * action legality, command authorization, and state transitions.
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
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "fe-se-interrupted-mode-11");

const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "tablet", width: 834, height: 1112 },
];

const OPERATION_ID = 42;
const STATION_ID = "STATION_01";
const SESSION_ID = "sess-qa-interrupted-11";

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

function makeQueue() {
  return {
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
        status: "PAUSED",
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
    ],
  };
}

function baseOperationDetail() {
  return {
    id: OPERATION_ID,
    code: "OP-042",
    name: "Mix component A",
    wo_id: 100,
    wo_code: "WO-100",
    work_order_number: "WO-100",
    production_order_number: "PO-1000",
    status: "PAUSED",
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
    actual_start: "2026-05-20T07:35:00Z",
    actual_end: null,
    paused_total_ms: 5 * 60 * 1000,
    downtime_total_ms: 0,
    downtime_open: false,
    reopen_count: 0,
    routing_operation_code: "RO-042",
    allowed_actions: [],
  };
}

const SCENARIOS = [
  {
    id: "A-paused-no-downtime",
    label: "PAUSED / no downtime",
    viewport: "desktop",
    detailOverrides: {
      status: "PAUSED",
      downtime_open: false,
      // Backend allows resume + start_downtime + complete, no reporting.
      allowed_actions: ["resume_execution", "start_downtime", "complete_execution"],
    },
    expect: {
      andonSeverity: "warning",
      primaryAction: "resume_execution",
      reportingTestid: "report-input-disabled",
      allowedActionsIncluded: ["resume_execution", "start_downtime", "complete_execution"],
      forbiddenActions: ["pause_execution", "start_execution", "end_downtime", "report_production"],
      // FE-SE-INTERRUPTED-MODE-11-CORRECTION: assert visible operator guidance.
      bannerTextRegex: /resume/i,
      reportingTextRegex: /paused|resume/i,
    },
  },
  {
    id: "B-blocked-downtime-open",
    label: "BLOCKED / downtime_open",
    viewport: "desktop",
    detailOverrides: {
      status: "BLOCKED",
      downtime_open: true,
      paused_total_ms: 0,
      downtime_total_ms: 15 * 60 * 1000,
      allowed_actions: ["end_downtime"],
    },
    expect: {
      andonSeverity: "danger",
      primaryAction: "end_downtime",
      reportingTestid: "report-input-disabled",
      allowedActionsIncluded: ["end_downtime"],
      forbiddenActions: [
        "resume_execution",
        "pause_execution",
        "start_execution",
        "report_production",
        "complete_execution",
        "start_downtime",
      ],
      bannerTextRegex: /end.*downtime|open downtime/i,
      reportingTextRegex: /downtime|end downtime/i,
    },
  },
  {
    id: "C-paused-downtime-open",
    label: "PAUSED / downtime_open",
    viewport: "desktop",
    detailOverrides: {
      status: "PAUSED",
      downtime_open: true,
      paused_total_ms: 3 * 60 * 1000,
      downtime_total_ms: 7 * 60 * 1000,
      allowed_actions: ["end_downtime", "resume_execution"],
    },
    expect: {
      // Per spec: BLOCKED OR downtime_open => danger + end_downtime primary.
      andonSeverity: "danger",
      primaryAction: "end_downtime",
      reportingTestid: "report-input-disabled",
      allowedActionsIncluded: ["end_downtime", "resume_execution"],
      forbiddenActions: [
        "pause_execution",
        "start_execution",
        "report_production",
        "complete_execution",
        "start_downtime",
      ],
      bannerTextRegex: /end.*downtime|open downtime/i,
      reportingTextRegex: /downtime|end downtime/i,
    },
  },
  {
    id: "D-paused-no-downtime-tablet",
    label: "PAUSED / no downtime (tablet)",
    viewport: "tablet",
    detailOverrides: {
      status: "PAUSED",
      downtime_open: false,
      allowed_actions: ["resume_execution", "start_downtime", "complete_execution"],
    },
    expect: {
      andonSeverity: "warning",
      primaryAction: "resume_execution",
      reportingTestid: "report-input-disabled",
      allowedActionsIncluded: ["resume_execution", "start_downtime", "complete_execution"],
      forbiddenActions: ["pause_execution", "start_execution", "end_downtime", "report_production"],
      bannerTextRegex: /resume/i,
      reportingTextRegex: /paused|resume/i,
    },
  },
];

function buildDetailForScenario(scenario) {
  return { ...baseOperationDetail(), ...scenario.detailOverrides };
}

async function installMocksForScenario(page, devServerUrl, scenario) {
  const detail = buildDetailForScenario(scenario);
  const queue = makeQueue();
  // Reflect status in queue too so the queue item ownership/status is
  // consistent with the detail returned for the explicit deep link.
  queue.items[0].status = detail.status;

  await page.route(`${devServerUrl}/api/**`, async (route) => {
    const request = route.request();
    const url = request.url();
    const method = request.method();
    const json = (body, status = 200) => {
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
      return json(detail);
    if (url.includes("/v1/station/queue") && method === "GET") return json(queue);
    if (url.includes("/v1/station/sessions/current") && method === "GET") return json(MOCK_SESSION_CURRENT);
    if (url.includes(`/v1/station/operations/${OPERATION_ID}/detail`) && method === "GET")
      return json(detail);

    return route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
  });
}

async function assertAndonBanner(page, scenarioId, expectedSeverity) {
  const banner = await page.waitForSelector('[data-testid="station-andon-banner"]', { timeout: 15000 });
  const severity = await banner.getAttribute("data-andon-severity");
  if (severity !== expectedSeverity) {
    throw new Error(
      `[${scenarioId}]: andon banner severity=${severity} but expected ${expectedSeverity}`,
    );
  }
  // Above-the-fold check: top must be within current viewport height.
  const box = await banner.boundingBox();
  const viewport = page.viewportSize();
  if (!box || box.y < 0 || box.y > viewport.height - 40) {
    throw new Error(
      `[${scenarioId}]: andon banner not above the fold (y=${box?.y}, viewport.height=${viewport.height})`,
    );
  }
  console.log(`PASS [${scenarioId}]: andon banner visible, severity=${expectedSeverity}, above the fold (y=${Math.round(box.y)}).`);
}

async function assertPrimaryAction(page, scenarioId, expectedActionId) {
  const primary = await page.waitForSelector('[data-action-role="primary"]', { timeout: 15000 });
  const actionId = await primary.getAttribute("data-action");
  if (actionId !== expectedActionId) {
    throw new Error(
      `[${scenarioId}]: primary action data-action=${actionId} but expected ${expectedActionId}`,
    );
  }
  console.log(`PASS [${scenarioId}]: primary action = ${expectedActionId}.`);
}

async function assertAllowedActionsRendered(page, scenarioId, includedIds, forbiddenIds) {
  for (const id of includedIds) {
    const el = await page.$(`[data-action="${id}"]`);
    if (!el) {
      throw new Error(
        `[${scenarioId}]: expected backend-allowed action '${id}' to be rendered (primary or secondary) but it was not found in DOM`,
      );
    }
  }
  for (const id of forbiddenIds) {
    const el = await page.$(`[data-action="${id}"]`);
    if (el) {
      throw new Error(
        `[${scenarioId}]: forbidden action '${id}' rendered but backend did NOT include it in allowed_actions`,
      );
    }
  }
  console.log(
    `PASS [${scenarioId}]: rendered actions match backend allowed_actions (included=${includedIds.join(",")}; forbidden absent=${forbiddenIds.join(",")}).`,
  );
}

async function assertBannerGuidanceText(page, scenarioId, regex) {
  // FE-SE-INTERRUPTED-MODE-11-CORRECTION: visible operator guidance text inside the andon banner.
  const banner = await page.waitForSelector('[data-testid="station-andon-banner"]', { timeout: 15000 });
  const text = ((await banner.textContent()) ?? "").trim();
  if (!text) {
    throw new Error(`[${scenarioId}]: andon banner rendered but textContent is empty`);
  }
  if (!regex.test(text)) {
    throw new Error(
      `[${scenarioId}]: andon banner text did not match ${regex}. Observed: "${text}"`,
    );
  }
  console.log(`PASS [${scenarioId}]: andon banner guidance text matches ${regex}. Observed: "${text}"`);
}

async function assertReportingDisabledReasonText(page, scenarioId, regex) {
  // FE-SE-INTERRUPTED-MODE-11-CORRECTION: visible disabled-reporting reason text.
  const section = await page.$('[data-testid="report-input-disabled"]');
  if (!section) {
    throw new Error(
      `[${scenarioId}]: expected report-input-disabled section to be present for reason-text assertion`,
    );
  }
  const text = ((await section.textContent()) ?? "").trim();
  if (!text) {
    throw new Error(`[${scenarioId}]: report-input-disabled section rendered but textContent is empty`);
  }
  if (!regex.test(text)) {
    throw new Error(
      `[${scenarioId}]: report-input-disabled reason text did not match ${regex}. Observed: "${text}"`,
    );
  }
  console.log(`PASS [${scenarioId}]: reporting-disabled reason text matches ${regex}. Observed: "${text}"`);
}

async function assertReportingTestid(page, scenarioId, expectedTestid) {
  const el = await page.$(`[data-testid="${expectedTestid}"]`);
  if (!el) {
    throw new Error(
      `[${scenarioId}]: expected reporting section data-testid='${expectedTestid}' but it was not found`,
    );
  }
  // And the opposite testid must NOT be present.
  const opposite = expectedTestid === "report-input-disabled" ? "report-input-enabled" : "report-input-disabled";
  const oppositeEl = await page.$(`[data-testid="${opposite}"]`);
  if (oppositeEl) {
    throw new Error(
      `[${scenarioId}]: reporting section unexpectedly also has data-testid='${opposite}'`,
    );
  }
  console.log(`PASS [${scenarioId}]: reporting section = ${expectedTestid}.`);
}

async function assertNoImplicitFirstItemSelect(page, scenarioId, devServerUrl) {
  // Navigate to /station with NO operationId; the page must NOT auto-select
  // the first queue item (Navigation Intent Gate / FE-SE-NAV-INTENT-11).
  await page.goto(`${devServerUrl}/station`, { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(800);
  const url = new URL(page.url());
  if (url.searchParams.has("operationId")) {
    throw new Error(
      `[${scenarioId}/nav-intent-regression]: /station landing mutated URL to include operationId=${url.searchParams.get(
        "operationId",
      )}; first-item auto-select regression`,
    );
  }
  const zone = await page.$('[data-testid="allowed-action-zone"]');
  if (zone) {
    throw new Error(
      `[${scenarioId}/nav-intent-regression]: AllowedActionZone visible on default /station landing; first-item auto-select regression`,
    );
  }
  console.log(`PASS [${scenarioId}/nav-intent-regression]: /station landing did not auto-select first queue item.`);
}

async function runScenario(browser, devServerUrl, scenario) {
  const viewport = VIEWPORTS.find((v) => v.name === scenario.viewport) ?? VIEWPORTS[0];
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
  });
  await context.addInitScript((tokenKey) => {
    window.localStorage.setItem(tokenKey, "qa-interrupted-token");
  }, TOKEN_KEY);

  const page = await context.newPage();
  page.on("console", (msg) => console.log(`[page.${msg.type()}] ${msg.text()}`));
  page.on("pageerror", (err) => console.log(`[page.error] ${err.message}`));
  page.on("requestfailed", (req) =>
    console.log(`[page.requestfailed] ${req.url()} ${req.failure()?.errorText}`),
  );

  await installMocksForScenario(page, devServerUrl, scenario);

  // Navigation Intent regression check (one per scenario is cheap and proves
  // we did not weaken FE-SE-NAV-INTENT-11).
  await assertNoImplicitFirstItemSelect(page, scenario.id, devServerUrl);

  // Drive cockpit via explicit deep link, never via items[0] auto-select.
  await page.goto(`${devServerUrl}/station?operationId=${OPERATION_ID}`, {
    waitUntil: "networkidle",
    timeout: 30000,
  });
  await page.waitForSelector('[data-testid="allowed-action-zone"]', { timeout: 15000 });

  await assertAndonBanner(page, scenario.id, scenario.expect.andonSeverity);
  await assertPrimaryAction(page, scenario.id, scenario.expect.primaryAction);
  await assertAllowedActionsRendered(
    page,
    scenario.id,
    scenario.expect.allowedActionsIncluded,
    scenario.expect.forbiddenActions,
  );
  await assertReportingTestid(page, scenario.id, scenario.expect.reportingTestid);
  if (scenario.expect.bannerTextRegex) {
    await assertBannerGuidanceText(page, scenario.id, scenario.expect.bannerTextRegex);
  }
  if (
    scenario.expect.reportingTestid === "report-input-disabled" &&
    scenario.expect.reportingTextRegex
  ) {
    await assertReportingDisabledReasonText(page, scenario.id, scenario.expect.reportingTextRegex);
  }

  const screenshotPath = path.join(OUTPUT_DIR, `${scenario.id}-${viewport.name}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(`Saved: ${path.relative(REPO_ROOT, screenshotPath)}`);

  await context.close();
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
    console.log("Starting FE-SE-INTERRUPTED-MODE-11 interrupted-state QA harness");
    console.log("Visual QA only: mocked API. Does NOT prove backend truth or E2E.");
    for (const scenario of SCENARIOS) {
      console.log(`-- Scenario: ${scenario.id} (${scenario.label}) viewport=${scenario.viewport}`);
      await runScenario(browser, devServerUrl, scenario);
    }
    console.log("Completed FE-SE-INTERRUPTED-MODE-11 interrupted-state QA harness");
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
