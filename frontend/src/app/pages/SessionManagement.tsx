import { useState } from "react";
import { Lock, LogOut, Globe } from "lucide-react";
import { GovernancePageShell } from "@/app/components";
import { useI18n } from "@/app/i18n";

interface Session {
  id: string;
  user: string;
  device: string;
  ip_address: string;
  started_at: string;
  last_activity: string;
  status: "active" | "idle" | "expired";
}

const mockSessions: Session[] = [
  {
    id: "SESS-001",
    user: "john_doe",
    device: "Chrome / Windows",
    ip_address: "192.168.1.100",
    started_at: "2024-04-30 08:15",
    last_activity: "2024-04-30 16:45",
    status: "active",
  },
  {
    id: "SESS-002",
    user: "jane_smith",
    device: "Safari / macOS",
    ip_address: "192.168.1.105",
    started_at: "2024-04-30 09:30",
    last_activity: "2024-04-30 14:20",
    status: "idle",
  },
  {
    id: "SESS-003",
    user: "bob_wilson",
    device: "Firefox / Linux",
    ip_address: "192.168.1.110",
    started_at: "2024-04-29 22:00",
    last_activity: "2024-04-29 23:30",
    status: "expired",
  },
];

export function SessionManagement() {
  const { t } = useI18n();
  const [sessions] = useState(mockSessions);

  return (
    <GovernancePageShell
      title="Session Management"
      subtitle="Active user sessions and revocation controls"
      phase="SHELL"
      bannerNote="Session management is not yet connected to backend. Backend authentication system remains source of truth for active sessions and revocation."
      actions={
        <button
          disabled
          className="px-4 py-2 bg-gray-300 text-gray-600 rounded-lg cursor-not-allowed flex items-center gap-2"
          title="This action requires backend session management"
        >
          <Lock className="w-4 h-4" />
          Revoke All Sessions (Future)
        </button>
      }
    >

      {/* Sessions Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        <table className="w-full">
          <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">User</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Device</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">IP Address</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Started</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Last Activity</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockSessions.map((session) => (
                <tr key={session.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{session.user}</td>
                  <td className="px-6 py-4 text-sm text-gray-600 flex items-center gap-2">
                    <Globe className="w-4 h-4 text-blue-600" />
                    {session.device}
                  </td>
                  <td className="px-6 py-4 text-sm font-mono text-gray-600">{session.ip_address}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{session.started_at}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{session.last_activity}</td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`inline-flex px-2 py-1 rounded text-xs font-medium ${
                        session.status === "active"
                          ? "bg-green-50 text-green-700"
                          : session.status === "idle"
                            ? "bg-yellow-50 text-yellow-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {session.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <button
                      disabled
                      className="p-2 text-gray-400 cursor-not-allowed"
                      title="This action requires backend session management"
                    >
                      <LogOut className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </GovernancePageShell>
  );
}
