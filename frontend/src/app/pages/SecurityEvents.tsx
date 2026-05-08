import { useEffect, useState } from "react";
import { AlertTriangle, Search } from "lucide-react";
import { toast } from "sonner";
import { GovernancePageShell } from "@/app/components";
import { iamApi } from "@/app/api/iamApi";
import type { SecurityEventItem } from "@/app/api/iamApi";
import { useI18n } from "@/app/i18n";

export function SecurityEvents() {
  const { t } = useI18n();
  const [events, setEvents] = useState<SecurityEventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchValue, setSearchValue] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("");

  const loadEvents = () => {
    setLoading(true);
    iamApi
      .listSecurityEvents({ limit: 200, event_type: eventTypeFilter || undefined })
      .then(setEvents)
      .catch(() => toast.error(t("securityEvents.notice.failed_to_load_security_events")))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEvents();
  }, [eventTypeFilter]);

  const filteredEvents = events.filter(
    (e) =>
      e.event_type.toLowerCase().includes(searchValue.toLowerCase()) ||
      (e.actor_user_id ?? "").toLowerCase().includes(searchValue.toLowerCase()) ||
      (e.resource_type ?? "").toLowerCase().includes(searchValue.toLowerCase()) ||
      (e.detail ?? "").toLowerCase().includes(searchValue.toLowerCase())
  );

  return (
    <GovernancePageShell
      title={t("securityEvents.tooltip.security_events")}
      subtitle={t("securityEvents.tooltip.threat_detection_and_incident_monitoring")}
      phase="PARTIAL"
      bannerNote={t("securityEvents.notice.live_backend")}
    >
      {/* Search & Filter */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder={t("securityEvents.placeholder.search_events")}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-full sm:w-72"
          />
        </div>
        <input
          type="text"
          placeholder={t("securityEvents.placeholder.filter_by_event_type")}
          value={eventTypeFilter}
          onChange={(e) => setEventTypeFilter(e.target.value)}
          onBlur={loadEvents}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring text-sm w-56"
        />
        <span className="text-sm text-gray-500">
          {t("securityEvents.label.events_count", { count: filteredEvents.length })}
        </span>
      </div>

      {/* Events Table */}
      <div className="flex-1 overflow-auto border border-gray-200 rounded-lg">
        {loading ? (
          <div className="p-8 text-center text-gray-400 text-sm">{t("securityEvents.label.loading_events")}</div>
        ) : (
          <table className="w-full min-w-[700px]">
            <thead className="bg-gray-50 border-b sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">{t("securityEvents.label.timestamp")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">{t("securityEvents.label.event_type")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">{t("securityEvents.label.actor")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">{t("securityEvents.label.resource")}</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wide">{t("securityEvents.label.detail")}</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-400 text-sm">
                    {t("securityEvents.state.empty")}
                  </td>
                </tr>
              ) : (
                filteredEvents.map((ev, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3 text-xs text-gray-500 whitespace-nowrap">
                      {new Date(ev.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      <span className="inline-flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-orange-400" />
                        {ev.event_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{ev.actor_user_id ?? t("common.na")}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {ev.resource_type
                        ? `${ev.resource_type}${ev.resource_id ? ` / ${ev.resource_id}` : ""}`
                        : t("common.na")}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">
                      {ev.detail ?? t("common.na")}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </GovernancePageShell>
  );
}


