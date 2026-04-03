import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { LoginPage } from "./pages/LoginPage";
import { Home } from "./pages/Home";
import { Dashboard } from "./pages/Dashboard";
import { ProductionOrderList } from "./pages/ProductionOrderList";
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
      { path: "dispatch", Component: DispatchQueue },
      
      // Routes & Operations
      { path: "routes", Component: RouteList },
      { path: "routes/:routeId", Component: RouteDetail },
      
      // Work Order Execution Flow (3 screens)
      { path: "work-orders", Component: OperationList }, // WO Status List (all)
      { path: "production-orders/:orderId/work-orders", Component: OperationList }, // WO Status List
      { path: "work-orders/:woId/operations", Component: OperationExecutionOverview }, // WO-scoped Gantt Overview
      { path: "operations", Component: GlobalOperationList }, // Global Operation Monitoring (read-only)
      { path: "operations/:operationId/detail", Component: OperationExecutionDetail }, // Operation Detail Tabs
      
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
      
      // Settings
      { path: "settings", Component: Dashboard }, // Placeholder
    ],
  },
]);