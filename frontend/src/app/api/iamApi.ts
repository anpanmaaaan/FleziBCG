import { request } from "./httpClient";

// ── User lifecycle ──────────────────────────────────────────────────────────

export interface UserLifecycleItem {
  user_id: string;
  username: string;
  email: string | null;
  tenant_id: string;
  is_active: boolean;
}

export interface UserLifecycleListResponse {
  users: UserLifecycleItem[];
}

export interface UserLifecycleActionResponse {
  status: string;
  user_id: string;
  tenant_id: string;
  is_active: boolean;
  action: string;
}

// ── Security events ─────────────────────────────────────────────────────────

export interface SecurityEventItem {
  tenant_id: string;
  actor_user_id: string | null;
  event_type: string;
  resource_type: string | null;
  resource_id: string | null;
  detail: string | null;
  created_at: string;
}

export interface ListSecurityEventsParams {
  limit?: number;
  offset?: number;
  event_type?: string;
  actor_user_id?: string;
}

// ── Execution timeline ───────────────────────────────────────────────────────

export interface ExecutionTimelineOperation {
  operation_id: number;
  operation_number: string;
  sequence: number;
  name: string;
  workstation: string;
  status: string;
  planned_start: string | null;
  planned_end: string | null;
  actual_start: string | null;
  actual_end: string | null;
  delay_minutes: number | null;
  timing_status: "EARLY" | "ON_TIME" | "LATE";
  qc_required: boolean;
}

export interface WorkOrderExecutionTimeline {
  work_order_id: number;
  work_order_number: string;
  production_order_id: number;
  production_order_number: string;
  operations: ExecutionTimelineOperation[];
}

// ── API object ───────────────────────────────────────────────────────────────

export const iamApi = {
  listUsers(includeInactive = false): Promise<UserLifecycleListResponse> {
    const q = includeInactive ? "?include_inactive=true" : "";
    return request<UserLifecycleListResponse>(`/v1/users${q}`);
  },

  activateUser(userId: string): Promise<UserLifecycleActionResponse> {
    return request<UserLifecycleActionResponse>(`/v1/users/${userId}/activate`, { method: "POST" });
  },

  deactivateUser(userId: string): Promise<UserLifecycleActionResponse> {
    return request<UserLifecycleActionResponse>(`/v1/users/${userId}/deactivate`, { method: "POST" });
  },

  lockUser(userId: string): Promise<UserLifecycleActionResponse> {
    return request<UserLifecycleActionResponse>(`/v1/users/${userId}/lock`, { method: "POST" });
  },

  unlockUser(userId: string): Promise<UserLifecycleActionResponse> {
    return request<UserLifecycleActionResponse>(`/v1/users/${userId}/unlock`, { method: "POST" });
  },

  listSecurityEvents(params: ListSecurityEventsParams = {}): Promise<SecurityEventItem[]> {
    const q = new URLSearchParams();
    if (params.limit != null) q.set("limit", String(params.limit));
    if (params.offset != null) q.set("offset", String(params.offset));
    if (params.event_type) q.set("event_type", params.event_type);
    if (params.actor_user_id) q.set("actor_user_id", params.actor_user_id);
    const qs = q.toString();
    return request<SecurityEventItem[]>(`/v1/security-events${qs ? `?${qs}` : ""}`);
  },

  getWorkOrderExecutionTimeline(workOrderId: string | number): Promise<WorkOrderExecutionTimeline> {
    return request<WorkOrderExecutionTimeline>(
      `/v1/work-orders/${workOrderId}/execution-timeline`
    );
  },
};
