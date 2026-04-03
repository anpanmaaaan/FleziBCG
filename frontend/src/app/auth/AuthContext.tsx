import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { authApi, type AuthUser } from "../api/authApi";
import { setHttpContextProvider } from "../api/httpClient";

const AUTH_TOKEN_KEY = "mes.auth.token";

interface AuthContextValue {
  isAuthenticated: boolean;
  currentUser: AuthUser | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshCurrentUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function getStoredToken(): string | null {
  try {
    return window.localStorage.getItem(AUTH_TOKEN_KEY);
  } catch {
    return null;
  }
}

function setStoredToken(token: string | null): void {
  try {
    if (!token) {
      window.localStorage.removeItem(AUTH_TOKEN_KEY);
      return;
    }
    window.localStorage.setItem(AUTH_TOKEN_KEY, token);
  } catch {
    // Ignore storage errors in AuthN-only phase.
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    setHttpContextProvider(() => ({
      authToken: token,
      tenantId: currentUser?.tenant_id ?? null,
    }));
  }, [token, currentUser]);

  const refreshCurrentUser = useCallback(async (tokenOverride?: string | null) => {
    const activeToken = tokenOverride ?? token;

    if (!activeToken) {
      setCurrentUser(null);
      return;
    }

    try {
      const me = await authApi.me();
      setCurrentUser(me);
    } catch {
      // Keep compatibility behavior: failed auth bootstrap should not change screen behavior.
      setCurrentUser(null);
    }
  }, [token]);

  useEffect(() => {
    refreshCurrentUser();
  }, [refreshCurrentUser]);

  const login = useCallback(async (username: string, password: string) => {
    const response = await authApi.login({ username, password });
    setToken(response.access_token);
    setStoredToken(response.access_token);
    await refreshCurrentUser(response.access_token);
  }, [refreshCurrentUser]);

  const logout = useCallback(() => {
    setToken(null);
    setStoredToken(null);
    setCurrentUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated: Boolean(token && currentUser),
      currentUser,
      token,
      login,
      logout,
      refreshCurrentUser,
    }),
    [currentUser, token, login, logout, refreshCurrentUser],
  );

  // TODO(Phase 6B): Add persona enforcement wiring based on authenticated role_code.
  // TODO(Phase 6B): Add route guard integration after authorization model is defined.

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
