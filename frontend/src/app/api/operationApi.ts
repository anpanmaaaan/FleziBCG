
export type DowntimeReasonClass =
  | "UNSPECIFIED"
  | "PLANNED_MAINTENANCE"
  | "UNPLANNED_BREAKDOWN"
  | "MATERIAL_SHORTAGE"
  | "QUALITY_HOLD"
  | "OTHER";

export interface StartDowntimePayload {
  reason_class: DowntimeReasonClass;
  note?: string | null;
}
import { request } from "./httpClient";

export type OperationExecutionStatus =
  | "PLANNED"
  | "IN_PROGRESS"
  | "PAUSED"
  | "COMPLETED"
  | "ABORTED";

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
  operator_id: string | null;
}

interface OperatorPayload {
  operator_id: string | null;
}

interface CompletePayload extends OperatorPayload {
  completed_at?: string;
}

export interface PausePayload {
  reason_code?: string | null;
  note?: string | null;
}

export interface ResumePayload {
  note?: string | null;
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

  pause(operationId: string | number, payload: PausePayload = {}) {
    return request<OperationDetail>(`${operationPath(operationId)}/pause`, {
      method: "POST",
      body: payload,
    });
  },

  resume(operationId: string | number, payload: ResumePayload = {}) {
    return request<OperationDetail>(`${operationPath(operationId)}/resume`, {
      method: "POST",
      body: payload,
    });
  },

  complete(operationId: string | number, payload: CompletePayload = { operator_id: null }) {
    return request<OperationDetail>(`${operationPath(operationId)}/complete`, {
      method: "POST",
      body: payload,
    });
  },

  startDowntime(operationId: string | number, payload: StartDowntimePayload) {
    return request<OperationDetail>(`${operationPath(operationId)}/start-downtime`, {
      method: "POST",
      body: payload,
    });
  },
};