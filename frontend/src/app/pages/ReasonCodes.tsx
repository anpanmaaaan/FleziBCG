import { useEffect, useMemo, useState } from "react";
import { Search, Tag } from "lucide-react";
import { ScreenStatusBadge } from "@/app/components";
import { HttpError } from "@/app/api";
import { useI18n } from "@/app/i18n";
import { reasonCodeApi } from "@/app/api/reasonCodeApi";
import type { ReasonCodeCapabilities, ReasonCodeItemFromAPI, ReasonCodeCreateRequest, ReasonCodeUpdateRequest } from "@/app/api/reasonCodeApi";

// MMD-FULLSTACK-13: Write-intent controls added.
// MMD-FULLSTACK-13B: Write controls now governed by backend-derived allowed_actions.
// MMD-FULLSTACK-13C: Page-level create capability from GET /reason-codes/capabilities.
// Backend remains authorization truth. Frontend sends intent only.
// No lifecycle_status, no downtime_reason_id, no execution/quality/material/ERP behavior.

function DomainBadge({ domain }: { domain: string }) {
  const upper = domain.toUpperCase();
  const map: Record<string, string> = {
    DOWNTIME: "bg-orange-100 text-orange-800 border-orange-200",
    SCRAP: "bg-red-100 text-red-800 border-red-200",
    PAUSE: "bg-blue-100 text-blue-800 border-blue-200",
    REOPEN: "bg-purple-100 text-purple-800 border-purple-200",
    QUALITYHOLD: "bg-yellow-100 text-yellow-800 border-yellow-200",
  };
  const cls = map[upper] ?? "bg-gray-100 text-gray-600 border-gray-200";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${cls}`}>
      {domain}
    </span>
  );
}

function LifecycleBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    RELEASED: "bg-green-100 text-green-800 border-green-200",
    DRAFT: "bg-yellow-100 text-yellow-800 border-yellow-200",
    RETIRED: "bg-gray-100 text-gray-600 border-gray-200",
  };
  const cls = map[status.toUpperCase()] ?? "bg-gray-100 text-gray-600 border-gray-200";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

// MMD-FULLSTACK-13D: Approved Reason Code domain enum values.
// Source: reason-code-foundation-contract.md §2. Backend remains final validator.
const REASON_DOMAINS = [
  "EXECUTION_PAUSE",
  "DOWNTIME",
  "SCRAP",
  "QUALITY_HOLD",
  "MAINTENANCE",
  "MATERIAL",
  "REWORK",
  "EXCEPTION",
  "GENERAL",
] as const;

export function ReasonCodes() {
  const { t } = useI18n();

  const [codes, setCodes] = useState<ReasonCodeItemFromAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [domainFilter, setDomainFilter] = useState<string>("all");
  const [includeInactive, setIncludeInactive] = useState(false);

  // MMD-FULLSTACK-13C: Page-level create capability from backend.
  // Null = loading; resolved once capabilities endpoint responds.
  // Failure = keep disabled; backend 403 remains final guard.
  const [rcCapabilities, setRcCapabilities] = useState<ReasonCodeCapabilities | null>(null);

  // Write-intent state
  const [actionBusy, setActionBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    reasonDomain: "",
    reasonCategory: "",
    reasonCode: "",
    reasonName: "",
    description: "",
    requiresComment: false,
    sortOrder: "",
  });

  const [editTarget, setEditTarget] = useState<ReasonCodeItemFromAPI | null>(null);
  const [editForm, setEditForm] = useState({
    reasonName: "",
    description: "",
    requiresComment: false,
    sortOrder: "",
    isActive: true,
  });

  const [confirmRelease, setConfirmRelease] = useState<ReasonCodeItemFromAPI | null>(null);
  const [confirmRetire, setConfirmRetire] = useState<ReasonCodeItemFromAPI | null>(null);

  // MMD-FULLSTACK-13D: Field-level validation error state.
  const [createFieldErrors, setCreateFieldErrors] = useState<Record<string, string>>({});
  const [editFieldErrors, setEditFieldErrors] = useState<Record<string, string>>({});

  const resolveWriteError = (err: unknown): string => {
    if (err instanceof HttpError) {
      if (err.status === 401) return t("rcWrite.error.unauthorized");
      if (err.status === 403) return t("rcWrite.error.manageForbidden");
      if (err.status === 404) return t("rcWrite.error.notFound");
      if (err.status === 409) return t("rcWrite.error.conflict");
      if (err.status === 422) return t("rcWrite.error.validation");
      if (typeof err.message === "string" && err.message.trim().length > 0) return err.message;
    }
    return t("rcWrite.error.actionFailed");
  };

  // MMD-FULLSTACK-13D: Extract field-level errors from backend 422 or 409 responses.
  // 422: FastAPI detail array → [{loc: ["body", "field"], msg: "..."}]
  // 409 duplicate code → maps to reason_code field
  const extractFieldErrors = (err: unknown): Record<string, string> | null => {
    if (!(err instanceof HttpError)) return null;
    if (err.status === 422) {
      const detail = err.detail;
      if (Array.isArray(detail) && detail.length > 0) {
        const fieldErrors: Record<string, string> = {};
        for (const item of detail) {
          if (item && typeof item === "object" && "loc" in item && Array.isArray((item as { loc: unknown[] }).loc)) {
            const loc = (item as { loc: string[]; msg?: string }).loc;
            const rawField = String(loc[loc.length - 1]);
            const msg =
              typeof (item as { msg?: string }).msg === "string" && (item as { msg?: string }).msg!.trim()
                ? (item as { msg: string }).msg
                : t("rcWrite.error.validation");
            fieldErrors[rawField] = msg;
          }
        }
        if (Object.keys(fieldErrors).length > 0) return fieldErrors;
      }
    }
    if (err.status === 409) {
      return { reason_code: t("rcWrite.error.field.reasonCode.duplicate") };
    }
    return null;
  };

  const refreshCodes = () => {
    setLoading(true);
    setError(null);
    reasonCodeApi
      .listReasonCodes({ include_inactive: includeInactive })
      .then((data) => {
        setCodes(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err?.name === "AbortError") return;
        setError(t("reasonCodes.error.load"));
        setLoading(false);
      });
  };

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    reasonCodeApi
      .listReasonCodes({ include_inactive: includeInactive }, controller.signal)
      .then((data) => {
        setCodes(data);
        setLoading(false);
      })
      .catch((err) => {
        if (err?.name === "AbortError") return;
        setError(t("reasonCodes.error.load"));
        setLoading(false);
      });

    return () => controller.abort();
  }, [includeInactive, t]);

  // MMD-FULLSTACK-13C: Fetch page-level create capability once on mount.
  useEffect(() => {
    const controller = new AbortController();
    reasonCodeApi
      .getCapabilities(controller.signal)
      .then((cap) => setRcCapabilities(cap))
      .catch((err) => {
        if (err?.name === "AbortError") return;
        // On failure, leave null — Create button stays disabled; backend 403 is final guard.
      });
    return () => controller.abort();
  }, []);

  const availableDomains = useMemo(() => {
    const seen = new Set<string>();
    for (const c of codes) seen.add(c.reason_domain);
    return Array.from(seen).sort();
  }, [codes]);

  const filtered = useMemo(() => {
    return codes.filter((c) => {
      const matchesDomain = domainFilter === "all" || c.reason_domain === domainFilter;
      const query = search.toLowerCase();
      const matchesSearch =
        !query ||
        c.reason_code.toLowerCase().includes(query) ||
        c.reason_name.toLowerCase().includes(query) ||
        c.reason_category.toLowerCase().includes(query) ||
        (c.description ?? "").toLowerCase().includes(query);
      return matchesDomain && matchesSearch;
    });
  }, [codes, domainFilter, search]);

  // MMD-FULLSTACK-13D: Category suggestions from existing loaded data, filtered by selected domain.
  // Backend is source of truth; free text allowed if no suggestions exist for the domain.
  const categorySuggestions = useMemo(() => {
    const seen = new Set<string>();
    for (const c of codes) {
      if (!createForm.reasonDomain || c.reason_domain === createForm.reasonDomain) {
        seen.add(c.reason_category);
      }
    }
    return Array.from(seen).sort();
  }, [codes, createForm.reasonDomain]);

  // ── Write handlers ──────────────────────────────────────────────────────────

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();

    // MMD-FULLSTACK-13D: Client-side field validation before submit.
    const errs: Record<string, string> = {};
    if (!createForm.reasonDomain) errs.reason_domain = t("rcWrite.error.field.reasonDomain.required");
    if (!createForm.reasonCategory.trim()) errs.reason_category = t("rcWrite.error.field.reasonCategory.required");
    if (!createForm.reasonCode.trim()) errs.reason_code = t("rcWrite.error.field.reasonCode.required");
    if (!createForm.reasonName.trim()) errs.reason_name = t("rcWrite.error.field.reasonName.required");
    if (createForm.sortOrder !== "" && !Number.isInteger(Number(createForm.sortOrder))) {
      errs.sort_order = t("rcWrite.error.field.sortOrder.invalidNumber");
    }
    if (Object.keys(errs).length > 0) {
      setCreateFieldErrors(errs);
      const focusOrder = ["reason_domain", "reason_category", "reason_code", "reason_name", "sort_order"];
      const firstKey = focusOrder.find((k) => errs[k]);
      if (firstKey) {
        const idMap: Record<string, string> = {
          reason_domain: "create-reasonDomain",
          reason_category: "create-reasonCategory",
          reason_code: "create-reasonCode",
          reason_name: "create-reasonName",
          sort_order: "create-sortOrder",
        };
        document.getElementById(idMap[firstKey])?.focus();
      }
      return;
    }

    setCreateFieldErrors({});
    setActionBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      const payload: ReasonCodeCreateRequest = {
        reason_domain: createForm.reasonDomain.trim(),
        reason_category: createForm.reasonCategory.trim(),
        reason_code: createForm.reasonCode.trim(),
        reason_name: createForm.reasonName.trim(),
        description: createForm.description.trim() || null,
        requires_comment: createForm.requiresComment,
        sort_order: createForm.sortOrder !== "" ? parseInt(createForm.sortOrder, 10) : null,
      };
      await reasonCodeApi.createReasonCode(payload);
      setCreateOpen(false);
      setCreateForm({ reasonDomain: "", reasonCategory: "", reasonCode: "", reasonName: "", description: "", requiresComment: false, sortOrder: "" });
      setCreateFieldErrors({});
      setActionMessage(t("rcWrite.message.created"));
      refreshCodes();
    } catch (err) {
      const fieldErrors = extractFieldErrors(err);
      if (fieldErrors) {
        setCreateFieldErrors(fieldErrors);
        const focusOrder = ["reason_domain", "reason_category", "reason_code", "reason_name", "sort_order"];
        const firstKey = focusOrder.find((k) => fieldErrors[k]);
        if (firstKey) {
          const idMap: Record<string, string> = {
            reason_domain: "create-reasonDomain",
            reason_category: "create-reasonCategory",
            reason_code: "create-reasonCode",
            reason_name: "create-reasonName",
            sort_order: "create-sortOrder",
          };
          document.getElementById(idMap[firstKey])?.focus();
        }
        setActionError(t("rcWrite.error.validation"));
      } else {
        setActionError(resolveWriteError(err));
      }
    } finally {
      setActionBusy(false);
    }
  };

  const openEdit = (code: ReasonCodeItemFromAPI) => {
    setEditTarget(code);
    setEditForm({
      reasonName: code.reason_name,
      description: code.description ?? "",
      requiresComment: code.requires_comment,
      sortOrder: String(code.sort_order),
      isActive: code.is_active,
    });
    setEditFieldErrors({});
    setActionError(null);
    setActionMessage(null);
  };

  const handleEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editTarget) return;

    // MMD-FULLSTACK-13D: Client-side validation for mutable fields only.
    // reason_code, reason_domain, reason_category are immutable — never validated here.
    const errs: Record<string, string> = {};
    if (!editForm.reasonName.trim()) errs.reason_name = t("rcWrite.error.field.reasonName.required");
    if (editForm.sortOrder !== "" && !Number.isInteger(Number(editForm.sortOrder))) {
      errs.sort_order = t("rcWrite.error.field.sortOrder.invalidNumber");
    }
    if (Object.keys(errs).length > 0) {
      setEditFieldErrors(errs);
      const firstKey = Object.keys(errs)[0];
      const idMap: Record<string, string> = { reason_name: "edit-reasonName", sort_order: "edit-sortOrder" };
      document.getElementById(idMap[firstKey] ?? "")?.focus();
      return;
    }

    setEditFieldErrors({});
    setActionBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      const payload: ReasonCodeUpdateRequest = {
        reason_name: editForm.reasonName.trim() || null,
        description: editForm.description.trim() || null,
        requires_comment: editForm.requiresComment,
        sort_order: editForm.sortOrder !== "" ? parseInt(editForm.sortOrder, 10) : null,
        is_active: editForm.isActive,
      };
      await reasonCodeApi.updateReasonCode(editTarget.reason_code_id, payload);
      setEditTarget(null);
      setEditFieldErrors({});
      setActionMessage(t("rcWrite.message.updated"));
      refreshCodes();
    } catch (err) {
      const fieldErrors = extractFieldErrors(err);
      if (fieldErrors) {
        setEditFieldErrors(fieldErrors);
        const firstKey = Object.keys(fieldErrors)[0];
        const idMap: Record<string, string> = { reason_name: "edit-reasonName", sort_order: "edit-sortOrder" };
        document.getElementById(idMap[firstKey] ?? "")?.focus();
        setActionError(t("rcWrite.error.validation"));
      } else {
        setActionError(resolveWriteError(err));
      }
    } finally {
      setActionBusy(false);
    }
  };

  const handleRelease = async () => {
    if (!confirmRelease) return;
    setActionBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      await reasonCodeApi.releaseReasonCode(confirmRelease.reason_code_id);
      setConfirmRelease(null);
      setActionMessage(t("rcWrite.message.released"));
      refreshCodes();
    } catch (err) {
      setActionError(resolveWriteError(err));
      setConfirmRelease(null);
    } finally {
      setActionBusy(false);
    }
  };

  const handleRetire = async () => {
    if (!confirmRetire) return;
    setActionBusy(true);
    setActionError(null);
    setActionMessage(null);
    try {
      await reasonCodeApi.retireReasonCode(confirmRetire.reason_code_id);
      setConfirmRetire(null);
      setActionMessage(t("rcWrite.message.retired"));
      refreshCodes();
    } catch (err) {
      setActionError(resolveWriteError(err));
      setConfirmRetire(null);
    } finally {
      setActionBusy(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Tag className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("reasonCodes.title")}</h1>
            <ScreenStatusBadge phase="PARTIAL" />
          </div>
          {/* Create button — page-level backend-derived capability (MMD-FULLSTACK-13C).
              Disabled until rcCapabilities resolves; can_create=false disables with hint.
              Backend 403 remains final authority if user bypasses the UI guard. */}
          <button
            onClick={() => { setCreateOpen(true); setActionError(null); setActionMessage(null); }}
            disabled={actionBusy || !rcCapabilities?.can_create}
            title={rcCapabilities?.can_create === false ? t("rcWrite.tooltip.createForbidden") : ""}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed border border-blue-700"
          >
            {t("reasonCodes.action.create")}
          </button>
        </div>

        {/* Governance notice — backend is authorization truth */}
        <div className="mb-4 px-3 py-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
          {t("rcWrite.notice.governance")}
        </div>

        {/* Action feedback */}
        {actionMessage && (
          <div className="mb-3 px-3 py-2 bg-green-50 border border-green-200 rounded text-xs text-green-800">
            {actionMessage}
          </div>
        )}
        {actionError && (
          <div className="mb-3 px-3 py-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
            {actionError}
          </div>
        )}

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4 flex-wrap">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("reasonCodes.search.placeholder")}
              className="w-full pl-9 pr-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={domainFilter}
            onChange={(e) => setDomainFilter(e.target.value)}
            className="px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="all">{t("reasonCodes.filter.domain.all")}</option>
            {availableDomains.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          <label className="flex items-center gap-1.5 text-sm text-gray-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
              className="rounded border-gray-300"
            />
            {t("reasonCodes.filter.includeInactive")}
          </label>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex items-center justify-center py-12 text-gray-400">
            {t("reasonCodes.loading")}
          </div>
        )}

        {/* Error state */}
        {!loading && error && (
          <div className="flex items-center justify-center py-12 text-red-500 text-sm">
            {error}
          </div>
        )}

        {/* Table */}
        {!loading && !error && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.code")}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.name")}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.domain")}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.category")}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.description")}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.status")}</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.requiresComment")}</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-gray-400">{t("reasonCodes.empty")}</td>
                  </tr>
                ) : (
                  filtered.map((c) => {
                    const aa = c.allowed_actions;
                    return (
                      <tr key={c.reason_code_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-xs font-medium text-slate-700">{c.reason_code}</td>
                        <td className="px-4 py-3 text-slate-700 text-xs">{c.reason_name}</td>
                        <td className="px-4 py-3"><DomainBadge domain={c.reason_domain} /></td>
                        <td className="px-4 py-3 text-slate-700">{c.reason_category}</td>
                        <td className="px-4 py-3 text-gray-600 text-xs max-w-[300px]">{c.description ?? ""}</td>
                        <td className="px-4 py-3"><LifecycleBadge status={c.lifecycle_status} /></td>
                        <td className="px-4 py-3 text-center">
                          {c.requires_comment ? (
                            <span className="inline-block w-4 h-4 rounded-full bg-amber-400" title={t("reasonCodes.tooltip.comment_required")} />
                          ) : (
                            <span className="inline-block w-4 h-4 rounded-full bg-gray-200" title={t("reasonCodes.tooltip.comment_optional")} />
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => openEdit(c)}
                              disabled={!aa.can_update || actionBusy}
                              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed"
                              title={!aa.can_update ? t("rcWrite.tooltip.editDraftOnly") : ""}
                            >
                              {t("reasonCodes.action.edit")}
                            </button>
                            <button
                              onClick={() => { setConfirmRelease(c); setActionError(null); setActionMessage(null); }}
                              disabled={!aa.can_release || actionBusy}
                              className="inline-flex items-center gap-1 text-xs text-green-700 hover:text-green-900 disabled:text-gray-400 disabled:cursor-not-allowed"
                              title={!aa.can_release ? t("rcWrite.tooltip.releaseDraftOnly") : ""}
                            >
                              {t("reasonCodes.action.release")}
                            </button>
                            <button
                              onClick={() => { setConfirmRetire(c); setActionError(null); setActionMessage(null); }}
                              disabled={!aa.can_retire || actionBusy}
                              className="inline-flex items-center gap-1 text-xs text-orange-700 hover:text-orange-900 disabled:text-gray-400 disabled:cursor-not-allowed"
                              title={!aa.can_retire ? t("rcWrite.tooltip.retireNotRetired") : ""}
                            >
                              {t("reasonCodes.action.retire")}
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}

        <p className="mt-4 text-xs text-gray-400">
          {t("rcWrite.notice.backendAuth")}
        </p>
      </div>

      {/* ── Create Modal ──────────────────────────────────────────────────────── */}
      {createOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">{t("rcWrite.modal.create.title")}</h2>
            <form onSubmit={handleCreate} className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.reasonDomain")} *</span>
                  <select
                    id="create-reasonDomain"
                    value={createForm.reasonDomain}
                    onChange={(e) => setCreateForm((f) => ({ ...f, reasonDomain: e.target.value, reasonCategory: "" }))}
                    aria-invalid={!!createFieldErrors.reason_domain}
                    aria-describedby={createFieldErrors.reason_domain ? "create-reasonDomain-error" : undefined}
                    className={`mt-1 w-full px-2 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white ${createFieldErrors.reason_domain ? "border-red-400" : "border-gray-300"}`}
                  >
                    <option value="">{t("rcWrite.modal.field.reasonDomain.placeholder")}</option>
                    {REASON_DOMAINS.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                  {createFieldErrors.reason_domain && (
                    <p id="create-reasonDomain-error" role="alert" className="mt-0.5 text-xs text-red-600">{createFieldErrors.reason_domain}</p>
                  )}
                </label>
                <label className="block">
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.reasonCategory")} *</span>
                  <input
                    id="create-reasonCategory"
                    type="text"
                    list="create-category-suggestions"
                    value={createForm.reasonCategory}
                    onChange={(e) => setCreateForm((f) => ({ ...f, reasonCategory: e.target.value }))}
                    aria-invalid={!!createFieldErrors.reason_category}
                    aria-describedby={createFieldErrors.reason_category ? "create-reasonCategory-error" : undefined}
                    className={`mt-1 w-full px-2 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${createFieldErrors.reason_category ? "border-red-400" : "border-gray-300"}`}
                  />
                  <datalist id="create-category-suggestions">
                    {categorySuggestions.map((cat) => (
                      <option key={cat} value={cat} />
                    ))}
                  </datalist>
                  {createFieldErrors.reason_category && (
                    <p id="create-reasonCategory-error" role="alert" className="mt-0.5 text-xs text-red-600">{createFieldErrors.reason_category}</p>
                  )}
                </label>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.reasonCode")} *</span>
                  <input
                    id="create-reasonCode"
                    type="text"
                    value={createForm.reasonCode}
                    onChange={(e) => setCreateForm((f) => ({ ...f, reasonCode: e.target.value }))}
                    aria-invalid={!!createFieldErrors.reason_code}
                    aria-describedby={createFieldErrors.reason_code ? "create-reasonCode-error" : undefined}
                    className={`mt-1 w-full px-2 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${createFieldErrors.reason_code ? "border-red-400" : "border-gray-300"}`}
                  />
                  {createFieldErrors.reason_code && (
                    <p id="create-reasonCode-error" role="alert" className="mt-0.5 text-xs text-red-600">{createFieldErrors.reason_code}</p>
                  )}
                </label>
                <label className="block">
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.reasonName")} *</span>
                  <input
                    id="create-reasonName"
                    type="text"
                    value={createForm.reasonName}
                    onChange={(e) => setCreateForm((f) => ({ ...f, reasonName: e.target.value }))}
                    aria-invalid={!!createFieldErrors.reason_name}
                    aria-describedby={createFieldErrors.reason_name ? "create-reasonName-error" : undefined}
                    className={`mt-1 w-full px-2 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${createFieldErrors.reason_name ? "border-red-400" : "border-gray-300"}`}
                  />
                  {createFieldErrors.reason_name && (
                    <p id="create-reasonName-error" role="alert" className="mt-0.5 text-xs text-red-600">{createFieldErrors.reason_name}</p>
                  )}
                </label>
              </div>
              <label className="block">
                <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.description")}</span>
                <input
                  type="text"
                  value={createForm.description}
                  onChange={(e) => setCreateForm((f) => ({ ...f, description: e.target.value }))}
                  className="mt-1 w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </label>
              <div className="grid grid-cols-2 gap-3 items-start">
                <label className="flex items-center gap-2 cursor-pointer mt-1">
                  <input
                    type="checkbox"
                    checked={createForm.requiresComment}
                    onChange={(e) => setCreateForm((f) => ({ ...f, requiresComment: e.target.checked }))}
                    className="rounded border-gray-300"
                  />
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.requiresComment")}</span>
                </label>
                <label className="block">
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.sortOrder")}</span>
                  <input
                    id="create-sortOrder"
                    type="number"
                    value={createForm.sortOrder}
                    onChange={(e) => setCreateForm((f) => ({ ...f, sortOrder: e.target.value }))}
                    aria-invalid={!!createFieldErrors.sort_order}
                    aria-describedby={createFieldErrors.sort_order ? "create-sortOrder-error" : undefined}
                    className={`mt-1 w-full px-2 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${createFieldErrors.sort_order ? "border-red-400" : "border-gray-300"}`}
                  />
                  {createFieldErrors.sort_order && (
                    <p id="create-sortOrder-error" role="alert" className="mt-0.5 text-xs text-red-600">{createFieldErrors.sort_order}</p>
                  )}
                </label>
              </div>
              {actionError && (
                <p className="text-xs text-red-600">{actionError}</p>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => { setCreateOpen(false); setCreateFieldErrors({}); setActionError(null); }}
                  className="px-3 py-1.5 rounded text-sm border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  {t("common.action.cancel")}
                </button>
                <button
                  type="submit"
                  disabled={actionBusy}
                  className="px-3 py-1.5 rounded text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {actionBusy ? t("common.loading") : t("common.action.save")}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Edit Modal ────────────────────────────────────────────────────────── */}
      {editTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-1">{t("rcWrite.modal.edit.title")}</h2>
            <p className="text-xs text-gray-500 mb-4 font-mono">{editTarget.reason_code}</p>
            <form onSubmit={handleEdit} className="space-y-3">
              <label className="block">
                <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.reasonName")} *</span>
                <input
                  id="edit-reasonName"
                  type="text"
                  value={editForm.reasonName}
                  onChange={(e) => setEditForm((f) => ({ ...f, reasonName: e.target.value }))}
                  aria-invalid={!!editFieldErrors.reason_name}
                  aria-describedby={editFieldErrors.reason_name ? "edit-reasonName-error" : undefined}
                  className={`mt-1 w-full px-2 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${editFieldErrors.reason_name ? "border-red-400" : "border-gray-300"}`}
                />
                {editFieldErrors.reason_name && (
                  <p id="edit-reasonName-error" role="alert" className="mt-0.5 text-xs text-red-600">{editFieldErrors.reason_name}</p>
                )}
              </label>
              <label className="block">
                <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.description")}</span>
                <input
                  type="text"
                  value={editForm.description}
                  onChange={(e) => setEditForm((f) => ({ ...f, description: e.target.value }))}
                  className="mt-1 w-full px-2 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </label>
              <div className="grid grid-cols-2 gap-3 items-center">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editForm.requiresComment}
                    onChange={(e) => setEditForm((f) => ({ ...f, requiresComment: e.target.checked }))}
                    className="rounded border-gray-300"
                  />
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.requiresComment")}</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={editForm.isActive}
                    onChange={(e) => setEditForm((f) => ({ ...f, isActive: e.target.checked }))}
                    className="rounded border-gray-300"
                  />
                  <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.isActive")}</span>
                </label>
              </div>
              <label className="block">
                <span className="text-xs font-medium text-gray-700">{t("rcWrite.modal.field.sortOrder")}</span>
                <input
                  id="edit-sortOrder"
                  type="number"
                  value={editForm.sortOrder}
                  onChange={(e) => setEditForm((f) => ({ ...f, sortOrder: e.target.value }))}
                  aria-invalid={!!editFieldErrors.sort_order}
                  aria-describedby={editFieldErrors.sort_order ? "edit-sortOrder-error" : undefined}
                  className={`mt-1 w-full px-2 py-1.5 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${editFieldErrors.sort_order ? "border-red-400" : "border-gray-300"}`}
                />
                {editFieldErrors.sort_order && (
                  <p id="edit-sortOrder-error" role="alert" className="mt-0.5 text-xs text-red-600">{editFieldErrors.sort_order}</p>
                )}
              </label>
              {actionError && (
                <p className="text-xs text-red-600">{actionError}</p>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => { setEditTarget(null); setEditFieldErrors({}); setActionError(null); }}
                  className="px-3 py-1.5 rounded text-sm border border-gray-300 text-gray-700 hover:bg-gray-50"
                >
                  {t("common.action.cancel")}
                </button>
                <button
                  type="submit"
                  disabled={actionBusy}
                  className="px-3 py-1.5 rounded text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {actionBusy ? t("common.loading") : t("common.action.save")}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── Release Confirm ───────────────────────────────────────────────────── */}
      {confirmRelease && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-sm p-6">
            <h2 className="text-base font-semibold text-slate-900 mb-2">{t("rcWrite.confirm.release.title")}</h2>
            <p className="text-sm text-gray-600 mb-4">
              {t("rcWrite.confirm.release.body")} <span className="font-mono font-medium">{confirmRelease.reason_code}</span>?
            </p>
            {actionError && <p className="text-xs text-red-600 mb-2">{actionError}</p>}
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setConfirmRelease(null); setActionError(null); }}
                className="px-3 py-1.5 rounded text-sm border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                {t("common.action.cancel")}
              </button>
              <button
                onClick={handleRelease}
                disabled={actionBusy}
                className="px-3 py-1.5 rounded text-sm bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
              >
                {actionBusy ? t("common.loading") : t("reasonCodes.action.release")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Retire Confirm ────────────────────────────────────────────────────── */}
      {confirmRetire && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-sm p-6">
            <h2 className="text-base font-semibold text-slate-900 mb-2">{t("rcWrite.confirm.retire.title")}</h2>
            <p className="text-sm text-gray-600 mb-4">
              {t("rcWrite.confirm.retire.body")} <span className="font-mono font-medium">{confirmRetire.reason_code}</span>?
            </p>
            {actionError && <p className="text-xs text-red-600 mb-2">{actionError}</p>}
            <div className="flex justify-end gap-2">
              <button
                onClick={() => { setConfirmRetire(null); setActionError(null); }}
                className="px-3 py-1.5 rounded text-sm border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                {t("common.action.cancel")}
              </button>
              <button
                onClick={handleRetire}
                disabled={actionBusy}
                className="px-3 py-1.5 rounded text-sm bg-orange-600 text-white hover:bg-orange-700 disabled:opacity-50"
              >
                {actionBusy ? t("common.loading") : t("reasonCodes.action.retire")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
