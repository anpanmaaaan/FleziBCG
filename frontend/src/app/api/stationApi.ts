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

const STATION_BASE_PATH = "/v1/station/queue";

export const stationApi = {
  getQueue() {
    return request<StationQueueResponse>("/v1/station/queue");
  },

  getOperationDetail(operationId: number) {
    return request<OperationDetail>(`${STATION_BASE_PATH}/${operationId}/detail`);
  },
};
