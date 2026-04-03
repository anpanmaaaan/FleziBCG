export type Persona =
  | "OPERATOR"
  | "SHIFT_LEADER"
  | "SUPERVISOR"
  | "MANAGER"
  | "OFFICE"
  | "IE"
  | "PROCESS"
  | "QA";

export type AppRoutePath =
  | "/station-execution"
  | "/work-orders"
  | "/dashboard"
  | "/operations"
  | "/quality";

const DEFAULT_LANDING_BY_PERSONA: Record<Persona, AppRoutePath> = {
  OPERATOR: "/station-execution",
  SHIFT_LEADER: "/work-orders",
  SUPERVISOR: "/work-orders",
  MANAGER: "/dashboard",
  OFFICE: "/dashboard",
  IE: "/operations",
  PROCESS: "/operations",
  QA: "/quality",
};

export function getDefaultLandingByPersona(persona: Persona): AppRoutePath {
  return DEFAULT_LANDING_BY_PERSONA[persona];
}

export function getCurrentPersona(): Persona | null {
  // TODO(Phase 4B): Replace with real persona source once auth/session exposes role claims.
  // This function intentionally returns null to avoid changing runtime behavior in Phase 4 prep.
  return null;
}

// TODO(Phase 4B): Apply persona landing only at controlled entry points (login + root reload).
// TODO(Phase 4B): Add guardrail helpers for read/write layer boundaries using resolved persona.
// TODO(Phase 4B): Add persona-driven menu visibility helpers after role source is wired.
