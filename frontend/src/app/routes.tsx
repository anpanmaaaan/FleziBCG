import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { LoginPage } from "./pages/LoginPage";
import { Home } from "./pages/Home";
import { Dashboard } from "./pages/Dashboard";
import { ProductionOrderList } from "./pages/ProductionOrderList";
import { ProductList } from "./pages/ProductList";
import { ProductDetail } from "./pages/ProductDetail";
import { RouteList } from "./pages/RouteList";
import { RouteDetail } from "./pages/RouteDetail";
import { OperationList } from "./pages/OperationList";
import { OperationExecutionOverview } from "./pages/OperationExecutionOverview";
import { OperationExecutionDetail } from "./pages/OperationExecutionDetail";
import { GlobalOperationList } from "./pages/GlobalOperationList";
import { DispatchQueue } from "./pages/DispatchQueue";
import { QCCheckpoints } from "./pages/QCCheckpoints";
import { DefectManagement } from "./pages/DefectManagement";
import { Traceability } from "./pages/Traceability";
import { APSScheduling } from "./pages/APSScheduling";
import { StationExecution } from "./pages/StationExecution";
import { OEEDeepDive } from "./pages/OEEDeepDive";
import { GanttStressTestPage } from "./pages/GanttStressTestPage";
import { UserManagement } from "./pages/UserManagement";
import { RoleManagement } from "./pages/RoleManagement";
import { ActionRegistry } from "./pages/ActionRegistry";
import { ScopeAssignments } from "./pages/ScopeAssignments";
import { SessionManagement } from "./pages/SessionManagement";
import { AuditLog } from "./pages/AuditLog";
import { SecurityEvents } from "./pages/SecurityEvents";
import { TenantSettings } from "./pages/TenantSettings";
import { PlantHierarchy } from "./pages/PlantHierarchy";
import { BomList } from "./pages/BomList";
import { BomDetail } from "./pages/BomDetail";
import { RoutingOperationDetail } from "./pages/RoutingOperationDetail";
import { ResourceRequirements } from "./pages/ResourceRequirements";
import { ReasonCodes } from "./pages/ReasonCodes";
import { OperationTimeline } from "./pages/OperationTimeline";
import { StationSession } from "./pages/StationSession";
import { OperatorIdentification } from "./pages/OperatorIdentification";
import { EquipmentBinding } from "./pages/EquipmentBinding";
import { LineMonitor } from "./pages/LineMonitor";
import { StationMonitor } from "./pages/StationMonitor";
import { DowntimeAnalysis } from "./pages/DowntimeAnalysis";
import { ShiftSummary } from "./pages/ShiftSummary";
import { SupervisoryOperationDetail } from "./pages/SupervisoryOperationDetail";
import { PersonaLandingRedirect } from "./persona/PersonaLandingRedirect";
import { RequireAuth } from "./auth/RequireAuth";

export const router = createBrowserRouter([
  // Public route
  {
    path: "/login",
    Component: LoginPage,
  },
  // Protected routes
  {
    path: "/",
    element: (
      <RequireAuth>
        <Layout />
      </RequireAuth>
    ),
    children: [
      // Execution Tracking (Main)
      { index: true, Component: PersonaLandingRedirect },
      { path: "home", Component: Home },
      
      // Dashboard
      { path: "dashboard", Component: Dashboard },
      
      // Performance Analytics
      { path: "performance/oee-deep-dive", Component: OEEDeepDive },
      
      // Production Management
      { path: "production-orders", Component: ProductionOrderList },
      { path: "products", Component: ProductList },
      { path: "products/:productId", Component: ProductDetail },
      { path: "dispatch", Component: DispatchQueue },
      
      // Routes & Operations
      { path: "routes", Component: RouteList },
      { path: "routes/:routeId", Component: RouteDetail },
      { path: "routes/:routeId/operations/:operationId", Component: RoutingOperationDetail },

      // Manufacturing Master Data shells
      { path: "bom", Component: BomList },
      { path: "bom/:bomId", Component: BomDetail },
      { path: "resource-requirements", Component: ResourceRequirements },
      { path: "reason-codes", Component: ReasonCodes },
      
      // Work Order Execution Flow (3 screens)
      { path: "work-orders", Component: OperationList }, // WO Status List (all)
      { path: "production-orders/:orderId/work-orders", Component: OperationList }, // WO Status List
      { path: "work-orders/:woId/operations", Component: OperationExecutionOverview }, // WO-scoped Gantt Overview
      { path: "operations", Component: GlobalOperationList }, // Global Operation Monitoring (read-only)
      { path: "operations/:operationId/detail", Component: OperationExecutionDetail }, // Operation Detail Tabs
      { path: "operations/:operationId/timeline", Component: OperationTimeline }, // Operation Event Timeline (shell)
      
      // Execution / Supervisory shells
      { path: "station-session", Component: StationSession },
      { path: "operator-identification", Component: OperatorIdentification },
      { path: "equipment-binding", Component: EquipmentBinding },
      { path: "line-monitor", Component: LineMonitor },
      { path: "station-monitor", Component: StationMonitor },
      { path: "downtime-analysis", Component: DowntimeAnalysis },
      { path: "shift-summary", Component: ShiftSummary },
      { path: "supervisory/operations/:operationId", Component: SupervisoryOperationDetail },
      
      // Station Execution
      { path: "station", Component: StationExecution },
      { path: "station-execution", Component: StationExecution },
      
      // Quality Management
      { path: "quality", Component: QCCheckpoints },
      { path: "defects", Component: DefectManagement },
      
      // Traceability
      { path: "traceability", Component: Traceability },
      
      // APS Scheduling
      { path: "scheduling", Component: APSScheduling },

      // Foundation & Governance (Admin)
      { path: "users", Component: UserManagement },
      { path: "roles", Component: RoleManagement },
      { path: "action-registry", Component: ActionRegistry },
      { path: "scope-assignments", Component: ScopeAssignments },
      { path: "sessions", Component: SessionManagement },
      { path: "audit-log", Component: AuditLog },
      { path: "security-events", Component: SecurityEvents },
      { path: "tenant-settings", Component: TenantSettings },
      { path: "plant-hierarchy", Component: PlantHierarchy },

      // Dev-only stress harness for virtualized Gantt rows
      ...(import.meta.env.DEV ? [{ path: "dev/gantt-stress", Component: GanttStressTestPage }] : []),
      
      // Settings
      { path: "settings", Component: Dashboard }, // Placeholder
    ],
  },
]);