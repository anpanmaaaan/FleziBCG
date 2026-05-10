// Station Session — PARTIAL (backend-connected)
// Shows current session state from GET /v1/station/sessions/current.
// Session truth is managed by the backend execution system.

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { MonitorCheck, User, Cpu, Power, RefreshCw, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { stationApi } from "@/app/api/stationApi";
import type { StationSessionItem } from "@/app/api/stationApi";
import {
  normalizeStationCommandError,
  type StationCommandErrorMessage,
} from "@/app/components/station-execution/stationCommandErrorMessages";
import { StationWorkflowShell } from "@/app/components/station-execution/StationWorkflowShell";
import { StationEntryHandoff } from "@/app/components/station-execution/StationEntryHandoff";

export function StationSession() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const stationId = searchParams.get("stationId") ?? "";
  const [session, setSession] = useState<StationSessionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [closing, setClosing] = useState(false);
  const [showCloseConfirm, setShowCloseConfirm] = useState(false);
  const [commandError, setCommandError] = useState<StationCommandErrorMessage | null>(null);

  const presentSessionError = (error: unknown, fallbackKey: string) => {
    const normalized = normalizeStationCommandError(error);
    setCommandError(normalized);

    if (normalized.code !== "UNKNOWN") {
      toast.error(t(normalized.messageKey));
      return;
    }

    toast.error(t(fallbackKey));
  };

  const loadSession = () => {
    if (!stationId) { setLoading(false); return; }
    setLoading(true);
    stationApi
      .getCurrentSession(stationId)
      .then((res) => {
        setSession(res.session ?? null);
        setCommandError(null);
        setShowCloseConfirm(false);
      })
      .catch((error) => presentSessionError(error, "stationSession.notice.failed_to_load_session"))
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
        setCommandError(null);
        setShowCloseConfirm(false);
        toast.success(t("stationSession.toast.closed"));
      })
      .catch((error) => presentSessionError(error, "stationSession.toast.closeFailed"))
      .finally(() => setClosing(false));
  };

  const goToOperatorIdentification = () => {
    const params = new URLSearchParams();
    if (stationId) {
      params.set("stationId", stationId);
    }
    if (session?.session_id) {
      params.set("sessionId", session.session_id);
    }
    const query = params.toString();
    navigate(query ? `/operator-identification?${query}` : "/operator-identification");
  };

  const goToEquipmentBinding = () => {
    const params = new URLSearchParams();
    if (stationId) {
      params.set("stationId", stationId);
    }
    if (session?.session_id) {
      params.set("sessionId", session.session_id);
    }
    const query = params.toString();
    navigate(query ? `/equipment-binding?${query}` : "/equipment-binding");
  };

  const goToStationCockpit = () => {
    navigate("/station");
  };

  const sessionRecoveryBanner = commandError ? (
    <div
      className={`rounded-lg border px-4 py-3 text-sm ${commandError.severity === "danger" ? "border-red-200 bg-red-50 text-red-800" : "border-amber-200 bg-amber-50 text-amber-800"}`}
      role="alert"
    >
      <p className="font-semibold">{t(commandError.titleKey)}</p>
      <p className="mt-1">{t(commandError.messageKey)}</p>
      <p className="mt-1 text-xs">{t(commandError.recoveryKey)}</p>
    </div>
  ) : undefined;

  const handoffSessionState = !stationId
    ? "not_confirmed"
    : !session
    ? "missing"
    : session.status === "open"
    ? "open"
    : "closed";

  const handoffOperatorState = !session
    ? "not_confirmed"
    : session.operator_user_id
    ? "identified"
    : "missing";

  const handoffEquipmentState = commandError?.code === "EQUIPMENT_REQUIRED"
    ? session?.equipment_id
      ? "bound"
      : "required_missing"
    : session?.equipment_id
    ? "bound"
    : session
    ? "optional_unknown"
    : "not_confirmed";

  const nextStepKey = !stationId
    ? "station.handoff.next.resolveStationContext"
    : !session
    ? "station.handoff.next.openSession"
    : session.status !== "open"
    ? "station.handoff.next.openNewSession"
    : !session.operator_user_id
    ? "station.handoff.next.identifyOperator"
    : handoffEquipmentState === "required_missing"
    ? "station.handoff.next.bindEquipmentBeforeExecution"
    : handoffEquipmentState === "optional_unknown"
    ? "station.handoff.next.equipmentOptionalUnknown"
    : "station.handoff.next.goToCockpit";

  const sessionPrimaryCta = nextStepKey === "station.handoff.next.goToCockpit"
    ? "station.handoff.cta.stationCockpit"
    : nextStepKey === "station.handoff.next.bindEquipmentBeforeExecution"
    ? "station.handoff.cta.equipmentBinding"
    : "station.handoff.cta.operatorIdentification";

  const isOpenSession = session?.status === "open";

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
            {t("common.action.refresh")}
          </button>
        </div>
      </div>

      <StationWorkflowShell
        currentStage={isOpenSession ? "STX_009_END_SESSION" : "STX_001_STATION_SESSION"}
        stationId={stationId || null}
        sessionId={session?.session_id ?? null}
        operatorUserId={session?.operator_user_id ?? null}
        equipmentId={session?.equipment_id ?? null}
        recoveryBanner={isOpenSession ? undefined : sessionRecoveryBanner}
      >
        <StationEntryHandoff
          stationState={stationId ? "selected" : "missing"}
          sessionState={handoffSessionState}
          operatorState={handoffOperatorState}
          equipmentState={handoffEquipmentState}
          nextStepKey={nextStepKey}
          ctas={[
            {
              labelKey: "station.handoff.cta.operatorIdentification",
              onClick: goToOperatorIdentification,
              tone: sessionPrimaryCta === "station.handoff.cta.operatorIdentification" ? "primary" : "neutral",
            },
            {
              labelKey: "station.handoff.cta.equipmentBinding",
              onClick: goToEquipmentBinding,
              tone: sessionPrimaryCta === "station.handoff.cta.equipmentBinding" ? "primary" : "neutral",
            },
            {
              labelKey: "station.handoff.cta.stationCockpit",
              onClick: goToStationCockpit,
              tone: sessionPrimaryCta === "station.handoff.cta.stationCockpit" ? "primary" : "neutral",
            },
          ]}
        />

        {!stationId && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-700">
            {t("stationSession.notice.missingStationId")}
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
            {isOpenSession && (
              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Power className="h-4 w-4 text-slate-500" />
                      <h2 className="text-base font-semibold text-slate-900">
                        {t("stationSession.endSession.title")}
                      </h2>
                    </div>
                    <p className="mt-2 text-sm text-slate-700">
                      {t("stationSession.endSession.description")}
                    </p>
                    <p className="mt-2 text-xs text-slate-500">
                      {t("stationSession.endSession.guardHint")}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={goToStationCockpit}
                    className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95"
                  >
                    {t("stationSession.endSession.returnToCockpit")}
                  </button>
                </div>

                <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                    <div className="min-w-0">
                      <p className="font-medium">{t("stationSession.endSession.closeConfirmHint")}</p>
                      <p className="mt-1 text-xs text-amber-800">{t("stationSession.endSession.blockedRecovery")}</p>
                    </div>
                  </div>
                </div>

                {sessionRecoveryBanner ? <div className="mt-4">{sessionRecoveryBanner}</div> : null}

                <div className="mt-4 flex flex-wrap gap-2">
                  {showCloseConfirm ? (
                    <>
                      <button
                        type="button"
                        onClick={handleClose}
                        disabled={closing}
                        className="min-h-11 rounded-lg bg-red-600 px-4 text-sm font-medium text-white transition hover:bg-red-700 active:scale-95 disabled:opacity-50"
                      >
                        {t("stationSession.action.closeSession")}
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowCloseConfirm(false)}
                        disabled={closing}
                        className="min-h-11 rounded-lg border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95 disabled:opacity-50"
                      >
                        {t("common.action.cancel")}
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setShowCloseConfirm(true)}
                      disabled={closing}
                      className="min-h-11 rounded-lg border border-red-200 bg-red-50 px-4 text-sm font-medium text-red-700 transition hover:bg-red-100 active:scale-95 disabled:opacity-50"
                    >
                      {t("stationSession.action.closeSession")}
                    </button>
                  )}
                </div>
              </section>
            )}

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
      </StationWorkflowShell>
    </div>
  );
}


