import type { AuthUser } from "../api/authApi";

export type Persona = "OPR" | "SUP" | "IEP" | "QCI" | "PMG" | "EXE";
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
  QCI: "/operations?lens=qc",
  PMG: "/dashboard",
  EXE: "/dashboard",
};

const MENU_ITEMS_BY_PERSONA: Record<Persona, PersonaMenuItem[]> = {
  OPR: [{ label: "Station Execution", to: "/station" }],
  SUP: [{ label: "Global Operations", to: "/operations?lens=supervisor" }],
  IEP: [{ label: "Global Operations", to: "/operations?lens=ie" }],
  QCI: [{ label: "Global Operations", to: "/operations?lens=qc" }],
  PMG: [
    { label: "Dashboard", to: "/dashboard" },
    { label: "Global Operations", to: "/operations?lens=supervisor" },
  ],
  EXE: [{ label: "Dashboard", to: "/dashboard" }],
};

const ALLOWED_LENSES_BY_PERSONA: Record<Persona, OperationLens[]> = {
  OPR: [],
  SUP: ["supervisor"],
  IEP: ["ie"],
  QCI: ["qc"],
  PMG: ["supervisor", "ie", "qc"],
  EXE: [],
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
    return "QCI";
  }
  if (normalizedRoleCode === "PMG") {
    return "PMG";
  }
  if (normalizedRoleCode === "EXE") {
    return "EXE";
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
  return persona === "PMG" || persona === "EXE";
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

  if (pathname === "/operations") {
    return canAccessOperations(persona, getNormalizedLens(search));
  }

  if (pathname.startsWith("/operations/")) {
    return getAllowedOperationLenses(persona).length > 0;
  }

  if (pathname === "/station" || pathname === "/station-execution") {
    return canAccessStation(persona);
  }

  return false;
}
