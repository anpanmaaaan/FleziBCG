import { request } from "./httpClient";

export type OperationExecutionStatus = "PENDING" | "IN_PROGRESS" | "COMPLETED" | string;

export interface OperationDetail {
  id: number;
  operation_number: string;
  name: string;
  sequence: number;
  status: OperationExecutionStatus;
  planned_start: string | null;
  planned_end: string | null;
  actual_start: string | null;
  actual_end: string | null;
  quantity: number;
  completed_qty: number;
  good_qty: number;
  scrap_qty: number;
  progress: number;
  work_order_id: number;
  work_order_number: string;
  production_order_id: number;
  production_order_number: string;
  qc_required: boolean;
}

export interface ReportQuantityPayload {
  good_qty: number;
  scrap_qty: number;
  operator_id: number | null;
}

interface OperatorPayload {
  operator_id: number | null;
}

const OPERATION_BASE_PATH = "/v1/operations";

const operationPath = (operationId: string | number) =>
  `${OPERATION_BASE_PATH}/${encodeURIComponent(String(operationId))}`;

export const operationApi = {
  get(operationId: string | number) {
    return request<OperationDetail>(operationPath(operationId));
  },

  start(operationId: string | number, payload: OperatorPayload = { operator_id: null }) {
    return request<OperationDetail>(`${operationPath(operationId)}/start`, {
      method: "POST",
      body: payload,
    });
  },

  reportQuantity(operationId: string | number, payload: ReportQuantityPayload) {
    return request<OperationDetail>(`${operationPath(operationId)}/report-quantity`, {
      method: "POST",
      body: payload,
    });
  },

  complete(operationId: string | number, payload: OperatorPayload = { operator_id: null }) {
    return request<OperationDetail>(`${operationPath(operationId)}/complete`, {
      method: "POST",
      body: payload,
    });
  },
};