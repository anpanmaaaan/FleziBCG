import { request } from "./httpClient";
import type { OperationDetail, OperationExecutionStatus } from "./operationApi";

/**
 * StationSession control context for queue item.
 * Backend-projected session-control truth used by queue UI.
 */
export interface SessionOwnershipSummary {
  target_owner_type: string;
  session_id: string | null;
  station_id: string | null;
  session_status: string | null;
  operator_user_id: string | null;
  owner_state: string;
  has_open_session: boolean;
}

export interface StationQueueItem {
  operation_id: number;
  operation_number: string;
  name: string;
  work_order_number: string;
  production_order_number: string;
  status: OperationExecutionStatus;
  planned_start: string | null;
  planned_end: string | null;
  /** Session-control projection from StationSession context. */
  ownership: SessionOwnershipSummary;
  downtime_open: boolean;
}

export interface StationQueueResponse {
  items: StationQueueItem[];
  station_scope_value: string;
}

export interface OpenStationSessionPayload {
  station_id: string;
  equipment_id?: string | null;
  current_operation_id?: number | null;
}

export interface StationSessionItem {
  session_id: string;
  tenant_id: string;
  station_id: string;
  operator_user_id: string | null;
  equipment_id: string | null;
  status: string;
  opened_at: string;
  closed_at: string | null;
}

const STATION_BASE_PATH = "/v1/station/queue";

export const stationApi = {
  getQueue() {
    return request<StationQueueResponse>("/v1/station/queue");
  },

  getOperationDetail(operationId: number) {
    return request<OperationDetail>(`${STATION_BASE_PATH}/${operationId}/detail`);
  },

  openSession(payload: OpenStationSessionPayload) {
    return request<StationSessionItem>("/v1/station/sessions", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  closeSession(sessionId: string) {
    return request<StationSessionItem>(`/v1/station/sessions/${sessionId}/close`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  },
};
