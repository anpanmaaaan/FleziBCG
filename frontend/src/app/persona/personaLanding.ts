import type { AuthUser } from "@/app/api";

export type Persona = "OPR" | "SUP" | "IEP" | "QC" | "PMG" | "EXE" | "ADM";
export type ResolvedPersona = Persona | "DENY";
export type OperationLens = "supervisor" | "ie" | "qc";
export type PersonaEnforcementMode = "DEV" | "STRICT";

export interface PersonaMenuItem {
  label: string;
  to: string;
}

const DEFAULT_LANDING_BY_PERSONA: Record<Persona, string> = {
  OPR: "/station",
  SUP: "/operations?lens=supervisor",
  IEP: "/operations?lens=ie",
  QC: "/operations?lens=qc",
  PMG: "/dashboard",
  EXE: "/dashboard",
  ADM: "/dashboard",
};

const MENU_ITEMS_BY_PERSONA: Record<Persona, PersonaMenuItem[]> = {
  OPR: [{ label: "Station Execution", to: "/station" }],
  SUP: [
    { label: "Global Operations", to: "/operations?lens=supervisor" },
    { label: "Production Orders", to: "/production-orders" },
    { label: "Work Orders", to: "/work-orders" },
    { label: "Products", to: "/products" },
    { label: "Routes", to: "/routes" },
    { label: "Quality", to: "/quality" },
    { label: "Defects", to: "/defects" },
  ],
  IEP: [
    { label: "Global Operations", to: "/operations?lens=ie" },
    { label: "Production Orders", to: "/production-orders" },
    { label: "Work Orders", to: "/work-orders" },
    { label: "Products", to: "/products" },
    { label: "Routes", to: "/routes" },
    { label: "Traceability", to: "/traceability" },
    { label: "Quality", to: "/quality" },
  ],
  QC: [
    { label: "Global Operations", to: "/operations?lens=qc" },
    { label: "Quality", to: "/quality" },
    { label: "Defects", to: "/defects" },
    { label: "Traceability", to: "/traceability" },
    { label: "Production Orders", to: "/production-orders" },
    { label: "Work Orders", to: "/work-orders" },
    { label: "Products", to: "/products" },
    { label: "Routes", to: "/routes" },
  ],
  PMG: [
    { label: "Dashboard", to: "/dashboard" },
    { label: "OEE Deep Dive", to: "/performance/oee-deep-dive" },
    { label: "Global Operations", to: "/operations" },
    { label: "Production Orders", to: "/production-orders" },
    { label: "Work Orders", to: "/work-orders" },
    { label: "Products", to: "/products" },
    { label: "Routes", to: "/routes" },
    { label: "Dispatch", to: "/dispatch" },
    { label: "Quality", to: "/quality" },
    { label: "Defects", to: "/defects" },
    { label: "Traceability", to: "/traceability" },
    { label: "Scheduling", to: "/scheduling" },
  ],
  EXE: [{ label: "Dashboard", to: "/dashboard" }],
  ADM: [
    { label: "Dashboard", to: "/dashboard" },
    { label: "Settings", to: "/settings" },
  ],
};

const ALLOWED_LENSES_BY_PERSONA: Record<Persona, OperationLens[]> = {
  OPR: [],
  SUP: ["supervisor"],
  IEP: ["ie"],
  QC: ["qc"],
  PMG: ["supervisor", "ie", "qc"],
  EXE: [],
  ADM: [],
};

const PERSONA_ENFORCEMENT_MODE: PersonaEnforcementMode =
  (import.meta.env.VITE_PERSONA_ENFORCEMENT_MODE ?? "DEV") === "STRICT" ? "STRICT" : "DEV";

const resolverLogKeys = new Set<string>();

function logResolverOnce(level: "warn" | "error", key: string, message: string): void {
  if (resolverLogKeys.has(key)) {
    return;
  }

  resolverLogKeys.add(key);
  if (level === "error") {
    console.error(message);
    return;
  }

  console.warn(message);
}

function normalizeRoleCode(roleCode?: string | null): string {
  if (!roleCode) {
    return "";
  }

  return roleCode.trim().toUpperCase();
}

export function resolvePersonaFromRoleCode(roleCode?: string | null): ResolvedPersona {
  const normalizedRoleCode = normalizeRoleCode(roleCode);

  if (normalizedRoleCode === "OPR") {
    return "OPR";
  }
  if (normalizedRoleCode === "SUP") {
    return "SUP";
  }
  if (normalizedRoleCode === "IEP") {
    return "IEP";
  }
  if (normalizedRoleCode === "QCI" || normalizedRoleCode === "QAL") {
    return "QC";
  }
  if (normalizedRoleCode === "PMG") {
    return "PMG";
  }
  if (normalizedRoleCode === "EXE") {
    return "EXE";
  }
  if (normalizedRoleCode === "ADM" || normalizedRoleCode === "OTS") {
    return "ADM";
  }
  if (normalizedRoleCode === "PLN" || normalizedRoleCode === "INV") {
    return "PMG";
  }

  if (PERSONA_ENFORCEMENT_MODE === "STRICT") {
    logResolverOnce(
      "error",
      `STRICT:${normalizedRoleCode || "MISSING"}`,
      `[persona] STRICT mode access denied for unresolved role_code: ${normalizedRoleCode || "<missing>"}`,
    );
    return "DENY";
  }

  logResolverOnce(
    "warn",
    `DEV:${normalizedRoleCode || "MISSING"}`,
    `[persona] DEV mode fallback to PMG for unresolved role_code: ${normalizedRoleCode || "<missing>"}`,
  );
  return "PMG";
}

export function getPersonaEnforcementMode(): PersonaEnforcementMode {
  return PERSONA_ENFORCEMENT_MODE;
}

export function resolvePersonaFromUser(currentUser: AuthUser | null): ResolvedPersona {
  return resolvePersonaFromRoleCode(currentUser?.role_code);
}

export function getDefaultLandingForPersona(persona: ResolvedPersona): string {
  if (persona === "DENY") {
    return "/";
  }

  return DEFAULT_LANDING_BY_PERSONA[persona];
}

export function getMenuItemsForPersona(persona: ResolvedPersona): PersonaMenuItem[] {
  if (persona === "DENY") {
    return [];
  }

  return MENU_ITEMS_BY_PERSONA[persona];
}

export function getAllowedOperationLenses(persona: ResolvedPersona): OperationLens[] {
  if (persona === "DENY") {
    return [];
  }

  return ALLOWED_LENSES_BY_PERSONA[persona];
}

export function getFallbackOperationLens(persona: ResolvedPersona): OperationLens {
  const allowedLenses = getAllowedOperationLenses(persona);
  if (allowedLenses.length > 0) {
    return allowedLenses[0];
  }

  return "supervisor";
}

export function canAccessDashboard(persona: ResolvedPersona): boolean {
  return persona === "PMG" || persona === "EXE" || persona === "ADM";
}

export function canAccessStation(persona: ResolvedPersona): boolean {
  return persona === "OPR";
}

export function canAccessOperations(persona: ResolvedPersona, lens?: string | null): boolean {
  const allowedLenses = getAllowedOperationLenses(persona);
  if (allowedLenses.length === 0) {
    return false;
  }

  if (!lens) {
    return persona === "PMG";
  }

  return allowedLenses.includes(lens as OperationLens);
}

function canAccessProductionOrders(persona: ResolvedPersona): boolean {
  return persona === "SUP" || persona === "IEP" || persona === "QC" || persona === "PMG";
}

function canAccessWorkOrders(persona: ResolvedPersona): boolean {
  return canAccessProductionOrders(persona);
}

function canAccessRoutes(persona: ResolvedPersona): boolean {
  return persona === "SUP" || persona === "IEP" || persona === "QC" || persona === "PMG";
}

function canAccessProducts(persona: ResolvedPersona): boolean {
  return persona === "SUP" || persona === "IEP" || persona === "QC" || persona === "PMG";
}

function canAccessQuality(persona: ResolvedPersona): boolean {
  return persona === "SUP" || persona === "IEP" || persona === "QC" || persona === "PMG";
}

function canAccessDefects(persona: ResolvedPersona): boolean {
  return persona === "SUP" || persona === "QC" || persona === "PMG";
}

function canAccessTraceability(persona: ResolvedPersona): boolean {
  return persona === "IEP" || persona === "QC" || persona === "PMG";
}

function canAccessDispatch(persona: ResolvedPersona): boolean {
  return persona === "PMG";
}

function canAccessScheduling(persona: ResolvedPersona): boolean {
  return persona === "PMG";
}

function canAccessOeeDeepDive(persona: ResolvedPersona): boolean {
  return persona === "PMG" || persona === "EXE";
}

function canAccessSettings(persona: ResolvedPersona): boolean {
  return persona === "ADM";
}

function getNormalizedLens(search: string): string | null {
  const lens = new URLSearchParams(search).get("lens")?.trim().toLowerCase();
  return lens || null;
}

export function isRouteAllowedForPersona(persona: ResolvedPersona, pathname: string, search: string): boolean {
  if (persona === "DENY") {
    return false;
  }

  if (pathname === "/") {
    return true;
  }

  if (pathname === "/dashboard") {
    return canAccessDashboard(persona);
  }

  if (pathname === "/home") {
    return true;
  }

  if (pathname === "/operations") {
    return canAccessOperations(persona, getNormalizedLens(search));
  }

  if (pathname.startsWith("/operations/")) {
    return getAllowedOperationLenses(persona).length > 0;
  }

  if (pathname === "/station" || pathname === "/station-execution") {
    return canAccessStation(persona);
  }

  if (pathname === "/production-orders") {
    return canAccessProductionOrders(persona);
  }

  if (pathname.startsWith("/production-orders/") && pathname.endsWith("/work-orders")) {
    return canAccessWorkOrders(persona);
  }

  if (pathname === "/work-orders" || pathname.startsWith("/work-orders/")) {
    return canAccessWorkOrders(persona);
  }

  if (pathname === "/routes" || pathname.startsWith("/routes/")) {
    return canAccessRoutes(persona);
  }

  if (pathname === "/products" || pathname.startsWith("/products/")) {
    return canAccessProducts(persona);
  }

  if (pathname === "/quality") {
    return canAccessQuality(persona);
  }

  if (pathname === "/defects") {
    return canAccessDefects(persona);
  }

  if (pathname === "/traceability") {
    return canAccessTraceability(persona);
  }

  if (pathname === "/dispatch") {
    return canAccessDispatch(persona);
  }

  if (pathname === "/scheduling") {
    return canAccessScheduling(persona);
  }

  if (pathname === "/performance/oee-deep-dive") {
    return canAccessOeeDeepDive(persona);
  }

  if (pathname === "/settings") {
    return canAccessSettings(persona);
  }

  return false;
}
