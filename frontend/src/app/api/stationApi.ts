import { request } from "./httpClient";
import type { OperationDetail, OperationExecutionStatus } from "./operationApi";

export type QueueClaimState = "none" | "mine" | "other";

export interface ClaimSummary {
  state: QueueClaimState;
  expires_at: string | null;
  claimed_by_user_id: string | null;
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
  claim: ClaimSummary;
  downtime_open: boolean;
}

export interface StationQueueResponse {
  items: StationQueueItem[];
  station_scope_value: string;
}

export interface ClaimResponse {
  operation_id: number;
  station_scope_value: string;
  claimed_by_user_id: string;
  claimed_at: string;
  expires_at: string;
  state: QueueClaimState;
}

const STATION_BASE_PATH = "/v1/station/queue";

export const stationApi = {
  getQueue() {
    return request<StationQueueResponse>("/v1/station/queue");
  },

  claim(operationId: number, payload: { reason?: string; duration_minutes?: number } = {}) {
    return request<ClaimResponse>(`${STATION_BASE_PATH}/${operationId}/claim`, {
      method: "POST",
      body: payload,
    });
  },

  release(operationId: number, payload: { reason: string }) {
    return request<ClaimResponse>(`${STATION_BASE_PATH}/${operationId}/release`, {
      method: "POST",
      body: payload,
    });
  },

  getClaim(operationId: number) {
    return request<{ state: QueueClaimState; expires_at: string | null; claimed_by_user_id: string | null }>(
      `${STATION_BASE_PATH}/${operationId}/claim`,
    );
  },

  getOperationDetail(operationId: number) {
    return request<OperationDetail>(`${STATION_BASE_PATH}/${operationId}/detail`);
  },
};
