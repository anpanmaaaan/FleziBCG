import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { authApi, type AuthUser } from "@/app/api";
import { setHttpContextProvider, setUnauthorizedHandler } from "@/app/api";

const AUTH_TOKEN_KEY = "mes.auth.token";
const REFRESH_TOKEN_KEY = "mes.auth.refresh_token";

interface AuthContextValue {
  isAuthenticated: boolean;
  isInitializing: boolean;
  currentUser: AuthUser | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  logoutAll: () => Promise<void>;
  refreshCurrentUser: () => Promise<void>;
  refreshTokens: () => Promise<boolean>;
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

function getStoredRefreshToken(): string | null {
  try {
    return window.localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
}

function setStoredRefreshToken(token: string | null): void {
  try {
    if (!token) {
      window.localStorage.removeItem(REFRESH_TOKEN_KEY);
      return;
    }
    window.localStorage.setItem(REFRESH_TOKEN_KEY, token);
  } catch {
    // Ignore storage errors in AuthN-only phase.
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getStoredToken());
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const isLoggingOutRef = useRef(false);
  const isRefreshingRef = useRef(false);

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
    if (!response.refresh_token) {
      // Backend contract requires a refresh token on login.
      throw new Error("Auth contract error: login response missing refresh_token");
    }
    // Set access token and refresh token before fetching user identity.
    setToken(response.access_token);
    setStoredToken(response.access_token);
    setStoredRefreshToken(response.refresh_token);
    await refreshCurrentUser(response.access_token);
  }, [refreshCurrentUser]);

  const clearLocalAuthState = useCallback(() => {
    setToken(null);
    setStoredToken(null);
    setStoredRefreshToken(null);
    setCurrentUser(null);
  }, []);

  /**
   * Attempt to rotate the access + refresh token pair using the persisted refresh token.
   * Returns true if tokens were successfully rotated, false on any failure.
   *
   * INVARIANT: Only one refresh attempt at a time (isRefreshingRef guard).
   * INVARIANT: On failure, auth state is cleared — caller must redirect to login.
   * INVARIANT: Raw refresh token is never logged or displayed.
   */
  const refreshTokens = useCallback(async (): Promise<boolean> => {
    if (isRefreshingRef.current) {
      // Already refreshing — do not stack a second attempt.
      return false;
    }

    const storedRefreshToken = getStoredRefreshToken();
    if (!storedRefreshToken) {
      clearLocalAuthState();
      return false;
    }

    isRefreshingRef.current = true;
    try {
      const response = await authApi.refresh({ refresh_token: storedRefreshToken });
      if (!response.refresh_token) {
        // Backend must return a new refresh token on rotation.
        clearLocalAuthState();
        return false;
      }
      // Atomically replace both tokens.
      setToken(response.access_token);
      setStoredToken(response.access_token);
      setStoredRefreshToken(response.refresh_token);
      // Update HTTP context immediately so the next request uses the new token.
      setHttpContextProvider(() => ({
        authToken: response.access_token,
        tenantId: currentUser?.tenant_id ?? null,
      }));
      return true;
    } catch {
      // Refresh failed (401 = rotated/revoked/expired token). Clear all state.
      clearLocalAuthState();
      return false;
    } finally {
      isRefreshingRef.current = false;
    }
  }, [clearLocalAuthState, currentUser]);

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
      // On 401, attempt token rotation first. If refresh succeeds the caller
      // can retry. If it fails, clearLocalAuthState is called inside refreshTokens.
      // We do not await here — the unauthorized handler is fire-and-forget;
      // state will be cleared synchronously if needed.
      void refreshTokens();
    });
  }, [refreshTokens]);

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
      refreshTokens,
    }),
    [currentUser, isInitializing, token, login, logout, logoutAll, refreshCurrentUser, refreshTokens],
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
