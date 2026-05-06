/**
 * MMD-FE-QA-02 — MMD Write UI Runtime Visual QA Screenshot Harness
 *
 * Captures Product Version, BOM, and Reason Code write UI screens at
 * multiple viewports. Uses mocked API responses — no backend mutations
 * are performed. QA only: screenshots do not represent live backend truth.
 *
 * Scenarios captured:
 *   - Products list (manage user)
 *   - Product detail with PV write controls (manage user)
 *   - Product detail with PV write controls (read-only user)
 *   - BOM list with create capability (manage user)
 *   - BOM detail with write controls (manage user, DRAFT)
 *   - Reason Codes list with write controls (manage user, mixed lifecycle)
 *   - Reason Codes list (read-only user, all controls disabled)
 *   - Reason Codes empty list (manage user, can_create=true)
 *   - Reason Codes empty list (read-only user, can_create=false)
 *
 * Usage:
 *   node scripts/mmd-runtime-visual-qa.mjs
 *
 * Requires:
 *   - Vite dev server at http://localhost:5173 (started separately)
 *   - playwright package installed (already in devDependencies)
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
const OUTPUT_DIR = path.join(REPO_ROOT, "docs", "audit", "mmd-fe-qa-02-screenshots");

const VIEWPORTS = {
  desktop: { width: 1440, height: 900 },
  tablet: { width: 1024, height: 768 },
  mobile: { width: 430, height: 932 },
};

// ── Mock user identities ──────────────────────────────────────────────────────

const ADMIN_USER = {
  user_id: "adm-001",
  username: "admin",
  role_code: "ADM",
  tenant_id: "default",
};

// PMG (Production Manager) persona has access to /products. ADM does NOT (UX persona routing).
const PMG_USER = {
  user_id: "pmg-001",
  username: "prod_manager",
  role_code: "PMG",
  tenant_id: "default",
};

const READONLY_USER = {
  user_id: "opr-001",
  username: "operator",
  role_code: "OPR",
  tenant_id: "default",
};

// ── Mock API data ─────────────────────────────────────────────────────────────

const MOCK_PRODUCTS = [
  {
    product_id: "prod-001",
    tenant_id: "default",
    product_code: "PART-VALVE-01",
    product_name: "Control Valve Assembly",
    product_type: "MANUFACTURED",
    lifecycle_status: "RELEASED",
    description: "Main control valve assembly for hydraulic system",
    display_metadata: null,
    created_at: "2026-01-10T08:00:00Z",
    updated_at: "2026-04-15T10:30:00Z",
    product_version_capabilities: { can_create: true },
    bom_capabilities: { can_create: true },
  },
  {
    product_id: "prod-002",
    tenant_id: "default",
    product_code: "PART-PUMP-02",
    product_name: "Hydraulic Pump Unit",
    product_type: "MANUFACTURED",
    lifecycle_status: "RELEASED",
    description: "High-pressure hydraulic pump unit — 250 bar rated",
    display_metadata: null,
    created_at: "2026-01-15T09:00:00Z",
    updated_at: "2026-04-20T14:00:00Z",
    product_version_capabilities: { can_create: true },
    bom_capabilities: { can_create: true },
  },
  {
    product_id: "prod-003",
    tenant_id: "default",
    product_code: "RAW-STEEL-01",
    product_name: "Steel Billet 50mm",
    product_type: "PURCHASED",
    lifecycle_status: "RELEASED",
    description: "Grade S355 steel billet for CNC machining",
    display_metadata: null,
    created_at: "2026-02-01T07:00:00Z",
    updated_at: "2026-03-10T11:00:00Z",
    product_version_capabilities: { can_create: true },
    bom_capabilities: { can_create: true },
  },
];

const MOCK_PRODUCTS_READONLY = MOCK_PRODUCTS.map((p) => ({
  ...p,
  product_version_capabilities: { can_create: false },
  bom_capabilities: { can_create: false },
}));

const MOCK_PRODUCT_VERSIONS_MANAGE = [
  {
    product_version_id: "pv-001",
    tenant_id: "default",
    product_id: "prod-001",
    version_code: "V1.0",
    version_name: "Initial Release",
    lifecycle_status: "RELEASED",
    is_current: true,
    effective_from: "2026-01-10",
    effective_to: null,
    description: "First production release of Control Valve Assembly",
    created_at: "2026-01-10T08:00:00Z",
    updated_at: "2026-04-15T10:30:00Z",
    allowed_actions: { can_update: false, can_release: false, can_retire: true, can_create_sibling: true },
  },
  {
    product_version_id: "pv-002",
    tenant_id: "default",
    product_id: "prod-001",
    version_code: "V2.0",
    version_name: "Revised Tolerances",
    lifecycle_status: "DRAFT",
    is_current: false,
    effective_from: null,
    effective_to: null,
    description: "Revised tolerance stack for improved yield",
    created_at: "2026-04-01T09:00:00Z",
    updated_at: "2026-04-28T15:00:00Z",
    allowed_actions: { can_update: true, can_release: true, can_retire: true, can_create_sibling: true },
  },
];

const MOCK_PRODUCT_VERSIONS_READONLY = MOCK_PRODUCT_VERSIONS_MANAGE.map((v) => ({
  ...v,
  allowed_actions: { can_update: false, can_release: false, can_retire: false, can_create_sibling: false },
}));

const MOCK_BOMS = [
  {
    bom_id: "bom-001",
    tenant_id: "default",
    product_id: "prod-001",
    bom_code: "BOM-VALVE-01",
    bom_name: "Control Valve BOM v1",
    lifecycle_status: "DRAFT",
    effective_from: null,
    effective_to: null,
    description: "Bill of Materials for Control Valve Assembly",
    created_at: "2026-02-01T08:00:00Z",
    updated_at: "2026-04-28T10:00:00Z",
    allowed_actions: {
      can_update: true,
      can_release: true,
      can_retire: true,
      can_add_item: true,
      can_update_item: true,
      can_remove_item: true,
      can_create_sibling: true,
    },
  },
  {
    bom_id: "bom-002",
    tenant_id: "default",
    product_id: "prod-002",
    bom_code: "BOM-PUMP-01",
    bom_name: "Hydraulic Pump BOM v1",
    lifecycle_status: "RELEASED",
    effective_from: "2026-03-01",
    effective_to: null,
    description: "Bill of Materials for Hydraulic Pump Unit",
    created_at: "2026-03-01T08:00:00Z",
    updated_at: "2026-03-20T16:00:00Z",
    allowed_actions: {
      can_update: false,
      can_release: false,
      can_retire: true,
      can_add_item: false,
      can_update_item: false,
      can_remove_item: false,
      can_create_sibling: true,
    },
  },
];

const MOCK_BOM_DETAIL = {
  ...MOCK_BOMS[0],
  items: [
    {
      bom_item_id: "bi-001",
      tenant_id: "default",
      bom_id: "bom-001",
      component_product_id: "prod-003",
      line_no: 10,
      quantity: 2,
      unit_of_measure: "PCS",
      scrap_factor: 0.02,
      reference_designator: null,
      notes: "Grade S355 only",
      created_at: "2026-02-01T08:00:00Z",
      updated_at: "2026-02-01T08:00:00Z",
    },
    {
      bom_item_id: "bi-002",
      tenant_id: "default",
      bom_id: "bom-001",
      component_product_id: "prod-001",
      line_no: 20,
      quantity: 1,
      unit_of_measure: "PCS",
      scrap_factor: null,
      reference_designator: "REF-A",
      notes: null,
      created_at: "2026-02-01T08:00:00Z",
      updated_at: "2026-02-01T08:00:00Z",
    },
  ],
};

const MOCK_REASON_CODES_MANAGE = [
  {
    reason_code_id: "rc-001",
    tenant_id: "default",
    reason_domain: "DOWNTIME",
    reason_category: "MECHANICAL",
    reason_code: "MECH_FAIL",
    reason_name: "Mechanical Failure",
    description: "Equipment mechanical failure — unplanned",
    lifecycle_status: "RELEASED",
    requires_comment: true,
    is_active: true,
    sort_order: 10,
    created_at: "2026-01-01T08:00:00Z",
    updated_at: "2026-04-01T10:00:00Z",
    allowed_actions: { can_update: false, can_release: false, can_retire: true, can_create_sibling: true },
  },
  {
    reason_code_id: "rc-002",
    tenant_id: "default",
    reason_domain: "DOWNTIME",
    reason_category: "ELECTRICAL",
    reason_code: "ELEC_TRIP",
    reason_name: "Electrical Trip / Overload",
    description: "Electrical protection trip — circuit overload",
    lifecycle_status: "RELEASED",
    requires_comment: true,
    is_active: true,
    sort_order: 20,
    created_at: "2026-01-15T08:00:00Z",
    updated_at: "2026-04-01T10:00:00Z",
    allowed_actions: { can_update: false, can_release: false, can_retire: true, can_create_sibling: true },
  },
  {
    reason_code_id: "rc-003",
    tenant_id: "default",
    reason_domain: "PAUSE",
    reason_category: "CHANGEOVER",
    reason_code: "CHANGEOVER",
    reason_name: "Product Changeover",
    description: "Line changeover for new production order",
    lifecycle_status: "DRAFT",
    requires_comment: false,
    is_active: true,
    sort_order: 10,
    created_at: "2026-04-01T08:00:00Z",
    updated_at: "2026-04-28T15:00:00Z",
    allowed_actions: { can_update: true, can_release: true, can_retire: true, can_create_sibling: true },
  },
  {
    reason_code_id: "rc-004",
    tenant_id: "default",
    reason_domain: "SCRAP",
    reason_category: "QUALITY",
    reason_code: "DIM_OOT",
    reason_name: "Dimension Out of Tolerance",
    description: "Part rejected — dimensional non-conformance",
    lifecycle_status: "RETIRED",
    requires_comment: true,
    is_active: false,
    sort_order: 30,
    created_at: "2025-06-01T08:00:00Z",
    updated_at: "2026-03-01T10:00:00Z",
    allowed_actions: { can_update: false, can_release: false, can_retire: false, can_create_sibling: true },
  },
];

const MOCK_REASON_CODES_READONLY = MOCK_REASON_CODES_MANAGE.map((rc) => ({
  ...rc,
  allowed_actions: { can_update: false, can_release: false, can_retire: false, can_create_sibling: false },
}));

const MOCK_RC_CAPABILITIES_MANAGE = { can_create: true, reason: null };
const MOCK_RC_CAPABILITIES_READONLY = { can_create: false, reason: null };

// ── Helper: build mock router ──────────────────────────────────────────────────

function buildApiMock(user, products, productVersions, boms, bomDetail, reasonCodes, rcCapabilities) {
  return async function installQaMocks(page) {
    await page.route(`${DEV_SERVER_URL}/api/**`, async (route) => {
      const url = route.request().url();

      const json = (body, status = 200) =>
        route.fulfill({
          status,
          contentType: "application/json",
          body: JSON.stringify(body),
        });

      // Auth
      if (url.includes("/v1/auth/me")) return json(user);

      // Reason Code capabilities — must come BEFORE generic reason-codes handler
      if (url.includes("/v1/reason-codes/capabilities")) return json(rcCapabilities);

      // Reason Codes list
      if (url.match(/\/v1\/reason-codes(\?|$)/)) return json(reasonCodes);

      // Product versions
      if (url.match(/\/v1\/products\/[^/]+\/versions(\?|$)/)) return json(productVersions);

      // Product detail
      if (url.match(/\/v1\/products\/prod-001(\?|$)/)) return json(products[0]);
      if (url.match(/\/v1\/products\/prod-002(\?|$)/)) return json(products[1]);

      // BOM detail
      if (url.match(/\/v1\/boms\/bom-001(\?|$)/)) return json(bomDetail);
      if (url.match(/\/v1\/boms\/bom-002(\?|$)/)) return json({ ...MOCK_BOMS[1], items: [] });

      // BOM list (all products)
      if (url.match(/\/v1\/boms(\?|$)/) || url.includes("/boms")) return json(boms);

      // Products list
      if (url.match(/\/v1\/products(\?|$)/)) return json(products);

      // Pass through everything else
      return route.continue();
    });
  };
}

// ── Screenshot helpers ─────────────────────────────────────────────────────────

function screenshotPath(filename) {
  return path.join(OUTPUT_DIR, filename);
}

async function capture(page, filename, options = {}) {
  const { waitFor = "networkidle", selector = null } = options;
  try {
    if (selector) {
      await page.waitForSelector(selector, { timeout: 10000 });
    }
    await page.waitForTimeout(400); // settle animations
    const outputFile = screenshotPath(filename);
    await page.screenshot({ path: outputFile, fullPage: true });
    const relPath = path.relative(REPO_ROOT, outputFile);
    console.log(`  ✓ ${relPath}`);
    return { status: "ok", file: relPath };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`  ✗ ${filename}: ${msg}`);
    return { status: "error", error: msg, file: filename };
  }
}

async function navigate(page, targetPath, waitFor = "networkidle") {
  await page.goto(`${DEV_SERVER_URL}${targetPath}`, {
    waitUntil: waitFor,
    timeout: 25000,
  });
}

async function newAuthPage(browser, viewport, mockInstaller) {
  const context = await browser.newContext({ viewport });
  await context.addInitScript((tokenKey) => {
    window.localStorage.setItem(tokenKey, "qa-mmd-token");
  }, TOKEN_KEY);
  const page = await context.newPage();
  await mockInstaller(page);
  // Navigate to root once to initialize app
  await page.goto(DEV_SERVER_URL, { waitUntil: "domcontentloaded", timeout: 20000 });
  return { context, page };
}

// ── Main capture sequence ─────────────────────────────────────────────────────

async function main() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const results = [];

  try {
    console.log("MMD-FE-QA-02 — MMD Write UI Runtime Visual QA");
    console.log(`Output: ${OUTPUT_DIR}`);
    console.log("---");

    // ── Mock installers ──────────────────────────────────────────────────────
    // NOTE: ADM persona CANNOT access /products (UX persona routing: canAccessProducts returns false
    // for ADM). Use PMG user for Products screenshots. ADM can access /bom and /reason-codes.

    const manageMock = buildApiMock(
      ADMIN_USER,
      MOCK_PRODUCTS,
      MOCK_PRODUCT_VERSIONS_MANAGE,
      MOCK_BOMS,
      MOCK_BOM_DETAIL,
      MOCK_REASON_CODES_MANAGE,
      MOCK_RC_CAPABILITIES_MANAGE,
    );

    // PMG user for Products pages (ADM cannot access /products per UX persona routing)
    const pmgManageMock = buildApiMock(
      PMG_USER,
      MOCK_PRODUCTS,
      MOCK_PRODUCT_VERSIONS_MANAGE,
      MOCK_BOMS,
      MOCK_BOM_DETAIL,
      MOCK_REASON_CODES_MANAGE,
      MOCK_RC_CAPABILITIES_MANAGE,
    );

    // SUP user for Products read-only (PMG with read-only product capabilities)
    const pmgReadonlyMock = buildApiMock(
      PMG_USER,
      MOCK_PRODUCTS_READONLY,
      MOCK_PRODUCT_VERSIONS_READONLY,
      MOCK_BOMS,
      MOCK_BOM_DETAIL,
      MOCK_REASON_CODES_READONLY,
      MOCK_RC_CAPABILITIES_READONLY,
    );

    const readonlyMock = buildApiMock(
      // ADM user — can access /bom and /reason-codes. OPR cannot.
      // "Readonly" is conveyed by allowed_actions all false + can_create false in response data.
      ADMIN_USER,
      MOCK_PRODUCTS_READONLY,
      MOCK_PRODUCT_VERSIONS_READONLY,
      MOCK_BOMS.map((b) => ({
        ...b,
        allowed_actions: {
          can_update: false, can_release: false, can_retire: false,
          can_add_item: false, can_update_item: false, can_remove_item: false,
          can_create_sibling: false,
        },
      })),
      { ...MOCK_BOM_DETAIL, allowed_actions: {
        can_update: false, can_release: false, can_retire: false,
        can_add_item: false, can_update_item: false, can_remove_item: false,
        can_create_sibling: false,
      }},
      MOCK_REASON_CODES_READONLY,
      MOCK_RC_CAPABILITIES_READONLY,
    );

    const emptyListManageMock = buildApiMock(
      ADMIN_USER,
      MOCK_PRODUCTS,
      [],
      [],
      MOCK_BOM_DETAIL,
      [],
      MOCK_RC_CAPABILITIES_MANAGE,
    );

    const emptyListReadonlyMock = buildApiMock(
      // ADM user — same rationale as readonlyMock
      ADMIN_USER,
      MOCK_PRODUCTS_READONLY,
      [],
      [],
      MOCK_BOM_DETAIL,
      [],
      MOCK_RC_CAPABILITIES_READONLY,
    );

    // ── 01: Products list — desktop (PMG manage user — ADM cannot access /products) ────────────────────────────
    console.log("\n01 — Products list (PMG manage user, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, pmgManageMock);
      await navigate(page, "/products");
      results.push(await capture(page, "01-products-list-desktop.png", { selector: "main, h1, [class*='product']" }));
      await context.close();
    }

    // ── 02: Products list — tablet ───────────────────────────────────────────
    console.log("\n02 — Products list (PMG manage user, tablet)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.tablet, pmgManageMock);
      await navigate(page, "/products");
      results.push(await capture(page, "02-products-list-tablet.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 03: Product detail — desktop (PMG manage user, PV write controls) ────────
    console.log("\n03 — Product detail with PV write controls (PMG manage user, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, pmgManageMock);
      await navigate(page, "/products/prod-001");
      results.push(await capture(page, "03-product-detail-pv-manage-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 04: Product detail — desktop (PMG read-only, PV controls disabled) ──
    console.log("\n04 — Product detail (PMG read-only, PV controls disabled, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, pmgReadonlyMock);
      await navigate(page, "/products/prod-001");
      results.push(await capture(page, "04-product-detail-pv-readonly-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 05: BOM list — desktop (manage user) ─────────────────────────────────
    console.log("\n05 — BOM list (manage user, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, manageMock);
      await navigate(page, "/bom");
      results.push(await capture(page, "05-bom-list-manage-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 06: BOM list — tablet ─────────────────────────────────────────────────
    console.log("\n06 — BOM list (manage user, tablet)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.tablet, manageMock);
      await navigate(page, "/bom");
      results.push(await capture(page, "06-bom-list-manage-tablet.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 07: BOM detail — desktop (manage user, DRAFT BOM) ────────────────────
    console.log("\n07 — BOM detail (manage user, DRAFT, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, manageMock);
      await navigate(page, "/bom/bom-001");
      results.push(await capture(page, "07-bom-detail-manage-draft-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 08: BOM detail — desktop (read-only user) ─────────────────────────────
    console.log("\n08 — BOM detail (read-only user, controls disabled, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, readonlyMock);
      await navigate(page, "/bom/bom-001");
      results.push(await capture(page, "08-bom-detail-readonly-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 09: Reason Codes — desktop (manage user, mixed lifecycle) ────────────
    console.log("\n09 — Reason Codes list (manage user, mixed lifecycle, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, manageMock);
      await navigate(page, "/reason-codes");
      results.push(await capture(page, "09-reason-codes-manage-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 10: Reason Codes — tablet (manage user) ───────────────────────────────
    console.log("\n10 — Reason Codes list (manage user, tablet)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.tablet, manageMock);
      await navigate(page, "/reason-codes");
      results.push(await capture(page, "10-reason-codes-manage-tablet.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 11: Reason Codes — mobile (manage user) ───────────────────────────────
    console.log("\n11 — Reason Codes list (manage user, mobile)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.mobile, manageMock);
      await navigate(page, "/reason-codes");
      results.push(await capture(page, "11-reason-codes-manage-mobile.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 12: Reason Codes — read-only user (all controls disabled) ────────────
    console.log("\n12 — Reason Codes list (read-only user, all controls disabled, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, readonlyMock);
      await navigate(page, "/reason-codes");
      results.push(await capture(page, "12-reason-codes-readonly-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 13: Reason Codes — empty list, manage user (Create enabled) ──────────
    console.log("\n13 — Reason Codes empty list (manage user, can_create=true, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, emptyListManageMock);
      await navigate(page, "/reason-codes");
      results.push(await capture(page, "13-reason-codes-empty-manage-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── 14: Reason Codes — empty list, read-only user (Create disabled) ──────
    console.log("\n14 — Reason Codes empty list (read-only user, can_create=false, desktop)");
    {
      const { context, page } = await newAuthPage(browser, VIEWPORTS.desktop, emptyListReadonlyMock);
      await navigate(page, "/reason-codes");
      results.push(await capture(page, "14-reason-codes-empty-readonly-desktop.png", { selector: "main, h1" }));
      await context.close();
    }

    // ── Summary ──────────────────────────────────────────────────────────────
    const ok = results.filter((r) => r.status === "ok").length;
    const errors = results.filter((r) => r.status === "error").length;

    console.log(`\n--- Summary ---`);
    console.log(`${ok} screenshots captured, ${errors} errors`);

    if (errors > 0) {
      console.log("\nErrors:");
      for (const r of results.filter((r) => r.status === "error")) {
        console.log(`  ✗ ${r.file}: ${r.error}`);
      }
      process.exitCode = 1;
    } else {
      console.log("PASS — All screenshots captured.");
    }

    // Write results JSON
    const resultFile = path.join(OUTPUT_DIR, "results.json");
    await fs.writeFile(resultFile, JSON.stringify({ screenshots: results, total: results.length, ok, errors }, null, 2));
    console.log(`\nResults: ${path.relative(REPO_ROOT, resultFile)}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  if (message.includes("ERR_CONNECTION_REFUSED") || message.includes("net::ERR_CONNECTION_REFUSED")) {
    console.error("FAIL: dev server not reachable at http://localhost:5173 — start frontend dev server first.");
  } else {
    console.error(`FAIL: screenshot harness crashed: ${message}`);
  }
  process.exitCode = 1;
});
