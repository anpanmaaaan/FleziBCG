import { request } from "./httpClient";
import type { OperationDetail, OperationExecutionStatus } from "./operationApi";

/**
 * StationSession ownership context for queue item.
 * Target ownership truth (introduced in 08D, consumed in 08H2+).
 * Replaces claim-based ownership logic in frontend.
 */
export interface SessionOwnershipSummary {
  target_owner_type: string;
  ownership_migration_status: string;
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
  /** Target ownership truth (H2+): ownership block from StationSession context */
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
