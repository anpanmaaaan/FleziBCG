import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "../auth/AuthContext";
import { useImpersonation } from "../impersonation/ImpersonationContext";

const ALLOWED_ACTING_ROLES = ["OPR", "SUP", "IEP", "QCI", "QAL", "PMG", "EXE"];

function normalizeRole(roleCode?: string | null): string {
  if (!roleCode) {
    return "";
  }
  return roleCode.trim().toUpperCase();
}

export function ImpersonationSwitcher({ roleCode }: { roleCode?: string | null }) {
  const { isAuthenticated, currentUser } = useAuth();
  const { startImpersonation, isImpersonating, isLoading } = useImpersonation();
  const [open, setOpen] = useState(false);
  const [actingRoleCode, setActingRoleCode] = useState("OPR");
  const [scopeHint, setScopeHint] = useState("");
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const isMountedRef = useRef(true);

  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const normalizedRole = normalizeRole(roleCode ?? currentUser?.role_code);
  const canOpen = normalizedRole === "ADM" || normalizedRole === "OTS";

  useEffect(() => {
    if (!open) {
      return;
    }
    if (!isAuthenticated || !canOpen) {
      setOpen(false);
    }
  }, [open, isAuthenticated, canOpen]);

  const submitDisabled = useMemo(() => {
    return submitting || isLoading || reason.trim().length === 0;
  }, [submitting, isLoading, reason]);

  if (!canOpen) {
    return null;
  }

  const onStart = async () => {
    if (!reason.trim()) {
      return;
    }

    setSubmitting(true);
    try {
      const scopePrefix = scopeHint.trim() ? `[scope:${scopeHint.trim()}] ` : "";
      await startImpersonation({
        acting_role_code: actingRoleCode,
        reason: `${scopePrefix}${reason.trim()}`,
        duration_minutes: durationMinutes,
      });
      toast.success("Impersonation started.");
      if (isMountedRef.current) {
        setOpen(false);
        setReason("");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to start impersonation.";
      toast.error(message);
    } finally {
      if (isMountedRef.current) {
        setSubmitting(false);
      }
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        disabled={submitting}
        className="px-3 py-2 text-sm font-medium text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-50 disabled:opacity-50"
      >
        {isImpersonating ? "Switch Acting Role" : "Act as..."}
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white shadow-xl border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Start Impersonation</h3>
              <button
                onClick={() => setOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>

            <div className="px-5 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Acting role</label>
                <select
                  value={actingRoleCode}
                  onChange={(event) => setActingRoleCode(event.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  {ALLOWED_ACTING_ROLES.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Scope hint (optional)</label>
                <input
                  value={scopeHint}
                  onChange={(event) => setScopeHint(event.target.value)}
                  placeholder="e.g. STATION_01"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Duration (minutes)</label>
                <input
                  type="number"
                  min={1}
                  max={480}
                  value={durationMinutes}
                  onChange={(event) => setDurationMinutes(Number(event.target.value) || 60)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                <textarea
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  rows={3}
                  placeholder="Required for audit trail"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>

            <div className="px-5 py-4 border-t border-gray-100 flex justify-end gap-2">
              <button
                onClick={() => setOpen(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={onStart}
                disabled={submitDisabled}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? "Starting..." : "Start"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
