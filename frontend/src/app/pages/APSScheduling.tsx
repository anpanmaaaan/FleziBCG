import { useState, useMemo } from "react";
import { Play, RefreshCw, Calendar, Settings, TrendingUp, Clock } from "lucide-react";
import { toast } from "sonner";

interface ScheduledOrder {
  id: string;
  po_id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  priority: number;
  due_date: string;
  estimated_duration: number; // hours
  scheduled_start: string;
  scheduled_end: string;
  station_id: string;
  status: 'Scheduled' | 'Running' | 'Completed' | 'Delayed';
  aps_score: number; // 0-100
}

interface SchedulingMetrics {
  totalOrders: number;
  onTimeRate: number;
  utilizationRate: number;
  avgLeadTime: number;
  bottleneckStation: string;
}

const mockScheduledOrders: ScheduledOrder[] = [
  {
    id: 'SCH-001',
    po_id: 'PO-2024-001',
    product_id: 'PROD-001',
    product_name: 'Engine Block',
    quantity: 50,
    priority: 1,
    due_date: '2024-04-20',
    estimated_duration: 12,
    scheduled_start: '2024-04-15 08:00',
    scheduled_end: '2024-04-15 20:00',
    station_id: 'ST-01',
    status: 'Scheduled',
    aps_score: 95,
  },
  {
    id: 'SCH-002',
    po_id: 'PO-2024-002',
    product_id: 'PROD-002',
    product_name: 'Transmission Housing',
    quantity: 30,
    priority: 2,
    due_date: '2024-04-22',
    estimated_duration: 8,
    scheduled_start: '2024-04-16 08:00',
    scheduled_end: '2024-04-16 16:00',
    station_id: 'ST-02',
    status: 'Scheduled',
    aps_score: 88,
  },
  {
    id: 'SCH-003',
    po_id: 'PO-2024-003',
    product_id: 'PROD-003',
    product_name: 'Cylinder Head',
    quantity: 100,
    priority: 1,
    due_date: '2024-04-18',
    estimated_duration: 16,
    scheduled_start: '2024-04-15 06:00',
    scheduled_end: '2024-04-15 22:00',
    station_id: 'ST-03',
    status: 'Running',
    aps_score: 92,
  },
];

const mockMetrics: SchedulingMetrics = {
  totalOrders: 15,
  onTimeRate: 94.5,
  utilizationRate: 87.3,
  avgLeadTime: 2.8,
  bottleneckStation: 'ST-01',
};

export function APSScheduling() {
  const [orders, setOrders] = useState(mockScheduledOrders);
  const [metrics] = useState(mockMetrics);
  const [algorithm, setAlgorithm] = useState<'EDD' | 'SPT' | 'LPT' | 'Priority' | 'ATC'>('EDD');
  const [isOptimizing, setIsOptimizing] = useState(false);

  const sortedOrders = useMemo(() => {
    let sorted = [...orders];
    switch (algorithm) {
      case 'EDD': // Earliest Due Date
        sorted.sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
        break;
      case 'SPT': // Shortest Processing Time
        sorted.sort((a, b) => a.estimated_duration - b.estimated_duration);
        break;
      case 'LPT': // Longest Processing Time
        sorted.sort((a, b) => b.estimated_duration - a.estimated_duration);
        break;
      case 'Priority':
        sorted.sort((a, b) => a.priority - b.priority);
        break;
      case 'ATC': // Apparent Tardiness Cost
        sorted.sort((a, b) => b.aps_score - a.aps_score);
        break;
    }
    return sorted;
  }, [orders, algorithm]);

  const handleOptimize = () => {
    setIsOptimizing(true);
    toast.info(`Running ${algorithm} scheduling algorithm...`);
    
    setTimeout(() => {
      setIsOptimizing(false);
      toast.success(`Schedule optimized using ${algorithm} algorithm!`);
    }, 2000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Scheduled': return 'bg-blue-100 text-blue-800';
      case 'Running': return 'bg-green-100 text-green-800';
      case 'Completed': return 'bg-gray-100 text-gray-800';
      case 'Delayed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: number) => {
    if (priority === 1) return 'bg-red-100 text-red-800';
    if (priority === 2) return 'bg-orange-100 text-orange-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="flex-1 flex flex-col p-6">
        {/* Control Panel */}
        <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-700">Scheduling Algorithm:</span>
              </div>
              <select
                value={algorithm}
                onChange={(e) => setAlgorithm(e.target.value as any)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-focus-ring"
              >
                <option value="EDD">EDD - Earliest Due Date</option>
                <option value="SPT">SPT - Shortest Processing Time</option>
                <option value="LPT">LPT - Longest Processing Time</option>
                <option value="Priority">Priority Based</option>
                <option value="ATC">ATC - Apparent Tardiness Cost</option>
              </select>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleOptimize}
                disabled={isOptimizing}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 disabled:opacity-50"
              >
                {isOptimizing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Run Optimization
                  </>
                )}
              </button>
              <button
                onClick={() => toast.info('Apply to Dispatch Queue feature coming soon')}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
              >
                <Calendar className="w-4 h-4" />
                Apply to Queue
              </button>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-blue-600 font-medium">Total Orders</div>
                <div className="text-2xl font-bold text-blue-800">{metrics.totalOrders}</div>
              </div>
              <Calendar className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-green-600 font-medium">On-Time Rate</div>
                <div className="text-2xl font-bold text-green-800">{metrics.onTimeRate}%</div>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-purple-600 font-medium">Utilization</div>
                <div className="text-2xl font-bold text-purple-800">{metrics.utilizationRate}%</div>
              </div>
              <Settings className="w-8 h-8 text-purple-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-orange-600 font-medium">Avg Lead Time</div>
                <div className="text-2xl font-bold text-orange-800">{metrics.avgLeadTime} days</div>
              </div>
              <Clock className="w-8 h-8 text-orange-500" />
            </div>
          </div>

          <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-red-600 font-medium">Bottleneck</div>
                <div className="text-xl font-bold text-red-800">{metrics.bottleneckStation}</div>
              </div>
              <Settings className="w-8 h-8 text-red-500" />
            </div>
          </div>
        </div>

        {/* Algorithm Info */}
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start gap-2">
            <TrendingUp className="w-5 h-5 text-yellow-600 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-yellow-800">Algorithm: {algorithm}</div>
              <div className="text-sm text-yellow-700">
                {algorithm === 'EDD' && 'Orders scheduled by earliest due date first. Minimizes maximum lateness.'}
                {algorithm === 'SPT' && 'Shortest jobs processed first. Minimizes average completion time.'}
                {algorithm === 'LPT' && 'Longest jobs processed first. Balances machine utilization.'}
                {algorithm === 'Priority' && 'Orders scheduled by priority level. High priority orders first.'}
                {algorithm === 'ATC' && 'Advanced scheduling considering tardiness cost and processing time.'}
              </div>
            </div>
          </div>
        </div>

        {/* Schedule Table */}
        <div className="flex-1 overflow-auto border rounded-lg">
          <table className="w-full">
            <thead className="bg-gray-50 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sequence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Production Order
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priority
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Duration
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Scheduled Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Station
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  APS Score
                </th>
              </tr>
            </thead>
            <tbody className="bg-background divide-y divide-surface-divider">
              {sortedOrders.map((order, index) => (
                <tr key={order.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-mono font-bold text-lg text-blue-600">{index + 1}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-blue-600">{order.po_id}</div>
                    <div className="text-sm text-gray-500">{order.id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium">{order.product_name}</div>
                    <div className="text-sm text-gray-500">{order.product_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-medium">{order.quantity}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(order.priority)}`}>
                      P{order.priority}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm">{order.due_date}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm">{order.estimated_duration}h</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm">{order.scheduled_start}</div>
                    <div className="text-xs text-gray-500">{order.scheduled_end}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium rounded bg-blue-50 text-blue-700">
                      {order.station_id}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 w-16">
                        <div
                          className={`h-2 rounded-full ${
                            order.aps_score >= 90 ? 'bg-green-500' :
                            order.aps_score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${order.aps_score}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{order.aps_score}</span>
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