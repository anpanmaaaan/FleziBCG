import type { OperationDetail } from "@/app/api";
import { useI18n } from "@/app/i18n";

export interface AllowedActionZoneProps {
  operation: OperationDetail;
  actionLoading: boolean;
  downtimeLoading: boolean;
  canExecuteByClaim: boolean;
  canPauseExecution: boolean;
  canStartDowntime: boolean;
  canCompleteExecution: boolean;
  canResumeExecution: boolean;
  canEndDowntimeAction: boolean;
  canDo: (action: string) => boolean;
  onStartOperation: () => void;
  onPauseOperation: () => void;
  onOpenDowntimeModal: () => void;
  onCompleteOperation: () => void;
  onResumeOperation: () => void;
  onEndDowntime: () => void;
}

export function AllowedActionZone({
  operation,
  actionLoading,
  downtimeLoading,
  canExecuteByClaim,
  canPauseExecution,
  canStartDowntime,
  canCompleteExecution,
  canResumeExecution,
  canEndDowntimeAction,
  canDo,
  onStartOperation,
  onPauseOperation,
  onOpenDowntimeModal,
  onCompleteOperation,
  onResumeOperation,
  onEndDowntime,
}: AllowedActionZoneProps) {
  const { t } = useI18n();

  return (
    <section className="shrink-0 flex flex-col gap-3 sm:gap-4 pb-1">
      {operation.status === "PLANNED" && (
        <button
          onClick={onStartOperation}
          disabled={actionLoading || operation.closure_status === "CLOSED" || !canExecuteByClaim || !canDo("start_execution")}
          className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold tracking-wide bg-green-600 text-white hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl"
        >
          {t("station.action.clockOn")}
        </button>
      )}

      {operation.status === "IN_PROGRESS" && (
        <>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={onPauseOperation}
              disabled={actionLoading || operation.closure_status === "CLOSED" || !canPauseExecution}
              className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-amber-400 text-slate-900 hover:bg-amber-500 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {t("station.action.pause")}
            </button>
            <button
              onClick={onOpenDowntimeModal}
              disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canStartDowntime}
              className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-slate-600 text-white hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {t("station.action.startDowntime")}
            </button>
          </div>
          {canCompleteExecution && (
            <button
              onClick={onCompleteOperation}
              disabled={actionLoading || operation.closure_status === "CLOSED" || !canCompleteExecution}
              className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl border-2 border-amber-500 bg-white text-amber-700 hover:bg-amber-50 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {t("station.action.completeOperation")}
            </button>
          )}
        </>
      )}

      {operation.status === "PAUSED" && (
        <>
          {!operation.downtime_open ? (
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={onResumeOperation}
                disabled={actionLoading || operation.closure_status === "CLOSED" || !canResumeExecution}
                className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {t("station.action.resume")}
              </button>
              <button
                onClick={onOpenDowntimeModal}
                disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canStartDowntime}
                className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-slate-600 text-white hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {t("station.action.startDowntime")}
              </button>
            </div>
          ) : (
            <button
              onClick={onEndDowntime}
              disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canEndDowntimeAction}
              className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {t("station.action.endDowntime")}
            </button>
          )}
        </>
      )}

      {operation.status === "BLOCKED" && operation.downtime_open && (
        <button
          onClick={onEndDowntime}
          disabled={downtimeLoading || operation.closure_status === "CLOSED" || !canEndDowntimeAction}
          className="min-h-14 w-full rounded-2xl px-6 text-xl font-bold shadow-sm active:scale-[0.98] transition sm:min-h-16 sm:text-2xl md:min-h-18 md:px-8 md:text-3xl bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {t("station.action.endDowntime")}
        </button>
      )}
    </section>
  );
}