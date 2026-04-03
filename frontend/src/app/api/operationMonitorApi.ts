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
  name: string;
  sequence: number;
  status: string;
  supervisorBucket?: "BLOCKED" | "DELAYED" | "IN_PROGRESS" | "OTHER";
  plannedStart: string | null;
  plannedEnd: string | null;
  quantity: number;
  completedQty: number;
  progress: number;
  workOrderNumber?: string | null;
  workCenter?: string | null;
  delayMinutes?: number | null;
  blockReasonCode?: string | null;
  qcRiskFlag?: boolean;
  woBlockedOperations?: number;
  woDelayedOperations?: number;
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
