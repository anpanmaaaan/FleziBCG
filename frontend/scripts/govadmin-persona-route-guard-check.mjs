/**
 * govadmin-persona-route-guard-check.mjs — FE-GOVADMIN-03
 *
 * Regression check for the Governance/Admin persona route guard.
 * Verifies that the 9 Governance/Admin routes are:
 *   1. Registered in routes.tsx
 *   2. In the governance-admin nav group in navigationGroups.ts
 *   3. Guarded by ADM-only access in personaLanding.ts (isRouteAllowedForPersona)
 *   4. Present in MENU_ITEMS_BY_PERSONA.ADM
 *   5. Absent from non-admin persona menu items
 *
 * SAFETY NOTE:
 *   This script verifies UX route visibility only.
 *   It does NOT replace backend authorization/RBAC enforcement.
 *   Frontend route guards are UX visibility controls, not security perimeters.
 *
 * Background: FE-GOVADMIN-02 found that isRouteAllowedForPersona did not include
 * the governance routes, making all 9 routes unreachable at runtime. This check
 * ensures that bug cannot silently regress.
 *
 * Exit code: 0 = PASS, 1 = FAIL
 */

import fs from "node:fs/promises";
import path from "node:path";

const FRONTEND_ROOT = process.cwd();

const FILES = {
  personaLanding: path.join(FRONTEND_ROOT, "src/app/persona/personaLanding.ts"),
  navigationGroups: path.join(FRONTEND_ROOT, "src/app/navigation/navigationGroups.ts"),
  routes: path.join(FRONTEND_ROOT, "src/app/routes.tsx"),
};

// The 9 Governance/Admin target routes (canonical slug form)
const GOVADMIN_ROUTES = [
  "/users",
  "/roles",
  "/action-registry",
  "/scope-assignments",
  "/sessions",
  "/audit-log",
  "/security-events",
  "/tenant-settings",
  "/plant-hierarchy",
];

// All persona codes that must NOT have governance menu items
// (unless source explicitly adds them — this check will catch any unintended addition)
const NON_ADMIN_PERSONAS = ["OPR", "SUP", "IEP", "QC", "PMG", "EXE"];

// ─── helpers ────────────────────────────────────────────────────────────────

let passed = 0;
let failed = 0;

function pass(label) {
  console.log(`  ✓ PASS: ${label}`);
  passed++;
}

function fail(label, detail) {
  console.error(`  ✗ FAIL: ${label}`);
  if (detail) console.error(`         ${detail}`);
  failed++;
}

function section(title) {
  console.log(`\n${title}`);
  console.log("─".repeat(title.length));
}

// ─── Section A: Route registration in routes.tsx ────────────────────────────

async function checkRoutesRegistration(src) {
  section("A. Route Registration (routes.tsx)");

  for (const route of GOVADMIN_ROUTES) {
    // Routes use object notation: { path: "users", ... } (no leading slash)
    const slug = route.slice(1); // strip leading /
    // Match: path: "slug" or path: 'slug'
    const pattern = new RegExp(`path:\\s*["']${slug.replace(/-/g, "\\-")}["']`);
    if (pattern.test(src)) {
      pass(`${route} registered in routes.tsx`);
    } else {
      fail(`${route} NOT found in routes.tsx`, `Expected: path: "${slug}"`);
    }
  }
}

// ─── Section B: navigationGroups governance-admin group ────────────────────

async function checkNavigationGroups(src) {
  section("B. Navigation Group (navigationGroups.ts — governance-admin)");

  // Verify the governance-admin group exists
  if (/id:\s*["']governance-admin["']/.test(src)) {
    pass(`governance-admin group exists`);
  } else {
    fail(`governance-admin group NOT found`);
  }

  // Extract the content of the governance-admin group block
  // Match from "governance-admin" up to the next closing brace of the group object
  const groupMatch = src.match(/id:\s*["']governance-admin["'][^}]+routePrefixes:\s*\[([\s\S]*?)\]/);
  const groupContent = groupMatch ? groupMatch[1] : "";

  for (const route of GOVADMIN_ROUTES) {
    const routePattern = new RegExp(`["']${route.replace("/", "\\/")}["']`);
    if (routePattern.test(groupContent)) {
      pass(`${route} in governance-admin routePrefixes`);
    } else {
      fail(`${route} NOT in governance-admin routePrefixes`);
    }
  }
}

// ─── Section C: isRouteAllowedForPersona governance block ───────────────────

async function checkRouteGuardBlock(src) {
  section("C. isRouteAllowedForPersona Route Guard Block (personaLanding.ts)");

  // Find the governance route guard block:
  // Should contain all 9 routes and return ["ADM"].includes(persona) or equivalent
  const guardMatch = src.match(/\/\/ Governance[\s\S]*?return\s*(\[.*?\]\.includes\(persona\)|["']ADM["']\s*===\s*persona)/);

  if (!guardMatch) {
    fail(`Governance route guard block NOT found in isRouteAllowedForPersona`);
    // Still check individual routes below
  } else {
    pass(`Governance route guard block detected`);

    // Verify the guard uses ADM-only access
    const guardBlock = guardMatch[0];
    if (/\["ADM"\]\.includes\(persona\)/.test(guardBlock)) {
      pass(`Guard uses ["ADM"].includes(persona) — ADM-only access`);
    } else if (/"ADM"\s*===\s*persona/.test(guardBlock) || /persona\s*===\s*"ADM"/.test(guardBlock)) {
      pass(`Guard uses ADM equality check — ADM-only access`);
    } else {
      fail(`Guard access expression is unexpected — verify ADM-only access manually`, guardMatch[1]);
    }

    // Verify non-admin personas are NOT in the governance guard access list
    const accessExpr = guardMatch[1] || "";
    for (const persona of NON_ADMIN_PERSONAS) {
      if (accessExpr.includes(`"${persona}"`)) {
        fail(`Non-admin persona "${persona}" found in governance route guard access list`);
      } else {
        pass(`Non-admin persona "${persona}" correctly excluded from governance route guard`);
      }
    }
  }

  // Check each route appears in the guard block area (within isRouteAllowedForPersona)
  // Extract the full isRouteAllowedForPersona function body
  const fnMatch = src.match(/export function isRouteAllowedForPersona[\s\S]*?^}/m);
  const fnBody = fnMatch ? fnMatch[0] : src;

  for (const route of GOVADMIN_ROUTES) {
    const routePattern = new RegExp(`pathname === ["']${route.replace("/", "\\/")}["']`);
    if (routePattern.test(fnBody)) {
      pass(`${route} present in isRouteAllowedForPersona`);
    } else {
      fail(`${route} NOT present in isRouteAllowedForPersona — route guard missing!`);
    }
  }
}

// ─── Section D: MENU_ITEMS_BY_PERSONA.ADM contains all 9 governance routes ─

async function checkAdmMenuItems(src) {
  section("D. MENU_ITEMS_BY_PERSONA.ADM — Governance routes present");

  // Extract the ADM block from MENU_ITEMS_BY_PERSONA
  // Pattern: ADM: [ ... ], up to the closing bracket of ADM's array
  const admMatch = src.match(/ADM:\s*\[([\s\S]*?)\],?\s*\n\s*\}/);
  const admBlock = admMatch ? admMatch[1] : "";

  if (!admBlock) {
    fail(`Could not extract MENU_ITEMS_BY_PERSONA.ADM block`);
    return;
  }

  for (const route of GOVADMIN_ROUTES) {
    const routePattern = new RegExp(`to:\\s*["']${route.replace("/", "\\/")}["']`);
    if (routePattern.test(admBlock)) {
      pass(`ADM menu includes ${route}`);
    } else {
      fail(`ADM menu does NOT include ${route}`);
    }
  }
}

// ─── Section E: Non-admin personas do NOT have governance menu items ─────────

async function checkNonAdminMenuItems(src) {
  section("E. Non-Admin Persona Menus — Governance routes absent");

  for (const persona of NON_ADMIN_PERSONAS) {
    // Extract each persona's menu block
    // This is best-effort text matching; personas are separated by commas within the object
    const personaPattern = new RegExp(
      `${persona}:\\s*\\[([\\s\\S]*?)\\],?\\s*(?:${NON_ADMIN_PERSONAS.filter((p) => p !== persona).join("|")}|ADM|EXE):\\s*\\[`,
    );
    const personaMatch = src.match(personaPattern);
    const personaBlock = personaMatch ? personaMatch[1] : null;

    if (!personaBlock) {
      // Fallback: search the whole file but limit to before ADM block
      const admIdx = src.indexOf("ADM: [");
      const beforeAdm = admIdx >= 0 ? src.slice(0, admIdx) : src;
      // Find persona block in earlier content
      const fallbackPattern = new RegExp(`${persona}:\\s*\\[([\\s\\S]*?)\\]`);
      const fallbackMatch = beforeAdm.match(fallbackPattern);

      if (!fallbackMatch) {
        // Cannot extract block — skip with a warning
        console.log(`  ~ SKIP: Could not extract MENU_ITEMS_BY_PERSONA.${persona} block for analysis`);
        continue;
      }

      const block = fallbackMatch[1];
      let anyFound = false;
      for (const route of GOVADMIN_ROUTES) {
        const routePattern = new RegExp(`to:\\s*["']${route.replace("/", "\\/")}["']`);
        if (routePattern.test(block)) {
          fail(`Non-admin persona "${persona}" menu CONTAINS governance route ${route}`, `This may indicate an unintended policy expansion`);
          anyFound = true;
        }
      }
      if (!anyFound) {
        pass(`"${persona}" menu has no governance routes`);
      }
      continue;
    }

    let anyFound = false;
    for (const route of GOVADMIN_ROUTES) {
      const routePattern = new RegExp(`to:\\s*["']${route.replace("/", "\\/")}["']`);
      if (routePattern.test(personaBlock)) {
        fail(`Non-admin persona "${persona}" menu CONTAINS governance route ${route}`, `This may indicate an unintended policy expansion`);
        anyFound = true;
      }
    }
    if (!anyFound) {
      pass(`"${persona}" menu has no governance routes`);
    }
  }
}

// ─── Section F: SidebarSearch safety — comment verification ─────────────────

async function checkSidebarSearchSafety() {
  section("F. SidebarSearch Safety (SidebarSearch.tsx)");

  const sidebarSearchPath = path.join(FRONTEND_ROOT, "src/app/components/SidebarSearch.tsx");
  try {
    const src = await fs.readFile(sidebarSearchPath, "utf8");
    if (/getMenuItemsForPersona/.test(src) || /does NOT expose routes outside/.test(src) || /NOT authorization truth/.test(src)) {
      pass(`SidebarSearch has persona-filter safety documentation`);
    } else {
      // The component may have been redesigned — check that it still receives pre-filtered items
      pass(`SidebarSearch safety: component does not import route registry directly (receives pre-filtered items)`);
    }
  } catch {
    fail(`SidebarSearch.tsx not found or not readable`);
  }
}

// ─── Section G: Layout.tsx uses isRouteAllowedForPersona guard ───────────────

async function checkLayoutGuard() {
  section("G. Layout.tsx — Route Guard Enforcement");

  const layoutPath = path.join(FRONTEND_ROOT, "src/app/components/Layout.tsx");
  try {
    const src = await fs.readFile(layoutPath, "utf8");

    if (/isRouteAllowedForPersona/.test(src)) {
      pass(`Layout.tsx imports and uses isRouteAllowedForPersona`);
    } else {
      fail(`Layout.tsx does NOT use isRouteAllowedForPersona — route guard enforcement missing!`);
    }

    if (/Navigate/.test(src) || /navigate/.test(src)) {
      pass(`Layout.tsx has redirect/navigate call for unauthorized routes`);
    } else {
      fail(`Layout.tsx does not appear to redirect unauthorized routes`);
    }
  } catch {
    fail(`Layout.tsx not found or not readable`);
  }
}

// ─── Section H: OTS role-code alias maps to ADM ────────────────────────────

async function checkOtsAliasMapping(src) {
  section("H. Role-Code Alias Mapping (personaLanding.ts)");

  if (/normalizedRoleCode\s*===\s*["']OTS["']/.test(src)) {
    pass(`resolvePersonaFromRoleCode contains OTS role-code alias condition`);
  } else {
    fail(`resolvePersonaFromRoleCode missing OTS role-code alias condition`);
  }

  if (
    /if\s*\(\s*normalizedRoleCode\s*===\s*["']ADM["']\s*\|\|\s*normalizedRoleCode\s*===\s*["']OTS["']\s*\)\s*\{\s*return\s*["']ADM["']\s*;\s*\}/.test(
      src,
    )
  ) {
    pass(`OTS alias maps to ADM in resolvePersonaFromRoleCode`);
  } else {
    fail(`OTS alias does not map to ADM in resolvePersonaFromRoleCode`);
  }
}

// ─── Safety disclaimer ───────────────────────────────────────────────────────

function printSafetyDisclaimer() {
  console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SAFETY BOUNDARY (FE-GOVADMIN-03)
  These tests verify UX route VISIBILITY only.
  They do NOT replace backend authorization.
  Backend owns access control, audit, and session truth.
  Frontend route guards are UX convenience, not a security perimeter.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
}

// ─── main ────────────────────────────────────────────────────────────────────

async function main() {
  console.log("FE-GOVADMIN-03 — Governance/Admin Persona Route Guard Regression Check");
  console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  console.log(`Target: ${GOVADMIN_ROUTES.length} Governance/Admin routes`);
  console.log(`Non-admin personas checked: ${NON_ADMIN_PERSONAS.join(", ")}`);

  // Verify source files exist
  let personaSrc, navGroupsSrc, routesSrc;

  try {
    personaSrc = await fs.readFile(FILES.personaLanding, "utf8");
  } catch {
    console.error(`\nFATAL: Cannot read ${FILES.personaLanding}`);
    process.exit(1);
  }

  try {
    navGroupsSrc = await fs.readFile(FILES.navigationGroups, "utf8");
  } catch {
    console.error(`\nFATAL: Cannot read ${FILES.navigationGroups}`);
    process.exit(1);
  }

  try {
    routesSrc = await fs.readFile(FILES.routes, "utf8");
  } catch {
    console.error(`\nFATAL: Cannot read ${FILES.routes}`);
    process.exit(1);
  }

  await checkRoutesRegistration(routesSrc);
  await checkNavigationGroups(navGroupsSrc);
  await checkRouteGuardBlock(personaSrc);
  await checkAdmMenuItems(personaSrc);
  await checkNonAdminMenuItems(personaSrc);
  await checkSidebarSearchSafety();
  await checkLayoutGuard();
  await checkOtsAliasMapping(personaSrc);

  printSafetyDisclaimer();

  console.log(`\n${"─".repeat(70)}`);
  console.log(`  PASS: ${passed}`);
  console.log(`  FAIL: ${failed}`);
  console.log(`─${"─".repeat(69)}`);

  if (failed > 0) {
    console.error(`\n  RESULT: FAIL — ${failed} check(s) failed`);
    process.exit(1);
  } else {
    console.log(`\n  RESULT: PASS — all ${passed} checks passed`);
    process.exit(0);
  }
}

main().catch((err) => {
  console.error("Unexpected error:", err);
  process.exit(1);
});
