import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { useImpersonation } from "../impersonation/ImpersonationContext";

function getStructuredScopeLabel(activeSession: {
  acting_scope_type?: string | null;
  acting_scope_id?: string | null;
  scope_type?: string | null;
  scope_value?: string | null;
}): string {
  const scopeType = activeSession.acting_scope_type ?? activeSession.scope_type;
  const scopeId = activeSession.acting_scope_id ?? activeSession.scope_value;

  if (!scopeType && !scopeId) {
    return "-";
  }
  if (!scopeType) {
    return String(scopeId);
  }
  if (!scopeId) {
    return String(scopeType);
  }
  return `${scopeType}:${scopeId}`;
}

export function ActiveImpersonationBanner() {
  const { activeSession, isImpersonating, endImpersonation, isLoading } = useImpersonation();
  const [now, setNow] = useState(() => Date.now());
  const [ending, setEnding] = useState(false);

  useEffect(() => {
    if (!isImpersonating) {
      return;
    }
    const timer = window.setInterval(() => setNow(Date.now()), 30000);
    return () => window.clearInterval(timer);
  }, [isImpersonating]);

  const expiresInMinutes = useMemo(() => {
    if (!activeSession) {
      return 0;
    }
    const expiresAt = new Date(activeSession.expires_at).getTime();
    const diffMs = Math.max(0, expiresAt - now);
    return Math.ceil(diffMs / 60000);
  }, [activeSession, now]);

  if (!isImpersonating || !activeSession) {
    return null;
  }
  const scopeLabel = getStructuredScopeLabel(activeSession);

  const onEnd = async () => {
    setEnding(true);
    try {
      await endImpersonation();
      toast.success("Impersonation ended.");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to end impersonation.";
      toast.error(message);
    } finally {
      setEnding(false);
    }
  };

  return (
    <div className="px-6 py-2 bg-amber-100 border-b border-amber-200 text-amber-900 text-sm flex items-center justify-between gap-3">
      <div className="leading-tight">
        <div>
          Acting as <span className="font-semibold">{activeSession.acting_role_code}</span>
          {` (expires in ${expiresInMinutes} min)`}
        </div>
        <div className="text-xs opacity-90">Scope: {scopeLabel}</div>
      </div>
      <button
        onClick={onEnd}
        disabled={ending || isLoading}
        className="px-3 py-1 rounded-md border border-amber-400 hover:bg-amber-200 disabled:opacity-50"
      >
        {ending ? "Ending..." : "End"}
      </button>
    </div>
  );
}
