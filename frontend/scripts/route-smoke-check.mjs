import fs from "node:fs/promises";
import path from "node:path";

const FRONTEND_ROOT = process.cwd();

const TARGET_FILES = {
  routes: path.join(FRONTEND_ROOT, "src/app/routes.tsx"),
  persona: path.join(FRONTEND_ROOT, "src/app/persona/personaLanding.ts"),
  screenStatus: path.join(FRONTEND_ROOT, "src/app/screenStatus.ts"),
  layout: path.join(FRONTEND_ROOT, "src/app/components/Layout.tsx"),
};

const REQUIRED_ROUTES = [
  "/products",
  "/products/:productId",
  "/routes",
  "/routes/:routeId",
];

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

function extractRoutes(routesText) {
  const found = new Set();
  const routeRegex = /path:\s*"([^"]+)"/g;
  for (const match of routesText.matchAll(routeRegex)) {
    found.add(normalizeRoutePath(match[1]));
  }
  return found;
}

function extractScreenStatusPatterns(screenStatusText) {
  const patterns = new Set();
  const patternRegex = /routePattern:\s*"([^"]+)"/g;
  for (const match of screenStatusText.matchAll(patternRegex)) {
    patterns.add(match[1]);
  }
  return patterns;
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

async function main() {
  const [routesText, personaText, screenStatusText, layoutText] = await Promise.all([
    fs.readFile(TARGET_FILES.routes, "utf8"),
    fs.readFile(TARGET_FILES.persona, "utf8"),
    fs.readFile(TARGET_FILES.screenStatus, "utf8"),
    fs.readFile(TARGET_FILES.layout, "utf8"),
  ]);

  const routeSet = extractRoutes(routesText);
  const screenStatusPatterns = extractScreenStatusPatterns(screenStatusText);
  const menuByPersona = extractPersonaMenu(personaText);

  for (const route of REQUIRED_ROUTES) {
    if (routeSet.has(route)) {
      pass("Route registered", route);
    } else {
      fail("Route missing in routes.tsx", route);
    }

    if (screenStatusPatterns.has(route)) {
      pass("screenStatus routePattern present", route);
    } else {
      fail("screenStatus routePattern missing", route);
    }
  }

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
