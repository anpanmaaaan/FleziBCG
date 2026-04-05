import { request } from "./httpClient";

export interface WorkOrderSummaryFromAPI {
  id: number;
  workOrderNumber: string;
  status: string;
  plannedStart: string | null;
  plannedEnd: string | null;
  actualStart: string | null;
  actualEnd: string | null;
  operationsCount: number;
  completedOperations: number;
  overallProgress: number;
}

export interface ProductionOrderDetailFromAPI {
  id: number;
  orderNumber: string;
  productName: string;
  quantity: number;
  status: string;
  routeId: string | null;
  workOrders: WorkOrderSummaryFromAPI[];
}

export interface ProductionOrderSummaryFromAPI {
  id: number;
  orderNumber: string;
  productName: string;
  quantity: number;
  status: string;
  serialNumber?: string;
  lotId?: string;
  customer?: string;
  priority?: string;
  machineNumber?: string;
  routeId?: string;
  materialCode?: string;
  assignee?: string;
  department?: string;
  releasedDate?: string;
  plannedStartDate?: string;
  plannedCompletionDate?: string;
  actualStartDate?: string;
  actualCompletionDate?: string;
  progress?: number | null;
}

const BASE_PATH = "/v1/production-orders";

export const productionOrderApi = {
  list() {
    return request<ProductionOrderSummaryFromAPI[]>(BASE_PATH);
  },

  get(orderId: string | number) {
    return request<ProductionOrderDetailFromAPI>(`${BASE_PATH}/${encodeURIComponent(String(orderId))}`);
  },
};
