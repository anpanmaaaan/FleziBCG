import type { OperationClosureStatus } from "@/app/api";
import { useI18n } from "@/app/i18n";

export interface ClosureStatePanelProps {
  closureStatus: OperationClosureStatus;
  canCloseOperation: boolean;
  canReopenOperation: boolean;
  actionLoading: boolean;
  onCloseOperation: () => void;
  onOpenReopenModal: () => void;
}

export function ClosureStatePanel({
  closureStatus,
  canCloseOperation,
  canReopenOperation,
  actionLoading,
  onCloseOperation,
  onOpenReopenModal,
}: ClosureStatePanelProps) {
  const { t } = useI18n();

  if (!(canCloseOperation || canReopenOperation || closureStatus === "CLOSED")) {
    return null;
  }

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm sm:p-5 md:p-6 shrink-0">
      <p className="text-base font-semibold uppercase tracking-wide text-slate-500 md:text-lg mb-2">
        {t("station.closure.sectionTitle")}
      </p>
      <p className="mt-2 text-sm sm:text-base text-slate-600 md:text-xl mb-5">
        {t(closureStatus === "CLOSED" ? "station.closed.secondaryHint" : "station.closure.secondaryHint")}
      </p>
      <div className="flex flex-col gap-3">
        {canCloseOperation && (
          <button
            onClick={onCloseOperation}
            disabled={actionLoading || !canCloseOperation}
            className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl border-2 border-slate-400 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            {t("station.action.closeOperation")}
          </button>
        )}
        {canReopenOperation && (
          <button
            onClick={onOpenReopenModal}
            disabled={actionLoading || !canReopenOperation}
            className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {t("station.action.reopen")}
          </button>
        )}
      </div>
    </section>
  );
}
