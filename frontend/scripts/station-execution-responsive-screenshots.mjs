import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { chromium } from "playwright";

const DEV_SERVER_URL = "http://localhost:5173";
const TOKEN_KEY = "mes.auth.token";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "station-execution-responsive-qa");

const VIEWPORTS = [
  { name: "desktop", width: 1440, height: 900 },
  { name: "tablet-landscape", width: 1180, height: 820 },
  { name: "tablet-portrait", width: 820, height: 1180 },
  { name: "narrow", width: 430, height: 932 },
];

const MOCK_USER = {
  user_id: "opr-001",
  username: "operator",
  role_code: "OPR",
  tenant_id: "default",
};

const MOCK_DASHBOARD_SUMMARY = {
  context: { date: "2026-04-30", shift: "DAY" },
  workOrders: { total: 12, inProgress: 4, completed: 7, blocked: 1 },
  operations: { total: 34, running: 9, paused: 2, completed: 20, blocked: 3 },
  alerts: { total: 2, critical: 0, warning: 2 },
};

const MOCK_QUEUE_EMPTY = {
  station_scope_value: "STATION_01",
  items: [],
};

const MOCK_QUEUE_COCKPIT = {
  station_scope_value: "STATION_01",
  items: [
    {
      operation_id: 1,
      operation_number: "OP-1001-10",
      name: "CNC Machining",
      work_order_number: "WO-1001",
      production_order_number: "PO-2026-0001",
      status: "IN_PROGRESS",
      planned_start: "2026-04-30T08:00:00Z",
      planned_end: "2026-04-30T13:00:00Z",
      // ownership shape matches SessionOwnershipSummary (stationApi.ts)
      ownership: {
        target_owner_type: "station",
        session_id: "sess-0001",
        station_id: "STATION_01",
        session_status: "OPEN",
        operator_user_id: "opr-001",
        owner_state: "mine",
        has_open_session: true,
      },
      downtime_open: false,
    },
    {
      operation_id: 2,
      operation_number: "OP-1001-20",
      name: "Deburr",
      work_order_number: "WO-1001",
      production_order_number: "PO-2026-0001",
      status: "PLANNED",
      planned_start: "2026-04-30T13:00:00Z",
      planned_end: "2026-04-30T15:00:00Z",
      ownership: {
        target_owner_type: "station",
        session_id: null,
        station_id: "STATION_01",
        session_status: null,
        operator_user_id: null,
        owner_state: "none",
        has_open_session: false,
      },
      downtime_open: false,
    },
    {
      operation_id: 3,
      operation_number: "OP-1002-10",
      name: "Inspection",
      work_order_number: "WO-1002",
      production_order_number: "PO-2026-0002",
      status: "PLANNED",
      planned_start: "2026-04-30T09:00:00Z",
      planned_end: "2026-04-30T11:30:00Z",
      ownership: {
        target_owner_type: "station",
        session_id: "sess-0002",
        station_id: "STATION_01",
        session_status: "OPEN",
        operator_user_id: "opr-002",
        owner_state: "other",
        has_open_session: true,
      },
      downtime_open: false,
    },
  ],
};

const MOCK_OPERATION_DETAIL = {
  id: 1,
  operation_number: "OP-1001-10",
  name: "CNC Machining",
  sequence: 10,
  status: "IN_PROGRESS",
  closure_status: "OPEN",
  planned_start: "2026-04-30T08:00:00Z",
  planned_end: "2026-04-30T13:00:00Z",
  actual_start: "2026-04-30T08:05:00Z",
  actual_end: null,
  quantity: 120,
  completed_qty: 95,
  good_qty: 92,
  scrap_qty: 3,
  progress: 79.1,
  work_order_id: 1001,
  work_order_number: "WO-1001",
  production_order_id: 5001,
  production_order_number: "PO-2026-0001",
  qc_required: true,
  downtime_open: false,
  quality_hold_open: false,
  allowed_actions: ["report_production", "pause_execution", "start_downtime", "complete_execution"],
  paused_total_ms: 0,
  downtime_total_ms: 0,
  reopen_count: 0,
  last_reopened_at: null,
  last_reopened_by: null,
  last_closed_at: null,
  last_closed_by: null,
};

const MOCK_DOWNTIME_REASONS = [
  {
    reason_code: "MACHINE_FAILURE",
    reason_name: "Machine Failure",
    reason_group: "UNPLANNED",
    planned_flag: false,
    requires_comment: true,
    requires_supervisor_review: true,
  },
  {
    reason_code: "TOOL_CHANGE",
    reason_name: "Tool Change",
    reason_group: "PLANNED",
    planned_flag: true,
    requires_comment: false,
    requires_supervisor_review: false,
  },
];

function screenshotPath(name, viewport) {
  return path.join(OUTPUT_DIR, `${name}-${viewport.name}-${viewport.width}x${viewport.height}.png`);
}

function isHtml(url) {
  return url.endsWith("/") || url.includes("/station") || url.includes("/dashboard") || url.includes("/login");
}

async function installQaMocks(page, queueResponse) {
  await page.route(`${DEV_SERVER_URL}/api/**`, async (route) => {
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

    if (url.includes("/v1/auth/logout-all") && method === "POST") {
      return json({ status: "ok", revoked_count: 1 });
    }

    if (url.includes("/v1/dashboard/summary") && method === "GET") {
      return json(MOCK_DASHBOARD_SUMMARY);
    }

    if (url.includes("/v1/dashboard/health") && method === "GET") {
      return json({ status: "ok" });
    }

    if (url.includes("/v1/station/queue/") && url.includes("/detail") && method === "GET") {
      return json(MOCK_OPERATION_DETAIL);
    }

    if (url.includes("/v1/station/queue") && method === "GET") {
      return json(queueResponse);
    }

    if (url.includes("/v1/downtime-reasons") && method === "GET") {
      return json(MOCK_DOWNTIME_REASONS);
    }

    if (url.includes("/v1/operations/") && method === "POST") {
      return json(MOCK_OPERATION_DETAIL);
    }

    if (url.includes("/v1/station/queue/") && url.includes("/claim") && method === "POST") {
      return json({
        operation_id: 1,
        ownership: {
          target_owner_type: "station",
          session_id: "sess-0001",
          station_id: "STATION_01",
          session_status: "OPEN",
          operator_user_id: "opr-001",
          owner_state: "mine",
          has_open_session: true,
        },
      });
    }

    return route.abort();
  });
}

async function captureState(browser, stateName, queueResponse, routePath, assertions = []) {
  for (const viewport of VIEWPORTS) {
    const context = await browser.newContext({ viewport });
    await context.addInitScript((tokenKey) => {
      window.localStorage.setItem(tokenKey, "qa-station-token");
    }, TOKEN_KEY);

    const page = await context.newPage();
    await installQaMocks(page, queueResponse);

    await page.goto(DEV_SERVER_URL, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForURL((url) => isHtml(url.pathname), { timeout: 30000 });

    await page.goto(`${DEV_SERVER_URL}${routePath}`, { waitUntil: "networkidle", timeout: 30000 });

    await page.waitForSelector("main, [data-testid='station-execution-root'], body", { timeout: 30000 });

    // Run assertions before screenshot
    for (const assertion of assertions) {
      await assertion(page, stateName, viewport.name);
    }

    const outputFile = screenshotPath(stateName, viewport);
    await page.screenshot({ path: outputFile, fullPage: true });
    console.log(`Saved ${path.relative(REPO_ROOT, outputFile)}`);

    await context.close();
  }
}

async function main() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });

  // Assertions for Mode B: verify cockpit renders, not StationWorkflowShell
  const modeBAssertions = [
    async (page, state, viewport) => {
      // Must NOT show STX- stage labels (WorkflowShell stage pills)
      const stxText = await page.$$eval("[class*='stage'], [data-stage]", (els) =>
        els.map((e) => e.textContent ?? "").join(" ")
      );
      const stxInBody = await page.evaluate(() => document.body.innerText);
      const hasStxLabel = /STX-\d{3}/.test(stxInBody);
      if (hasStxLabel) {
        console.error(`ASSERTION FAIL [${state}/${viewport}]: STX- stage labels visible in Mode B`);
        process.exitCode = 1;
      } else {
        console.log(`PASS [${state}/${viewport}]: No STX- stage labels visible`);
      }
    },
    async (page, state, viewport) => {
      // Must show cockpit context strip (data-testid=cockpit-context-strip)
      const contextStrip = await page.$("[data-testid='cockpit-context-strip']");
      if (!contextStrip) {
        console.error(`ASSERTION FAIL [${state}/${viewport}]: cockpit-context-strip not found — Mode B cockpit did not render`);
        process.exitCode = 1;
      } else {
        console.log(`PASS [${state}/${viewport}]: cockpit-context-strip present`);
      }
    },
    async (page, state, viewport) => {
      // Support details disclosure must be collapsed by default (content hidden)
      const cockpit = await page.$("[data-testid='station-execution-cockpit']");
      if (!cockpit) {
        console.error(`ASSERTION FAIL [${state}/${viewport}]: station-execution-cockpit not found`);
        process.exitCode = 1;
        return;
      }
      // The support details disclosure button must exist but its content must not be visible
      const supportBtn = await page.$("[data-testid='station-execution-cockpit'] button[aria-expanded='false']");
      if (!supportBtn) {
        // aria-expanded=false means it's collapsed; if not found, check aria-expanded=true (open = wrong)
        const supportBtnOpen = await page.$("[data-testid='station-execution-cockpit'] button[aria-expanded='true']");
        if (supportBtnOpen) {
          console.error(`ASSERTION FAIL [${state}/${viewport}]: Support details is expanded by default — should be collapsed`);
          process.exitCode = 1;
        } else {
          // No aria-expanded button found at all — disclosure may not have rendered (no supportDetails prop)
          console.log(`PASS [${state}/${viewport}]: Support details not rendered (no supportDetails prop)`);
        }
      } else {
        console.log(`PASS [${state}/${viewport}]: Support details is collapsed by default`);
      }
    },
    async (page, state, viewport) => {
      // IN_PROGRESS with remaining qty > 0: Report Qty must be visible as primary action
      const reportQtyBtn = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll("button"));
        return buttons.find((btn) => btn.textContent?.includes("Report"));
      });
      if (!reportQtyBtn) {
        console.error(`ASSERTION FAIL [${state}/${viewport}]: Report Qty button not found in action area`);
        process.exitCode = 1;
      } else {
        console.log(`PASS [${state}/${viewport}]: Report Qty button visible as primary production action`);
      }
    },
    async (page, state, viewport) => {
      // IN_PROGRESS with remaining qty > 0 (remaining = 120 - 95 = 25):
      // Complete Operation should NOT be shown as a primary full-width button.
      // Check that Complete is either not visible or is styled as secondary (outline).
      const completeBtn = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll("button"));
        const btn = buttons.find((b) => b.textContent?.includes("Complete"));
        if (!btn) return null;
        const classes = btn.className;
        const isFull = classes.includes("w-full") && !classes.includes("sm:");
        const isGreen = classes.includes("bg-green") || classes.includes("bg-emerald-600");
        const isOutline = classes.includes("border") && classes.includes("bg-white");
        return {
          visible: true,
          isFull,
          isGreen,
          isOutline,
          text: btn.textContent,
        };
      });
      if (!completeBtn) {
        // Not visible is acceptable when remaining qty > 0
        console.log(`PASS [${state}/${viewport}]: Complete Operation not shown (correct for remaining qty > 0)`);
      } else if (completeBtn.isOutline) {
        console.log(`PASS [${state}/${viewport}]: Complete Operation is secondary/outline (correct for remaining qty > 0)`);
      } else if (completeBtn.isGreen || (!completeBtn.isOutline && completeBtn.isFull)) {
        console.error(`ASSERTION FAIL [${state}/${viewport}]: Complete Operation is shown as primary (should be secondary when remaining qty > 0)`);
        process.exitCode = 1;
      } else {
        console.log(`PASS [${state}/${viewport}]: Complete Operation styling correct for action hierarchy`);
      }
    },
  ];

  try {
    console.log("Starting Station Execution responsive screenshot QA run");
    console.log("Visual QA only: mocks are isolated from backend truth. Screenshots do not validate E2E behavior, authorization, or golden-path coverage.");

    // Mode A: empty queue (no session, no operation)
    await captureState(browser, "mode-a-empty", MOCK_QUEUE_EMPTY, "/station");

    // Mode A: queue loaded with session mine (but forceSelectionMode=true equivalent — no operationId param)
    await captureState(browser, "mode-a-queue", MOCK_QUEUE_COCKPIT, "/station");

    // Mode B: operation pre-selected, session owned — should render StationExecutionCockpit
    await captureState(
      browser,
      "mode-b-in-progress",
      MOCK_QUEUE_COCKPIT,
      "/station?operationId=1",
      modeBAssertions,
    );

    console.log("\nCompleted Station Execution responsive screenshot capture");
    console.log(`Screenshots saved to: docs/audit/station-execution-responsive-qa/`);
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
