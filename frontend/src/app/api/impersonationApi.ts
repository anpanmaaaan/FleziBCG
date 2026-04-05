import { request } from "./httpClient";

export interface ImpersonationSession {
  id: number;
  real_user_id: string;
  real_role_code: string;
  acting_role_code: string;
  acting_scope_type?: string | null;
  acting_scope_id?: string | null;
  scope_type?: string | null;
  scope_value?: string | null;
  tenant_id: string;
  reason: string;
  expires_at: string;
  revoked_at: string | null;
  created_at: string;
  is_active: boolean;
}

export interface StartImpersonationPayload {
  acting_role_code: string;
  reason: string;
  duration_minutes: number;
}

const BASE_PATH = "/v1/impersonations";

export const impersonationApi = {
  getCurrent() {
    return request<ImpersonationSession | null>(`${BASE_PATH}/current`);
  },

  start(payload: StartImpersonationPayload) {
    return request<ImpersonationSession>(BASE_PATH, {
      method: "POST",
      body: payload,
    });
  },

  revoke(sessionId: number) {
    return request<ImpersonationSession>(`${BASE_PATH}/${sessionId}/revoke`, {
      method: "POST",
    });
  },
};
