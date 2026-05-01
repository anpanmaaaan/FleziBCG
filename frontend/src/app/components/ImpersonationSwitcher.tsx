import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";

import { useAuth } from "@/app/auth";
import { useI18n } from "@/app/i18n";
import { useImpersonation } from "@/app/impersonation";

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
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [actingRoleCode, setActingRoleCode] = useState("OPR");
  const [scopeHint, setScopeHint] = useState("");
  const [durationMinutes, setDurationMinutes] = useState(60);
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const isMountedRef = useRef(true);
  const triggerRef = useRef<HTMLButtonElement>(null);

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

  useEffect(() => {
    if (!open) {
      return;
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpen(false);
        triggerRef.current?.focus();
      }
    }

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [open]);

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
      toast.success(t("impersonation.toast.started"));
      if (isMountedRef.current) {
        setOpen(false);
        triggerRef.current?.focus();
        setReason("");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : t("impersonation.toast.startFailed");
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
        ref={triggerRef}
        type="button"
        aria-expanded={open}
        aria-controls="impersonation-modal-panel"
        onClick={() => setOpen(true)}
        disabled={submitting}
        className="px-3 py-2 text-sm font-medium text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-50 disabled:opacity-50"
      >
        {isImpersonating ? t("impersonation.dialog.title") : t("impersonation.trigger")}
      </button>

      {open && (
        <div id="impersonation-modal-panel" className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white shadow-xl border border-gray-200">
            <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">{t("impersonation.dialog.subtitle")}</h3>
              <button
                type="button"
                aria-label={t("common.action.close")}
                onClick={() => { setOpen(false); triggerRef.current?.focus(); }}
                className="text-gray-500 hover:text-gray-700"
              >
                {t("common.action.close")}
              </button>
            </div>

            <div className="px-5 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t("impersonation.form.role")}</label>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">{t("impersonation.form.scope")}</label>
                <input
                  value={scopeHint}
                  onChange={(event) => setScopeHint(event.target.value)}
                  placeholder={t("impersonation.form.scopePlaceholder")}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t("impersonation.form.duration")}</label>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">{t("impersonation.form.reason")}</label>
                <textarea
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  rows={3}
                  placeholder={t("impersonation.form.reasonHelp")}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>
            </div>

            <div className="px-5 py-4 border-t border-gray-100 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => { setOpen(false); triggerRef.current?.focus(); }}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
              >
                {t("common.action.cancel")}
              </button>
              <button
                type="button"
                onClick={onStart}
                disabled={submitDisabled}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {submitting ? t("impersonation.action.starting") : t("impersonation.action.start")}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
