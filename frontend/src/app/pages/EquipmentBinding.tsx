// Equipment Binding — PARTIAL (backend-connected)
// Connects to station session current + bind-equipment endpoints.

import { useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { Cpu, MonitorCheck, Activity, Link2 } from "lucide-react";
import { toast } from "sonner";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { stationApi } from "@/app/api/stationApi";
import type { StationSessionItem } from "@/app/api/stationApi";

export function EquipmentBinding() {
  const { t } = useI18n();
  const [searchParams] = useSearchParams();
  const stationId = searchParams.get("stationId") ?? "";
  const [session, setSession] = useState<StationSessionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [equipmentId, setEquipmentId] = useState("");
  const [binding, setBinding] = useState(false);

  const loadSession = () => {
    if (!stationId) { setLoading(false); return; }
    setLoading(true);
    stationApi
      .getCurrentSession(stationId)
      .then((res) => setSession(res.session ?? null))
      .catch(() => toast.error(t("equipmentBinding.notice.failed_to_load_session")))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadSession(); }, [stationId]);

  const handleBind = () => {
    if (!session) { toast.error(t("equipmentBinding.error.noSession")); return; }
    if (!equipmentId.trim()) { toast.error(t("equipmentBinding.error.equipmentRequired")); return; }
    setBinding(true);
    stationApi
      .bindEquipment(session.session_id, equipmentId.trim())
      .then((updated) => {
        setSession(updated);
        toast.success(t("equipmentBinding.toast.bound"));
        setEquipmentId("");
      })
      .catch(() => toast.error(t("equipmentBinding.toast.bindFailed")))
      .finally(() => setBinding(false));
  };

  return (
    <div className="flex flex-col gap-4 p-4 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("equipmentBinding.title")}
          </h1>
          <ScreenStatusBadge phase="PARTIAL" />
        </div>
      </div>

      {!stationId && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-700">
          No station ID provided. Navigate from Station Execution with a station context.
        </div>
      )}

      {loading ? (
        <div className="p-8 text-center text-gray-400 text-sm">{t("equipmentBinding.label.loading_session")}</div>
      ) : (
        <>
          {/* Session info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Station / Session Panel */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
                <MonitorCheck className="w-4 h-4 text-blue-500" />
                {t("equipmentBinding.section.station")}
              </div>
              <div className="flex flex-col gap-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("equipmentBinding.label.station_id")}</span>
                  <span className="font-mono text-gray-700">{session?.station_id ?? "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("equipmentBinding.label.session_id")}</span>
                  <span className="font-mono text-xs text-gray-600">{session?.session_id ?? "—"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("equipmentBinding.label.session_status")}</span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${session?.status === "open" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}
                  >
                    {session?.status ?? "no session"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">{t("equipmentBinding.label.operator")}</span>
                  <span className="text-gray-700">{session?.operator_user_id ?? "—"}</span>
                </div>
              </div>
            </div>

            {/* Equipment Panel */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-3">
                <Cpu className="w-4 h-4 text-purple-500" />
                {t("equipmentBinding.section.equipment")}
              </div>
              {session?.equipment_id ? (
                <div className="flex flex-col gap-2 text-sm">
                  <div className="flex items-center gap-2 text-green-700">
                    <Activity className="w-4 h-4" />
                    <span className="font-medium">{t("equipmentBinding.status.bound")}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">{t("equipmentBinding.label.equipment_id")}</span>
                    <span className="font-mono text-gray-700">{session.equipment_id}</span>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-gray-400 italic">{t("equipmentBinding.unbound")}</p>
              )}
            </div>
          </div>

          {/* Bind action */}
          {session && session.status === "open" && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-col gap-3">
              <div className="text-sm font-semibold text-gray-700">{t("equipmentBinding.action.bind")}</div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={equipmentId}
                  onChange={(e) => setEquipmentId(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleBind()}
                  placeholder={t("equipmentBinding.input.placeholder")}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                />
                <button
                  onClick={handleBind}
                  disabled={binding || !equipmentId.trim()}
                  className="flex items-center gap-1 px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Link2 className="w-3 h-3" />
                  {binding ? t("equipmentBinding.action.binding") : t("equipmentBinding.action.bind")}
                </button>
              </div>
            </div>
          )}

          {!session && stationId && (
            <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-500">
              No active session for station {stationId}. Open a session first.
            </div>
          )}
        </>
      )}
    </div>
  );
}


