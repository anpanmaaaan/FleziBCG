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
    notes: "Product detail reads backend API. Product Version create/update/release/retire intent is connected; product lifecycle actions remain disabled.",
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
      "Execution actions are connected to the real API. Session-owned execution model (STX-000/001/002 v4.0).",
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
  bomList: {
    routePattern: "/bom",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "BOM list reads backend MMD API with product-scoped lookup. Product selection is required. Mutation actions remain disabled.",
  },
  bomDetail: {
    routePattern: "/bom/:id",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "BOM detail reads backend MMD API by productId (query param) and bomId. Component display uses component_product_id as identifier. Mutation actions remain disabled.",
  },
  routingOpDetail: {
    routePattern: "/routes/:routeId/operations/:operationId",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "Routing operation detail reads backend routing API by routeId and operationId. All mutation actions remain disabled.",
  },
  resourceRequirements: {
    routePattern: "/resource-requirements",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "Read integration active via routing + operation resource requirement endpoints. Mutation actions remain disabled and backend-governed.",
  },
  reasonCodes: {
    routePattern: "/reason-codes",
    phase: "PARTIAL",
    dataSource: "BACKEND_API",
    notes: "Reason code list reads backend MMD API (/v1/reason-codes). Supports domain/category/lifecycle/include_inactive filters. Create/edit/retire actions remain disabled. MMD-FULLSTACK-08.",
  },
  operationTimeline: {
    routePattern: "/operations/:operationId/timeline",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Operation event timeline is a shell. Real event history requires backend execution event system integration.",
  },
  stationSession: {
    routePattern: "/station-session",
    phase: "SHELL",
    dataSource: "NONE",
    notes: "Station session shell for to-be visualization. Session state, operator assignment, and equipment binding are backend execution truths.",
  },
  operatorIdentification: {
    routePattern: "/operator-identification",
    phase: "SHELL",
    dataSource: "NONE",
    notes: "Operator identification shell. Operator identity and authorization are verified by backend authentication and authorization system.",
  },
  equipmentBinding: {
    routePattern: "/equipment-binding",
    phase: "SHELL",
    dataSource: "NONE",
    notes: "Equipment binding shell. Equipment binding and readiness are managed by backend execution and maintenance systems.",
  },
  lineMonitor: {
    routePattern: "/line-monitor",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Line monitor shell for to-be visualization. Live line/station state is provided by backend execution projection system.",
  },
  stationMonitor: {
    routePattern: "/station-monitor",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Station monitor shell for to-be visualization. Live station execution state is provided by backend execution projection system.",
  },
  downtimeAnalysis: {
    routePattern: "/downtime-analysis",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Downtime analysis shell for to-be visualization. Downtime truth is recorded by backend execution system.",
  },
  shiftSummary: {
    routePattern: "/shift-summary",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Shift summary shell for to-be visualization. Shift summary truth is generated by backend reporting and projection system.",
  },
  supervisoryOperationDetail: {
    routePattern: "/supervisory/operations/:operationId",
    phase: "SHELL",
    dataSource: "NONE",
    notes: "Supervisory operation detail shell. Supervisory authority, override actions, and execution truth are managed by backend command and authorization system.",
  },
  qualityDashboard: {
    routePattern: "/quality-dashboard",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Quality Lite Dashboard shell. Quality evaluation and disposition are managed by the backend quality domain.",
  },
  measurementEntry: {
    routePattern: "/quality-measurements",
    phase: "SHELL",
    dataSource: "NONE",
    notes: "Measurement entry shell. Pass/fail evaluation and disposition are managed by the backend quality domain.",
  },
  qualityHolds: {
    routePattern: "/quality-holds",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Quality holds shell for supervisory review. Hold release and approval are managed by the backend quality domain.",
  },
  materialReadiness: {
    routePattern: "/material-readiness",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Material readiness shell for execution planning. Inventory truth and material availability are managed by backend inventory/material system.",
  },
  stagingKitting: {
    routePattern: "/staging-kitting",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Staging & kitting shell for material coordination. WMS transactions and material movements are managed by backend inventory/material system.",
  },
  wipBuffers: {
    routePattern: "/wip-buffers",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "WIP queue and buffers shell for production planning. WIP position and flow are managed by backend inventory/material system.",
  },

  // ── Integration shells — FE-COVERAGE-01E ──
  integrationDashboard: {
    routePattern: "/integration",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Integration Dashboard is a shell. Integration state, posting status, and reconciliation truth are managed by backend integration and ERP systems.",
  },
  externalSystems: {
    routePattern: "/integration/systems",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "External Systems Registry is a shell. Real system registration, configuration, and connection management require backend integration module.",
  },
  erpMapping: {
    routePattern: "/integration/erp-mapping",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "ERP Mapping is a shell. Real ERP field mapping, validation, and publishing require backend integration and ERP adapter modules.",
  },
  inboundMessages: {
    routePattern: "/integration/inbound",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Inbound Messages is a shell. Real message processing, acceptance, and replay are managed by backend integration event bus.",
  },
  outboundMessages: {
    routePattern: "/integration/outbound",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Outbound Messages is a shell. Real message sending and delivery confirmation are managed by backend integration event bus.",
  },
  postingRequests: {
    routePattern: "/integration/posting-requests",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Posting Requests is a shell. ERP posting truth, retry, and cancel operations are managed by backend integration and ERP adapter modules. Do not use as source of ERP posting truth.",
  },
  reconciliation: {
    routePattern: "/integration/reconciliation",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Reconciliation is a shell. MOM vs ERP/WMS reconciliation truth, discrepancy resolution, and approval are managed by backend integration and ERP reconciliation modules.",
  },
  retryQueue: {
    routePattern: "/integration/retry-queue",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Retry / Failure Queue is a shell. Real retry execution, skip, and dead-letter operations are managed by backend integration fault-tolerance module.",
  },

  // ── Reporting shells — FE-COVERAGE-01E ──
  productionPerfReport: {
    routePattern: "/reports/production-performance",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Production Performance Report is a shell. Deterministic production KPIs, plan vs actual calculations, and report exports require backend reporting module.",
  },
  qualityPerfReport: {
    routePattern: "/reports/quality-performance",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Quality Performance Report is a shell. Official quality metrics, defect rates, and NCR counts require backend quality and reporting modules.",
  },
  materialWipReport: {
    routePattern: "/reports/material-wip",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Material / WIP Report is a shell. WIP position, inventory truth, and material consumption reports require backend inventory and material modules.",
  },
  integrationStatusReport: {
    routePattern: "/reports/integration-status",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Integration Status Report is a shell. Real integration monitoring, failure rates, and message throughput require backend integration and observability modules.",
  },
  shiftReport: {
    routePattern: "/reports/shift",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Shift Report is a shell. Official shift close reports require backend reporting and shift management modules.",
  },
  downtimeReport: {
    routePattern: "/reports/downtime",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Downtime Report is a shell. Aggregated downtime analytics and official downtime reporting require backend execution and reporting modules.",
  },

  // ── AI / Intelligence shells — FE-COVERAGE-01F ──
  aiInsightsDashboard: {
    routePattern: "/ai/insights",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "AI Insights is a shell. AI advisory outputs require validated ML models and backend AI inference service. This screen does NOT produce actionable AI decisions.",
  },
  aiShiftSummary: {
    routePattern: "/ai/shift-summary",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "AI Shift Summary is a shell. Official shift summary requires backend reporting and shift management modules. AI narrative is advisory demo only.",
  },
  anomalyDetection: {
    routePattern: "/ai/anomaly-detection",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Anomaly Detection is a shell. Real anomaly detection requires backend ML inference and execution event stream integration.",
  },
  bottleneckExplanation: {
    routePattern: "/ai/bottleneck-explanation",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Bottleneck Explanation is a shell. Real bottleneck analysis requires backend execution projection and AI advisory service. AI may NOT influence execution directly.",
  },
  naturalLanguageInsight: {
    routePattern: "/ai/natural-language-insight",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Natural Language Insight is a shell. Real NL query requires backend LLM integration and operational data API. Demo queries must not be confused with live data.",
  },

  // ── Digital Twin shells — FE-COVERAGE-01F ──
  digitalTwinOverview: {
    routePattern: "/digital-twin",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Digital Twin Overview is a shell. Live twin sync requires backend deterministic projection and validated twin model. This screen does NOT show live operational state.",
  },
  twinStateGraph: {
    routePattern: "/digital-twin/state-graph",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Twin State Graph is a shell. Graph reflects static demo structure only. Real twin state requires backend projection and validated equipment/material binding.",
  },
  whatIfScenario: {
    routePattern: "/digital-twin/what-if",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "What-if Scenario is a shell. Real scenario simulation requires backend APS/planning engine. Running scenarios does NOT alter production plans.",
  },

  // ── Compliance shells — FE-COVERAGE-01F ──
  complianceRecordPackage: {
    routePattern: "/compliance/record-package",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Compliance Record Package is a shell. Official compliance records require backend quality, execution, and audit modules. Do NOT use as legally binding record.",
  },
  eSignature: {
    routePattern: "/compliance/e-signature",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "E-Signature is a shell. Real e-signature requires backend signature workflow and compliance service. Do NOT use as legally binding signature.",
  },
  electronicBatchRecord: {
    routePattern: "/compliance/electronic-batch-record",
    phase: "SHELL",
    dataSource: "MOCK_FIXTURE",
    notes: "Electronic Batch Record is a shell. Real eBR requires backend quality, execution, and compliance record modules. Do NOT use as regulated eBR record.",
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
