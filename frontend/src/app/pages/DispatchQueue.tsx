import { useState, useMemo } from "react";
import { ArrowUpDown, Search, Play, Pause, X, Lock } from "lucide-react";
import { toast } from "sonner";
import { useI18n } from "@/app/i18n/useI18n";
import { MockWarningBanner, ScreenStatusBadge } from "@/app/components";

interface DispatchItem {
  id: string;
  wo_id: string;
  product_id: string;
  product_name: string;
  station_id: string;
  station_name: string;
  sequence_no: number;
  priority: 'High' | 'Normal' | 'Low';
  status: 'Waiting' | 'In Progress' | 'Completed' | 'Blocked';
  operator_id?: string;
  planned_start: string;
  estimated_duration: number; // minutes
}

const mockDispatchQueue: DispatchItem[] = [
  {
    id: 'DQ-001',
    wo_id: 'WO-2024-001',
    product_id: 'PROD-001',
    product_name: 'Engine Block',
    station_id: 'ST-01',
    station_name: 'Machining Center 1',
    sequence_no: 1,
    priority: 'High',
    status: 'Waiting',
    planned_start: '2024-04-15 08:00',
    estimated_duration: 45,
  },
  {
    id: 'DQ-002',
    wo_id: 'WO-2024-002',
    product_id: 'PROD-002',
    product_name: 'Transmission Housing',
    station_id: 'ST-01',
    station_name: 'Machining Center 1',
    sequence_no: 2,
    priority: 'Normal',
    status: 'Waiting',
    planned_start: '2024-04-15 08:45',
    estimated_duration: 60,
  },
  {
    id: 'DQ-003',
    wo_id: 'WO-2024-003',
    product_id: 'PROD-003',
    product_name: 'Cylinder Head',
    station_id: 'ST-02',
    station_name: 'Assembly Line 1',
    sequence_no: 1,
    priority: 'High',
    status: 'In Progress',
    operator_id: 'OP-123',
    planned_start: '2024-04-15 08:00',
    estimated_duration: 30,
  },
  {
    id: 'DQ-004',
    wo_id: 'WO-2024-004',
    product_id: 'PROD-004',
    product_name: 'Camshaft',
    station_id: 'ST-03',
    station_name: 'Grinding Station',
    sequence_no: 1,
    priority: 'Low',
    status: 'Waiting',
    planned_start: '2024-04-15 09:00',
    estimated_duration: 90,
  },
];

export function DispatchQueue() {
  const [queue, setQueue] = useState(mockDispatchQueue);
  const [selectedStation, setSelectedStation] = useState<string>('all');
  const [searchValue, setSearchValue] = useState('');
  const { t } = useI18n();

  const stations = useMemo(() => {
    const uniqueStations = new Set(queue.map(item => item.station_id));
    return Array.from(uniqueStations);
  }, [queue]);

  const filteredQueue = useMemo(() => {
    let filtered = queue;

    if (selectedStation !== 'all') {
      filtered = filtered.filter(item => item.station_id === selectedStation);
    }

    if (searchValue) {
      filtered = filtered.filter(item =>
        item.wo_id.toLowerCase().includes(searchValue.toLowerCase()) ||
        item.product_name.toLowerCase().includes(searchValue.toLowerCase())
      );
    }

    return filtered.sort((a, b) => a.sequence_no - b.sequence_no);
  }, [queue, selectedStation, searchValue]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Waiting': return 'bg-blue-100 text-blue-800';
      case 'In Progress': return 'bg-yellow-100 text-yellow-800';
      case 'Completed': return 'bg-green-100 text-green-800';
      case 'Blocked': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-800';
      case 'Normal': return 'bg-blue-100 text-blue-800';
      case 'Low': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleStart = (item: DispatchItem) => {
    toast.success(t("dispatch.toast.started", { id: item.wo_id, station: item.station_name }));
  };

  const handlePause = (item: DispatchItem) => {
    toast.warning(t("dispatch.toast.paused", { id: item.wo_id }));
  };

  const handleRemove = (item: DispatchItem) => {
    toast.error(t("dispatch.toast.removed", { id: item.wo_id }));
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <MockWarningBanner phase="MOCK" note="Dispatch queue is not yet connected to real work orders. Use this for dispatch workflow visualization only." />
      <div className="flex-1 flex flex-col p-6">
        {/* Page header with status badge */}
        <div className="flex items-center gap-3 mb-6">
          <h1 className="text-2xl font-bold">Dispatch Queue</h1>
          <ScreenStatusBadge phase="MOCK" />
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder={t("dispatch.search.placeholder")}
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring w-80"
              />
            </div>

            <select
              value={selectedStation}
              onChange={(e) => setSelectedStation(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
            >
              <option value="all">{t("dispatch.filter.allStations")}</option>
              {stations.map(station => (
                <option key={station} value={station}>{station}</option>
              ))}
            </select>

            <div className="text-sm text-gray-600">
              Queue: <strong>{filteredQueue.length}</strong> {t("dispatch.queue.count", { n: filteredQueue.length })}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => toast.info(t("dispatch.toast.comingSoon"))}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {t("dispatch.action.resequence")}
            </button>
          </div>
        </div>

        {/* Queue Table */}
        <div className="flex-1 overflow-auto border rounded-lg">
          <table className="w-full">
            <thead className="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Seq
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.workOrder")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.product")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.station")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.priority")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.status")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.plannedStart")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.duration")}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t("dispatch.col.actions")}
                </th>
              </tr>
            </thead>
            <tbody className="bg-background divide-y divide-surface-divider">
              {filteredQueue.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-mono font-bold text-lg">{item.sequence_no}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-blue-600">{item.wo_id}</div>
                    <div className="text-sm text-gray-500">{item.product_id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium">{item.product_name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div>{item.station_id}</div>
                    <div className="text-sm text-gray-500">{item.station_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(item.priority)}`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.planned_start}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.estimated_duration} min
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {item.status === 'Waiting' && (
                        <button
                          disabled
                          onClick={() => handleStart(item)}
                          className="p-2 text-gray-400 cursor-not-allowed"
                          title="This action is not available for mock data"
                        >
                          <Lock className="w-4 h-4" />
                        </button>
                      )}
                      {item.status === 'In Progress' && (
                        <button
                          disabled
                          onClick={() => handlePause(item)}
                          className="p-2 text-gray-400 cursor-not-allowed"
                          title="This action is not available for mock data"
                        >
                          <Lock className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        disabled
                        onClick={() => handleRemove(item)}
                        className="p-2 text-gray-400 cursor-not-allowed"
                        title="This action is not available for mock data"
                      >
                        <Lock className="w-4 h-4" />
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