import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { Dashboard } from "./pages/Dashboard";
import { ProductionOrderList } from "./pages/ProductionOrderList";
import { RouteList } from "./pages/RouteList";
import { RouteDetail } from "./pages/RouteDetail";
import { OperationList } from "./pages/OperationList";
import { OperationExecutionOverview } from "./pages/OperationExecutionOverview";
import { OperationExecutionDetail } from "./pages/OperationExecutionDetail";
import { DispatchQueue } from "./pages/DispatchQueue";
import { QCCheckpoints } from "./pages/QCCheckpoints";
import { DefectManagement } from "./pages/DefectManagement";
import { Traceability } from "./pages/Traceability";
import { APSScheduling } from "./pages/APSScheduling";
import { StationExecution } from "./pages/StationExecution";
import { OEEDeepDive } from "./pages/OEEDeepDive";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      // Execution Tracking (Main)
      { index: true, Component: Home },
      
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
      { path: "production-order/:orderId", Component: OperationList }, // WO Status List
      { path: "operation/:woId", Component: OperationExecutionOverview }, // Gantt Overview
      { path: "operation-detail/:operationId", Component: OperationExecutionDetail }, // Detail Tabs
      
      // Station Execution
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