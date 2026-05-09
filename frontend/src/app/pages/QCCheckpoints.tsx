import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Plus, RefreshCw } from "lucide-react";
import { ScreenStatusBadge } from "@/app/components";
import {
  HttpError,
  qualityApi,
  type QualityGateDefinitionCreateRequest,
  type QualityGateDefinitionResponse,
} from "@/app/api";
import { useI18n } from "@/app/i18n";

const EMPTY_FORM: QualityGateDefinitionCreateRequest = {
  code: "",
  name: "",
  gate_type: "PRE_ACCEPTANCE",
  rule_set_version: "v1",
  applicability_scope_type: "OPERATION",
  applicability_scope_value: "",
};

function checkpointGateTypeKey(gateType: string) {
  switch (gateType) {
    case "PRE_ACCEPTANCE":
      return "qcCheckpoints.gateType.preAcceptance";
    case "MEASUREMENT":
      return "qcCheckpoints.gateType.measurement";
    case "VISUAL":
      return "qcCheckpoints.gateType.visual";
    case "MIXED":
      return "qcCheckpoints.gateType.mixed";
    default:
      return null;
  }
}

function checkpointScopeTypeKey(scopeType: string) {
  switch (scopeType) {
    case "OPERATION":
      return "qcCheckpoints.scopeType.operation";
    case "WORK_ORDER":
      return "qcCheckpoints.scopeType.workOrder";
    default:
      return null;
  }
}

function checkpointStatusKey(status: string) {
  switch (status) {
    case "DRAFT":
      return "qcCheckpoints.status.draft";
    case "ACTIVE":
      return "qcCheckpoints.status.active";
    case "RETIRED":
      return "qcCheckpoints.status.retired";
    default:
      return null;
  }
}

export function QCCheckpoints() {
  const { t } = useI18n();
  const [items, setItems] = useState<QualityGateDefinitionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchValue, setSearchValue] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [form, setForm] = useState<QualityGateDefinitionCreateRequest>(EMPTY_FORM);

  const loadGateDefinitions = async (silent = false) => {
    setError(null);
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const response = await qualityApi.listGateDefinitions();
      setItems(response);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(typeof err.detail === "string" ? err.detail : t("qcCheckpoints.error.loadFailed"));
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qcCheckpoints.error.loadFailed"));
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadGateDefinitions();
  }, []);

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      if (filterType !== "all" && item.gate_type !== filterType) {
        return false;
      }
      if (filterStatus !== "all" && item.status !== filterStatus) {
        return false;
      }
      if (!searchValue.trim()) {
        return true;
      }

      const q = searchValue.toLowerCase();
      return (
        item.code.toLowerCase().includes(q)
        || item.name.toLowerCase().includes(q)
        || item.applicability_scope_value.toLowerCase().includes(q)
      );
    });
  }, [filterStatus, filterType, items, searchValue]);

  const gateTypes = useMemo(
    () => Array.from(new Set(items.map((item) => item.gate_type))).sort(),
    [items]
  );
  const statuses = useMemo(
    () => Array.from(new Set(items.map((item) => item.status))).sort(),
    [items]
  );

  const activeCount = useMemo(
    () => items.filter((item) => item.status === "ACTIVE").length,
    [items]
  );

  const submitCreate = async () => {
    if (!form.code.trim() || !form.name.trim() || !form.applicability_scope_value.trim()) {
      setError(t("qcCheckpoints.error.invalidForm"));
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      await qualityApi.createGateDefinition({
        ...form,
        code: form.code.trim(),
        name: form.name.trim(),
        rule_set_version: form.rule_set_version.trim() || "v1",
        applicability_scope_value: form.applicability_scope_value.trim(),
      });
      setForm(EMPTY_FORM);
      setShowCreateForm(false);
      await loadGateDefinitions(true);
    } catch (err) {
      if (err instanceof HttpError) {
        setError(typeof err.detail === "string" ? err.detail : t("qcCheckpoints.error.createFailed"));
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(t("qcCheckpoints.error.createFailed"));
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("qcCheckpoints.title")}</h1>
        <ScreenStatusBadge phase="CONNECTED" />
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
          <div className="mb-1 text-xs text-blue-600">{t("qcCheckpoints.metric.total")}</div>
          <div className="text-2xl font-bold text-blue-800">{items.length}</div>
        </div>
        <div className="rounded-lg border border-green-200 bg-green-50 p-3">
          <div className="mb-1 text-xs text-green-600">{t("qcCheckpoints.metric.active")}</div>
          <div className="text-2xl font-bold text-green-800">{activeCount}</div>
        </div>
        <div className="rounded-lg border border-purple-200 bg-purple-50 p-3">
          <div className="mb-1 text-xs text-purple-600">{t("qcCheckpoints.metric.types")}</div>
          <div className="text-2xl font-bold text-purple-800">{gateTypes.length}</div>
        </div>
        <div className="flex items-end justify-end gap-2">
          <button
            type="button"
            onClick={() => void loadGateDefinitions(true)}
            disabled={loading || refreshing}
            className="inline-flex items-center gap-2 rounded border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            {t("qcCheckpoints.action.refresh")}
          </button>
          <button
            type="button"
            onClick={() => setShowCreateForm((prev) => !prev)}
            className="inline-flex items-center gap-2 rounded bg-blue-600 px-3 py-2 text-sm text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            {showCreateForm ? t("qcCheckpoints.action.cancel") : t("qcCheckpoints.action.add")}
          </button>
        </div>
      </div>

      {showCreateForm ? (
        <div className="rounded-lg border border-blue-200 bg-blue-50/60 p-4">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <input
              type="text"
              value={form.code}
              onChange={(e) => setForm((prev) => ({ ...prev, code: e.target.value }))}
              placeholder={t("qcCheckpoints.form.code")}
              className="rounded border border-blue-200 bg-white px-3 py-2 text-sm"
            />
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              placeholder={t("qcCheckpoints.form.name")}
              className="rounded border border-blue-200 bg-white px-3 py-2 text-sm"
            />
            <select
              value={form.gate_type}
              onChange={(e) => setForm((prev) => ({ ...prev, gate_type: e.target.value }))}
              className="rounded border border-blue-200 bg-white px-3 py-2 text-sm"
            >
              <option value="PRE_ACCEPTANCE">{t("qcCheckpoints.gateType.preAcceptance")}</option>
            </select>
            <input
              type="text"
              value={form.rule_set_version}
              onChange={(e) => setForm((prev) => ({ ...prev, rule_set_version: e.target.value }))}
              placeholder={t("qcCheckpoints.form.ruleSetVersion")}
              className="rounded border border-blue-200 bg-white px-3 py-2 text-sm"
            />
            <select
              value={form.applicability_scope_type}
              onChange={(e) => setForm((prev) => ({ ...prev, applicability_scope_type: e.target.value }))}
              className="rounded border border-blue-200 bg-white px-3 py-2 text-sm"
            >
              <option value="OPERATION">{t("qcCheckpoints.scopeType.operation")}</option>
              <option value="WORK_ORDER">{t("qcCheckpoints.scopeType.workOrder")}</option>
            </select>
            <input
              type="text"
              value={form.applicability_scope_value}
              onChange={(e) => setForm((prev) => ({ ...prev, applicability_scope_value: e.target.value }))}
              placeholder={t("qcCheckpoints.form.scopeValue")}
              className="rounded border border-blue-200 bg-white px-3 py-2 text-sm"
            />
          </div>
          <div className="mt-3 flex justify-end">
            <button
              type="button"
              onClick={() => void submitCreate()}
              disabled={submitting}
              className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {t("qcCheckpoints.form.submit")}
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

      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-gray-200 bg-white px-3 py-3">
        <input
          type="text"
          placeholder={t("qcCheckpoints.search.placeholder")}
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          className="min-w-[260px] flex-1 rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="all">{t("qcCheckpoints.filter.allTypes")}</option>
          {gateTypes.map((gateType) => (
            <option key={gateType} value={gateType}>{gateType}</option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="all">{t("qcCheckpoints.filter.allStatus")}</option>
          {statuses.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
      </div>

      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
              <th className="px-4 py-2">{t("qcCheckpoints.col.code")}</th>
              <th className="px-4 py-2">{t("qcCheckpoints.col.name")}</th>
              <th className="px-4 py-2">{t("qcCheckpoints.col.type")}</th>
              <th className="px-4 py-2">{t("qcCheckpoints.col.scope")}</th>
              <th className="px-4 py-2">{t("qcCheckpoints.col.status")}</th>
              <th className="px-4 py-2">{t("qcCheckpoints.col.ruleSet")}</th>
              <th className="px-4 py-2">{t("qcCheckpoints.col.createdAt")}</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-4 text-sm text-gray-500">
                  {t("qcCheckpoints.state.loading")}
                </td>
              </tr>
            ) : filteredItems.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-4 text-sm italic text-gray-500">
                  {t("qcCheckpoints.state.empty")}
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => (
                <tr key={item.gate_definition_id} className="border-t border-gray-100">
                  <td className="px-4 py-2 font-mono text-xs text-gray-700">{item.code}</td>
                  <td className="px-4 py-2 font-medium text-gray-900">{item.name}</td>
                  <td className="px-4 py-2 text-gray-700">
                    {checkpointGateTypeKey(item.gate_type) !== null ? t(checkpointGateTypeKey(item.gate_type)!) : item.gate_type}
                  </td>
                  <td className="px-4 py-2 text-gray-700">
                    {checkpointScopeTypeKey(item.applicability_scope_type) !== null
                      ? t(checkpointScopeTypeKey(item.applicability_scope_type)!)
                      : item.applicability_scope_type}:{" "}
                    <span className="font-mono text-xs">{item.applicability_scope_value}</span>
                  </td>
                  <td className="px-4 py-2">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                      item.status === "ACTIVE"
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-700"
                    }`}>
                      <CheckCircle2 className="mr-1 h-3 w-3" />
                      {checkpointStatusKey(item.status) !== null ? t(checkpointStatusKey(item.status)!) : item.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-700">{item.rule_set_version}</td>
                  <td className="px-4 py-2 text-gray-500">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}