import { useState } from "react";
import { Link } from "react-router";
import { Search, Plus, Upload, Lock, Eye, FileText } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface BomItem {
  bom_id: string;
  bom_code: string;
  bom_name: string;
  product_code: string;
  product_name: string;
  version: string;
  status: string;
  component_count: number;
  updated_at: string;
}

const mockBoms: BomItem[] = [
  {
    bom_id: "BOM-001",
    bom_code: "BOM-SHAFT-001",
    bom_name: "Main Drive Shaft Assembly",
    product_code: "PROD-001",
    product_name: "Drive Shaft Model A",
    version: "1.2",
    status: "RELEASED",
    component_count: 12,
    updated_at: "2026-04-10T09:30:00Z",
  },
  {
    bom_id: "BOM-002",
    bom_code: "BOM-GEAR-001",
    bom_name: "Gear Housing Assembly",
    product_code: "PROD-002",
    product_name: "Gear Housing Mk2",
    version: "2.0",
    status: "RELEASED",
    component_count: 8,
    updated_at: "2026-04-15T14:00:00Z",
  },
  {
    bom_id: "BOM-003",
    bom_code: "BOM-BEARING-001",
    bom_name: "Bearing Pack Assembly",
    product_code: "PROD-003",
    product_name: "Bearing Pack Standard",
    version: "1.0",
    status: "DRAFT",
    component_count: 5,
    updated_at: "2026-04-28T11:00:00Z",
  },
  {
    bom_id: "BOM-004",
    bom_code: "BOM-SHAFT-002",
    bom_name: "Output Shaft Sub-Assembly",
    product_code: "PROD-001",
    product_name: "Drive Shaft Model A",
    version: "0.9",
    status: "RETIRED",
    component_count: 9,
    updated_at: "2026-03-01T08:00:00Z",
  },
];

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toUpperCase();
  const map: Record<string, string> = {
    RELEASED: "bg-green-100 text-green-800 border-green-200",
    DRAFT: "bg-yellow-100 text-yellow-800 border-yellow-200",
    RETIRED: "bg-gray-100 text-gray-600 border-gray-200",
  };
  const cls = map[normalized] ?? "bg-gray-100 text-gray-600 border-gray-200";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

export function BomList() {
  const { t } = useI18n();
  const [boms] = useState(mockBoms);
  const [search, setSearch] = useState("");

  const filtered = boms.filter(
    (b) =>
      b.bom_code.toLowerCase().includes(search.toLowerCase()) ||
      b.bom_name.toLowerCase().includes(search.toLowerCase()) ||
      b.product_code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="SHELL"
        note="BOM definitions are visualized here for product owner review. Backend manufacturing master data system is source of truth."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("bomList.title")}</h1>
            <ScreenStatusBadge phase="SHELL" />
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
              title="Backend MMD governance workflow required"
            >
              <Lock className="w-3.5 h-3.5" />
              {t("bomList.action.import")}
            </button>
            <button
              disabled
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
              title="Backend MMD governance workflow required"
            >
              <Lock className="w-3.5 h-3.5" />
              <Plus className="w-3.5 h-3.5" />
              {t("bomList.action.create")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice
          message={t("bomList.notice.shell")}
          tone="blue"
        />

        {/* Search */}
        <div className="flex items-center gap-2 mb-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t("bomList.search.placeholder")}
              className="w-full pl-9 pr-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Table */}
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.bomCode")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.bomName")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.product")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.version")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.status")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.components")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomList.col.updated")}</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-400">{t("bomList.empty")}</td>
                </tr>
              ) : (
                filtered.map((bom) => (
                  <tr key={bom.bom_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs font-medium text-slate-700">{bom.bom_code}</td>
                    <td className="px-4 py-3 text-slate-900">{bom.bom_name}</td>
                    <td className="px-4 py-3">
                      <div className="text-slate-700">{bom.product_name}</div>
                      <div className="text-xs text-gray-400 font-mono">{bom.product_code}</div>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{bom.version}</td>
                    <td className="px-4 py-3"><StatusBadge status={bom.status} /></td>
                    <td className="px-4 py-3 text-slate-600">{bom.component_count}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{new Date(bom.updated_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/bom/${bom.bom_id}`}
                        className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        {t("bomList.action.view")}
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <p className="mt-4 text-xs text-gray-400">
          BOM data shown is for visualization only. Backend MMD system manages all BOM lifecycle, versioning, and release decisions.
        </p>
      </div>
    </div>
  );
}
