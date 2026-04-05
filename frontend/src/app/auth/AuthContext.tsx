import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { authApi, type AuthUser } from "../api/authApi";
import { setHttpContextProvider, setUnauthorizedHandler } from "../api/httpClient";

const AUTH_TOKEN_KEY = "mes.auth.token";

interface AuthContextValue {
  isAuthenticated: boolean;
  isInitializing: boolean;
  currentUser: AuthUser | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
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
  const [isInitializing, setIsInitializing] = useState(true);
  const isLoggingOutRef = useRef(false);

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
      // If we have a token override (e.g., during login), temporarily update HTTP context
      // to ensure the /me request uses the new token before it's set in state.
      if (tokenOverride) {
        setHttpContextProvider(() => ({
          authToken: tokenOverride,
          tenantId: "default",
        }));
      }

      const me = await authApi.me();
      setCurrentUser(me);
    } catch (error) {
      // Log the error for debugging
      console.error("Failed to fetch current user:", error);
      setCurrentUser(null);
      // If this was a 401 during login, re-throw so the login fails
      if (tokenOverride) {
        throw error;
      }
    }
  }, [token]);

  useEffect(() => {
    refreshCurrentUser().finally(() => setIsInitializing(false));
  }, [refreshCurrentUser]);

  const login = useCallback(async (username: string, password: string) => {
    const response = await authApi.login({ username, password });
    // Set token and call refreshCurrentUser with the token override.
    // This ensures /me request uses the new token before state updates propagate.
    setToken(response.access_token);
    setStoredToken(response.access_token);
    await refreshCurrentUser(response.access_token);
  }, [refreshCurrentUser]);

  const clearLocalAuthState = useCallback(() => {
    setToken(null);
    setStoredToken(null);
    setCurrentUser(null);
  }, []);

  const logout = useCallback(async () => {
    if (isLoggingOutRef.current) {
      return;
    }

    isLoggingOutRef.current = true;
    try {
      await authApi.logout();
    } catch {
      // Best effort only: local logout must always succeed.
    } finally {
      clearLocalAuthState();
      isLoggingOutRef.current = false;
    }
  }, [clearLocalAuthState]);

  const logoutAll = useCallback(async () => {
    if (isLoggingOutRef.current) {
      return;
    }

    isLoggingOutRef.current = true;
    try {
      await authApi.logoutAll();
    } catch {
      // Best effort only: local logout must always succeed.
    } finally {
      clearLocalAuthState();
      isLoggingOutRef.current = false;
    }
  }, [clearLocalAuthState]);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      void logout();
    });
  }, [logout]);

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated: Boolean(token && currentUser),
      isInitializing,
      currentUser,
      token,
      login,
      logout,
      logoutAll,
      refreshCurrentUser,
    }),
    [currentUser, isInitializing, token, login, logout, logoutAll, refreshCurrentUser],
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
