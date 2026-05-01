/**
 * Screen Status Registry — FleziBCG FE-1 Guardrails
 *
 * Classifies every registered route by its data connection maturity.
 * Used by PagePhaseBanner and ScreenStatusBadge to surface accurate
 * screen-phase labels to developers and operators.
 *
 * Phases:
 *   CONNECTED  — real backend API, no mock data
 *   PARTIAL    — mix of real API and placeholder data
 *   MOCK       — all data from static fixture / hardcoded
 *   SHELL      — page shell only, no data or routing intent
 *   FUTURE     — planned screen, not yet implemented
 *   DISABLED   — intentionally disabled
 *   UNKNOWN    — classification not yet assessed
 *
 * Data sources:
 *   BACKEND_API   — fetches from real /v1/... endpoints
 *   MOCK_FIXTURE  — reads from src/app/data/ or inline constants
 *   MIXED         — some real, some mock
 *   NONE          — no data
 */

export type ScreenPhase =
  | "CONNECTED"
  | "PARTIAL"
  | "MOCK"
  | "SHELL"
  | "FUTURE"
  | "DISABLED"
  | "UNKNOWN";

export type DataSource = "BACKEND_API" | "MOCK_FIXTURE" | "MIXED" | "NONE";

export interface ScreenStatusEntry {
  routePattern: string;
  phase: ScreenPhase;
  dataSource: DataSource;
  notes?: string;
}

export interface ScreenStatusMatch {
  screenId: string;
  entry: ScreenStatusEntry;
}

export const SCREEN_STATUS_REGISTRY: Record<string, ScreenStatusEntry> = {
  login: {
    routePattern: "/login",
    phase: "CONNECTED",
    dataSource: "BACKEND_API",
  },
  home: {
    routePattern: "/home",
    phase: "MOCK",
    dataSource: "MOCK_FIXTURE",
    notes: "Station/line data is hardcoded. Not connected to station API.",
  },
  dashboard: {
    routePattern: "/dashboard",
    phase: "CONNECTED",
    dataSource: "BACKEND_API",
  },
  oeeDeepDive: {
    routePattern: "/performance/oee-deep-dive",
    phase: "MOCK",
    dataSource: "MOCK_FIXTURE",
    notes:
      "All OEE metrics, six big losses, and AI insight panels come from oee-mock-data.ts. No live OEE API connected.",
  },
  productionOrders: {
    routePattern: "/production-orders",
    phase: "CONNECTED",
    dataSource: "BACKEND_API",
  },
  productList: {
    routePattern: "/products",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "Product list reads backend API. Create action remains disabled in FE-4A.",
  },
  productDetail: {
    routePattern: "/products/:productId",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "Product detail reads backend API. Lifecycle mutation actions remain disabled in FE-4A.",
  },
  dispatchQueue: {
    routePattern: "/dispatch",
    phase: "MOCK",
    dataSource: "MOCK_FIXTURE",
    notes: "Dispatch queue is hardcoded fixture data. No dispatch API connected.",
  },
  routeList: {
    routePattern: "/routes",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "Routing list reads backend API. Create/update/release actions remain disabled in FE-5 read-only slice.",
  },
  routeDetail: {
    routePattern: "/routes/:routeId",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "Routing detail reads backend API and operations list. Lifecycle and mutation actions remain disabled in FE-5 read-only slice.",
  },
  workOrders: {
    routePattern: "/work-orders",
    phase: "CONNECTED",
    dataSource: "BACKEND_API",
  },
  workOrderOperations: {
    routePattern: "/work-orders/:woId/operations",
    phase: "CONNECTED",
    dataSource: "BACKEND_API",
  },
  globalOperations: {
    routePattern: "/operations",
    phase: "CONNECTED",
    dataSource: "BACKEND_API",
  },
  operationDetail: {
    routePattern: "/operations/:operationId/detail",
    phase: "PARTIAL",
    dataSource: "MIXED",
    notes:
      "Operation header, status, and KPIs are real. Quality, Materials, Timeline, and Documents tabs contain placeholder data.",
  },
  stationExecution: {
    routePattern: "/station",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes:
      "Execution actions are connected to the real API. This screen uses the compatibility claim model. Target design is session-owned execution (STX-000/001/002 v4.0).",
  },
  qcCheckpoints: {
    routePattern: "/quality",
    phase: "MOCK",
    dataSource: "MOCK_FIXTURE",
    notes: "QC checkpoint data is hardcoded. No quality management API connected.",
  },
  defectManagement: {
    routePattern: "/defects",
    phase: "MOCK",
    dataSource: "MOCK_FIXTURE",
    notes: "Defect records are hardcoded fixture data. No defect management API connected.",
  },
  traceability: {
    routePattern: "/traceability",
    phase: "MOCK",
    dataSource: "MOCK_FIXTURE",
    notes: "Serial/lot data and genealogy graph are hardcoded. No traceability API connected.",
  },
  apsScheduling: {
    routePattern: "/scheduling",
    phase: "MOCK",
    dataSource: "MOCK_FIXTURE",
    notes: "Scheduled orders and APS metrics are hardcoded. No APS engine API connected.",
  },
  settings: {
    routePattern: "/settings",
    phase: "SHELL",
    dataSource: "NONE",
    notes: "Settings screen is a placeholder. Currently redirects to Dashboard.",
  },
  userManagement: {
    routePattern: "/users",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "User management interface is a shell. Backend IAM system manages actual users, roles, and authentication.",
  },
  roleManagement: {
    routePattern: "/roles",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Role management interface is a shell. Backend RBAC system defines actual role permissions.",
  },
  actionRegistry: {
    routePattern: "/action-registry",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Action registry is read-only shell for visualization. Backend authorization system remains source of truth.",
  },
  scopeAssignments: {
    routePattern: "/scope-assignments",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Scope assignment interface is a shell. Backend tenant isolation and RBAC manage actual scopes.",
  },
  sessionManagement: {
    routePattern: "/sessions",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Session management interface is a shell. Backend authentication system manages actual sessions.",
  },
  auditLog: {
    routePattern: "/audit-log",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Audit log display is a shell for visualization. Backend compliance system maintains immutable audit records.",
  },
  securityEvents: {
    routePattern: "/security-events",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Security events interface is a shell. Backend security system manages threat detection and incident response.",
  },
  tenantSettings: {
    routePattern: "/tenant-settings",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Tenant settings interface is a shell. Backend multi-tenant system manages actual tenant configurations.",
  },
  plantHierarchy: {
    routePattern: "/plant-hierarchy",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Plant hierarchy display is a shell for visualization. Backend master data system manages actual hierarchy.",
  },
};

const SCREEN_ROUTE_ALIASES: Record<string, string> = {
  "/station-execution": "/station",
};

function normalizePath(pathname: string): string {
  if (!pathname) return "/";
  const withoutQuery = pathname.split("?")[0].split("#")[0];
  if (withoutQuery.length > 1 && withoutQuery.endsWith("/")) {
    return withoutQuery.slice(0, -1);
  }
  return withoutQuery;
}

function toSegments(path: string): string[] {
  return path.split("/").filter(Boolean);
}

function matchesRoutePattern(routePattern: string, pathname: string): boolean {
  const patternSegments = toSegments(routePattern);
  const pathSegments = toSegments(pathname);
  if (patternSegments.length !== pathSegments.length) {
    return false;
  }
  for (let i = 0; i < patternSegments.length; i += 1) {
    const patternSegment = patternSegments[i];
    const pathSegment = pathSegments[i];
    if (patternSegment.startsWith(":")) {
      continue;
    }
    if (patternSegment !== pathSegment) {
      return false;
    }
  }
  return true;
}

function routeSpecificity(routePattern: string): number {
  return toSegments(routePattern).reduce((score, segment) => {
    return segment.startsWith(":") ? score : score + 1;
  }, 0);
}

export function getScreenStatusMatchByRoute(pathname: string): ScreenStatusMatch | undefined {
  const normalizedPath = normalizePath(pathname);
  const aliasedPath = SCREEN_ROUTE_ALIASES[normalizedPath] ?? normalizedPath;

  const matches: ScreenStatusMatch[] = Object.entries(SCREEN_STATUS_REGISTRY)
    .filter(([, entry]) => matchesRoutePattern(entry.routePattern, aliasedPath))
    .map(([screenId, entry]) => ({ screenId, entry }));

  if (matches.length === 0) {
    return undefined;
  }

  return matches.sort((a, b) => {
    return routeSpecificity(b.entry.routePattern) - routeSpecificity(a.entry.routePattern);
  })[0];
}

export function getScreenStatusByRoute(pathname: string): ScreenStatusEntry | undefined {
  return getScreenStatusMatchByRoute(pathname)?.entry;
}

export function getScreenStatusByScreenId(screenId: string): ScreenStatusEntry | undefined {
  return SCREEN_STATUS_REGISTRY[screenId];
}

export function isMockLikeStatus(phase: ScreenPhase): boolean {
  return phase === "MOCK" || phase === "PARTIAL";
}

export function isFutureLikeStatus(phase: ScreenPhase): boolean {
  return phase === "FUTURE" || phase === "SHELL" || phase === "DISABLED";
}
