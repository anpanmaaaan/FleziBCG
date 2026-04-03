import type { I18nRegistry } from "../keys";

// EN placeholder registry for Phase 5A infrastructure only.
// No runtime language switching is enabled in this phase.
export const enRegistry: I18nRegistry = {
  "common.loading": "Loading",
  "common.error.load_failed": "Load failed",

  "navigation.dashboard": "Dashboard",
  "navigation.work_orders_execution": "Execution - Work Orders",
  "navigation.operations_global": "Operations (Global)",

  "execution.station_execution": "Station Execution",
  "execution.work_orders": "Work Orders",
  "execution.operation_detail": "Operation Detail",

  "operations.global_monitoring": "Global Operation Monitoring",
  "operations.status.pending": "Pending",
  "operations.status.in_progress": "In Progress",
  "operations.status.completed": "Completed",
  "operations.status.blocked": "Blocked",
  "operations.status.late": "Late",

  "dashboard.summary.title": "Dashboard Summary",
  "dashboard.health.title": "Health",
  "dashboard.alert.severity.low": "Low",
  "dashboard.alert.severity.medium": "Medium",
  "dashboard.alert.severity.high": "High",

  "quality.checkpoints": "QC Checkpoints",

  "persona.operator": "Operator",
  "persona.shift_leader": "Shift Leader",
  "persona.supervisor": "Supervisor",
  "persona.manager": "Manager",
  "persona.office": "Office",
  "persona.ie": "IE",
  "persona.process": "Process",
  "persona.qa": "QA",
};

// TODO(Phase 5B): Replace placeholder coverage with complete key catalog.
