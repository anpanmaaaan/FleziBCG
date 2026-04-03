import { request } from "./httpClient";

export type AlertSeverityCode = "LOW" | "MEDIUM" | "HIGH";
export type BottleneckScopeType = "WORK_ORDER";
export type BottleneckStatusCode = "NORMAL" | "DELAYED" | "BLOCKED";
export type RiskLevelCode = "LOW" | "MEDIUM" | "HIGH";
export type RiskReasonCode = "LATE_SCHEDULE" | "UPSTREAM_DELAY" | "BLOCKED_OPERATION";

export interface DashboardSummaryResponse {
  context: {
    date: string;
    shift: string;
  };
  workOrders: {
    total: number;
    onTime: number;
    atRisk: number;
    late: number;
  };
  operations: {
    inProgress: number;
    blocked: number;
  };
  alerts: {
    count: number;
    highestSeverity: AlertSeverityCode;
  };
}

export interface DashboardHealthResponse {
  bottlenecks: Array<{
    scopeType: BottleneckScopeType;
    scopeCode: string;
    status: BottleneckStatusCode;
    affectedWorkOrders: number;
  }>;
  riskWorkOrders: Array<{
    workOrderNumber: string;
    riskLevel: RiskLevelCode;
    reasonCode: RiskReasonCode;
  }>;
}

export const dashboardApi = {
  getSummary() {
    return request<DashboardSummaryResponse>("/v1/dashboard/summary");
  },

  getHealth() {
    return request<DashboardHealthResponse>("/v1/dashboard/health");
  },
};
