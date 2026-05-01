import { request } from "./httpClient";
import type { OperationDetail, OperationExecutionStatus } from "./operationApi";

export type QueueClaimState = "none" | "mine" | "other";

/**
 * Compatibility payload from legacy claim model.
 * Do not use for primary queue ownership or execution affordance.
 * Target ownership is StationSession-derived `ownership`.
 * Types retained until H9 backend payload null-only contract.
 */
export interface ClaimSummary {
  state: QueueClaimState;
  expires_at: string | null;
  claimed_by_user_id: string | null;
}

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
  /**
   * Compatibility payload from legacy claim model (H8+: not consumed by queue UI).
   * Do not use for queue ownership display, lock, filter, summary, or execution affordance.
   * Will be null-only after H9 backend payload contract update.
   */
  claim: ClaimSummary;
  /** Target ownership truth (H2+): ownership block from StationSession context */
  ownership: SessionOwnershipSummary;
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

  /**
   * DEPRECATED (H2+): Use queue ownership context instead.
   * Claim is compatibility-only; ownership block is primary.
   * May be removed in 08H4+.
   */
  claim(operationId: number, payload: { reason?: string; duration_minutes?: number } = {}) {
    return request<ClaimResponse>(`${STATION_BASE_PATH}/${operationId}/claim`, {
      method: "POST",
      body: payload,
    });
  },

  /**
   * DEPRECATED (H2+): Use queue ownership context instead.
   * Claim is compatibility-only; ownership block is primary.
   * May be removed in 08H4+.
   */
  release(operationId: number, payload: { reason: string }) {
    return request<ClaimResponse>(`${STATION_BASE_PATH}/${operationId}/release`, {
      method: "POST",
      body: payload,
    });
  },

  /**
   * DEPRECATED (H2+): Use queue ownership context instead.
   * Claim is compatibility-only; ownership block is primary.
   * May be removed in 08H4+.
   */
  getClaim(operationId: number) {
    return request<{ state: QueueClaimState; expires_at: string | null; claimed_by_user_id: string | null }>(
      `${STATION_BASE_PATH}/${operationId}/claim`,
    );
  },

  getOperationDetail(operationId: number) {
    return request<OperationDetail>(`${STATION_BASE_PATH}/${operationId}/detail`);
  },
};
