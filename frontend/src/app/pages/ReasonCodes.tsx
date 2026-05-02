import { useEffect, useMemo, useState } from "react";
import { Search, Lock, Tag } from "lucide-react";
import { ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";
import { reasonCodeApi } from "@/app/api/reasonCodeApi";
import type { ReasonCodeItemFromAPI } from "@/app/api/reasonCodeApi";

// MMD-FULLSTACK-08: Connected to backend /v1/reason-codes read API.
// Read-only. No write, release, retire, or downtime_reason integration.

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

export function ReasonCodes() {
  const { t } = useI18n();

  const [codes, setCodes] = useState<ReasonCodeItemFromAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [domainFilter, setDomainFilter] = useState<string>("all");
  const [includeInactive, setIncludeInactive] = useState(false);

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

  // Derive domain list from loaded data (backend is source of truth for valid domains).
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
          <button
            disabled
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
            title="Backend MMD governance workflow required"
          >
            <Lock className="w-3.5 h-3.5" />
            {t("reasonCodes.action.create")}
          </button>
        </div>

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
                  filtered.map((c) => (
                    <tr key={c.reason_code_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs font-medium text-slate-700">{c.reason_code}</td>
                      <td className="px-4 py-3 text-slate-700 text-xs">{c.reason_name}</td>
                      <td className="px-4 py-3"><DomainBadge domain={c.reason_domain} /></td>
                      <td className="px-4 py-3 text-slate-700">{c.reason_category}</td>
                      <td className="px-4 py-3 text-gray-600 text-xs max-w-[300px]">{c.description ?? ""}</td>
                      <td className="px-4 py-3"><LifecycleBadge status={c.lifecycle_status} /></td>
                      <td className="px-4 py-3 text-center">
                        {c.requires_comment ? (
                          <span className="inline-block w-4 h-4 rounded-full bg-amber-400" title="Comment required" />
                        ) : (
                          <span className="inline-block w-4 h-4 rounded-full bg-gray-200" title="Comment optional" />
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button disabled className="inline-flex items-center gap-1 text-xs text-gray-400 cursor-not-allowed" title="Backend MMD governance workflow required">
                            <Lock className="w-3 h-3" />
                            {t("reasonCodes.action.edit")}
                          </button>
                          <button disabled className="inline-flex items-center gap-1 text-xs text-gray-400 cursor-not-allowed" title="Backend MMD governance workflow required">
                            <Lock className="w-3 h-3" />
                            {t("reasonCodes.action.retire")}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        <p className="mt-4 text-xs text-gray-400">
          {t("reasonCodes.notice.readonly")}
        </p>
      </div>
    </div>
  );
}
