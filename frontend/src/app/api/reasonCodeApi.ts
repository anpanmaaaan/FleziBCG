import { request } from "./httpClient";

// MMD-FULLSTACK-08: Reason Code read-only API type.
// Shape mirrors backend ReasonCodeItem schema (backend/app/schemas/reason_code.py).
// Read-only. No write helpers. No downtime_reason integration.
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
}

export interface ListReasonCodesParams {
  domain?: string;
  category?: string;
  lifecycle_status?: "DRAFT" | "RELEASED" | "RETIRED";
  include_inactive?: boolean;
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
};
