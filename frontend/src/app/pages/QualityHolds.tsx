import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Clock, RefreshCw } from "lucide-react";
import { BackendRequiredNotice, MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { HttpError, qualityApi, type QualityDispositionRequest, type QualityDispositionResponse, type QualityHoldItem } from "@/app/api";
import { useI18n } from "@/app/i18n";

const DISPOSITION_CODES: QualityDispositionRequest["disposition_code"][] = [
  "RELEASE_QC_HOLD",
  "ACCEPT_WITH_DEVIATION",
  "REQUIRE_RECHECK",
  "CONFIRM_SCRAP",
];

export function QualityHolds() {
  const { t } = useI18n();
  const [holds, setHolds] = useState<QualityHoldItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDisposition, setSelectedDisposition] = useState<Record<number, QualityDispositionRequest["disposition_code"]>>({});
  const [submittingHoldId, setSubmittingHoldId] = useState<number | null>(null);
  const [decisionResult, setDecisionResult] = useState<QualityDispositionResponse | null>(null);

  const activeCount = useMemo(() => holds.filter((h) => h.status === "ACTIVE").length, [holds]);
  const pendingCount = useMemo(() => holds.filter((h) => h.review_status === "DECISION_PENDING").length, [holds]);

  const loadHolds = async (silent = false) => {
    setError(null);
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const data = await qualityApi.listHolds();
      setHolds(data);
      setSelectedDisposition((prev) => {
        const next: Record<number, QualityDispositionRequest["disposition_code"]> = { ...prev };
        for (const hold of data) {
          if (!next[hold.hold_id]) {
            next[hold.hold_id] = "RELEASE_QC_HOLD";
          }
        }
        return next;
      });
    } catch (err) {
      if (err instanceof HttpError) {
        setError(typeof err.detail === "string" ? err.detail : t("qualityHolds.error.loadFailed"));
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qualityHolds.error.loadFailed"));
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadHolds();
  }, []);

  const submitDisposition = async (holdId: number) => {
    const dispositionCode = selectedDisposition[holdId] || "RELEASE_QC_HOLD";
    setSubmittingHoldId(holdId);
    setError(null);

    try {
      const result = await qualityApi.recordDisposition(holdId, {
        disposition_code: dispositionCode,
      });
      setDecisionResult(result);
      await loadHolds(true);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(typeof err.detail === "string" ? err.detail : t("qualityHolds.error.dispositionFailed"));
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qualityHolds.error.dispositionFailed"));
      }
    } finally {
      setSubmittingHoldId(null);
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="PARTIAL" note={t("qualityHolds.notice.partial")} />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("qualityHolds.title")}</h1>
        <ScreenStatusBadge phase="PARTIAL" />
      </div>

      <BackendRequiredNotice message={t("qualityHolds.notice.backend")} />

      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <div className="rounded-lg border border-red-200 bg-red-50 p-3">
          <div className="mb-1 text-xs text-red-600">{t("qualityHolds.metric.active")}</div>
          <div className="text-2xl font-bold text-red-800">{activeCount}</div>
        </div>
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3">
          <div className="mb-1 text-xs text-yellow-600">{t("qualityHolds.metric.pending")}</div>
          <div className="text-2xl font-bold text-yellow-800">{pendingCount}</div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-3">
          <div className="mb-1 text-xs text-gray-600">{t("qualityHolds.metric.total")}</div>
          <div className="text-2xl font-bold text-gray-800">{holds.length}</div>
        </div>
        <div className="flex items-end justify-end">
          <button
            type="button"
            onClick={() => void loadHolds(true)}
            disabled={refreshing || loading}
            className="inline-flex items-center gap-2 rounded border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            {t("qualityHolds.action.refresh")}
          </button>
        </div>
      </div>

      {error ? (
        <div className="flex items-start gap-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <div className="flex items-center gap-2 border-b border-gray-100 px-4 py-3 text-sm font-semibold text-gray-700">
          <AlertTriangle className="h-4 w-4 text-red-500" />
          {t("qualityHolds.section.held")}
        </div>

        {loading ? (
          <div className="p-4 text-sm text-gray-500">{t("qualityHolds.state.loading")}</div>
        ) : holds.length === 0 ? (
          <div className="p-4 text-sm italic text-gray-500">{t("qualityHolds.empty")}</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs uppercase tracking-wide text-gray-500">
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.item")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.reason")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.timestamp")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.disposition")}</th>
                <th className="px-4 py-2 text-left">{t("qualityHolds.col.action")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {holds.map((hold) => (
                <tr key={hold.hold_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{hold.operation_number}</div>
                    <div className="text-xs text-gray-500">
                      {t("qualityHolds.meta.holdId")} {hold.hold_id}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{hold.reason}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-700">
                      <Clock className="h-3 w-3" />
                      {hold.review_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-600">{new Date(hold.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <select
                      value={selectedDisposition[hold.hold_id] || "RELEASE_QC_HOLD"}
                      onChange={(e) =>
                        setSelectedDisposition((prev) => ({
                          ...prev,
                          [hold.hold_id]: e.target.value as QualityDispositionRequest["disposition_code"],
                        }))
                      }
                      className="w-full rounded border border-gray-300 px-2 py-1 text-xs"
                    >
                      {DISPOSITION_CODES.map((code) => (
                        <option key={code} value={code}>
                          {code}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      type="button"
                      onClick={() => void submitDisposition(hold.hold_id)}
                      disabled={submittingHoldId === hold.hold_id}
                      className="rounded bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300"
                    >
                      {submittingHoldId === hold.hold_id
                        ? t("qualityHolds.action.submitting")
                        : t("qualityHolds.action.recordDisposition")}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {decisionResult ? (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-green-800">
            <CheckCircle2 className="h-4 w-4" />
            {t("qualityHolds.decision.title")}
          </div>
          <div className="grid grid-cols-1 gap-2 text-sm text-gray-800 md:grid-cols-2">
            <div>{t("qualityHolds.decision.holdId")} {decisionResult.hold_id}</div>
            <div>{t("qualityHolds.decision.code")} {decisionResult.disposition_code}</div>
            <div>{t("qualityHolds.decision.qualityStatus")} {decisionResult.quality_status}</div>
            <div>{t("qualityHolds.decision.holdStatus")} {decisionResult.hold_status}</div>
            <div>{t("qualityHolds.decision.acceptedRelease")} {decisionResult.accepted_good_release_qty}</div>
            <div>{t("qualityHolds.decision.heldPending")} {decisionResult.held_pending_good_qty}</div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
