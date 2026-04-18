import { useState, useEffect, useMemo, useCallback } from "react";
import {
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  Clock,
  Search,
  Filter,
  User,
  XCircle,
  Activity,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  CheckCircle2,
  ArrowRight,
  UserCheck,
  X,
  TrendingUp,
  Zap,
  Square
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate, Link } from "react-router";
import { useI18n } from "@/app/i18n/useI18n";

interface ProductionOrder {
  id: string;
  releaseDate: string;
  quantity: string;
  progress: number;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Late';
}

interface Station {
  id: string;
  name: string;
  operator?: {
    name: string;
    badge: string;
  };
  status: 'Running' | 'Idle' | 'Stopped';
  currentWO?: string;
  cycleTime: number;
  unitsProduced: number;
  defects: number;
}

interface ProductionLine {
  id: string;
  name: string;
  shift: string;
  status: 'Running' | 'Stopped' | 'Idle';
  efficiency: number;
  stations: Station[];
  totalUnits: number;
  totalDefects: number;
  avgCycleTime: number;
}

interface DefectAlert {
  id: string;
  timestamp: string;
  line: string;
  station: string;
  defectType: string;
  severity: 'High' | 'Medium' | 'Low';
}

const initialQueueOrders: ProductionOrder[] = [
  { id: 'PO-001', releaseDate: '2024-03-27 08:00', quantity: '50 units', progress: 75, status: 'In Progress' },
  { id: 'PO-002', releaseDate: '2024-03-27 09:00', quantity: '100 units', progress: 45, status: 'In Progress' },
  { id: 'PO-003', releaseDate: '2024-03-27 10:00', quantity: '75 units', progress: 0, status: 'Pending' },
  { id: 'PO-004', releaseDate: '2024-03-27 11:00', quantity: '120 units', progress: 0, status: 'Pending' },
  { id: 'PO-005', releaseDate: '2024-03-27 12:00', quantity: '80 units', progress: 0, status: 'Pending' },
  { id: 'PO-006', releaseDate: '2024-03-27 13:00', quantity: '90 units', progress: 0, status: 'Pending' },
  { id: 'PO-007', releaseDate: '2024-03-27 14:00', quantity: '110 units', progress: 0, status: 'Pending' },
  { id: 'PO-008', releaseDate: '2024-03-27 15:00', quantity: '60 units', progress: 0, status: 'Pending' },
];

const initialProductionLines: ProductionLine[] = [
  {
    id: 'LINE-01',
    name: 'Assembly Line 1',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 87,
    totalUnits: 245,
    totalDefects: 3,
    avgCycleTime: 120,
    stations: [
      { id: 'ST-01', name: 'Machining', operator: { name: 'John Smith', badge: 'B-001' }, status: 'Running', currentWO: 'PO-001', cycleTime: 110, unitsProduced: 38, defects: 0 },
      { id: 'ST-02', name: 'Assembly', operator: { name: 'Mary Johnson', badge: 'B-002' }, status: 'Running', currentWO: 'PO-001', cycleTime: 125, unitsProduced: 38, defects: 1 },
      { id: 'ST-03', name: 'QC Inspection', operator: { name: 'Robert Lee', badge: 'B-003' }, status: 'Idle', cycleTime: 0, unitsProduced: 37, defects: 2 },
    ],
  },
  {
    id: 'LINE-02',
    name: 'Assembly Line 2',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 92,
    totalUnits: 180,
    totalDefects: 1,
    avgCycleTime: 105,
    stations: [
      { id: 'ST-04', name: 'Welding', operator: { name: 'Sarah Kim', badge: 'B-004' }, status: 'Running', currentWO: 'PO-002', cycleTime: 95, unitsProduced: 45, defects: 0 },
      { id: 'ST-05', name: 'Painting', operator: { name: 'Mike Chen', badge: 'B-005' }, status: 'Running', currentWO: 'PO-002', cycleTime: 115, unitsProduced: 45, defects: 1 },
      { id: 'ST-06', name: 'Final Inspection', status: 'Idle', cycleTime: 0, unitsProduced: 44, defects: 0 },
    ],
  },
  {
    id: 'LINE-03',
    name: 'Assembly Line 3',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Stopped',
    efficiency: 0,
    totalUnits: 0,
    totalDefects: 0,
    avgCycleTime: 0,
    stations: [
      { id: 'ST-07', name: 'Machining', status: 'Stopped', cycleTime: 0, unitsProduced: 0, defects: 0 },
      { id: 'ST-08', name: 'Assembly', status: 'Stopped', cycleTime: 0, unitsProduced: 0, defects: 0 },
      { id: 'ST-09', name: 'Testing', status: 'Stopped', cycleTime: 0, unitsProduced: 0, defects: 0 },
    ],
  },
  {
    id: 'LINE-04',
    name: 'Packaging Line 1',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 78,
    totalUnits: 156,
    totalDefects: 2,
    avgCycleTime: 90,
    stations: [
      { id: 'ST-10', name: 'Packing', operator: { name: 'Tom Brown', badge: 'B-006' }, status: 'Running', cycleTime: 85, unitsProduced: 52, defects: 1 },
      { id: 'ST-11', name: 'Labeling', operator: { name: 'Lisa White', badge: 'B-007' }, status: 'Running', cycleTime: 95, unitsProduced: 52, defects: 1 },
    ],
  },
  {
    id: 'LINE-05',
    name: 'Testing Line 1',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 85,
    totalUnits: 198,
    totalDefects: 4,
    avgCycleTime: 135,
    stations: [
      { id: 'ST-12', name: 'Function Test', operator: { name: 'David Lee', badge: 'B-008' }, status: 'Running', cycleTime: 130, unitsProduced: 66, defects: 2 },
      { id: 'ST-13', name: 'Quality Check', operator: { name: 'Emma Davis', badge: 'B-009' }, status: 'Running', cycleTime: 140, unitsProduced: 66, defects: 2 },
    ],
  },
  {
    id: 'LINE-06',
    name: 'Assembly Line 4',
    shift: 'Night Shift (19:00-03:00)',
    status: 'Idle',
    efficiency: 45,
    totalUnits: 89,
    totalDefects: 1,
    avgCycleTime: 115,
    stations: [
      { id: 'ST-14', name: 'Machining', status: 'Idle', cycleTime: 0, unitsProduced: 30, defects: 0 },
      { id: 'ST-15', name: 'Assembly', status: 'Idle', cycleTime: 0, unitsProduced: 29, defects: 1 },
    ],
  },
  {
    id: 'LINE-07',
    name: 'Welding Line 1',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 91,
    totalUnits: 223,
    totalDefects: 0,
    avgCycleTime: 98,
    stations: [
      { id: 'ST-16', name: 'Spot Welding', operator: { name: 'Chris Martin', badge: 'B-010' }, status: 'Running', cycleTime: 95, unitsProduced: 75, defects: 0 },
      { id: 'ST-17', name: 'Inspection', operator: { name: 'Anna Taylor', badge: 'B-011' }, status: 'Running', cycleTime: 100, unitsProduced: 74, defects: 0 },
    ],
  },
  {
    id: 'LINE-08',
    name: 'Painting Line 1',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 88,
    totalUnits: 167,
    totalDefects: 5,
    avgCycleTime: 142,
    stations: [
      { id: 'ST-18', name: 'Surface Prep', operator: { name: 'Mark Wilson', badge: 'B-012' }, status: 'Running', cycleTime: 135, unitsProduced: 56, defects: 2 },
      { id: 'ST-19', name: 'Paint Apply', operator: { name: 'Sophie Moore', badge: 'B-013' }, status: 'Running', cycleTime: 150, unitsProduced: 55, defects: 3 },
    ],
  },
  {
    id: 'LINE-09',
    name: 'Final Assembly Line',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 94,
    totalUnits: 201,
    totalDefects: 1,
    avgCycleTime: 110,
    stations: [
      { id: 'ST-20', name: 'Component Assembly', operator: { name: 'Jake Anderson', badge: 'B-014' }, status: 'Running', cycleTime: 105, unitsProduced: 67, defects: 0 },
      { id: 'ST-21', name: 'Final Test', operator: { name: 'Olivia Thomas', badge: 'B-015' }, status: 'Running', cycleTime: 115, unitsProduced: 67, defects: 1 },
    ],
  },
  {
    id: 'LINE-10',
    name: 'CNC Machining Line',
    shift: 'Night Shift (19:00-03:00)',
    status: 'Stopped',
    efficiency: 0,
    totalUnits: 0,
    totalDefects: 0,
    avgCycleTime: 0,
    stations: [
      { id: 'ST-22', name: 'CNC Mill', status: 'Stopped', cycleTime: 0, unitsProduced: 0, defects: 0 },
      { id: 'ST-23', name: 'CNC Lathe', status: 'Stopped', cycleTime: 0, unitsProduced: 0, defects: 0 },
    ],
  },
  {
    id: 'LINE-11',
    name: 'Injection Molding Line',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 82,
    totalUnits: 334,
    totalDefects: 6,
    avgCycleTime: 45,
    stations: [
      { id: 'ST-24', name: 'Molding', operator: { name: 'Ryan Clark', badge: 'B-016' }, status: 'Running', cycleTime: 43, unitsProduced: 112, defects: 3 },
      { id: 'ST-25', name: 'Trimming', operator: { name: 'Mia Rodriguez', badge: 'B-017' }, status: 'Running', cycleTime: 47, unitsProduced: 111, defects: 3 },
    ],
  },
  {
    id: 'LINE-12',
    name: 'PCB Assembly Line',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Running',
    efficiency: 89,
    totalUnits: 145,
    totalDefects: 2,
    avgCycleTime: 155,
    stations: [
      { id: 'ST-26', name: 'SMT Placement', operator: { name: 'Alex Harris', badge: 'B-018' }, status: 'Running', cycleTime: 150, unitsProduced: 49, defects: 1 },
      { id: 'ST-27', name: 'Reflow', operator: { name: 'Sophia Lewis', badge: 'B-019' }, status: 'Running', cycleTime: 160, unitsProduced: 48, defects: 1 },
    ],
  },
  {
    id: 'LINE-13',
    name: 'Quality Control Line',
    shift: 'Day Shift (07:00-15:00)',
    status: 'Idle',
    efficiency: 62,
    totalUnits: 112,
    totalDefects: 8,
    avgCycleTime: 125,
    stations: [
      { id: 'ST-28', name: 'Visual Inspection', status: 'Idle', cycleTime: 0, unitsProduced: 56, defects: 4 },
      { id: 'ST-29', name: 'Dimensional Check', status: 'Idle', cycleTime: 0, unitsProduced: 56, defects: 4 },
    ],
  },
];

const initialDefectAlerts: DefectAlert[] = [
  { id: 'D-001', timestamp: '10:23:15', line: 'Line 1', station: 'Assembly', defectType: 'Scratch detected', severity: 'Medium' },
  { id: 'D-002', timestamp: '10:15:42', line: 'Line 2', station: 'Painting', defectType: 'Paint defect', severity: 'Low' },
  { id: 'D-003', timestamp: '10:08:33', line: 'Line 5', station: 'Quality Check', defectType: 'Failed test', severity: 'High' },
];

export function Home() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const [queueOrders, setQueueOrders] = useState<ProductionOrder[]>(initialQueueOrders);
  const [productionLines, setProductionLines] = useState<ProductionLine[]>(initialProductionLines);
  const [defectAlerts, setDefectAlerts] = useState<DefectAlert[]>(initialDefectAlerts);
  const [selectedLine, setSelectedLine] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [queueExpanded, setQueueExpanded] = useState(true);
  const [alertsExpanded, setAlertsExpanded] = useState(true);

  const selectedLineData = productionLines.find(line => line.id === selectedLine);

  // Real-time simulation
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      setProductionLines(prev => prev.map(line => {
        if (line.status !== 'Running') return line;

        return {
          ...line,
          totalUnits: line.totalUnits + Math.floor(Math.random() * 3),
          efficiency: Math.min(100, line.efficiency + (Math.random() > 0.5 ? 1 : -1)),
          stations: line.stations.map(station => {
            if (station.status !== 'Running') return station;

            return {
              ...station,
              cycleTime: Math.max(80, Math.min(150, station.cycleTime + (Math.random() > 0.5 ? 5 : -5))),
              unitsProduced: station.unitsProduced + (Math.random() > 0.3 ? 1 : 0),
            };
          }),
        };
      }));

      setQueueOrders(prev => prev.map(order => {
        if (order.status === 'In Progress' && order.progress < 100) {
          const newProgress = Math.min(100, order.progress + Math.floor(Math.random() * 5));
          return {
            ...order,
            progress: newProgress,
            status: newProgress === 100 ? 'Completed' : 'In Progress',
          };
        }
        return order;
      }));

      setLastUpdate(new Date());
    }, 3000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleLineControl = (lineId: string, action: 'start' | 'pause' | 'stop') => {
    setProductionLines(prev => prev.map(line => {
      if (line.id !== lineId) return line;

      let newStatus: 'Running' | 'Stopped' | 'Idle' = line.status;
      let newStationStatus: 'Running' | 'Stopped' | 'Idle' = line.status;

      if (action === 'start') {
        newStatus = 'Running';
        newStationStatus = 'Running';
        toast.success(t("home.toast.lineStarted", { name: line.name }));
      } else if (action === 'pause') {
        newStatus = 'Idle';
        newStationStatus = 'Idle';
        toast.warning(t("home.toast.linePaused", { name: line.name }));
      } else if (action === 'stop') {
        newStatus = 'Stopped';
        newStationStatus = 'Stopped';
        toast.error(t("home.toast.lineStopped", { name: line.name }));
      }

      return {
        ...line,
        status: newStatus,
        stations: line.stations.map(st => ({
          ...st,
          status: newStationStatus,
        })),
      };
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Running': return 'text-green-600 bg-green-100';
      case 'Idle': return 'text-yellow-600 bg-yellow-100';
      case 'Stopped': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getLineStatusIcon = (status: string) => {
    switch (status) {
      case 'Running': return <Activity className="w-5 h-5 text-green-600 animate-pulse" />;
      case 'Idle': return <Pause className="w-5 h-5 text-yellow-600" />;
      case 'Stopped': return <Square className="w-5 h-5 text-red-600" />;
      default: return null;
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Stats Bar */}
      <div className="px-6 py-4 bg-white border-b">
        <div className="flex items-center gap-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">{t("home.stats.activeLines")}</div>
              <div className="text-2xl font-bold">
                {productionLines.filter(l => l.status === 'Running').length}/{productionLines.length}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">{t("home.stats.totalUnits")}</div>
              <div className="text-2xl font-bold">
                {productionLines.reduce((sum, l) => sum + l.totalUnits, 0)}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Zap className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">{t("home.stats.avgEfficiency")}</div>
              <div className="text-2xl font-bold">
                {Math.round(productionLines.reduce((sum, l) => sum + l.efficiency, 0) / productionLines.length)}%
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">{t("home.stats.totalDefects")}</div>
              <div className="text-2xl font-bold text-red-600">
                {productionLines.reduce((sum, l) => sum + l.totalDefects, 0)}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-gray-100 rounded-lg">
              <Clock className="w-6 h-6 text-gray-600" />
            </div>
            <div>
              <div className="text-sm text-gray-600">{t("home.lastUpdate")}</div>
              <div className="text-sm font-medium">
                {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>

          <div className="flex-1"></div>

          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium ${
              autoRefresh ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? t("home.autoRefresh.on") : t("home.autoRefresh.off")}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Queue Sidebar - Collapsible */}
        <div className={`bg-white border-r flex-shrink-0 transition-all duration-300 ${queueExpanded ? 'w-80' : 'w-12'}`}>
          <div className="h-full flex flex-col">
            {queueExpanded ? (
              <>
                <div className="p-4 border-b flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold">{t("home.queue.title")}</h2>
                    <p className="text-sm text-gray-500">
                      {queueOrders.filter(o => o.status !== 'Completed').length} {t("home.orders.title")}
                    </p>
                  </div>
                  <button onClick={() => setQueueExpanded(false)} className="p-1 hover:bg-gray-100 rounded">
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto">
                  {queueOrders.map((order) => (
                    <div
                      key={order.id}
                      className={`bg-white rounded-lg p-4 border-l-4 hover:shadow-md transition-shadow cursor-pointer ${
                        order.status === 'In Progress' ? 'border-blue-500' :
                        order.status === 'Pending' ? 'border-gray-300' :
                        'border-green-500'
                      } ${
                        order.status === 'Completed' ? 'opacity-50' : ''
                      }`}
                      onClick={() => navigate(`/production-orders/${order.id}/work-orders`)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-semibold">{order.id}</h3>
                          {order.status === 'Completed' && (
                            <CheckCircle2 className="w-4 h-4 text-green-600" />
                          )}
                          {order.status === 'In Progress' && (
                            <Activity className="w-4 h-4 text-blue-600 animate-pulse" />
                          )}
                        </div>
                        <button className="opacity-0 group-hover:opacity-100">
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="text-xs text-gray-500 mb-2">
                        <p>{order.releaseDate}</p>
                        <p>{order.quantity}</p>
                      </div>

                      {order.status !== 'Pending' && (
                        <div>
                          <div className="flex justify-between text-xs mb-1">
                            <span className={order.status === 'Completed' ? 'text-green-600' : 'text-blue-600'}>
                              {order.status}
                            </span>
                            <span className="font-medium">{order.progress}%</span>
                          </div>
                          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                order.status === 'Completed' 
                                  ? 'bg-green-500' 
                                  : 'bg-gradient-to-r from-blue-500 to-purple-500'
                              }`}
                              style={{ width: `${order.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <div className="p-3 border-t">
                  <Link
                    to="/production-orders"
                    className="flex items-center justify-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    <span>{t("home.orders.viewAll")}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </>
            ) : (
              <button
                onClick={() => setQueueExpanded(true)}
                className="w-full h-full flex items-center justify-center hover:bg-gray-100"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>

        {/* Production Lines Grid - CENTER */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-4 gap-4">
            {productionLines.map((line) => {
              const runningStations = line.stations.filter(s => s.status === 'Running').length;
              const totalStations = line.stations.length;
              const progress = Math.round((runningStations / totalStations) * 100);

              return (
                <div
                  key={line.id}
                  className={`rounded-xl border-4 p-4 shadow-lg hover:shadow-xl transition-all cursor-pointer ${
                    line.status === 'Running' ? 'border-green-500 bg-gradient-to-br from-green-50 via-white to-green-50' :
                    line.status === 'Idle' ? 'border-yellow-500 bg-gradient-to-br from-yellow-50 via-white to-yellow-50' :
                    'border-gray-400 bg-gradient-to-br from-gray-100 via-white to-gray-100'
                  }`}
                  onClick={() => setSelectedLine(line.id)}
                >
                  {/* Line Name & Status */}
                  <div className="text-center mb-4">
                    <h3 className="text-base font-bold mb-1">{line.name}</h3>
                    <div className="flex items-center justify-center gap-2">
                      {getLineStatusIcon(line.status)}
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(line.status)}`}>
                        {line.status}
                      </span>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs font-semibold text-gray-700">{t("home.progress")}</span>
                      <span className="text-lg font-bold">{progress}%</span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                      <div
                        className={`h-full transition-all duration-500 ${
                          line.status === 'Running' ? 'bg-gradient-to-r from-green-500 to-green-600' :
                          line.status === 'Idle' ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                          'bg-gradient-to-r from-gray-400 to-gray-500'
                        }`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Efficiency (Number Only) */}
                  <div className="text-center">
                    <div className="text-xs text-gray-600 mb-1">{t("home.efficiency")}</div>
                    <div className={`text-3xl font-bold ${
                      line.efficiency >= 90 ? 'text-green-600' :
                      line.efficiency >= 70 ? 'text-blue-600' :
                      line.efficiency >= 50 ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {line.efficiency}%
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Alerts Sidebar - Collapsible */}
        <div className={`bg-white border-l flex-shrink-0 transition-all duration-300 ${alertsExpanded ? 'w-80' : 'w-12'}`}>
          <div className="h-full flex flex-col">
            {alertsExpanded ? (
              <>
                <div className="p-4 border-b flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    <div>
                      <h2 className="text-lg font-bold">{t("home.alerts.title")}</h2>
                      <p className="text-sm text-gray-500">{defectAlerts.length} {t("home.alerts.active")}</p>
                    </div>
                  </div>
                  <button onClick={() => setAlertsExpanded(false)} className="p-1 hover:bg-gray-100 rounded">
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto p-3 space-y-3">
                  {defectAlerts.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <CheckCircle2 className="w-12 h-12 mx-auto mb-2 text-green-500" />
                      <p className="text-sm">{t("home.alerts.empty")}</p>
                    </div>
                  ) : (
                    defectAlerts.map((alert) => (
                      <div
                        key={alert.id}
                        className={`p-3 rounded-lg border-l-4 ${
                          alert.severity === 'High' ? 'border-red-600 bg-red-50' :
                          alert.severity === 'Medium' ? 'border-yellow-600 bg-yellow-50' :
                          'border-blue-600 bg-blue-50'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <XCircle className={`w-4 h-4 ${
                              alert.severity === 'High' ? 'text-red-600' :
                              alert.severity === 'Medium' ? 'text-yellow-600' :
                              'text-blue-600'
                            }`} />
                            <span className={`text-xs font-medium ${
                              alert.severity === 'High' ? 'text-red-600' :
                              alert.severity === 'Medium' ? 'text-yellow-600' :
                              'text-blue-600'
                            }`}>
                              {alert.severity}
                            </span>
                          </div>
                          <span className="text-xs text-gray-600">{alert.timestamp}</span>
                        </div>
                        <div className="text-sm font-semibold mb-1">{alert.defectType}</div>
                        <div className="text-xs text-gray-600">
                          {alert.line} - {alert.station}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="p-3 border-t">
                  <Link
                    to="/defects"
                    className="flex items-center justify-center gap-2 text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    <span>{t("home.defects.viewAll")}</span>
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </>
            ) : (
              <button
                onClick={() => setAlertsExpanded(true)}
                className="w-full h-full flex items-center justify-center hover:bg-gray-100"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Line Detail Modal */}
      {selectedLineData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">{selectedLineData.name}</h2>
                <p className="text-gray-600 mt-1">{selectedLineData.shift}</p>
              </div>
              <button onClick={() => setSelectedLine(null)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                  <div className="text-sm text-blue-600 mb-1">{t("common.status")}</div>
                  <div className="text-2xl font-bold text-blue-700">{selectedLineData.status}</div>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                  <div className="text-sm text-green-600 mb-1">{t("home.efficiency")}</div>
                  <div className="text-2xl font-bold text-green-700">{selectedLineData.efficiency}%</div>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                  <div className="text-sm text-purple-600 mb-1">{t("home.stats.totalUnits")}</div>
                  <div className="text-2xl font-bold text-purple-700">{selectedLineData.totalUnits}</div>
                </div>
                <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4">
                  <div className="text-sm text-red-600 mb-1">{t("home.stats.totalDefects")}</div>
                  <div className="text-2xl font-bold text-red-700">{selectedLineData.totalDefects}</div>
                </div>
              </div>

              <h3 className="text-lg font-bold mb-4">{t("home.modal.stationDetails")}</h3>
              <div className="grid grid-cols-2 gap-4">
                {selectedLineData.stations.map((station) => (
                  <div key={station.id} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-bold text-lg">{station.name}</h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(station.status)}`}>
                        {station.status}
                      </span>
                    </div>

                    {station.operator && (
                      <div className="mb-3 p-3 bg-white rounded border">
                        <div className="flex items-center gap-2 text-sm">
                          <UserCheck className="w-4 h-4 text-blue-600" />
                          <span className="font-medium">{station.operator.name}</span>
                        </div>
                        <div className="text-xs text-gray-600 mt-1">{t("home.modal.badge")} {station.operator.badge}</div>
                      </div>
                    )}

                    <div className="grid grid-cols-3 gap-3">
                      <div>
                        <div className="text-xs text-gray-600">{t("home.modal.cycleTime")}</div>
                        <div className="text-lg font-bold">{station.cycleTime}s</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600">{t("home.modal.units")}</div>
                        <div className="text-lg font-bold">{station.unitsProduced}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-600">{t("home.modal.defects")}</div>
                        <div className={`text-lg font-bold ${station.defects > 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {station.defects}
                        </div>
                      </div>
                    </div>

                    {station.currentWO && (
                      <div className="mt-3 pt-3 border-t">
                        <div className="text-xs text-gray-600">{t("home.modal.currentWO")}</div>
                        <div className="font-mono font-bold text-blue-600">{station.currentWO}</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}