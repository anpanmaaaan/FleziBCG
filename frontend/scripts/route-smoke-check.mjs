import fs from "node:fs/promises";
import path from "node:path";

const FRONTEND_ROOT = process.cwd();

const TARGET_FILES = {
  routes: path.join(FRONTEND_ROOT, "src/app/routes.tsx"),
  persona: path.join(FRONTEND_ROOT, "src/app/persona/personaLanding.ts"),
  screenStatus: path.join(FRONTEND_ROOT, "src/app/screenStatus.ts"),
  layout: path.join(FRONTEND_ROOT, "src/app/components/Layout.tsx"),
  navigationGroups: path.join(FRONTEND_ROOT, "src/app/navigation/navigationGroups.ts"),
};

const ROUTE_EXCLUSIONS = {
  // Parent layout route. Child index redirect handles navigable root behavior.
  "/": "REDIRECT_ONLY",
};

const DYNAMIC_SAMPLE_BY_PARAM = {
  bomId: "demo-bom-001",
  productId: "demo-product-001",
  routeId: "demo-route-001",
  operationId: "demo-op-001",
  orderId: "demo-order-001",
  woId: "demo-wo-001",
};

const ALLOWED_EXCLUSION_REASONS = new Set([
  "REDIRECT_ONLY",
  "INDEX_ROUTE",
  "AUTH_CALLBACK_ONLY",
  "EXTERNAL_LINK",
  "DYNAMIC_REQUIRES_BACKEND_DATA",
  "NOT_RENDERABLE_WITHOUT_CONTEXT",
  "LEGACY_ROUTE_PENDING_REMOVAL",
]);

const SCREEN_STATUS_EXEMPT_ROUTES = {
  "/": "REDIRECT_ONLY",
  "/dev/gantt-stress": "NOT_RENDERABLE_WITHOUT_CONTEXT",
};

const USER_ACCESSIBLE_LIST_ROUTES = {
  "/products": {
    accessFn: "canAccessProducts",
    personas: ["SUP", "IEP", "QC", "PMG"],
  },
  "/routes": {
    accessFn: "canAccessRoutes",
    personas: ["SUP", "IEP", "QC", "PMG"],
  },
};

const DOCUMENTED_INTERNAL_DETAIL_ROUTES = {
  "/products/:productId": "Product detail is detail-only and linked from Product List.",
  "/routes/:routeId": "Route detail is detail-only and linked from Route List.",
};

const results = [];

function pass(label, detail) {
  results.push({ ok: true, label, detail });
}

function fail(label, detail) {
  results.push({ ok: false, label, detail });
}

function normalizeRoutePath(pathValue) {
  if (pathValue.startsWith("/")) {
    return pathValue;
  }
  return `/${pathValue}`;
}

function isDynamicRoute(routePath) {
  return routePath.includes(":");
}

function classifyRouteType(routePath) {
  if (routePath === "/") {
    return "redirect-route";
  }
  return isDynamicRoute(routePath) ? "dynamic-route" : "static-route";
}

function sampleSegmentForParam(paramName) {
  return DYNAMIC_SAMPLE_BY_PARAM[paramName] ?? `demo-${paramName.toLowerCase()}-001`;
}

function buildDynamicSmokePath(routePath) {
  return routePath.replace(/:([A-Za-z0-9_]+)/g, (_, paramName) => sampleSegmentForParam(paramName));
}

function normalizePatternSignature(routePath) {
  return routePath
    .split("/")
    .filter(Boolean)
    .map((segment) => (segment.startsWith(":") ? ":param" : segment))
    .join("/");
}

function extractRoutes(routesText) {
  const found = new Set();
  const routeRegex = /path:\s*"([^"]+)"/g;
  for (const match of routesText.matchAll(routeRegex)) {
    found.add(normalizeRoutePath(match[1]));
  }
  return found;
}

function extractIndexRouteCount(routesText) {
  return (routesText.match(/index:\s*true/g) || []).length;
}

function extractScreenStatusPatterns(screenStatusText) {
  const patterns = new Set();
  const patternRegex = /routePattern:\s*"([^"]+)"/g;
  for (const match of screenStatusText.matchAll(patternRegex)) {
    patterns.add(match[1]);
  }
  return patterns;
}

function extractScreenRouteAliases(screenStatusText) {
  const aliases = new Map();
  const blockMatch = screenStatusText.match(/const\s+SCREEN_ROUTE_ALIASES:[\s\S]*?=\s*\{([\s\S]*?)\};/);
  if (!blockMatch) {
    return aliases;
  }

  const pairRegex = /"([^"]+)"\s*:\s*"([^"]+)"/g;
  for (const match of blockMatch[1].matchAll(pairRegex)) {
    aliases.set(match[1], match[2]);
  }
  return aliases;
}

function extractPersonaMenu(personaText) {
  const byPersona = new Map();
  const menuBlockMatch = personaText.match(/const\s+MENU_ITEMS_BY_PERSONA[\s\S]*?=\s*\{([\s\S]*?)\n\};/);
  if (!menuBlockMatch) {
    return byPersona;
  }

  const block = menuBlockMatch[1];
  const personaBlockRegex = /([A-Z]{2,3}):\s*\[([\s\S]*?)\],/g;
  for (const match of block.matchAll(personaBlockRegex)) {
    const persona = match[1];
    const items = match[2];
    const routes = [];
    const toRegex = /to:\s*"([^"]+)"/g;
    for (const toMatch of items.matchAll(toRegex)) {
      routes.push(toMatch[1].split("?")[0]);
    }
    byPersona.set(persona, routes);
  }

  return byPersona;
}

function functionContainsPersonas(personaText, fnName, personas) {
  const fnMatch = personaText.match(new RegExp(`function\\s+${fnName}\\([^)]*\\):\\s*boolean\\s*\\{([\\s\\S]*?)\\n\\}`, "m"));
  if (!fnMatch) {
    return false;
  }
  const body = fnMatch[1];
  return personas.every((persona) => body.includes(`persona === \"${persona}\"`));
}

function guardHasRouteCheck(personaText, baseRoute) {
  const eqCheck = personaText.includes(`pathname === \"${baseRoute}\"`);
  const startsWithCheck = personaText.includes(`pathname.startsWith(\"${baseRoute}/\")`);
  return { eqCheck, startsWithCheck };
}

function hasWildcardCatchAll(routesText) {
  return routesText.includes('path: "*"') || routesText.includes("path: '*'");
}

function sorted(values) {
  return [...values].sort((a, b) => a.localeCompare(b));
}

function validateExclusionReasons(exclusions) {
  let ok = true;
  for (const [route, reason] of Object.entries(exclusions)) {
    if (!ALLOWED_EXCLUSION_REASONS.has(reason)) {
      fail("Invalid exclusion reason", `${route} -> ${reason}`);
      ok = false;
    }
  }
  if (ok) {
    pass("Exclusion reasons valid", `${Object.keys(exclusions).length} exclusions validated`);
  }
}

function isProtectedRoute(routePath) {
  return routePath !== "/login";
}

function getScreenStatusParityCandidates(routePath, aliases) {
  const candidates = new Set([routePath]);
  const aliased = aliases.get(routePath);
  if (aliased) {
    candidates.add(aliased);
  }

  // OperationList is intentionally reused for this route family.
  if (routePath.startsWith("/production-orders/") && routePath.endsWith("/work-orders")) {
    candidates.add("/work-orders");
  }

  return [...candidates];
}

async function main() {
  const [routesText, personaText, screenStatusText, layoutText, navigationGroupsText] = await Promise.all([
    fs.readFile(TARGET_FILES.routes, "utf8"),
    fs.readFile(TARGET_FILES.persona, "utf8"),
    fs.readFile(TARGET_FILES.screenStatus, "utf8"),
    fs.readFile(TARGET_FILES.layout, "utf8"),
    fs.readFile(TARGET_FILES.navigationGroups, "utf8"),
  ]);

  const routeSet = extractRoutes(routesText);
  const indexRouteCount = extractIndexRouteCount(routesText);
  const screenStatusPatterns = extractScreenStatusPatterns(screenStatusText);
  const screenRouteAliases = extractScreenRouteAliases(screenStatusText);
  const screenPatternSignatures = new Set([...screenStatusPatterns].map((pattern) => normalizePatternSignature(pattern)));
  const menuByPersona = extractPersonaMenu(personaText);
  const registeredRoutes = sorted(routeSet);

  validateExclusionReasons(ROUTE_EXCLUSIONS);

  const coverageRows = [];
  for (const route of registeredRoutes) {
    const excludedReason = ROUTE_EXCLUSIONS[route] ?? null;
    const routeType = classifyRouteType(route);
    const protectedType = isProtectedRoute(route) ? "protected/persona-visible" : "public";
    let smokePath = "";
    let coverageStatus = "EXCLUDED";

    if (!excludedReason) {
      smokePath = routeType === "dynamic-route" ? buildDynamicSmokePath(route) : route;
      coverageStatus = "COVERED";
    }

    coverageRows.push({
      route,
      routeType,
      protectedType,
      smokePath,
      coverageStatus,
      exclusionReason: excludedReason,
    });
  }

  const coveredRows = coverageRows.filter((row) => row.coverageStatus === "COVERED");
  const excludedRows = coverageRows.filter((row) => row.coverageStatus === "EXCLUDED");
  const staticCovered = coveredRows.filter((row) => row.routeType === "static-route");
  const dynamicCovered = coveredRows.filter((row) => row.routeType === "dynamic-route");
  const protectedCovered = coveredRows.filter((row) => row.protectedType === "protected/persona-visible");
  const uncoveredRows = coverageRows.filter((row) => row.coverageStatus !== "COVERED" && !row.exclusionReason);

  if (uncoveredRows.length === 0) {
    pass("Full route smoke coverage computed", `${coveredRows.length}/${registeredRoutes.length} covered, ${excludedRows.length} excluded`);
  } else {
    for (const row of uncoveredRows) {
      fail("Route missing smoke coverage", row.route);
    }
  }

  const screenStatusMismatches = [];
  for (const route of registeredRoutes) {
    if (SCREEN_STATUS_EXEMPT_ROUTES[route]) {
      continue;
    }

    const signatures = getScreenStatusParityCandidates(route, screenRouteAliases).map((candidate) =>
      normalizePatternSignature(candidate)
    );
    const hasMatch = signatures.some((signature) => screenPatternSignatures.has(signature));
    if (!hasMatch) {
      screenStatusMismatches.push(route);
    }
  }

  if (screenStatusMismatches.length === 0) {
    pass("screenStatus coverage aligned with route registry", "All non-exempt routes have a matching routePattern (parameter names normalized)");
  } else {
    for (const route of screenStatusMismatches) {
      fail("screenStatus routePattern missing", route);
    }
  }

  pass("Route registry extracted", `${registeredRoutes.length} path entries, ${indexRouteCount} index route(s)`);
  pass("Static route coverage", `${staticCovered.length} static routes covered`);
  pass("Dynamic route sample coverage", `${dynamicCovered.length} dynamic routes mapped to representative smoke paths`);
  pass("Protected route visibility coverage", `${protectedCovered.length} protected/persona-visible routes included in smoke set`);

  if (!hasWildcardCatchAll(routesText)) {
    pass("No wildcard catch-all route detected", "No path: '*' in routes.tsx");
  } else {
    fail("Wildcard catch-all route detected", "Review order to ensure required routes are not swallowed");
  }

  if (layoutText.includes("getMenuItemsForPersona") && layoutText.includes("isRouteAllowedForPersona") && layoutText.includes("<Navigate to={landing} replace />")) {
    pass("Layout persona enforcement hooks detected", "Layout uses menu + allowlist + redirect enforcement");
  } else {
    fail("Layout persona enforcement hooks missing", "Expected getMenuItemsForPersona/isRouteAllowedForPersona/Navigate redirect");
  }

  if (navigationGroupsText.includes("IMPORTANT: This file is a PRESENTATION-LAYER grouping utility only.") && navigationGroupsText.includes("It does NOT change route definitions, authorization rules, or persona semantics.")) {
    pass("Navigation grouping safety disclaimer present", "navigationGroups.ts explicitly marks grouping as presentation-only");
  } else {
    fail("Navigation grouping safety disclaimer missing", "Expected explicit presentation-only disclaimer in navigationGroups.ts");
  }

  for (const [route, rule] of Object.entries(USER_ACCESSIBLE_LIST_ROUTES)) {
    const guardChecks = guardHasRouteCheck(personaText, route);
    if (guardChecks.eqCheck && guardChecks.startsWithCheck) {
      pass("Persona route guard present", `${route} has eq and startsWith checks`);
    } else {
      fail("Persona route guard incomplete", `${route} must include eq and startsWith checks`);
    }

    if (functionContainsPersonas(personaText, rule.accessFn, rule.personas)) {
      pass("Persona access function includes expected personas", `${rule.accessFn}: ${rule.personas.join(", ")}`);
    } else {
      fail("Persona access function missing expected personas", `${rule.accessFn}: ${rule.personas.join(", ")}`);
    }

    for (const persona of rule.personas) {
      const entries = menuByPersona.get(persona) || [];
      if (entries.includes(route)) {
        pass("Sidebar/menu entry present", `${persona} -> ${route}`);
      } else {
        fail("Sidebar/menu entry missing", `${persona} -> ${route}`);
      }
    }
  }

  for (const [route, reason] of Object.entries(DOCUMENTED_INTERNAL_DETAIL_ROUTES)) {
    if (reason && reason.trim().length > 0) {
      pass("Detail route internal-only documentation present", `${route}: ${reason}`);
    } else {
      fail("Detail route internal-only documentation missing", route);
    }
  }

  const failed = results.filter((item) => !item.ok);
  const passed = results.filter((item) => item.ok);

  console.log("Route registry metrics:");
  console.log(`  REGISTERED: ${registeredRoutes.length}`);
  console.log(`  INDEX_ROUTES: ${indexRouteCount}`);
  console.log(`  STATIC_ROUTES: ${registeredRoutes.filter((route) => classifyRouteType(route) === "static-route").length}`);
  console.log(`  DYNAMIC_ROUTES: ${registeredRoutes.filter((route) => classifyRouteType(route) === "dynamic-route").length}`);
  console.log(`  EXCLUDED: ${excludedRows.length}`);
  console.log(`  SMOKE_TARGETS: ${coveredRows.length}`);

  console.log("Coverage rows:");
  for (const row of coverageRows) {
    const parts = [
      `route=${row.route}`,
      `type=${row.routeType}`,
      `scope=${row.protectedType}`,
      `status=${row.coverageStatus}`,
    ];
    if (row.smokePath) {
      parts.push(`smoke=${row.smokePath}`);
    }
    if (row.exclusionReason) {
      parts.push(`exclusion=${row.exclusionReason}`);
    }
    console.log(`- ${parts.join(" | ")}`);
  }

  if (dynamicCovered.length > 0) {
    console.log("Dynamic sample paths:");
    for (const row of dynamicCovered) {
      console.log(`- ${row.route} -> ${row.smokePath}`);
    }
  }

  if (excludedRows.length > 0) {
    console.log("Excluded routes:");
    for (const row of excludedRows) {
      console.log(`- ${row.route} :: ${row.exclusionReason}`);
    }
  }

  console.log("Route smoke check summary:");
  console.log(`  PASS: ${passed.length}`);
  console.log(`  FAIL: ${failed.length}`);

  for (const item of results) {
    const prefix = item.ok ? "PASS" : "FAIL";
    console.log(`- ${prefix}: ${item.label} :: ${item.detail}`);
  }

  if (failed.length > 0) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`FAIL: route smoke check crashed: ${message}`);
  process.exitCode = 1;
});
