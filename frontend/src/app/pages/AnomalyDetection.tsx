// Anomaly Detection — SHELL
// Advisory anomaly visualization for internal product walkthrough.
// Real anomaly detection requires backend ML inference and execution event stream integration.
// Do not use anomalies shown here as authoritative operational alerts.

import { AlertTriangle, Radio, Lock } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

const MOCK_ANOMALIES = [
  {
    id: "ANM-001",
    signal: "Cycle time deviation",
    source: "Station WS-04",
    severity: "High",
    status: "Open",
    detected: "Demo",
  },
  {
    id: "ANM-002",
    signal: "Downtime spike — unplanned",
    source: "Line B",
    severity: "Medium",
    status: "Open",
    detected: "Demo",
  },
  {
    id: "ANM-003",
    signal: "Defect rate above threshold",
    source: "QC Station QC-02",
    severity: "High",
    status: "Open",
    detected: "Demo",
  },
  {
    id: "ANM-004",
    signal: "Operator utilization below 60%",
    source: "Work Center WC-01",
    severity: "Low",
    status: "Informational",
    detected: "Demo",
  },
];

export function AnomalyDetection() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4">
      <MockWarningBanner phase="SHELL" />

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-gray-900">{t("anomalyDetection.title")}</h1>
        <ScreenStatusBadge phase="SHELL" />
      </div>

      <BackendRequiredNotice message={t("anomalyDetection.notice.shell")} />

      {/* Model-required notice */}
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 flex items-start gap-3">
        <Radio className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
        <p className="text-sm text-amber-800">{t("anomalyDetection.model.required")}</p>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: t("anomalyDetection.metric.total"), value: "—" },
          { label: t("anomalyDetection.metric.high"), value: "—" },
          { label: t("anomalyDetection.metric.open"), value: "—" },
          { label: t("anomalyDetection.metric.acknowledged"), value: "—" },
        ].map(({ label, value }) => (
          <div key={label} className="bg-slate-50 rounded-lg border border-slate-200 p-3">
            <div className="text-xs text-slate-600 mb-1">{label}</div>
            <div className="text-2xl font-bold text-slate-700">{value}</div>
          </div>
        ))}
      </div>

      {/* Anomaly list */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-700 border-b border-gray-100 px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          {t("anomalyDetection.section.list")}
          <span className="ml-2 text-xs font-normal text-slate-400 italic">({t("anomalyDetection.label.demo")})</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-xs text-slate-500 uppercase tracking-wide">
                <th className="text-left px-4 py-2">{t("anomalyDetection.col.id")}</th>
                <th className="text-left px-4 py-2">{t("anomalyDetection.col.signal")}</th>
                <th className="text-left px-4 py-2">{t("anomalyDetection.col.source")}</th>
                <th className="text-left px-4 py-2">{t("anomalyDetection.col.severity")}</th>
                <th className="text-left px-4 py-2">{t("anomalyDetection.col.status")}</th>
                <th className="text-left px-4 py-2">{t("anomalyDetection.col.actions")}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {MOCK_ANOMALIES.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2 font-mono text-xs text-slate-500">{a.id}</td>
                  <td className="px-4 py-2 text-slate-800">{a.signal}</td>
                  <td className="px-4 py-2 text-slate-600">{a.source}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      a.severity === "High" ? "bg-red-100 text-red-700" :
                      a.severity === "Medium" ? "bg-amber-100 text-amber-700" :
                      "bg-slate-100 text-slate-600"
                    }`}>{a.severity}</span>
                  </td>
                  <td className="px-4 py-2 text-slate-600 italic text-xs">{a.status}</td>
                  <td className="px-4 py-2">
                    <div className="flex gap-1">
                      <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1" title={t("anomalyDetection.action.acknowledge.disabled")}>
                        <Lock className="w-3 h-3" />{t("anomalyDetection.action.acknowledge")}
                      </button>
                      <button disabled className="text-xs px-2 py-1 rounded border border-slate-200 text-slate-400 cursor-not-allowed bg-slate-50 flex items-center gap-1" title={t("anomalyDetection.action.escalate.disabled")}>
                        <Lock className="w-3 h-3" />{t("anomalyDetection.action.escalate")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
