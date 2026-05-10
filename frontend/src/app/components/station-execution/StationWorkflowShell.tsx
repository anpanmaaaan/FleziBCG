import type { ReactNode } from "react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";
import {
  STATION_WORKFLOW_STAGES,
  type StationWorkflowStageId,
} from "./stationWorkflowStages";

interface StationWorkflowShellProps {
  currentStage: StationWorkflowStageId;
  stationId?: string | null;
  sessionId?: string | null;
  operatorUserId?: string | null;
  equipmentId?: string | null;
  compact?: boolean;
  recoveryBanner?: ReactNode;
  affordanceArea?: ReactNode;
  children: ReactNode;
}

export function StationWorkflowShell({
  currentStage,
  stationId,
  sessionId,
  operatorUserId,
  equipmentId,
  compact = false,
  recoveryBanner,
  affordanceArea,
  children,
}: StationWorkflowShellProps) {
  const { t } = useI18n();

  const currentStageLabel =
    STATION_WORKFLOW_STAGES.find((stage) => stage.id === currentStage)?.labelKey ??
    "station.workflow.value.notSelected";

  const resolvedStationId = stationId?.trim() ? stationId : null;
  const resolvedSessionId = sessionId?.trim() ? sessionId : null;
  const resolvedOperatorId = operatorUserId?.trim() ? operatorUserId : null;
  const resolvedEquipmentId = equipmentId?.trim() ? equipmentId : null;

  return (
    <div className="flex flex-col gap-3">
      <section className={`rounded-xl border border-gray-200 bg-white ${compact ? "p-3" : "p-4"}`}>
        <div className="flex flex-wrap items-center gap-3">
          <p className="text-sm font-semibold text-gray-900">
            {t("station.workflow.shell.title")}
          </p>
          {!compact ? (
            <span className="text-xs text-gray-500">
              {t("station.workflow.currentStage")}: {t(currentStageLabel as I18nSemanticKey)}
            </span>
          ) : null}
        </div>

        {!compact ? (
          <ol className="mt-3 flex gap-2 overflow-x-auto pb-1">
            {STATION_WORKFLOW_STAGES.map((stage) => {
              const active = stage.id === currentStage;
              return (
                <li
                  key={stage.id}
                  aria-current={active ? "step" : undefined}
                >
                  <span
                    className={`shrink-0 rounded-full border px-3 py-1 text-xs font-medium ${
                      active
                        ? "border-blue-600 bg-blue-50 text-blue-700"
                        : "border-gray-300 bg-gray-50 text-gray-600"
                    }`}
                  >
                    <span>{t(stage.labelKey as I18nSemanticKey)}</span>
                    {stage.supervisorOnly ? (
                      <span className="ml-1 rounded-full bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">
                        {t("station.workflow.supervisorOnly")}
                      </span>
                    ) : null}
                  </span>
                </li>
              );
            })}
          </ol>
        ) : null}

        <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg bg-gray-50 px-3 py-2 text-sm">
            <p className="text-xs text-gray-500">{t("station.workflow.context.station")}</p>
            <p className="font-medium text-gray-800">{resolvedStationId ?? t("station.workflow.value.notSelected")}</p>
          </div>
          <div className="rounded-lg bg-gray-50 px-3 py-2 text-sm">
            <p className="text-xs text-gray-500">{t("station.workflow.context.session")}</p>
            <p className="font-medium text-gray-800">{resolvedSessionId ?? t("station.workflow.value.notSelected")}</p>
          </div>
          <div className="rounded-lg bg-gray-50 px-3 py-2 text-sm">
            <p className="text-xs text-gray-500">{t("station.workflow.context.operator")}</p>
            <p className="font-medium text-gray-800">{resolvedOperatorId ?? t("station.workflow.value.notIdentified")}</p>
          </div>
          <div className="rounded-lg bg-gray-50 px-3 py-2 text-sm">
            <p className="text-xs text-gray-500">{t("station.workflow.context.equipment")}</p>
            <p className="font-medium text-gray-800">{resolvedEquipmentId ?? t("station.workflow.value.notBound")}</p>
          </div>
        </div>

        {!compact ? (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded-full bg-emerald-50 px-3 py-1 text-emerald-700">
              {t("station.workflow.operatorFlow")}
            </span>
            <span className="rounded-full bg-amber-50 px-3 py-1 text-amber-700">
              {t("station.workflow.supervisorOnly")}
            </span>
          </div>
        ) : null}
      </section>

      {recoveryBanner}

      <div>{children}</div>

      {affordanceArea ? <div>{affordanceArea}</div> : null}
    </div>
  );
}
