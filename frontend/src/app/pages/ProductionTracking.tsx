import { useState } from "react";
import { Search, Play, Pause, CheckCircle, AlertCircle } from "lucide-react";
import { useNavigate } from "react-router";
import { productionLines } from "../data/mockData";
import { PageHeader } from "../components/PageHeader";

interface Worker {
  id: string;
  name: string;
  status: 'Active' | 'Break' | 'Offline';
  station: string;
  efficiency: number;
}

export function ProductionTracking() {
  const navigate = useNavigate();
  const [selectedLine] = useState('BLK1');
  const [shift, setShift] = useState('1');
  
  const lineData = productionLines.find(line => line.id === selectedLine);

  const workers: Worker[] = [
    { id: 'W001', name: 'Nguyễn Văn A', status: 'Active', station: 'Station 1', efficiency: 95 },
    { id: 'W002', name: 'Trần Thị B', status: 'Active', station: 'Station 2', efficiency: 88 },
    { id: 'W003', name: 'Lê Văn C', status: 'Break', station: 'Station 3', efficiency: 92 },
    { id: 'W004', name: 'Phạm Thị D', status: 'Active', station: 'Station 4', efficiency: 97 },
  ];

  const metrics = {
    target: 52000,
    actual: 48500,
    defects: 120,
    efficiency: 93.2,
    oee: 85.5,
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <PageHeader 
        title={`Production Tracking - ${selectedLine}`}
        showBackButton={true}
        onBackClick={() => navigate("/production")}
      >
        <div className="flex items-center gap-4 ml-auto">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Shift:</span>
            <select
              value={shift}
              onChange={(e) => setShift(e.target.value)}
              className="px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="1">Shift 1 (6:00 - 14:00)</option>
              <option value="2">Shift 2 (14:00 - 22:00)</option>
              <option value="3">Shift 3 (22:00 - 6:00)</option>
            </select>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-green-50 rounded-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm">Line Active</span>
          </div>
        </div>
      </PageHeader>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="bg-white border rounded-lg p-4">
            <div className="text-sm text-gray-500 mb-2">Target Output</div>
            <div className="text-2xl mb-1">{metrics.target.toLocaleString()}</div>
            <div className="text-xs text-gray-400">units</div>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <div className="text-sm text-gray-500 mb-2">Actual Output</div>
            <div className="text-2xl mb-1">{metrics.actual.toLocaleString()}</div>
            <div className="flex items-center gap-1 text-xs text-orange-600">
              <AlertCircle className="w-3 h-3" />
              <span>{((metrics.actual / metrics.target) * 100).toFixed(1)}%</span>
            </div>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <div className="text-sm text-gray-500 mb-2">Defects</div>
            <div className="text-2xl mb-1">{metrics.defects}</div>
            <div className="text-xs text-red-600">
              {((metrics.defects / metrics.actual) * 100).toFixed(2)}% rate
            </div>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <div className="text-sm text-gray-500 mb-2">Efficiency</div>
            <div className="text-2xl mb-1">{metrics.efficiency}%</div>
            <div className="flex items-center gap-1 text-xs text-green-600">
              <CheckCircle className="w-3 h-3" />
              <span>Good</span>
            </div>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <div className="text-sm text-gray-500 mb-2">OEE</div>
            <div className="text-2xl mb-1">{metrics.oee}%</div>
            <div className="text-xs text-gray-400">Overall Equipment</div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Current Orders */}
          <div className="border rounded-lg">
            <div className="border-b px-4 py-3 bg-gray-50">
              <h2 className="text-lg">Current Production Orders</h2>
            </div>
            <div className="p-4 space-y-3">
              {lineData?.orders.slice(0, 3).map((order) => (
                <div key={order.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <div className="text-sm text-gray-500">Order ID</div>
                      <div className="font-medium">{order.orderId || 'N/A'}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {order.status === 'Late' ? (
                        <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">
                          Behind Schedule
                        </span>
                      ) : order.progress === 100 ? (
                        <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                          Completed
                        </span>
                      ) : (
                        <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                          In Progress
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mb-3">
                    <div className="text-sm text-gray-500 mb-1">Quantity: {order.quantity}</div>
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span>Progress</span>
                      <span className="font-medium">{order.progress}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          order.status === 'Late' ? 'bg-red-500' : 
                          order.progress === 100 ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                        style={{ width: `${order.progress}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 border rounded hover:bg-gray-50">
                      <Play className="w-4 h-4" />
                      <span className="text-sm">Start</span>
                    </button>
                    <button className="flex-1 flex items-center justify-center gap-2 px-3 py-2 border rounded hover:bg-gray-50">
                      <Pause className="w-4 h-4" />
                      <span className="text-sm">Pause</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Workers */}
          <div className="border rounded-lg">
            <div className="border-b px-4 py-3 bg-gray-50 flex items-center justify-between">
              <h2 className="text-lg">Workers on Line</h2>
              <button className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600">
                Assign Worker
              </button>
            </div>
            <div className="p-4">
              <div className="space-y-3">
                {workers.map((worker) => (
                  <div key={worker.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white">
                          {worker.name.charAt(0)}
                        </div>
                        <div>
                          <div className="font-medium">{worker.name}</div>
                          <div className="text-sm text-gray-500">{worker.id}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          worker.status === 'Active' ? 'bg-green-500' :
                          worker.status === 'Break' ? 'bg-yellow-500' : 'bg-gray-400'
                        }`} />
                        <span className="text-sm">{worker.status}</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-gray-500">Station</div>
                        <div>{worker.station}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Efficiency</div>
                        <div className="flex items-center gap-1">
                          <span>{worker.efficiency}%</span>
                          {worker.efficiency >= 90 && (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="mt-6 border rounded-lg">
          <div className="border-b px-4 py-3 bg-gray-50">
            <h2 className="text-lg">Production Timeline</h2>
          </div>
          <div className="p-4">
            <div className="space-y-3">
              {[
                { time: '08:30', event: 'Production started for Order PO4DL2', type: 'info' },
                { time: '09:15', event: 'Quality check passed - Station 3', type: 'success' },
                { time: '10:00', event: 'Material shortage detected', type: 'warning' },
                { time: '10:30', event: 'Material replenished, production resumed', type: 'success' },
                { time: '11:45', event: 'Defect reported - Station 2', type: 'error' },
              ].map((item, index) => (
                <div key={index} className="flex items-start gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      item.type === 'success' ? 'bg-green-500' :
                      item.type === 'warning' ? 'bg-yellow-500' :
                      item.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                    }`} />
                    <span className="text-sm text-gray-500 w-16">{item.time}</span>
                  </div>
                  <div className="flex-1 border-b pb-3">
                    <p className="text-sm">{item.event}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}