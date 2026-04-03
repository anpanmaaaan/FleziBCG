import { request } from "./httpClient";

export interface AuthUser {
  user_id: string;
  username: string;
  email?: string | null;
  tenant_id: string;
  role_code?: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
}

export const authApi = {
  login(payload: LoginRequest) {
    return request<LoginResponse>("/v1/auth/login", {
      method: "POST",
      body: payload,
    });
  },

  me() {
    return request<AuthUser>("/v1/auth/me");
  },
};
