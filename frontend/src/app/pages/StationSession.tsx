// Station Session — PARTIAL (backend-connected)
// Shows current session state from GET /v1/station/sessions/current.
// Session truth is managed by the backend execution system.

import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { MonitorCheck, User, Cpu, Power, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { stationApi } from "@/app/api/stationApi";
import type { StationSessionItem } from "@/app/api/stationApi";

export function StationSession() {
  const { t } = useI18n();
  const [searchParams] = useSearchParams();
  const stationId = searchParams.get("stationId") ?? "";
  const [session, setSession] = useState<StationSessionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [closing, setClosing] = useState(false);

  const loadSession = () => {
    if (!stationId) { setLoading(false); return; }
    setLoading(true);
    stationApi
      .getCurrentSession(stationId)
      .then((res) => setSession(res.session ?? null))
      .catch(() => toast.error(t("stationSession.notice.failed_to_load_session")))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadSession(); }, [stationId]);

  const handleClose = () => {
    if (!session) return;
    setClosing(true);
    stationApi
      .closeSession(session.session_id)
      .then((updated) => {
        setSession(updated);
        toast.success(t("stationSession.toast.closed"));
      })
      .catch(() => toast.error(t("stationSession.toast.closeFailed")))
      .finally(() => setClosing(false));
  };

  return (
    <div className="flex flex-col gap-4 p-4 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("stationSession.title")}
          </h1>
          <ScreenStatusBadge phase="PARTIAL" />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadSession}
            disabled={loading}
            className="flex items-center gap-1 px-3 py-2 rounded-md border border-gray-200 bg-white text-gray-600 text-sm hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className="w-3 h-3" />
            Refresh
          </button>
          {session?.status === "open" && (
            <button
              onClick={handleClose}
              disabled={closing}
              className="flex items-center gap-1 px-3 py-2 rounded-md bg-red-50 border border-red-200 text-red-600 text-sm hover:bg-red-100 disabled:opacity-50"
            >
              <Power className="w-4 h-4" />
              {t("stationSession.action.closeSession")}
            </button>
          )}
        </div>
      </div>

      {!stationId && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-700">
          No station ID provided. Navigate from Station Execution with a stationId query parameter.
        </div>
      )}

      {loading ? (
        <div className="p-8 text-center text-gray-400 text-sm">{t("stationSession.label.loading_session")}</div>
      ) : !session ? (
        <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-500 text-center">
          {t("stationSession.session.noActive")}
        </div>
      ) : (
        <>
          {/* Three-panel layout */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Station Identity */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2">
                <MonitorCheck className="w-4 h-4 text-blue-500" />
                {t("stationSession.section.station")}
              </div>
              <div className="flex flex-col gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("stationSession.label.station_id")}</span>
                  <span className="font-mono text-gray-700">{session.station_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("stationSession.label.session_id")}</span>
                  <span className="font-mono text-xs text-gray-600">{session.session_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("stationSession.label.opened_at")}</span>
                  <span className="text-gray-600 text-xs">{new Date(session.opened_at).toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Operator */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2">
                <User className="w-4 h-4 text-green-500" />
                {t("stationSession.section.operator")}
              </div>
              {session.operator_user_id ? (
                <div className="text-sm font-medium text-green-700">{session.operator_user_id}</div>
              ) : (
                <p className="text-sm text-gray-400 italic">
                  {t("stationSession.operator.unassigned")}
                </p>
              )}
            </div>

            {/* Equipment */}
            <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2">
                <Cpu className="w-4 h-4 text-purple-500" />
                {t("stationSession.section.equipment")}
              </div>
              {session.equipment_id ? (
                <div className="text-sm font-medium text-purple-700">{session.equipment_id}</div>
              ) : (
                <p className="text-sm text-gray-400 italic">
                  {t("stationSession.equipment.unbound")}
                </p>
              )}
            </div>
          </div>

          {/* Session State Panel */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
              <Power className="w-4 h-4 text-gray-500" />
              {t("stationSession.section.session")}
            </div>
            <div className="flex flex-col gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">{t("common.status")}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${session.status === "open" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {session.status}
                </span>
              </div>
              {session.closed_at && (
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("stationSession.label.closed_at")}</span>
                  <span className="text-gray-600 text-xs">{new Date(session.closed_at).toLocaleString()}</span>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}


