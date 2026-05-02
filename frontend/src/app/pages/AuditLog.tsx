import { useState } from "react";
import { Lock, Search, Download, Filter } from "lucide-react";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface AuditEvent {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource_type: string;
  resource_id: string;
  status: "success" | "failure";
  details: string;
}

const mockAuditEvents: AuditEvent[] = [
  {
    id: "AUD-001",
    timestamp: "2024-04-30 16:45:23",
    actor: "john_doe",
    action: "START_OPERATION",
    resource_type: "Operation",
    resource_id: "OP-12345",
    status: "success",
    details: "Operation started at Station ST-01",
  },
  {
    id: "AUD-002",
    timestamp: "2024-04-30 16:30:15",
    actor: "jane_smith",
    action: "CREATE_CHECKPOINT",
    resource_type: "QC_Checkpoint",
    resource_id: "QC-98765",
    status: "success",
    details: "Quality checkpoint created for product PROD-001",
  },
  {
    id: "AUD-003",
    timestamp: "2024-04-30 16:15:42",
    actor: "bob_wilson",
    action: "APPROVE_OPERATION",
    resource_type: "Operation",
    resource_id: "OP-12344",
    status: "success",
    details: "Operation approved and marked as complete",
  },
  {
    id: "AUD-004",
    timestamp: "2024-04-30 16:00:11",
    actor: "system",
    action: "SESSION_TIMEOUT",
    resource_type: "Session",
    resource_id: "SESS-999",
    status: "success",
    details: "Idle session expired after 30 minutes",
  },
];

export function AuditLog() {
  const { t } = useI18n();
  const [events] = useState(mockAuditEvents);
  const [searchValue, setSearchValue] = useState("");

  const filteredEvents = events.filter(
    (e) =>
      e.actor.toLowerCase().includes(searchValue.toLowerCase()) ||
      e.action.toLowerCase().includes(searchValue.toLowerCase()) ||
      e.resource_id.toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <GovernancePageShell
      title="Audit Log"
      subtitle="Immutable operational event history"
      phase="SHELL"
      bannerNote="Audit log is displayed for visualization only. Backend audit and compliance system remains source of truth for all operational events."
    >

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search events..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-full"
            />
          </div>
          <button
            disabled
            className="px-4 py-2 border border-gray-300 bg-gray-50 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
            title="This action requires backend audit export"
          >
            <Filter className="w-4 h-4" />
            Filter (Future)
          </button>
          <button
            disabled
            className="px-4 py-2 border border-gray-300 bg-gray-50 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
            title="This action requires backend audit export"
          >
            <Download className="w-4 h-4" />
            Export (Future)
          </button>
        </div>

      {/* Events Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        <table className="w-full min-w-[640px]">
          <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Timestamp</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actor</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Action</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Resource</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((event) => (
                <tr key={event.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-600">{event.timestamp}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{event.actor}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{event.action}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {event.resource_type} / {event.resource_id}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                        event.status === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
                      }`}
                    >
                      {event.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{event.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      {/* Note */}
      <div className="mt-4 p-3 bg-slate-50 border border-slate-200 rounded text-sm text-slate-700 flex items-start gap-2">
        <Lock className="w-4 h-4 mt-0.5 flex-shrink-0" />
        <span>All audit events are immutable records managed by backend compliance system.</span>
      </div>
    </GovernancePageShell>
  );
}
