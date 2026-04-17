import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { impersonationApi, type ImpersonationSession } from "@/app/api";
import { useAuth } from "@/app/auth";

interface StartImpersonationInput {
  acting_role_code: string;
  reason: string;
  duration_minutes: number;
}

interface ImpersonationContextValue {
  activeSession: ImpersonationSession | null;
  isLoading: boolean;
  isImpersonating: boolean;
  effectiveRoleCode: string | null;
  refreshSession: () => Promise<void>;
  startImpersonation: (payload: StartImpersonationInput) => Promise<void>;
  endImpersonation: () => Promise<void>;
}

const ImpersonationContext = createContext<ImpersonationContextValue | null>(null);

function normalizeRole(roleCode?: string | null): string {
  if (!roleCode) {
    return "";
  }
  return roleCode.trim().toUpperCase();
}

export function ImpersonationProvider({ children }: { children: ReactNode }) {
  const { currentUser, refreshCurrentUser, isAuthenticated } = useAuth();
  const [activeSession, setActiveSession] = useState<ImpersonationSession | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const refreshSession = useCallback(async () => {
    if (!isAuthenticated) {
      setActiveSession(null);
      return;
    }

    setIsLoading(true);
    try {
      const session = await impersonationApi.getCurrent();
      setActiveSession(session && session.is_active ? session : null);
    } catch {
      setActiveSession(null);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  const startImpersonation = useCallback(
    async (payload: StartImpersonationInput) => {
      await impersonationApi.start(payload);
      await refreshCurrentUser();
      await refreshSession();
    },
    [refreshCurrentUser, refreshSession],
  );

  const endImpersonation = useCallback(async () => {
    if (!activeSession) {
      return;
    }

    await impersonationApi.revoke(activeSession.id);
    await refreshCurrentUser();
    await refreshSession();
  }, [activeSession, refreshCurrentUser, refreshSession]);

  const effectiveRoleCode = useMemo(() => {
    const actingRole = normalizeRole(activeSession?.acting_role_code);
    if (actingRole) {
      return actingRole;
    }
    const baseRole = normalizeRole(currentUser?.role_code);
    return baseRole || null;
  }, [activeSession, currentUser?.role_code]);

  const value = useMemo<ImpersonationContextValue>(
    () => ({
      activeSession,
      isLoading,
      isImpersonating: Boolean(activeSession),
      effectiveRoleCode,
      refreshSession,
      startImpersonation,
      endImpersonation,
    }),
    [activeSession, isLoading, effectiveRoleCode, refreshSession, startImpersonation, endImpersonation],
  );

  return <ImpersonationContext.Provider value={value}>{children}</ImpersonationContext.Provider>;
}

export function useImpersonation(): ImpersonationContextValue {
  const context = useContext(ImpersonationContext);
  if (!context) {
    throw new Error("useImpersonation must be used within an ImpersonationProvider");
  }
  return context;
}
