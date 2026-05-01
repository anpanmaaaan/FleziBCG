// Operation Event Timeline — SHELL
// To-be visualization of backend execution event history.
// Event truth is managed by the backend execution event system.

import { Link, useParams } from "react-router";
import {
  ArrowLeft,
  Lock,
  Download,
  Filter,
  History,
  Activity,
  AlertTriangle,
  Package,
  Zap,
  Clock,
} from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge, BackendRequiredNotice } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface MockTimelineEvent {
  id: string;
  timestamp: string;
  type: string;
  typeKey: string;
  description: string;
  user?: string;
  details?: string;
}

const MOCK_EVENTS: MockTimelineEvent[] = [
  {
    id: "EVT-001",
    timestamp: "2026-05-01 08:00",
    type: "Status Change",
    typeKey: "statusChange",
    description: "Operation assigned to station",
    user: "System",
    details: "Assigned to Machining Center 1",
  },
  {
    id: "EVT-002",
    timestamp: "2026-05-01 08:35",
    type: "Operator Action",
    typeKey: "operatorAction",
    description: "Operation started",
    user: "J. Smith",
    details: "Status: PENDING → IN_PROGRESS",
  },
  {
    id: "EVT-003",
    timestamp: "2026-05-01 08:50",
    type: "Operator Action",
    typeKey: "operatorAction",
    description: "Setup completed",
    user: "J. Smith",
    details: "Machine configured for run",
  },
  {
    id: "EVT-004",
    timestamp: "2026-05-01 09:15",
    type: "Downtime Event",
    typeKey: "downtimeEvent",
    description: "Downtime started",
    user: "J. Smith",
    details: "Reason: TOOL_CHANGE (planned)",
  },
  {
    id: "EVT-005",
    timestamp: "2026-05-01 09:30",
    type: "Downtime Event",
    typeKey: "downtimeEvent",
    description: "Downtime ended",
    user: "J. Smith",
    details: "Duration: 15 min",
  },
  {
    id: "EVT-006",
    timestamp: "2026-05-01 10:45",
    type: "Material Event",
    typeKey: "materialEvent",
    description: "Quantity reported",
    user: "J. Smith",
    details: "Good: 20, Scrap: 2",
  },
  {
    id: "EVT-007",
    timestamp: "2026-05-01 11:20",
    type: "Quality Event",
    typeKey: "qualityEvent",
    description: "QC checkpoint recorded",
    user: "M. Johnson",
    details: "Bore diameter check: PASS",
  },
  {
    id: "EVT-008",
    timestamp: "2026-05-01 12:00",
    type: "Status Change",
    typeKey: "statusChange",
    description: "Operation completed",
    user: "J. Smith",
    details: "Status: IN_PROGRESS → COMPLETED",
  },
];

function getEventIcon(typeKey: string) {
  switch (typeKey) {
    case "statusChange":
      return <Activity className="w-4 h-4 text-blue-500" />;
    case "operatorAction":
      return <Clock className="w-4 h-4 text-green-500" />;
    case "downtimeEvent":
      return <AlertTriangle className="w-4 h-4 text-amber-500" />;
    case "materialEvent":
      return <Package className="w-4 h-4 text-purple-500" />;
    case "qualityEvent":
      return <Zap className="w-4 h-4 text-indigo-500" />;
    default:
      return <History className="w-4 h-4 text-gray-500" />;
  }
}

function getEventDotColor(typeKey: string): string {
  switch (typeKey) {
    case "statusChange":
      return "bg-blue-500";
    case "operatorAction":
      return "bg-green-500";
    case "downtimeEvent":
      return "bg-amber-500";
    case "materialEvent":
      return "bg-purple-500";
    case "qualityEvent":
      return "bg-indigo-500";
    default:
      return "bg-gray-400";
  }
}

export function OperationTimeline() {
  const { operationId } = useParams<{ operationId: string }>();
  const { t } = useI18n();

  return (
    <div className="flex flex-col gap-4 p-4 max-w-4xl mx-auto">
      {/* Shell disclosure banner */}
      <MockWarningBanner phase="SHELL" />

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <Link
              to={`/operations/${operationId}/detail`}
              className="flex items-center gap-1 text-sm text-blue-600 hover:underline"
            >
              <ArrowLeft className="w-4 h-4" />
              {t("operationTimeline.back")}
            </Link>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold text-gray-900">
              {t("operationTimeline.title")}
            </h1>
            <ScreenStatusBadge phase="SHELL" />
          </div>
          {operationId && (
            <p className="text-sm text-gray-500">Operation: {operationId}</p>
          )}
        </div>

        {/* Disabled header actions */}
        <div className="flex items-center gap-2 mt-1">
          <button
            disabled
            className="flex items-center gap-1 px-3 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
            title="Backend execution workflow required"
          >
            <Filter className="w-4 h-4" />
            {t("operationTimeline.action.filter")}
            <Lock className="w-3 h-3 ml-1" />
          </button>
          <button
            disabled
            className="flex items-center gap-1 px-3 py-2 rounded-md border border-gray-200 bg-gray-50 text-gray-400 text-sm cursor-not-allowed"
            title="Export event log requires backend audit system"
          >
            <Download className="w-4 h-4" />
            {t("operationTimeline.action.export")}
            <Lock className="w-3 h-3 ml-1" />
          </button>
        </div>
      </div>

      {/* Backend required notice */}
      <BackendRequiredNotice message={t("operationTimeline.notice.shell")} />

      {/* Column headers */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="grid grid-cols-12 gap-2 px-4 py-2 bg-gray-50 border-b border-gray-200 text-xs font-medium text-gray-500 uppercase tracking-wide">
          <div className="col-span-2">{t("operationTimeline.col.timestamp")}</div>
          <div className="col-span-2">{t("operationTimeline.col.type")}</div>
          <div className="col-span-4">{t("operationTimeline.col.description")}</div>
          <div className="col-span-2">{t("operationTimeline.col.user")}</div>
          <div className="col-span-2">{t("operationTimeline.col.details")}</div>
        </div>

        {/* Timeline entries */}
        <div className="divide-y divide-gray-100">
          {MOCK_EVENTS.map((event, idx) => (
            <div key={event.id} className="grid grid-cols-12 gap-2 px-4 py-3 items-start hover:bg-gray-50">
              {/* Timestamp + dot */}
              <div className="col-span-2 flex items-center gap-2">
                <div className="flex flex-col items-center">
                  <div className={`w-2 h-2 rounded-full ${getEventDotColor(event.typeKey)} mt-1`} />
                  {idx < MOCK_EVENTS.length - 1 && (
                    <div className="w-0.5 h-8 bg-gray-200 mt-1" />
                  )}
                </div>
                <span className="text-xs text-gray-600 font-mono">{event.timestamp}</span>
              </div>

              {/* Type */}
              <div className="col-span-2 flex items-center gap-1 text-xs text-gray-700">
                {getEventIcon(event.typeKey)}
                <span>{event.type}</span>
              </div>

              {/* Description */}
              <div className="col-span-4 text-sm text-gray-800">{event.description}</div>

              {/* User */}
              <div className="col-span-2 text-xs text-gray-600">{event.user ?? "—"}</div>

              {/* Details */}
              <div className="col-span-2 text-xs text-gray-500 italic">{event.details ?? "—"}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer notice */}
      <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
        ⚠ The event data shown above is static demonstration data. Real event history requires backend execution event system integration.
      </p>
    </div>
  );
}
