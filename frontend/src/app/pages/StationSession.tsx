// Station Session — CONNECTED (backend API)
// Shows current session state from GET /v1/station/sessions/current.
// Session truth is managed by the backend execution system.

import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { RefreshCw } from "lucide-react";
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
import { StationEntryPanel } from "@/app/components/station-execution/StationEntryPanel";
import { OpenSessionPanel } from "@/app/components/station-execution/OpenSessionPanel";
import { IdentifyOperatorPanel } from "@/app/components/station-execution/IdentifyOperatorPanel";
import { BindEquipmentPanel } from "@/app/components/station-execution/BindEquipmentPanel";
import { CloseSessionPanel } from "@/app/components/station-execution/CloseSessionPanel";
import type { I18nSemanticKey } from "@/app/i18n/keys";

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
      toast.error(t(normalized.messageKey as I18nSemanticKey));
      return;
    }

    toast.error(t(fallbackKey as I18nSemanticKey));
  };

  const loadSession = () => {
    if (!stationId) {
      setSession(null);
      setCommandError(null);
      setShowCloseConfirm(false);
      setLoading(false);
      return;
    }
    setLoading(true);
    stationApi
      .getCurrentSession(stationId)
      .then((res) => {
        setSession(res.session ?? null);
        setCommandError(null);
        setShowCloseConfirm(false);
      })
      .catch((error) => presentSessionError(error, "stationSession.notice.failed_to_load_session" as I18nSemanticKey))
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
        toast.success(t("stationSession.toast.closed" as I18nSemanticKey));
      })
      .catch((error) => presentSessionError(error, "stationSession.toast.closeFailed" as I18nSemanticKey))
      .finally(() => setClosing(false));
  };

  const handleOpenSession = () => {
    if (!stationId) {
      toast.error(t("stationSession.notice.missingStationId" as I18nSemanticKey));
      return;
    }
    setOpening(true);
    stationApi
      .openSession({ station_id: stationId })
      .then((opened) => {
        setSession(opened);
        setCommandError(null);
        setShowCloseConfirm(false);
        toast.success(t("stationSession.toast.opened" as I18nSemanticKey));
      })
      .catch((error) => presentSessionError(error, "stationSession.toast.openFailed" as I18nSemanticKey))
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
    ? ("stationSession.setup.next.selectStation" as I18nSemanticKey)
    : !session
    ? ("stationSession.setup.next.openSession" as I18nSemanticKey)
    : session.status !== "open"
    ? ("stationSession.setup.next.openSession" as I18nSemanticKey)
    : !session.operator_user_id
    ? ("stationSession.setup.next.identifyOperator" as I18nSemanticKey)
    : equipmentChecklistState === "required_missing"
    ? ("stationSession.setup.next.bindEquipment" as I18nSemanticKey)
    : equipmentChecklistState === "optional_unknown"
    ? ("stationSession.setup.next.optionalEquipmentUnknown" as I18nSemanticKey)
    : ("stationSession.setup.next.ready" as I18nSemanticKey);

  const isOpenSession = session?.status === "open";

  /**
   * BT-CORE-004: UI navigation readiness only — not backend authorization.
   * Backend revalidates session/operator/equipment on execution mutation commands.
   */
  const canNavigateToQueueByVisibleSetupState =
    Boolean(stationId) &&
    session?.status === "open" &&
    Boolean(session?.operator_user_id) &&
    equipmentChecklistState !== "required_missing";

  const showBackendRevalidateHint =
    equipmentChecklistState === "optional_unknown" || equipmentChecklistState === "not_confirmed";

  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("stationSession.setup.title" as I18nSemanticKey)}
          </h1>
          <ScreenStatusBadge phase="CONNECTED" />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadSession}
            disabled={loading}
            className="flex items-center gap-1 px-3 py-2 rounded-md border border-gray-200 bg-white text-gray-600 text-sm hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className="w-3 h-3" />
            {t("common.action.refresh" as I18nSemanticKey)}
          </button>
        </div>
      </div>

  <p className="text-sm text-slate-700">{t("stationSession.setup.subtitle" as I18nSemanticKey)}</p>

      <StationWorkflowShell
        currentStage={isOpenSession ? "STX_009_END_SESSION" : "STX_001_STATION_SESSION"}
        stationId={stationId || null}
        sessionId={session?.session_id ?? null}
        operatorUserId={session?.operator_user_id ?? null}
        equipmentId={session?.equipment_id ?? null}
        compact
        recoveryBanner={isOpenSession ? undefined : commandError ? <div
          className={`rounded-lg border px-4 py-3 text-sm ${commandError.severity === "danger" ? "border-red-200 bg-red-50 text-red-800" : "border-amber-200 bg-amber-50 text-amber-800"}`}
          role="alert"
        >
          <p className="font-semibold">{t(commandError.titleKey as I18nSemanticKey)}</p>
          <p className="mt-1">{t(commandError.messageKey as I18nSemanticKey)}</p>
          <p className="mt-1 text-xs">{t(commandError.recoveryKey as I18nSemanticKey)}</p>
        </div> : undefined}
      >
        {/* Mode A Setup Panels */}
        <StationEntryPanel
          stationId={stationId}
          sessionStatus={(session?.status ?? null) as "open" | "closed" | null}
          operatorUserId={session?.operator_user_id ?? null}
          equipmentId={session?.equipment_id ?? null}
          equipmentChecklistState={equipmentChecklistState}
        />

        {!stationId && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-700">
            {t("stationSession.notice.missingStationId" as I18nSemanticKey)}
          </div>
        )}

        {loading ? (
          <div className="p-8 text-center text-gray-400 text-sm">{t("stationSession.label.loading_session" as I18nSemanticKey)}</div>
        ) : !session ? (
          <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-500 text-center">
            {t("stationSession.session.noActive" as I18nSemanticKey)}
          </div>
        ) : (
          <>
            {/* Mode A Setup: Session Management */}
            <OpenSessionPanel
              sessionId={session.session_id}
              openedAt={session.opened_at}
              sessionStatus={session.status}
              loading={loading}
              opening={opening}
              onOpenSession={handleOpenSession}
              onEndSessionClick={() => setShowCloseConfirm(true)}
              onRefresh={loadSession}
            />

            {/* Mode A Setup: Operator Identification */}
            <IdentifyOperatorPanel
              operatorUserId={session.operator_user_id}
              sessionOpen={isOpenSession}
              onIdentifyOperator={goToOperatorIdentification}
            />

            {/* Mode A Setup: Equipment Binding */}
            <BindEquipmentPanel
              equipmentId={session.equipment_id}
              equipmentChecklistState={equipmentChecklistState}
              sessionOpen={isOpenSession}
              onBindEquipment={goToEquipmentBinding}
            />

            <section className="rounded-xl border border-blue-200 bg-blue-50 p-4 sm:p-5">
              <h2 className="text-sm font-semibold text-blue-900">{t("stationSession.setup.continue.title" as I18nSemanticKey)}</h2>
              <p className="mt-1 text-sm text-blue-800">{t(nextStepKey)}</p>
              {showBackendRevalidateHint ? (
                <p className="mt-2 text-xs text-blue-700">{t("stationSession.setup.continue.backendRevalidate" as I18nSemanticKey)}</p>
              ) : null}
              <button
                type="button"
                onClick={goToStationQueue}
                disabled={!canNavigateToQueueByVisibleSetupState}
                className="mt-3 min-h-11 rounded-lg border border-blue-600 bg-blue-600 px-4 text-sm font-semibold text-white transition hover:bg-blue-700 active:scale-95 disabled:opacity-50"
              >
                {t("stationSession.setup.continue.cta" as I18nSemanticKey)}
              </button>
            </section>

            {/* Mode A Cleanup: Close Session (only when open) */}
            <CloseSessionPanel
              isSessionOpen={isOpenSession}
              showCloseConfirm={showCloseConfirm}
              closing={closing}
              commandError={commandError}
              onClose={() => setShowCloseConfirm(true)}
              onConfirmClose={handleClose}
              onCancelClose={() => setShowCloseConfirm(false)}
            />
          </>
        )}
      </StationWorkflowShell>
    </div>
  );
}


