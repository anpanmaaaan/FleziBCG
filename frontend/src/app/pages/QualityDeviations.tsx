import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Clock, RefreshCw, XCircle } from "lucide-react";
import { BackendRequiredNotice, ScreenStatusBadge } from "@/app/components";
import {
  HttpError,
  qualityApi,
  type QualityDeviationRequestItem,
  type QualityDeviationResolveRequest,
} from "@/app/api";
import { useI18n } from "@/app/i18n";

const RESOLUTION_STATUSES: QualityDeviationResolveRequest["resolution_status"][] = [
  "APPROVED",
  "REJECTED",
  "CLOSED",
];

export function QualityDeviations() {
  const { t } = useI18n();
  const [deviations, setDeviations] = useState<QualityDeviationRequestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedResolution, setSelectedResolution] = useState<
    Record<number, QualityDeviationResolveRequest["resolution_status"]>
  >({});
  const [resolutionComment, setResolutionComment] = useState<Record<number, string>>({});
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [resolveResult, setResolveResult] = useState<QualityDeviationRequestItem | null>(null);

  const openCount = useMemo(
    () => deviations.filter((d) => d.status === "OPEN").length,
    [deviations]
  );
  const approvedCount = useMemo(
    () => deviations.filter((d) => d.status === "APPROVED").length,
    [deviations]
  );
  const rejectedCount = useMemo(
    () => deviations.filter((d) => d.status === "REJECTED").length,
    [deviations]
  );

  const loadDeviations = async (silent = false) => {
    setError(null);
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    try {
      const data = await qualityApi.listDeviations();
      setDeviations(data);
      setSelectedResolution((prev) => {
        const next: Record<number, QualityDeviationResolveRequest["resolution_status"]> = {
          ...prev,
        };
        for (const d of data) {
          if (!next[d.deviation_request_id]) {
            next[d.deviation_request_id] = "APPROVED";
          }
        }
        return next;
      });
    } catch (err) {
      if (err instanceof HttpError) {
        setError(
          typeof err.detail === "string" ? err.detail : t("qualityDeviations.error.loadFailed")
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qualityDeviations.error.loadFailed"));
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadDeviations();
  }, []);

  const resolveDeviation = async (deviationId: number) => {
    setResolvingId(deviationId);
    setError(null);
    try {
      const result = await qualityApi.resolveDeviation(deviationId, {
        resolution_status: selectedResolution[deviationId] ?? "APPROVED",
        resolution_comment: resolutionComment[deviationId] || null,
      });
      setResolveResult(result);
      await loadDeviations(true);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(
          typeof err.detail === "string" ? err.detail : t("qualityDeviations.error.resolveFailed")
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qualityDeviations.error.resolveFailed"));
      }
    } finally {
      setResolvingId(null);
    }
  };

  const statusIcon = (status: string) => {
    if (status === "APPROVED") return <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />;
    if (status === "REJECTED") return <XCircle className="w-3.5 h-3.5 text-red-500" />;
    if (status === "OPEN") return <Clock className="w-3.5 h-3.5 text-yellow-500" />;
    return <AlertTriangle className="w-3.5 h-3.5 text-gray-400" />;
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("qualityDeviations.title")}
          </h1>
          <ScreenStatusBadge phase="PARTIAL" />
        </div>
        <button
          onClick={() => void loadDeviations(true)}
          disabled={refreshing}
          className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
          {t("qualityDeviations.action.refresh")}
        </button>
      </div>

      <BackendRequiredNotice message={t("qualityDeviations.notice.backend")} />

      {/* KPI cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3">
          <div className="flex items-center gap-1 text-xs text-yellow-600 mb-1">
            <Clock className="w-3 h-3" />
            {t("qualityDeviations.metric.open")}
          </div>
          <div className="text-2xl font-bold text-yellow-800">{openCount}</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-3">
          <div className="flex items-center gap-1 text-xs text-green-600 mb-1">
            <CheckCircle2 className="w-3 h-3" />
            {t("qualityDeviations.metric.approved")}
          </div>
          <div className="text-2xl font-bold text-green-800">{approvedCount}</div>
        </div>
        <div className="bg-red-50 rounded-lg border border-red-200 p-3">
          <div className="flex items-center gap-1 text-xs text-red-600 mb-1">
            <XCircle className="w-3 h-3" />
            {t("qualityDeviations.metric.rejected")}
          </div>
          <div className="text-2xl font-bold text-red-800">{rejectedCount}</div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      {/* Resolve result */}
      {resolveResult && (
        <div className="flex items-start gap-2 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800">
          <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
          <div>
            <p className="font-semibold">{t("qualityDeviations.resolved.title")}</p>
            <p>
              {t("qualityDeviations.resolved.status")} {resolveResult.status}
            </p>
          </div>
        </div>
      )}

      {/* Deviation list */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-yellow-500" />
          {t("qualityDeviations.section.list")}
        </div>

        {loading ? (
          <p className="text-sm text-gray-400 italic p-4">{t("qualityDeviations.state.loading")}</p>
        ) : deviations.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("qualityDeviations.empty")}</p>
        ) : (
          <div className="divide-y divide-gray-100">
            {deviations.map((deviation) => (
              <div key={deviation.deviation_request_id} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {statusIcon(deviation.status)}
                    <span className="text-xs font-medium text-gray-500">
                      {t("qualityDeviations.col.id")} {deviation.deviation_request_id}
                    </span>
                    <span className="text-xs text-gray-400" aria-hidden="true">{String.fromCharCode(8226)}</span>
                    <span className="text-xs text-gray-500">
                      {t("qualityDeviations.col.holdId")} {deviation.hold_id}
                    </span>
                  </div>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      deviation.status === "APPROVED"
                        ? "bg-green-100 text-green-700"
                        : deviation.status === "REJECTED"
                        ? "bg-red-100 text-red-700"
                        : deviation.status === "OPEN"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-gray-100 text-gray-600"
                    }`}
                  >
                    {deviation.status}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-1">
                  <span className="font-medium">{t("qualityDeviations.col.reason")}:</span>{" "}
                  {deviation.reason}
                </p>
                <p className="text-xs text-gray-400">
                  {t("qualityDeviations.col.requestedBy")}: {deviation.requested_by} —{" "}
                  {new Date(deviation.requested_at).toLocaleString()}
                </p>
                {deviation.resolved_by && (
                  <p className="text-xs text-gray-400 mt-0.5">
                    {t("qualityDeviations.col.resolvedBy")}: {deviation.resolved_by} —{" "}
                    {deviation.resolved_at ? new Date(deviation.resolved_at).toLocaleString() : ""}
                    {deviation.resolution_comment ? ` — ${deviation.resolution_comment}` : ""}
                  </p>
                )}

                {/* Resolve form for OPEN requests */}
                {deviation.status === "OPEN" && (
                  <div className="mt-3 flex items-center gap-2 flex-wrap">
                    <div>
                      <label className="text-xs text-gray-500 block mb-0.5">
                        {t("qualityDeviations.label.resolutionStatus")}
                      </label>
                      <select
                        value={selectedResolution[deviation.deviation_request_id] ?? "APPROVED"}
                        onChange={(e) =>
                          setSelectedResolution((prev) => ({
                            ...prev,
                            [deviation.deviation_request_id]:
                              e.target.value as QualityDeviationResolveRequest["resolution_status"],
                          }))
                        }
                        className="text-sm border border-gray-300 rounded px-2 py-1"
                      >
                        {RESOLUTION_STATUSES.map((s) => (
                          <option key={s} value={s}>
                            {s}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block mb-0.5">
                        {t("qualityDeviations.label.resolutionComment")}
                      </label>
                      <input
                        type="text"
                        value={resolutionComment[deviation.deviation_request_id] ?? ""}
                        onChange={(e) =>
                          setResolutionComment((prev) => ({
                            ...prev,
                            [deviation.deviation_request_id]: e.target.value,
                          }))
                        }
                        className="text-sm border border-gray-300 rounded px-2 py-1 w-40"
                        placeholder={t("qualityDeviations.placeholder.optionalComment")}
                      />
                    </div>
                    <div className="mt-4">
                      <button
                        onClick={() => void resolveDeviation(deviation.deviation_request_id)}
                        disabled={resolvingId === deviation.deviation_request_id}
                        className="text-sm bg-blue-600 text-white rounded px-3 py-1.5 hover:bg-blue-700 disabled:opacity-50"
                      >
                        {resolvingId === deviation.deviation_request_id
                          ? t("qualityDeviations.action.resolving")
                          : t("qualityDeviations.action.resolve")}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
