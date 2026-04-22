export interface StartDowntimePayload {
  reason_code: string;
  note?: string | null;
}
import { request } from "./httpClient";

export type OperationExecutionStatus =
  | "PLANNED"
  | "IN_PROGRESS"
  | "PAUSED"
  | "BLOCKED"
  | "COMPLETED"
  | "ABORTED";

export type OperationClosureStatus = "OPEN" | "CLOSED";

export interface CloseOperationPayload {
  note?: string | null;
}

export interface ReopenOperationPayload {
  reason: string;
}

export interface EndDowntimePayload {
  note?: string | null;
}

export interface OperationDetail {
  id: number;
  operation_number: string;
  name: string;
  sequence: number;
  status: OperationExecutionStatus;
  closure_status: OperationClosureStatus;
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
  downtime_open: boolean;
  // Backend-derived per-operation capability list. Canonical command names
  // (report_production, pause_execution, resume_execution, start_downtime,
  // end_downtime, complete_execution, start_execution). Does NOT encode
  // identity-scoped guards (claim ownership, station-busy) — callers must
  // still apply those and handle 409 reject codes at request time.
  allowed_actions: string[];
  paused_total_ms: number;
  downtime_total_ms: number;
  reopen_count: number;
  last_reopened_at: string | null;
  last_reopened_by: string | null;
  last_closed_at: string | null;
  last_closed_by: string | null;
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

  endDowntime(operationId: string | number, payload: EndDowntimePayload = {}) {
    return request<OperationDetail>(`${operationPath(operationId)}/end-downtime`, {
      method: "POST",
      body: payload,
    });
  },

  close(operationId: string | number, payload: CloseOperationPayload = {}) {
    return request<OperationDetail>(`${operationPath(operationId)}/close`, {
      method: "POST",
      body: payload,
    });
  },

  reopen(operationId: string | number, payload: ReopenOperationPayload) {
    return request<OperationDetail>(`${operationPath(operationId)}/reopen`, {
      method: "POST",
      body: payload,
    });
  },
};