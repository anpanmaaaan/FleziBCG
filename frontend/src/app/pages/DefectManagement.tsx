import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle, Clock, Plus, RefreshCw } from "lucide-react";
import { ScreenStatusBadge } from "@/app/components";
import {
  HttpError,
  qualityApi,
  type QualityNonconformanceCreateRequest,
  type QualityNonconformanceItem,
} from "@/app/api";
import { useI18n } from "@/app/i18n";

const EMPTY_FORM: QualityNonconformanceCreateRequest = {
  operation_id: 0,
  nc_code: "",
  severity: "MAJOR",
  description: "",
};

function defectSeverityKey(severity: string) {
  switch (severity) {
    case "CRITICAL":
      return "defects.filter.severity.critical";
    case "MAJOR":
      return "defects.filter.severity.major";
    case "MINOR":
      return "defects.filter.severity.minor";
    default:
      return null;
  }
}

function defectStatusKey(status: string) {
  switch (status) {
    case "OPEN":
      return "defects.status.open";
    case "UNDER_REVIEW":
      return "defects.status.underReview";
    case "DISPOSITIONED":
      return "defects.status.dispositioned";
    case "CLOSED":
      return "defects.status.closed";
    default:
      return null;
  }
}

export function DefectManagement() {
  const { t } = useI18n();
  const [defects, setDefects] = useState<QualityNonconformanceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [form, setForm] = useState<QualityNonconformanceCreateRequest>(EMPTY_FORM);
  const [searchValue, setSearchValue] = useState("");
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterSeverity, setFilterSeverity] = useState("all");

  const loadDefects = async (silent = false) => {
    setError(null);
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const response = await qualityApi.listNonconformances();
      setDefects(response);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(typeof err.detail === "string" ? err.detail : t("defects.error.loadFailed"));
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("defects.error.loadFailed"));
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadDefects();
  }, []);

  const filteredDefects = useMemo(() => {
    return defects
      .filter((item) => {
        if (filterStatus !== "all" && item.status !== filterStatus) {
          return false;
        }
        if (filterSeverity !== "all" && item.severity !== filterSeverity) {
          return false;
        }
        if (!searchValue.trim()) {
          return true;
        }

        const q = searchValue.toLowerCase();
        return (
          item.nc_code.toLowerCase().includes(q)
          || item.description.toLowerCase().includes(q)
          || String(item.operation_id).includes(q)
        );
      })
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  }, [defects, filterSeverity, filterStatus, searchValue]);

  const statuses = useMemo(
    () => Array.from(new Set(defects.map((item) => item.status))).sort(),
    [defects]
  );

  const severities = useMemo(
    () => Array.from(new Set(defects.map((item) => item.severity))).sort(),
    [defects]
  );

  const stats = useMemo(
    () => ({
      open: defects.filter((item) => item.status === "OPEN").length,
      dispositioned: defects.filter((item) => item.status === "DISPOSITIONED").length,
      critical: defects.filter((item) => item.severity === "CRITICAL").length,
      total: defects.length,
    }),
    [defects]
  );

  const getStatusColor = (status: string) => {
    if (status === "OPEN") {
      return "bg-red-100 text-red-800";
    }
    if (status === "DISPOSITIONED") {
      return "bg-green-100 text-green-800";
    }
    if (status === "UNDER_REVIEW") {
      return "bg-yellow-100 text-yellow-800";
    }
    if (status === "CLOSED") {
      return "bg-gray-100 text-gray-800";
    }
    return "bg-gray-100 text-gray-700";
  };

  const getSeverityColor = (severity: string) => {
    if (severity === "CRITICAL") {
      return "bg-red-100 text-red-800";
    }
    if (severity === "MAJOR") {
      return "bg-orange-100 text-orange-800";
    }
    if (severity === "MINOR") {
      return "bg-yellow-100 text-yellow-800";
    }
    return "bg-gray-100 text-gray-700";
  };

  const submitCreate = async () => {
    if (!form.operation_id || !form.nc_code.trim() || !form.description.trim()) {
      setError(t("defects.error.invalidForm"));
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await qualityApi.createNonconformance({
        ...form,
        nc_code: form.nc_code.trim(),
        description: form.description.trim(),
      });
      setForm(EMPTY_FORM);
      setShowCreateForm(false);
      await loadDefects(true);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(typeof err.detail === "string" ? err.detail : t("defects.error.createFailed"));
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("defects.error.createFailed"));
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("defects.title")}</h1>
        <ScreenStatusBadge phase="CONNECTED" />
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <div className="rounded-lg border border-red-200 bg-red-50 p-3">
          <div className="mb-1 text-xs text-red-600">{t("defects.stats.openDefects")}</div>
          <div className="text-2xl font-bold text-red-800">{stats.open}</div>
        </div>
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-3">
          <div className="mb-1 text-xs text-yellow-600">{t("defects.stats.dispositioned")}</div>
          <div className="text-2xl font-bold text-yellow-800">{stats.dispositioned}</div>
        </div>
        <div className="rounded-lg border border-orange-200 bg-orange-50 p-3">
          <div className="mb-1 text-xs text-orange-600">{t("defects.stats.critical")}</div>
          <div className="text-2xl font-bold text-orange-800">{stats.critical}</div>
        </div>
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
          <div className="mb-1 text-xs text-blue-600">{t("defects.stats.total")}</div>
          <div className="text-2xl font-bold text-blue-800">{stats.total}</div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-gray-200 bg-white p-3">
        <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
          <input
            type="text"
            placeholder={t("defects.search.placeholder")}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="min-w-[240px] flex-1 rounded border border-gray-300 px-3 py-2 text-sm"
          />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="rounded border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="all">{t("defects.filter.status.all")}</option>
            {statuses.map((status) => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="rounded border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="all">{t("defects.filter.severity.all")}</option>
            {severities.map((severity) => (
              <option key={severity} value={severity}>{severity}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => void loadDefects(true)}
            disabled={loading || refreshing}
            className="inline-flex items-center gap-2 rounded border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            {t("defects.action.refresh")}
          </button>
          <button
            type="button"
            onClick={() => setShowCreateForm((prev) => !prev)}
            className="inline-flex items-center gap-2 rounded bg-red-600 px-3 py-2 text-sm text-white hover:bg-red-700"
          >
            <Plus className="h-4 w-4" />
            {showCreateForm ? t("defects.action.cancel") : t("defects.action.record")}
          </button>
        </div>
      </div>

      {showCreateForm ? (
        <div className="rounded-lg border border-red-200 bg-red-50/60 p-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
            <input
              type="number"
              value={form.operation_id || ""}
              onChange={(e) => setForm((prev) => ({ ...prev, operation_id: Number(e.target.value) || 0 }))}
              placeholder={t("defects.form.operationId")}
              className="rounded border border-red-200 bg-white px-3 py-2 text-sm"
            />
            <input
              type="text"
              value={form.nc_code}
              onChange={(e) => setForm((prev) => ({ ...prev, nc_code: e.target.value }))}
              placeholder={t("defects.form.code")}
              className="rounded border border-red-200 bg-white px-3 py-2 text-sm"
            />
            <select
              value={form.severity}
              onChange={(e) => setForm((prev) => ({ ...prev, severity: e.target.value }))}
              className="rounded border border-red-200 bg-white px-3 py-2 text-sm"
            >
              <option value="CRITICAL">{t("defects.filter.severity.critical")}</option>
              <option value="MAJOR">{t("defects.filter.severity.major")}</option>
              <option value="MINOR">{t("defects.filter.severity.minor")}</option>
            </select>
            <input
              type="number"
              value={form.hold_id ?? ""}
              onChange={(e) => {
                const value = e.target.value;
                setForm((prev) => ({
                  ...prev,
                  hold_id: value ? Number(value) : undefined,
                }));
              }}
              placeholder={t("defects.form.holdId")}
              className="rounded border border-red-200 bg-white px-3 py-2 text-sm"
            />
            <input
              type="text"
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              placeholder={t("defects.form.description")}
              className="rounded border border-red-200 bg-white px-3 py-2 text-sm"
            />
          </div>
          <div className="mt-3 flex justify-end">
            <button
              type="button"
              onClick={() => void submitCreate()}
              disabled={submitting}
              className="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {t("defects.form.submit")}
            </button>
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="flex items-start gap-2 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      ) : null}

      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
              <th className="px-4 py-2">{t("defects.col.defectNo")}</th>
              <th className="px-4 py-2">{t("defects.col.operationId")}</th>
              <th className="px-4 py-2">{t("defects.col.holdId")}</th>
              <th className="px-4 py-2">{t("defects.col.severity")}</th>
              <th className="px-4 py-2">{t("defects.col.description")}</th>
              <th className="px-4 py-2">{t("defects.col.status")}</th>
              <th className="px-4 py-2">{t("defects.col.detected")}</th>
              <th className="px-4 py-2">{t("defects.col.reportedBy")}</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} className="px-4 py-4 text-sm text-gray-500">
                  {t("defects.state.loading")}
                </td>
              </tr>
            ) : filteredDefects.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-4 text-sm italic text-gray-500">
                  {t("defects.state.empty")}
                </td>
              </tr>
            ) : (
              filteredDefects.map((defect) => (
                <tr key={defect.nonconformance_id} className="border-t border-gray-100">
                  <td className="px-4 py-2 font-medium text-blue-700">{defect.nc_code}</td>
                  <td className="px-4 py-2 text-gray-700">{defect.operation_id}</td>
                  <td className="px-4 py-2 text-gray-700">{defect.hold_id ?? "-"}</td>
                  <td className="px-4 py-2">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${getSeverityColor(defect.severity)}`}>
                      {defectSeverityKey(defect.severity) !== null ? t(defectSeverityKey(defect.severity)!) : defect.severity}
                    </span>
                  </td>
                  <td className="max-w-[360px] px-4 py-2 text-gray-700">{defect.description}</td>
                  <td className="px-4 py-2">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(defect.status)}`}>
                      {defectStatusKey(defect.status) !== null ? t(defectStatusKey(defect.status)!) : defect.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-500">{new Date(defect.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2 text-gray-700">{defect.reported_by}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}