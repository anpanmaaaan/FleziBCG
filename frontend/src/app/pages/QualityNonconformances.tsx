import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, ClipboardList, RefreshCw } from "lucide-react";
import { BackendRequiredNotice, ScreenStatusBadge } from "@/app/components";
import {
  HttpError,
  qualityApi,
  type QualityNonconformanceCreateRequest,
  type QualityNonconformanceItem,
} from "@/app/api";
import { useI18n } from "@/app/i18n";

const SEVERITY_OPTIONS = ["MINOR", "MAJOR", "CRITICAL"];

export function QualityNonconformances() {
  const { t } = useI18n();
  const [ncs, setNcs] = useState<QualityNonconformanceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [newNc, setNewNc] = useState<QualityNonconformanceCreateRequest>({
    operation_id: 0,
    nc_code: "",
    hold_id: undefined,
    severity: "MINOR",
    description: "",
  });
  const [createResult, setCreateResult] = useState<QualityNonconformanceItem | null>(null);
  const [showForm, setShowForm] = useState(false);

  const openCount = useMemo(() => ncs.filter((n) => n.status === "OPEN").length, [ncs]);
  const dispositionedCount = useMemo(
    () => ncs.filter((n) => n.status === "DISPOSITIONED").length,
    [ncs]
  );

  const loadNcs = async (silent = false) => {
    setError(null);
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    try {
      const data = await qualityApi.listNonconformances();
      setNcs(data);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(
          typeof err.detail === "string"
            ? err.detail
            : t("qualityNonconformances.error.loadFailed")
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qualityNonconformances.error.loadFailed"));
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadNcs();
  }, []);

  const createNc = async () => {
    setCreating(true);
    setError(null);
    try {
      const payload: QualityNonconformanceCreateRequest = {
        ...newNc,
        hold_id: newNc.hold_id || undefined,
      };
      const result = await qualityApi.createNonconformance(payload);
      setCreateResult(result);
      setShowForm(false);
      setNewNc({ operation_id: 0, nc_code: "", hold_id: undefined, severity: "MINOR", description: "" });
      await loadNcs(true);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(
          typeof err.detail === "string"
            ? err.detail
            : t("qualityNonconformances.error.createFailed")
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qualityNonconformances.error.createFailed"));
      }
    } finally {
      setCreating(false);
    }
  };

  const severityBadge = (severity: string) => {
    const cls =
      severity === "CRITICAL"
        ? "bg-red-100 text-red-700"
        : severity === "MAJOR"
        ? "bg-orange-100 text-orange-700"
        : "bg-yellow-100 text-yellow-700";
    return (
      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cls}`}>{severity}</span>
    );
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-gray-900">
            {t("qualityNonconformances.title")}
          </h1>
          <ScreenStatusBadge phase="PARTIAL" />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowForm((v) => !v)}
            className="flex items-center gap-1.5 text-sm bg-blue-600 text-white rounded px-3 py-1.5 hover:bg-blue-700"
          >
            <ClipboardList className="w-4 h-4" />
            {t("qualityNonconformances.action.create")}
          </button>
          <button
            onClick={() => void loadNcs(true)}
            disabled={refreshing}
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            {t("qualityNonconformances.action.refresh")}
          </button>
        </div>
      </div>

      <BackendRequiredNotice message={t("qualityNonconformances.notice.backend")} />

      {/* KPI cards */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-3">
          <div className="text-xs text-yellow-600 mb-1">{t("qualityNonconformances.metric.open")}</div>
          <div className="text-2xl font-bold text-yellow-800">{openCount}</div>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-3">
          <div className="text-xs text-green-600 mb-1">{t("qualityNonconformances.metric.dispositioned")}</div>
          <div className="text-2xl font-bold text-green-800">{dispositionedCount}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-3">
          <div className="text-xs text-gray-600 mb-1">{t("qualityNonconformances.metric.total")}</div>
          <div className="text-2xl font-bold text-gray-800">{ncs.length}</div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
          <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      {/* Create result */}
      {createResult && (
        <div className="flex items-start gap-2 rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-800">
          <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
          <div>
            <p className="font-semibold">{t("qualityNonconformances.created.title")}</p>
            <p>
              {t("qualityNonconformances.created.code")} {createResult.nc_code}
            </p>
          </div>
        </div>
      )}

      {/* Create form */}
      {showForm && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">
            {t("qualityNonconformances.action.create")}
          </h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500 block mb-0.5">
                {t("qualityNonconformances.form.operationId")}
              </label>
              <input
                type="number"
                value={newNc.operation_id || ""}
                onChange={(e) =>
                  setNewNc((p) => ({ ...p, operation_id: parseInt(e.target.value) || 0 }))
                }
                className="w-full text-sm border border-gray-300 rounded px-2 py-1.5"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-0.5">
                {t("qualityNonconformances.form.ncCode")}
              </label>
              <input
                type="text"
                value={newNc.nc_code}
                onChange={(e) => setNewNc((p) => ({ ...p, nc_code: e.target.value }))}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1.5"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-0.5">
                {t("qualityNonconformances.form.holdId")}
              </label>
              <input
                type="number"
                value={newNc.hold_id ?? ""}
                onChange={(e) =>
                  setNewNc((p) => ({
                    ...p,
                    hold_id: e.target.value ? parseInt(e.target.value) : undefined,
                  }))
                }
                className="w-full text-sm border border-gray-300 rounded px-2 py-1.5"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-0.5">
                {t("qualityNonconformances.form.severity")}
              </label>
              <select
                value={newNc.severity}
                onChange={(e) => setNewNc((p) => ({ ...p, severity: e.target.value }))}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1.5"
              >
                {SEVERITY_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-span-2">
              <label className="text-xs text-gray-500 block mb-0.5">
                {t("qualityNonconformances.form.description")}
              </label>
              <textarea
                value={newNc.description}
                onChange={(e) => setNewNc((p) => ({ ...p, description: e.target.value }))}
                className="w-full text-sm border border-gray-300 rounded px-2 py-1.5 h-16 resize-none"
              />
            </div>
          </div>
          <div className="flex justify-end mt-3">
            <button
              onClick={() => void createNc()}
              disabled={creating || !newNc.nc_code || !newNc.operation_id || !newNc.description}
              className="text-sm bg-blue-600 text-white rounded px-4 py-1.5 hover:bg-blue-700 disabled:opacity-50"
            >
              {creating
                ? t("qualityNonconformances.action.creating")
                : t("qualityNonconformances.action.create")}
            </button>
          </div>
        </div>
      )}

      {/* NC list */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <ClipboardList className="w-4 h-4 text-orange-500" />
          {t("qualityNonconformances.section.list")}
        </div>

        {loading ? (
          <p className="text-sm text-gray-400 italic p-4">
            {t("qualityNonconformances.state.loading")}
          </p>
        ) : ncs.length === 0 ? (
          <p className="text-sm text-gray-400 italic p-4">{t("qualityNonconformances.empty")}</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.code")}</th>
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.operationId")}</th>
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.holdId")}</th>
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.severity")}</th>
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.status")}</th>
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.description")}</th>
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.reportedBy")}</th>
                <th className="px-4 py-2 text-left">{t("qualityNonconformances.col.createdAt")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {ncs.map((nc) => (
                <tr key={nc.nonconformance_id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs">{nc.nc_code}</td>
                  <td className="px-4 py-2 text-gray-600">{nc.operation_id}</td>
                  <td className="px-4 py-2 text-gray-400">{nc.hold_id ?? "—"}</td>
                  <td className="px-4 py-2">{severityBadge(nc.severity)}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        nc.status === "DISPOSITIONED"
                          ? "bg-green-100 text-green-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {nc.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-600 max-w-xs truncate">{nc.description}</td>
                  <td className="px-4 py-2 text-gray-500">{nc.reported_by}</td>
                  <td className="px-4 py-2 text-gray-400 text-xs whitespace-nowrap">
                    {new Date(nc.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
