import { request } from "./httpClient";

// MMD-FULLSTACK-08: Reason Code read-only API type.
// MMD-FULLSTACK-13: Write helpers added. No downtime_reason integration.
// MMD-FULLSTACK-13B: Server-derived allowed_actions added. Mirrors BOM pattern.
// MMD-FULLSTACK-13C: Page-level create capability added (GET /reason-codes/capabilities).
// Shape mirrors backend ReasonCodeItem + ReasonCodeAllowedActions schemas.

// Page-level create capability (MMD-FULLSTACK-13C).
// Backend computes this from admin.master_data.reason_code.manage.
// Read does not require manage permission. Frontend must NOT infer from persona or lifecycle.
export interface ReasonCodeCapabilities {
  can_create: boolean;
  reason?: string | null;
}

// Server-derived write capability guard (MMD-FULLSTACK-13B).
// Backend computes this from admin.master_data.reason_code.manage + lifecycle.
// Frontend must NOT enable write controls based on lifecycle_status alone.
export interface ReasonCodeAllowedActions {
  can_update: boolean;
  can_release: boolean;
  can_retire: boolean;
  can_create_sibling: boolean;
}

export interface ReasonCodeItemFromAPI {
  reason_code_id: string;
  tenant_id: string;
  reason_domain: string;
  reason_category: string;
  reason_code: string;
  reason_name: string;
  description?: string | null;
  lifecycle_status: "DRAFT" | "RELEASED" | "RETIRED";
  requires_comment: boolean;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
  allowed_actions: ReasonCodeAllowedActions;
}

export interface ListReasonCodesParams {
  domain?: string;
  category?: string;
  lifecycle_status?: "DRAFT" | "RELEASED" | "RETIRED";
  include_inactive?: boolean;
}

// MMD-FULLSTACK-13: Write request types.
// FORBIDDEN fields in any payload: lifecycle_status, tenant_id, created_at, updated_at, downtime_reason_id.
// FORBIDDEN in update: reason_code, reason_domain, reason_category.
export interface ReasonCodeCreateRequest {
  reason_domain: string;
  reason_category: string;
  reason_code: string;
  reason_name: string;
  description?: string | null;
  requires_comment?: boolean | null;
  sort_order?: number | null;
  is_active?: boolean | null;
}

export interface ReasonCodeUpdateRequest {
  reason_name?: string | null;
  description?: string | null;
  requires_comment?: boolean | null;
  sort_order?: number | null;
  is_active?: boolean | null;
}

const BASE_PATH = "/v1/reason-codes";

export const reasonCodeApi = {
  listReasonCodes(params?: ListReasonCodesParams, signal?: AbortSignal) {
    const qs = new URLSearchParams();
    if (params?.domain) qs.set("domain", params.domain);
    if (params?.category) qs.set("category", params.category);
    if (params?.lifecycle_status) qs.set("lifecycle_status", params.lifecycle_status);
    if (params?.include_inactive) qs.set("include_inactive", "true");
    const queryString = qs.toString();
    const path = queryString ? `${BASE_PATH}?${queryString}` : BASE_PATH;
    return request<ReasonCodeItemFromAPI[]>(path, { signal });
  },

  getReasonCode(reasonCodeId: string, signal?: AbortSignal) {
    return request<ReasonCodeItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(reasonCodeId)}`,
      { signal },
    );
  },

  // MMD-FULLSTACK-13: Write helpers.
  createReasonCode(payload: ReasonCodeCreateRequest, signal?: AbortSignal) {
    return request<ReasonCodeItemFromAPI>(BASE_PATH, {
      method: "POST",
      body: payload,
      signal,
    });
  },

  updateReasonCode(reasonCodeId: string, payload: ReasonCodeUpdateRequest, signal?: AbortSignal) {
    return request<ReasonCodeItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(reasonCodeId)}`,
      { method: "PATCH", body: payload, signal },
    );
  },

  releaseReasonCode(reasonCodeId: string, signal?: AbortSignal) {
    return request<ReasonCodeItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(reasonCodeId)}/release`,
      { method: "POST", signal },
    );
  },

  retireReasonCode(reasonCodeId: string, signal?: AbortSignal) {
    return request<ReasonCodeItemFromAPI>(
      `${BASE_PATH}/${encodeURIComponent(reasonCodeId)}/retire`,
      { method: "POST", signal },
    );
  },

  // MMD-FULLSTACK-13C: Page-level create capability.
  // Read does not require manage permission — any authenticated user may call.
  getCapabilities(signal?: AbortSignal) {
    return request<ReasonCodeCapabilities>(`${BASE_PATH}/capabilities`, { signal });
  },
};
