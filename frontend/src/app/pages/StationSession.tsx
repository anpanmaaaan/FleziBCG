// Station Session — PARTIAL (backend-connected)
// Shows current session state from GET /v1/station/sessions/current.
// Session truth is managed by the backend execution system.

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { User, Cpu, Power, RefreshCw, AlertTriangle, CheckSquare } from "lucide-react";
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

export function StationSession() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const stationId = searchParams.get("stationId") ?? "";
  const [session, setSession] = useState<StationSessionItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [closing, setClosing] = useState(false);
  const [opening, setOpening] = useState(false);
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

  const handleOpenSession = () => {
    if (!stationId) {
      toast.error(t("stationSession.notice.missingStationId"));
      return;
    }
    setOpening(true);
    stationApi
      .openSession({ station_id: stationId })
      .then((opened) => {
        setSession(opened);
        setCommandError(null);
        setShowCloseConfirm(false);
        toast.success(t("stationSession.toast.opened"));
      })
      .catch((error) => presentSessionError(error, "stationSession.toast.openFailed"))
      .finally(() => setOpening(false));
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

  const goToStationQueue = () => {
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

  const stationChecklistState = stationId ? "ready" : "missing";
  const sessionChecklistState = !stationId
    ? "not_confirmed"
    : !session
    ? "missing"
    : session.status === "open"
    ? "open"
    : "closed";
  const operatorChecklistState = !session
    ? "not_confirmed"
    : session.operator_user_id
    ? "identified"
    : "missing";
  const equipmentChecklistState = commandError?.code === "EQUIPMENT_REQUIRED"
    ? session?.equipment_id
      ? "bound"
      : "required_missing"
    : session?.equipment_id
    ? "bound"
    : session
    ? "optional_unknown"
    : "not_confirmed";

  const nextStepKey = !stationId
    ? "stationSession.setup.next.selectStation"
    : !session
    ? "stationSession.setup.next.openSession"
    : session.status !== "open"
    ? "stationSession.setup.next.openSession"
    : !session.operator_user_id
    ? "stationSession.setup.next.identifyOperator"
    : equipmentChecklistState === "required_missing"
    ? "stationSession.setup.next.bindEquipment"
    : equipmentChecklistState === "optional_unknown"
    ? "stationSession.setup.next.optionalEquipmentUnknown"
    : "stationSession.setup.next.ready";

  const isOpenSession = session?.status === "open";
  const showBackendRevalidateHint =
    equipmentChecklistState === "optional_unknown" || equipmentChecklistState === "not_confirmed";

  const checklistToneClass = (state: string) => {
    if (state === "ready" || state === "open" || state === "identified" || state === "bound") {
      return "border-emerald-200 bg-emerald-50 text-emerald-800";
    }
    if (state === "missing" || state === "closed" || state === "required_missing") {
      return "border-amber-200 bg-amber-50 text-amber-900";
    }
    return "border-slate-200 bg-slate-50 text-slate-700";
  };

  const sessionStatusLabel = !session
    ? t("stationSession.state.missing")
    : isOpenSession
    ? t("stationSession.state.open")
    : t("stationSession.state.closed");

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("stationSession.setup.title")}
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

      <p className="text-sm text-slate-700">{t("stationSession.setup.subtitle")}</p>

      <StationWorkflowShell
        currentStage={isOpenSession ? "STX_009_END_SESSION" : "STX_001_STATION_SESSION"}
        stationId={stationId || null}
        sessionId={session?.session_id ?? null}
        operatorUserId={session?.operator_user_id ?? null}
        equipmentId={session?.equipment_id ?? null}
        compact
        recoveryBanner={isOpenSession ? undefined : sessionRecoveryBanner}
      >
        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2">
            <CheckSquare className="h-4 w-4 text-slate-600" />
            <h2 className="text-sm font-semibold text-slate-900">{t("stationSession.setup.checklist.title")}</h2>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
            <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(stationChecklistState)}`}>
              <p className="text-xs font-medium">{t("stationSession.setup.checklist.station")}</p>
              <p className="mt-1">{stationId || t("stationSession.state.notConfirmed")}</p>
            </div>
            <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(sessionChecklistState)}`}>
              <p className="text-xs font-medium">{t("stationSession.setup.checklist.session")}</p>
              <p className="mt-1">{sessionStatusLabel}</p>
            </div>
            <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(operatorChecklistState)}`}>
              <p className="text-xs font-medium">{t("stationSession.setup.checklist.operator")}</p>
              <p className="mt-1">{session?.operator_user_id || t("stationSession.state.missing")}</p>
            </div>
            <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(equipmentChecklistState)}`}>
              <p className="text-xs font-medium">{t("stationSession.setup.checklist.equipment")}</p>
              <p className="mt-1">{t(`station.handoff.state.equipment.${equipmentChecklistState}`)}</p>
            </div>
          </div>
        </section>

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
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
                <h2 className="text-sm font-semibold text-slate-900">{t("stationSession.setup.section.session")}</h2>
                <p className="mt-1 text-xs text-slate-500">{t("stationSession.setup.section.sessionHint")}</p>
                <dl className="mt-3 space-y-2 text-sm">
                  <div className="flex items-center justify-between gap-2">
                    <dt className="text-slate-500">{t("stationSession.label.session_id")}</dt>
                    <dd className="font-mono text-xs text-slate-700">{session.session_id}</dd>
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <dt className="text-slate-500">{t("common.status")}</dt>
                    <dd className="text-slate-700">{sessionStatusLabel}</dd>
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <dt className="text-slate-500">{t("stationSession.label.opened_at")}</dt>
                    <dd className="text-xs text-slate-700">{new Date(session.opened_at).toLocaleString()}</dd>
                  </div>
                </dl>

                <div className="mt-3 flex flex-wrap gap-2">
                  {!isOpenSession ? (
                    <button
                      type="button"
                      onClick={handleOpenSession}
                      disabled={opening || !stationId}
                      className="min-h-10 rounded-lg border border-blue-600 bg-blue-600 px-3 text-sm font-medium text-white transition hover:bg-blue-700 active:scale-95 disabled:opacity-50"
                    >
                      {opening ? t("stationSession.action.openingSession") : t("stationSession.action.openSession")}
                    </button>
                  ) : null}
                  <button
                    type="button"
                    onClick={loadSession}
                    disabled={loading}
                    className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95 disabled:opacity-50"
                  >
                    {t("stationSession.action.viewSession")}
                  </button>
                </div>
              </section>

              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-slate-500" />
                  <h2 className="text-sm font-semibold text-slate-900">{t("stationSession.setup.section.operator")}</h2>
                </div>
                <p className="mt-1 text-xs text-slate-500">{t("stationSession.setup.section.operatorHint")}</p>
                <p className="mt-3 text-sm text-slate-700">
                  {session.operator_user_id || t("stationSession.operator.unassigned")}
                </p>
                <button
                  type="button"
                  onClick={goToOperatorIdentification}
                  className="mt-3 min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95"
                >
                  {t("stationSession.action.identifyOperator")}
                </button>
              </section>

              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-slate-500" />
                  <h2 className="text-sm font-semibold text-slate-900">{t("stationSession.setup.section.equipment")}</h2>
                </div>
                <p className="mt-1 text-xs text-slate-500">{t("stationSession.setup.section.equipmentHint")}</p>
                <p className="mt-3 text-sm text-slate-700">
                  {session.equipment_id || t("station.handoff.state.equipment.optional_unknown")}
                </p>
                <button
                  type="button"
                  onClick={goToEquipmentBinding}
                  className="mt-3 min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95"
                >
                  {t("stationSession.action.openEquipmentContext")}
                </button>
              </section>
            </div>

            <section className="rounded-xl border border-blue-200 bg-blue-50 p-4 sm:p-5">
              <h2 className="text-sm font-semibold text-blue-900">{t("stationSession.setup.continue.title")}</h2>
              <p className="mt-1 text-sm text-blue-800">{t(nextStepKey)}</p>
              {showBackendRevalidateHint ? (
                <p className="mt-2 text-xs text-blue-700">{t("stationSession.setup.continue.backendRevalidate")}</p>
              ) : null}
              <button
                type="button"
                onClick={goToStationQueue}
                disabled={!stationId}
                className="mt-3 min-h-11 rounded-lg border border-blue-600 bg-blue-600 px-4 text-sm font-semibold text-white transition hover:bg-blue-700 active:scale-95 disabled:opacity-50"
              >
                {t("stationSession.setup.continue.cta")}
              </button>
            </section>

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
                    onClick={goToStationQueue}
                    className="min-h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-95"
                  >
                    {t("stationSession.setup.continue.cta")}
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
          </>
        )}
      </StationWorkflowShell>
    </div>
  );
}


