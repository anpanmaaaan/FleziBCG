import { useState } from "react";
import { Search, Lock, Tag } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

type Domain = "downtime" | "scrap" | "pause" | "reopen" | "qualityHold" | "all";

interface ReasonCode {
  code_id: string;
  code: string;
  domain: Exclude<Domain, "all">;
  category: string;
  description: string;
  status: string;
  requires_comment: boolean;
}

const mockReasonCodes: ReasonCode[] = [
  {
    code_id: "RC-001",
    code: "DT-MAINT-01",
    domain: "downtime",
    category: "Planned Maintenance",
    description: "Scheduled preventive maintenance — machine taken offline per maintenance plan",
    status: "ACTIVE",
    requires_comment: false,
  },
  {
    code_id: "RC-002",
    code: "DT-BREAK-01",
    domain: "downtime",
    category: "Unplanned Breakdown",
    description: "Machine breakdown — unexpected failure requiring repair before resumption",
    status: "ACTIVE",
    requires_comment: true,
  },
  {
    code_id: "RC-003",
    code: "SC-DEFECT-01",
    domain: "scrap",
    category: "Dimensional Defect",
    description: "Part scrapped due to out-of-tolerance dimension at final inspection",
    status: "ACTIVE",
    requires_comment: true,
  },
  {
    code_id: "RC-004",
    code: "SC-MATERIAL",
    domain: "scrap",
    category: "Raw Material Issue",
    description: "Material scrapped — incoming material quality non-conformance",
    status: "ACTIVE",
    requires_comment: true,
  },
  {
    code_id: "RC-005",
    code: "PAUSE-BREAK",
    domain: "pause",
    category: "Operator Break",
    description: "Standard operator rest break — operation paused",
    status: "ACTIVE",
    requires_comment: false,
  },
  {
    code_id: "RC-006",
    code: "REOPEN-REWORK",
    domain: "reopen",
    category: "Rework Required",
    description: "Closed operation reopened for rework following quality inspection failure",
    status: "ACTIVE",
    requires_comment: true,
  },
  {
    code_id: "RC-007",
    code: "QH-APPEARANCE",
    domain: "qualityHold",
    category: "Surface Appearance",
    description: "Quality hold — batch suspended pending surface finish inspection review",
    status: "ACTIVE",
    requires_comment: true,
  },
  {
    code_id: "RC-008",
    code: "DT-NO-MATERIAL",
    domain: "downtime",
    category: "Material Shortage",
    description: "Operation stopped — material not available at station, waiting for supply",
    status: "RETIRED",
    requires_comment: false,
  },
];

const DOMAINS: { value: Domain; label: string }[] = [
  { value: "all", label: "All Domains" },
  { value: "downtime", label: "Downtime" },
  { value: "scrap", label: "Scrap" },
  { value: "pause", label: "Pause" },
  { value: "reopen", label: "Reopen" },
  { value: "qualityHold", label: "Quality Hold" },
];

function DomainBadge({ domain }: { domain: Exclude<Domain, "all"> }) {
  const map: Record<string, string> = {
    downtime: "bg-orange-100 text-orange-800 border-orange-200",
    scrap: "bg-red-100 text-red-800 border-red-200",
    pause: "bg-blue-100 text-blue-800 border-blue-200",
    reopen: "bg-purple-100 text-purple-800 border-purple-200",
    qualityHold: "bg-yellow-100 text-yellow-800 border-yellow-200",
  };
  const cls = map[domain] ?? "bg-gray-100 text-gray-600 border-gray-200";
  const labels: Record<string, string> = {
    downtime: "Downtime",
    scrap: "Scrap",
    pause: "Pause",
    reopen: "Reopen",
    qualityHold: "Quality Hold",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${cls}`}>
      {labels[domain] ?? domain}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    ACTIVE: "bg-green-100 text-green-800 border-green-200",
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
  const [codes] = useState(mockReasonCodes);
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState<Domain>("all");

  const filtered = codes.filter((c) => {
    const matchesDomain = domain === "all" || c.domain === domain;
    const query = search.toLowerCase();
    const matchesSearch =
      !query ||
      c.code.toLowerCase().includes(query) ||
      c.category.toLowerCase().includes(query) ||
      c.description.toLowerCase().includes(query);
    return matchesDomain && matchesSearch;
  });

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="SHELL"
        note="Reason codes are visualized for product owner review. Backend manufacturing master data system is source of truth for reason code lifecycle."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Tag className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("reasonCodes.title")}</h1>
            <ScreenStatusBadge phase="SHELL" />
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

        <BackendRequiredNotice message={t("reasonCodes.notice.shell")} tone="blue" />

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4">
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
            value={domain}
            onChange={(e) => setDomain(e.target.value as Domain)}
            className="px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            {DOMAINS.map((d) => (
              <option key={d.value} value={d.value}>{d.label}</option>
            ))}
          </select>
        </div>

        {/* Table */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("reasonCodes.col.code")}</th>
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
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-400">{t("reasonCodes.empty")}</td>
                </tr>
              ) : (
                filtered.map((c) => (
                  <tr key={c.code_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs font-medium text-slate-700">{c.code}</td>
                    <td className="px-4 py-3"><DomainBadge domain={c.domain} /></td>
                    <td className="px-4 py-3 text-slate-700">{c.category}</td>
                    <td className="px-4 py-3 text-gray-600 text-xs max-w-[300px]">{c.description}</td>
                    <td className="px-4 py-3"><StatusBadge status={c.status} /></td>
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

        <p className="mt-4 text-xs text-gray-400">
          Reason code data is for visualization only. Backend MMD system manages all reason code creation, domain assignment, and lifecycle decisions.
        </p>
      </div>
    </div>
  );
}
