import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router";
import { ArrowLeft, Lock, GitBranch } from "lucide-react";
import { HttpError, routingApi, type RoutingItemFromAPI } from "@/app/api";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice, RoutingLifecycleBadge, RoutingOperationSequenceBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";

export function RoutingOperationDetail() {
  const { t } = useI18n();
  const { routeId, operationId } = useParams<{ routeId: string; operationId: string }>();

  const [routing, setRouting] = useState<RoutingItemFromAPI | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  const resolveErrorMessage = (error: unknown): string => {
    if (error instanceof HttpError && typeof error.message === "string" && error.message.trim().length > 0) {
      return error.message;
    }
    return t("common.error.load_failed");
  };

  const loadRouting = async (signal?: AbortSignal) => {
    if (!routeId || !operationId) {
      setRouting(null);
      setNotFound(true);
      setErrorMessage(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setNotFound(false);

    try {
      const data = await routingApi.getRouting(routeId, signal);
      const exists = data.operations.some((op) => op.operation_id === operationId);

      if (!exists) {
        setRouting(null);
        setNotFound(true);
        return;
      }

      setRouting(data);
    } catch (error) {
      if (signal?.aborted) {
        return;
      }
      if (error instanceof HttpError && error.status === 404) {
        setNotFound(true);
        setRouting(null);
      } else {
        setErrorMessage(resolveErrorMessage(error));
        setRouting(null);
      }
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    void loadRouting(controller.signal);
    return () => controller.abort();
  }, [routeId, operationId]);

  const operation = useMemo(() => {
    if (!routing || !operationId) {
      return null;
    }
    return routing.operations.find((op) => op.operation_id === operationId) ?? null;
  }, [routing, operationId]);

  const resourceSection = operation ? [
    { label: "Required Resource Type", value: operation.required_resource_type ?? "-" },
  ] : [];

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="PARTIAL"
        note="Operation execution eligibility and resource applicability are determined by backend execution and MMD systems."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Back nav */}
        <div className="mb-4">
          <Link to={routeId ? `/routes/${routeId}` : "/routes"} className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
            <ArrowLeft className="w-4 h-4" />
            {t("routingOpDetail.back")}
          </Link>
        </div>

        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <GitBranch className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("routingOpDetail.title")}</h1>
            <ScreenStatusBadge phase="PARTIAL" />
          </div>
          <div className="flex items-center gap-2">
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("routingOpDetail.action.release")}
            </button>
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("routingOpDetail.action.edit")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice message={t("routingOpDetail.notice.shell")} tone="blue" />

        {loading && (
          <div className="rounded-lg border border-gray-200 bg-white px-4 py-10 text-center text-sm text-gray-500 shadow-sm">
            {t("routingOpDetail.loading")}
          </div>
        )}

        {!loading && errorMessage && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-800 shadow-sm">
            {errorMessage}
          </div>
        )}

        {!loading && !errorMessage && operation && routing ? (
          <div className="space-y-6">
            {/* Identity section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{t("routingOpDetail.section.identity")}</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.operationCode")}</div>
                  <div className="font-mono text-sm font-medium text-slate-700">{operation.operation_code}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.operationName")}</div>
                  <div className="text-sm text-slate-900">{operation.operation_name}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.routeCode")}</div>
                  <div className="font-mono text-sm text-slate-700">{routing.routing_code}</div>
                  <div className="text-xs text-gray-400">{routing.routing_name}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.sequence")}</div>
                  <RoutingOperationSequenceBadge sequence={operation.sequence_no} />
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("routingOpDetail.field.workCenter")}</div>
                  <div className="font-mono text-sm text-slate-700">{operation.work_center_code ?? "—"}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.status")}</div>
                  <RoutingLifecycleBadge status={routing.lifecycle_status} />
                </div>
              </div>
            </div>

            {/* Timing section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{t("routingOpDetail.section.timing")}</h2>
              <div className="grid grid-cols-3 gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div>
                  <div className="text-xs text-blue-600 mb-1">{t("routingOpDetail.field.stdTime")}</div>
                  <div className="text-xl font-semibold text-blue-900">{operation.standard_cycle_time ?? "-"} min</div>
                </div>
                <div>
                  <div className="text-xs text-blue-600 mb-1">{t("routingOpDetail.field.setupTime")}</div>
                  <div className="text-xl font-semibold text-blue-900">{operation.setup_time != null ? `${operation.setup_time} min` : "—"}</div>
                </div>
                <div>
                  <div className="text-xs text-blue-600 mb-1">{t("routingOpDetail.field.runTime")}</div>
                  <div className="text-xl font-semibold text-blue-900">{operation.run_time_per_unit != null ? `${operation.run_time_per_unit} min` : "—"}</div>
                </div>
              </div>
            </div>

            {/* Resources section */}
            <div>
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{t("routingOpDetail.section.resources")}</h2>
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3">
                {resourceSection.map((r) => (
                  <div key={r.label} className="flex items-center gap-4">
                    <div className="w-48 text-xs text-gray-500">{r.label}</div>
                    <div className="font-mono text-sm text-slate-700">{r.value}</div>
                  </div>
                ))}
                <div className="flex items-center justify-between gap-4 pt-2 border-t border-gray-200">
                  <div className="text-xs text-gray-400 italic">Resource assignment and validation requires backend MMD and resource applicability check.</div>
                  {routeId && operationId && (
                    <Link
                      to={`/resource-requirements?routeId=${encodeURIComponent(routeId)}&operationId=${encodeURIComponent(operationId)}`}
                      className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 font-medium shrink-0"
                    >
                      {t("routingOpDetail.action.viewResourceReqs")}
                    </Link>
                  )}
                </div>
              </div>
            </div>

            {/* Description */}
          </div>
        ) : null}

        {!loading && !errorMessage && (notFound || !operation) && (
          <div className="p-8 text-center text-gray-400">{t("routingOpDetail.notFound")}</div>
        )}

        <p className="mt-6 text-xs text-gray-400">
          Operation data is for visualization only. Backend execution system determines actual execution eligibility and routing applicability.
        </p>
      </div>
    </div>
  );
}
