import { CheckSquare } from "lucide-react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

interface StationEntryPanelProps {
  stationId: string | null;
  sessionStatus: "open" | "closed" | null;
  operatorUserId: string | null;
  equipmentId: string | null;
  equipmentChecklistState: string;
}

export function StationEntryPanel({
  stationId,
  sessionStatus,
  operatorUserId,
  equipmentId,
  equipmentChecklistState,
}: StationEntryPanelProps) {
  const { t } = useI18n();

  const stationChecklistState = stationId ? "ready" : "missing";
  const sessionChecklistState = !stationId
    ? "not_confirmed"
    : !sessionStatus
    ? "missing"
    : sessionStatus === "open"
    ? "open"
    : "closed";
  const operatorChecklistState = !sessionStatus
    ? "not_confirmed"
    : operatorUserId
    ? "identified"
    : "missing";

  const checklistToneClass = (state: string) => {
    if (state === "ready" || state === "open" || state === "identified" || state === "bound") {
      return "border-emerald-200 bg-emerald-50 text-emerald-800";
    }
    if (state === "missing" || state === "closed" || state === "required_missing") {
      return "border-amber-200 bg-amber-50 text-amber-900";
    }
    return "border-slate-200 bg-slate-50 text-slate-700";
  };

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
      <div className="flex items-center gap-2">
        <CheckSquare className="h-4 w-4 text-slate-600" />
        <h2 className="text-sm font-semibold text-slate-900">
          {t("stationSession.setup.checklist.title" as I18nSemanticKey)}
        </h2>
      </div>
      <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
        <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(stationChecklistState)}`}>
          <p className="text-xs font-medium">
            {t("stationSession.setup.checklist.station" as I18nSemanticKey)}
          </p>
          <p className="mt-1">{stationId || t("stationSession.state.notConfirmed" as I18nSemanticKey)}</p>
        </div>
        <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(sessionChecklistState)}`}>
          <p className="text-xs font-medium">
            {t("stationSession.setup.checklist.session" as I18nSemanticKey)}
          </p>
          <p className="mt-1">
            {!sessionStatus
              ? t("stationSession.state.missing" as I18nSemanticKey)
              : sessionStatus === "open"
              ? t("stationSession.state.open" as I18nSemanticKey)
              : t("stationSession.state.closed" as I18nSemanticKey)}
          </p>
        </div>
        <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(operatorChecklistState)}`}>
          <p className="text-xs font-medium">
            {t("stationSession.setup.checklist.operator" as I18nSemanticKey)}
          </p>
          <p className="mt-1">
            {operatorUserId || t("stationSession.state.missing" as I18nSemanticKey)}
          </p>
        </div>
        <div className={`rounded-lg border px-3 py-2 text-sm ${checklistToneClass(equipmentChecklistState)}`}>
          <p className="text-xs font-medium">
            {t("stationSession.setup.checklist.equipment" as I18nSemanticKey)}
          </p>
          <p className="mt-1">
            {t(`station.handoff.state.equipment.${equipmentChecklistState}` as I18nSemanticKey)}
          </p>
        </div>
      </div>
    </section>
  );
}
