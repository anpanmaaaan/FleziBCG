import { request } from "./httpClient";

export interface AuthUser {
  user_id: string;
  username: string;
  email?: string | null;
  tenant_id: string;
  role_code?: string | null;
  session_id?: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  refresh_token: string | null;
  user: AuthUser;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type: "bearer";
  refresh_token: string | null;
  user: AuthUser;
}

export const authApi = {
  login(payload: LoginRequest) {
    return request<LoginResponse>("/v1/auth/login", {
      method: "POST",
      body: payload,
    });
  },

  refresh(payload: RefreshRequest) {
    return request<RefreshResponse>("/v1/auth/refresh", {
      method: "POST",
      body: payload,
    });
  },

  me() {
    return request<AuthUser>("/v1/auth/me");
  },

  logout() {
    return request<{ status: string; revoked_session_id: string }>("/v1/auth/logout", {
      method: "POST",
    });
  },

  logoutAll() {
    return request<{ status: string; revoked_count: number }>("/v1/auth/logout-all", {
      method: "POST",
    });
  },
};
