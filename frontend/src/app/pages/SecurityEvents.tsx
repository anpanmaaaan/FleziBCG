import { useState } from "react";
import { Lock, AlertTriangle, Search } from "lucide-react";
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface SecurityEvent {
  id: string;
  timestamp: string;
  severity: "critical" | "high" | "medium" | "low";
  event_type: string;
  source: string;
  description: string;
  status: "open" | "acknowledged" | "resolved";
}

const mockSecurityEvents: SecurityEvent[] = [
  {
    id: "SEC-001",
    timestamp: "2024-04-30 15:30:22",
    severity: "high",
    event_type: "Failed Login Attempt",
    source: "192.168.1.200",
    description: "Multiple failed login attempts from IP address",
    status: "acknowledged",
  },
  {
    id: "SEC-002",
    timestamp: "2024-04-30 14:15:45",
    severity: "medium",
    event_type: "Unusual Access Pattern",
    source: "john_doe",
    description: "User accessed sensitive resource outside normal hours",
    status: "acknowledged",
  },
  {
    id: "SEC-003",
    timestamp: "2024-04-30 12:00:00",
    severity: "medium",
    event_type: "Role Modification",
    source: "system",
    description: "User role was modified by administrator",
    status: "resolved",
  },
  {
    id: "SEC-004",
    timestamp: "2024-04-30 10:45:30",
    severity: "low",
    event_type: "Session Anomaly",
    source: "jane_smith",
    description: "Session activity pattern differs from baseline",
    status: "open",
  },
];

export function SecurityEvents() {
  const { t } = useI18n();
  const [events] = useState(mockSecurityEvents);
  const [searchValue, setSearchValue] = useState("");

  const filteredEvents = events.filter(
    (e) =>
      e.event_type.toLowerCase().includes(searchValue.toLowerCase()) ||
      e.source.toLowerCase().includes(searchValue.toLowerCase()) ||
      e.description.toLowerCase().includes(searchValue.toLowerCase())
  );

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-50 text-red-700";
      case "high":
        return "bg-orange-50 text-orange-700";
      case "medium":
        return "bg-yellow-50 text-yellow-700";
      case "low":
        return "bg-blue-50 text-blue-700";
      default:
        return "bg-gray-50 text-gray-700";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open":
        return "bg-red-50 text-red-700";
      case "acknowledged":
        return "bg-yellow-50 text-yellow-700";
      case "resolved":
        return "bg-green-50 text-green-700";
      default:
        return "bg-gray-50 text-gray-700";
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner
        phase="SHELL"
        note="Security events are displayed for visualization only. Backend security and incident response system remains source of truth for threat detection and remediation."
      />
      <div className="flex-1 flex flex-col p-6">
        {/* Page header */}
        <div className="flex items-center gap-3 mb-6">
          <h1 className="text-2xl font-bold">Security Events</h1>
          <ScreenStatusBadge phase="SHELL" />
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search events..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-full"
            />
          </div>
        </div>

        {/* Events Table */}
        <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
          <table className="w-full">
            <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Timestamp</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Severity</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Event Type</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Source</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Description</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((event) => (
                <tr key={event.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-600">{event.timestamp}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getSeverityColor(event.severity)}`}>
                      <AlertTriangle className="w-3 h-3" />
                      {event.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{event.event_type}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{event.source}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{event.description}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${getStatusColor(event.status)}`}>
                      {event.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      disabled
                      className="px-2 py-1 text-gray-400 cursor-not-allowed text-xs"
                      title="This action requires backend security incident management"
                    >
                      <Lock className="w-4 h-4 inline" /> Action
                    </button>
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
