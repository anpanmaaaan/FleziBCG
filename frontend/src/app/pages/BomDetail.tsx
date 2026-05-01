import { useState } from "react";
import { Link, useParams } from "react-router";
import { ArrowLeft, Lock, FileText } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface BomHeader {
  bom_id: string;
  bom_code: string;
  bom_name: string;
  product_code: string;
  product_name: string;
  version: string;
  status: string;
  effective_date: string;
  created_at: string;
}

interface BomComponent {
  seq: number;
  component_code: string;
  component_name: string;
  qty: number;
  uom: string;
  scrap_factor: number;
  item_type: string;
}

const mockBomHeaders: Record<string, BomHeader> = {
  "BOM-001": {
    bom_id: "BOM-001",
    bom_code: "BOM-SHAFT-001",
    bom_name: "Main Drive Shaft Assembly",
    product_code: "PROD-001",
    product_name: "Drive Shaft Model A",
    version: "1.2",
    status: "RELEASED",
    effective_date: "2026-03-01",
    created_at: "2026-01-15T08:00:00Z",
  },
  "BOM-002": {
    bom_id: "BOM-002",
    bom_code: "BOM-GEAR-001",
    bom_name: "Gear Housing Assembly",
    product_code: "PROD-002",
    product_name: "Gear Housing Mk2",
    version: "2.0",
    status: "RELEASED",
    effective_date: "2026-02-15",
    created_at: "2025-12-01T08:00:00Z",
  },
};

const mockBomComponents: Record<string, BomComponent[]> = {
  "BOM-001": [
    { seq: 10, component_code: "MAT-SHAFT-STL", component_name: "Alloy Steel Shaft Bar 40mm", qty: 1.0, uom: "PCS", scrap_factor: 5, item_type: "Raw Material" },
    { seq: 20, component_code: "MAT-BEARING-A", component_name: "Ball Bearing 6205 Z", qty: 2.0, uom: "PCS", scrap_factor: 2, item_type: "Purchased Part" },
    { seq: 30, component_code: "MAT-SEAL-01", component_name: "Oil Seal 25×42×8", qty: 1.0, uom: "PCS", scrap_factor: 3, item_type: "Purchased Part" },
    { seq: 40, component_code: "MAT-KEYWAY", component_name: "Keyway Stock 6×6mm", qty: 0.05, uom: "M", scrap_factor: 10, item_type: "Raw Material" },
    { seq: 50, component_code: "MAT-RETAINER", component_name: "Snap Ring DIN 472 42mm", qty: 2.0, uom: "PCS", scrap_factor: 2, item_type: "Purchased Part" },
  ],
  "BOM-002": [
    { seq: 10, component_code: "MAT-HOUSING-CAST", component_name: "GG25 Cast Iron Blank Housing", qty: 1.0, uom: "PCS", scrap_factor: 8, item_type: "Raw Material" },
    { seq: 20, component_code: "MAT-COVER-PLATE", component_name: "Steel Cover Plate 3mm", qty: 1.0, uom: "PCS", scrap_factor: 5, item_type: "Purchased Part" },
    { seq: 30, component_code: "MAT-GASKET-01", component_name: "EPDM Gasket 150×150mm", qty: 1.0, uom: "PCS", scrap_factor: 5, item_type: "Purchased Part" },
    { seq: 40, component_code: "MAT-BOLT-M8", component_name: "Hex Bolt M8×30 Grade 8.8", qty: 8.0, uom: "PCS", scrap_factor: 2, item_type: "Fastener" },
  ],
};

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

export function BomDetail() {
  const { t } = useI18n();
  const { bomId } = useParams<{ bomId: string }>();
  const [bomHeader] = useState<BomHeader | null>(bomId ? (mockBomHeaders[bomId] ?? null) : null);
  const [components] = useState<BomComponent[]>(bomId ? (mockBomComponents[bomId] ?? []) : []);

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="SHELL"
        note="BOM component truth is managed by backend MMD system. All create/edit/release/retire actions require backend connection."
      />
      <div className="flex-1 flex flex-col p-6 overflow-auto">
        {/* Back nav */}
        <div className="mb-4">
          <Link to="/bom" className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800">
            <ArrowLeft className="w-4 h-4" />
            {t("bomDetail.back")}
          </Link>
        </div>

        {/* Header row */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-slate-600" />
            <h1 className="text-2xl font-bold text-slate-900">{t("bomDetail.title")}</h1>
            <ScreenStatusBadge phase="SHELL" />
          </div>
          <div className="flex items-center gap-2">
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("bomDetail.action.release")}
            </button>
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("bomDetail.action.retire")}
            </button>
            <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
              <Lock className="w-3.5 h-3.5" />
              {t("bomDetail.action.edit")}
            </button>
          </div>
        </div>

        <BackendRequiredNotice message={t("bomDetail.notice.shell")} tone="blue" />

        {bomHeader ? (
          <>
            {/* BOM Header */}
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">{t("bomDetail.section.header")}</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.bomCode")}</div>
                  <div className="font-mono text-sm font-medium text-slate-700">{bomHeader.bom_code}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.bomName")}</div>
                  <div className="text-sm text-slate-900">{bomHeader.bom_name}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.product")}</div>
                  <div className="text-sm text-slate-900">{bomHeader.product_name}</div>
                  <div className="text-xs text-gray-400 font-mono">{bomHeader.product_code}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.version")}</div>
                  <div className="text-sm font-medium text-slate-700">{bomHeader.version}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">{t("bomList.col.status")}</div>
                  <StatusBadge status={bomHeader.status} />
                </div>
                <div>
                  <div className="text-xs text-gray-500 mb-1">Effective Date</div>
                  <div className="text-sm text-slate-700">{bomHeader.effective_date}</div>
                </div>
              </div>
            </div>

            {/* BOM Components */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">{t("bomDetail.section.components")}</h2>
                <button disabled className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-sm bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200" title="Backend MMD governance workflow required">
                  <Lock className="w-3.5 h-3.5" />
                  {t("bomDetail.action.addComponent")}
                </button>
              </div>
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.seq")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.component")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.qty")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.uom")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.scrapFactor")}</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">{t("bomDetail.col.type")}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {components.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-gray-400">{t("bomDetail.empty")}</td>
                      </tr>
                    ) : (
                      components.map((c) => (
                        <tr key={c.seq} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-slate-500 font-mono text-xs">{c.seq}</td>
                          <td className="px-4 py-3">
                            <div className="font-medium text-slate-900">{c.component_name}</div>
                            <div className="text-xs text-gray-400 font-mono">{c.component_code}</div>
                          </td>
                          <td className="px-4 py-3 text-slate-700">{c.qty}</td>
                          <td className="px-4 py-3 text-slate-600">{c.uom}</td>
                          <td className="px-4 py-3 text-slate-600">{c.scrap_factor}%</td>
                          <td className="px-4 py-3">
                            <span className="inline-flex px-2 py-0.5 rounded border text-xs bg-blue-50 text-blue-700 border-blue-200">{c.item_type}</span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="p-8 text-center text-gray-400">BOM not found in fixture data. Connect to backend MMD API for live data.</div>
        )}

        <p className="mt-6 text-xs text-gray-400">
          BOM component data is for visualization only. Backend MMD system manages all BOM lifecycle, component truth, and release governance.
        </p>
      </div>
    </div>
  );
}
