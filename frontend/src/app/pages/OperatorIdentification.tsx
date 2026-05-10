import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, BadgeCheck, RefreshCw, ShieldAlert, User } from "lucide-react";
import { useNavigate, useSearchParams } from "react-router";
import { toast } from "sonner";
import { BackendRequiredNotice, MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { stationApi, type StationSessionItem } from "@/app/api";
import { useAuth } from "@/app/auth";
import { useI18n } from "@/app/i18n";
import {
  normalizeStationCommandError,
  type StationCommandErrorMessage,
} from "@/app/components/station-execution/stationCommandErrorMessages";
import { StationWorkflowShell } from "@/app/components/station-execution/StationWorkflowShell";
import { StationEntryHandoff } from "@/app/components/station-execution/StationEntryHandoff";

type IdentifyStatus = "pending" | "verified" | "unauthorized";

export function OperatorIdentification() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [searchParams] = useSearchParams();

  const stationId = (searchParams.get("stationId") || "").trim();
  const sessionIdFromQuery = (searchParams.get("sessionId") || "").trim();
  const operationId = (searchParams.get("operationId") || "").trim();

  const [session, setSession] = useState<StationSessionItem | null>(null);
  const [operatorUserId, setOperatorUserId] = useState<string>(currentUser?.user_id ?? "");
  const [loadingSession, setLoadingSession] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [identifyStatus, setIdentifyStatus] = useState<IdentifyStatus>("pending");
  const [commandError, setCommandError] = useState<StationCommandErrorMessage | null>(null);

  const presentIdentifyError = (error: unknown, fallbackKey: string) => {
    const normalized = normalizeStationCommandError(error);
    setCommandError(normalized);

    if (normalized.code !== "UNKNOWN") {
      toast.error(t(normalized.messageKey));
      return;
    }

    toast.error(t(fallbackKey));
  };

  const hasSessionContext = Boolean((session?.session_id || sessionIdFromQuery).trim());

  const resolvedSessionId = useMemo(
    () => (session?.session_id || sessionIdFromQuery || "").trim(),
    [session?.session_id, sessionIdFromQuery]
  );

  const returnToStation = () => {
    const target = operationId ? `/station?operationId=${encodeURIComponent(operationId)}` : "/station";
    navigate(target);
  };

  const goToEquipmentBinding = () => {
    const params = new URLSearchParams();
    if (stationId) {
      params.set("stationId", stationId);
    }
    if (resolvedSessionId) {
      params.set("sessionId", resolvedSessionId);
    }
    if (operationId) {
      params.set("operationId", operationId);
    }
    const query = params.toString();
    navigate(query ? `/equipment-binding?${query}` : "/equipment-binding");
  };

  const goToStationCockpit = () => {
    const params = new URLSearchParams();
    if (operationId) {
      params.set("operationId", operationId);
    }
    const query = params.toString();
    navigate(query ? `/station?${query}` : "/station");
  };

  const loadCurrentSession = async () => {
    if (!stationId) {
      return;
    }
    setLoadingSession(true);
    try {
      const response = await stationApi.getCurrentSession(stationId);
      setSession(response.session);
      setCommandError(null);
      const sessionOperator = (response.session?.operator_user_id || "").trim();
      if (sessionOperator) {
        setOperatorUserId(sessionOperator);
        setIdentifyStatus("verified");
      } else {
        setIdentifyStatus("pending");
      }
    } catch (err) {
      setSession(null);
      setIdentifyStatus("unauthorized");
      presentIdentifyError(err, "operatorId.toast.sessionLoadFailed");
    } finally {
      setLoadingSession(false);
    }
  };

  useEffect(() => {
    void loadCurrentSession();
  }, [stationId]);

  useEffect(() => {
    if (currentUser?.user_id && !operatorUserId) {
      setOperatorUserId(currentUser.user_id);
    }
  }, [currentUser?.user_id, operatorUserId]);

  const submitIdentify = async () => {
    const normalizedOperatorId = operatorUserId.trim();
    if (!normalizedOperatorId) {
      toast.error(t("operatorId.toast.operatorRequired"));
      return;
    }

    if (!resolvedSessionId) {
      toast.error(t("operatorId.toast.sessionRequired"));
      return;
    }

    setSubmitting(true);
    try {
      const updated = await stationApi.identifyOperator(resolvedSessionId, normalizedOperatorId);
      setSession(updated);
      setIdentifyStatus("verified");
      setCommandError(null);
      toast.success(t("operatorId.toast.identified"));
    } catch (err) {
      setIdentifyStatus("unauthorized");
      presentIdentifyError(err, "operatorId.toast.identifyFailed");
    } finally {
      setSubmitting(false);
    }
  };

  const statusLabelKey =
    identifyStatus === "verified"
      ? "operatorId.status.verified"
      : identifyStatus === "unauthorized"
      ? "operatorId.status.unauthorized"
      : "operatorId.status.pending";

  const statusBadgeClass =
    identifyStatus === "verified"
      ? "bg-green-100 text-green-700"
      : identifyStatus === "unauthorized"
      ? "bg-red-100 text-red-700"
      : "bg-gray-100 text-gray-600";

  const handoffSessionState = !stationId
    ? "not_confirmed"
    : !resolvedSessionId
    ? "missing"
    : session?.status === "open"
    ? "open"
    : session?.status
    ? "closed"
    : "not_confirmed";

  const handoffOperatorState = identifyStatus === "verified"
    ? "identified"
    : identifyStatus === "pending"
    ? "missing"
    : "not_confirmed";

  const handoffEquipmentState = session?.equipment_id
    ? "bound"
    : commandError?.code === "EQUIPMENT_REQUIRED"
    ? "required_missing"
    : resolvedSessionId
    ? "optional_unknown"
    : "not_confirmed";

  const nextStepKey = handoffOperatorState !== "identified"
    ? "station.handoff.next.identifyOperatorBeforeExecution"
    : handoffEquipmentState === "required_missing"
    ? "station.handoff.next.bindEquipmentBeforeExecution"
    : handoffEquipmentState === "optional_unknown"
    ? "station.handoff.next.operatorDoneEquipmentUnknown"
    : "station.handoff.next.goToCockpit";

  return (
    <div className="flex flex-col gap-4 p-4 max-w-2xl mx-auto">
      <MockWarningBanner phase="PARTIAL" />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">{t("operatorId.title")}</h1>
          <ScreenStatusBadge phase="PARTIAL" />
        </div>
        <button
          type="button"
          onClick={returnToStation}
          className="min-h-10 px-3 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
        >
          <ArrowLeft className="inline w-4 h-4 mr-1" />
          {t("operatorId.action.backToStation")}
        </button>
      </div>

      <BackendRequiredNotice message={t("operatorId.notice.active")} />

      <StationWorkflowShell
        currentStage="STX_002_OPERATOR_IDENTIFICATION"
        stationId={stationId || null}
        sessionId={resolvedSessionId || null}
        operatorUserId={session?.operator_user_id ?? operatorUserId ?? null}
        equipmentId={session?.equipment_id ?? null}
        recoveryBanner={commandError ? (
          <div
            className={`rounded-lg border px-4 py-3 text-sm ${commandError.severity === "danger" ? "border-red-200 bg-red-50 text-red-800" : "border-amber-200 bg-amber-50 text-amber-800"}`}
            role="alert"
          >
            <p className="font-semibold">{t(commandError.titleKey)}</p>
            <p className="mt-1">{t(commandError.messageKey)}</p>
            <p className="mt-1 text-xs">{t(commandError.recoveryKey)}</p>
          </div>
        ) : undefined}
      >
        <StationEntryHandoff
          stationState={stationId ? "selected" : "missing"}
          sessionState={handoffSessionState}
          operatorState={handoffOperatorState}
          equipmentState={handoffEquipmentState}
          nextStepKey={nextStepKey}
          ctas={[
            { labelKey: "station.handoff.cta.equipmentBinding", onClick: goToEquipmentBinding, tone: "primary" },
            { labelKey: "station.handoff.cta.stationCockpit", onClick: goToStationCockpit },
          ]}
          footer={t("station.handoff.unknownPolicyHint")}
        />

        <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-4">
          <User className="w-4 h-4 text-blue-500" />
          {t("operatorId.section.identity")}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
          <div className="flex flex-col gap-1">
            <span className="text-xs text-gray-500">{t("operatorId.field.stationId")}</span>
            <span className="text-sm text-gray-800">{stationId || "-"}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs text-gray-500">{t("operatorId.field.sessionId")}</span>
            <span className="text-sm text-gray-800">{resolvedSessionId || "-"}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs text-gray-500">{t("operatorId.field.currentOperator")}</span>
            <span className="text-sm text-gray-800">
              {session?.operator_user_id || t("operatorId.unidentified")}
            </span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs text-gray-500">{t("operatorId.field.authenticatedUser")}</span>
            <span className="text-sm text-gray-800">{currentUser?.user_id || "-"}</span>
          </div>
        </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-4">
          <BadgeCheck className="w-4 h-4 text-purple-500" />
          {t("operatorId.section.scan")}
        </div>

        <div className="flex flex-col gap-3 py-1">
          <input
            type="text"
            value={operatorUserId}
            onChange={(event) => setOperatorUserId(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void submitIdentify();
              }
            }}
            placeholder={t("operatorId.input.placeholder")}
            className="min-h-12 px-4 rounded-lg border border-gray-300 text-sm text-gray-900"
            aria-label={t("operatorId.input.label")}
          />

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => void loadCurrentSession()}
              disabled={loadingSession || !stationId}
              className="min-h-11 px-4 rounded-lg border border-gray-300 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className="inline w-4 h-4 mr-1" />
              {t("operatorId.action.refreshSession")}
            </button>
            <button
              type="button"
              onClick={() => void submitIdentify()}
              disabled={submitting || !hasSessionContext}
              className="min-h-11 px-4 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              <BadgeCheck className="inline w-4 h-4 mr-1" />
              {submitting ? t("operatorId.action.submitting") : t("operatorId.action.identify")}
            </button>
          </div>

          {!hasSessionContext && (
            <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
              {t("operatorId.session.missing")}
            </p>
          )}
        </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-5">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 pb-2 mb-4">
          <ShieldAlert className="w-4 h-4 text-amber-500" />
          {t("operatorId.section.authorization")}
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{t("operatorId.field.status")}</span>
            <span className={`text-xs px-2 py-1 rounded-full ${statusBadgeClass}`}>
              {t(statusLabelKey)}
            </span>
          </div>

          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2 mt-2">
            {t("operatorId.notice.backendTruth")}
          </p>

          {loadingSession && (
            <p className="text-xs text-gray-500" role="status">
              {t("operatorId.status.loadingSession")}
            </p>
          )}

          {identifyStatus === "verified" && session?.operator_user_id && (
            <p className="text-xs text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">
              {t("operatorId.status.identifiedAs", { operatorId: session.operator_user_id })}
            </p>
          )}

          {identifyStatus === "unauthorized" && (
            <p className="text-xs text-red-700 bg-red-50 border border-red-200 rounded px-3 py-2" role="alert">
              {t("operatorId.status.unableToIdentify")}
            </p>
          )}
        </div>
        </div>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={returnToStation}
            className="flex-1 min-h-11 px-4 py-2 rounded-md border border-gray-200 bg-white text-gray-700 text-sm hover:bg-gray-50"
          >
            <ArrowLeft className="inline w-4 h-4 mr-1" />
            {t("operatorId.action.backToStation")}
          </button>
          <button
            type="button"
            onClick={() => void submitIdentify()}
            disabled={submitting || !hasSessionContext}
            className="flex-1 min-h-11 px-4 py-2 rounded-md bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? t("operatorId.action.submitting") : t("operatorId.action.identify")}
          </button>
        </div>
      </StationWorkflowShell>
    </div>
  );
}
