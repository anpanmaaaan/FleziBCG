import { Cpu } from "lucide-react";
import { useI18n } from "@/app/i18n";
import type { I18nSemanticKey } from "@/app/i18n/keys";

interface BindEquipmentPanelProps {
  equipmentId: string | null;
  equipmentChecklistState: string;
  sessionOpen: boolean;
  onBindEquipment: () => void;
}

export function BindEquipmentPanel({
  equipmentId,
  equipmentChecklistState,
  sessionOpen,
  onBindEquipment,
}: BindEquipmentPanelProps) {
  const { t } = useI18n();

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div className="flex items-center gap-2">
        <Cpu className="h-4 w-4 text-slate-500" />
        <h2 className="text-sm font-semibold text-slate-900">
          {t("stationSession.setup.section.equipment" as I18nSemanticKey)}
        </h2>
      </div>
      <p className="mt-1 text-xs text-slate-500">
        {t("stationSession.setup.section.equipmentHint" as I18nSemanticKey)}
      </p>
      <p className="mt-3 text-sm text-slate-700">
        {equipmentId || t(`station.handoff.state.equipment.${equipmentChecklistState}` as I18nSemanticKey)}
      </p>
      {sessionOpen && (
        <button
          type="button"
          onClick={onBindEquipment}
          className="mt-3 min-h-11 rounded-lg border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-50 active:scale-[0.98]"
        >
          {t("stationSession.action.openEquipmentContext" as I18nSemanticKey)}
        </button>
      )}
    </section>
  );
}
