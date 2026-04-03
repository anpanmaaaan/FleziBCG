import { request } from "./httpClient";

export interface ProductionOrderSummaryMonitor {
  id: number;
  orderNumber: string;
  productName: string;
  status: string;
}

export interface WorkOrderSummaryMonitor {
  id: number;
  workOrderNumber: string;
  status: string;
}

export interface ProductionOrderDetailMonitor {
  id: number;
  orderNumber: string;
  productName: string;
  status: string;
  workOrders: WorkOrderSummaryMonitor[];
}

export interface OperationListItemMonitor {
  id: number;
  operationNumber: string;
  operation_number?: string;
  name: string;
  sequence: number;
  status: string;
  supervisorBucket?: "BLOCKED" | "DELAYED" | "IN_PROGRESS" | "OTHER";
  supervisor_bucket?: "BLOCKED" | "DELAYED" | "IN_PROGRESS" | "OTHER";
  plannedStart: string | null;
  planned_start?: string | null;
  plannedEnd: string | null;
  planned_end?: string | null;
  quantity: number;
  completedQty: number;
  completed_qty?: number;
  progress: number;
  workOrderNumber?: string | null;
  work_order_number?: string | null;
  workCenter?: string | null;
  work_center?: string | null;
  delayMinutes?: number | null;
  delay_minutes?: number | null;
  blockReasonCode?: string | null;
  block_reason_code?: string | null;
  qcRiskFlag?: boolean;
  qc_risk_flag?: boolean;
  woBlockedOperations?: number;
  wo_blocked_operations?: number;
  woDelayedOperations?: number;
  wo_delayed_operations?: number;
  cycleTimeMinutes?: number | null;
  cycle_time_minutes?: number | null;
  cycleTimeDelta?: number | null;
  cycle_time_delta?: number | null;
  delayCount?: number;
  delay_count?: number;
  delayFrequency?: number;
  delay_frequency?: number;
  repeatFlag?: boolean;
  repeat_flag?: boolean;
  qcFailCount?: number;
  qc_fail_count?: number;
  highVarianceFlag?: boolean;
  high_variance_flag?: boolean;
  oftenLateFlag?: boolean;
  often_late_flag?: boolean;
  routeStep?: string | null;
  route_step?: string | null;
}

export const operationMonitorApi = {
  listProductionOrders() {
    return request<ProductionOrderSummaryMonitor[]>("/v1/production-orders");
  },

  getProductionOrder(productionOrderId: number | string) {
    return request<ProductionOrderDetailMonitor>(`/v1/production-orders/${encodeURIComponent(String(productionOrderId))}`);
  },

  getWorkOrderOperations(workOrderId: number | string) {
    return request<OperationListItemMonitor[]>(`/v1/work-orders/${encodeURIComponent(String(workOrderId))}/operations`);
  },
};
