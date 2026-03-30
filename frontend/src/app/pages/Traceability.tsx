import { useState, useCallback, useMemo } from "react";
import { Search, Package, GitBranch, Download, MapPin } from "lucide-react";
import { toast } from "sonner";
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

interface SerialRecord {
  serial_no: string;
  product_id: string;
  product_name: string;
  lot_no: string;
  status: 'In Production' | 'Completed' | 'Shipped' | 'Scrapped';
  created_at: string;
  current_station?: string;
  stations_completed: number;
  total_stations: number;
}

interface GenealogyNode {
  id: string;
  serial_no: string;
  product_name: string;
  station_id: string;
  timestamp: string;
  parent_id?: string;
}

const mockSerials: SerialRecord[] = [
  {
    serial_no: 'SN-001234',
    product_id: 'PROD-001',
    product_name: 'Engine Block',
    lot_no: 'LOT-2024-001',
    status: 'In Production',
    created_at: '2024-04-15 08:00',
    current_station: 'ST-03',
    stations_completed: 3,
    total_stations: 8,
  },
  {
    serial_no: 'SN-001235',
    product_id: 'PROD-003',
    product_name: 'Cylinder Head',
    lot_no: 'LOT-2024-002',
    status: 'Completed',
    created_at: '2024-04-15 07:30',
    stations_completed: 6,
    total_stations: 6,
  },
  {
    serial_no: 'SN-001236',
    product_id: 'PROD-002',
    product_name: 'Transmission Housing',
    lot_no: 'LOT-2024-001',
    status: 'Shipped',
    created_at: '2024-04-14 14:00',
    stations_completed: 7,
    total_stations: 7,
  },
];

const mockGenealogyData: GenealogyNode[] = [
  { id: '1', serial_no: 'SN-001234', product_name: 'Engine Block', station_id: 'ST-01', timestamp: '08:00' },
  { id: '2', serial_no: 'SN-001234', product_name: 'Engine Block', station_id: 'ST-02', timestamp: '08:45', parent_id: '1' },
  { id: '3', serial_no: 'SN-001234', product_name: 'Engine Block', station_id: 'ST-03', timestamp: '09:30', parent_id: '2' },
  { id: '4', serial_no: 'COMP-A001', product_name: 'Cylinder Head', station_id: 'ST-04', timestamp: '09:00' },
  { id: '5', serial_no: 'ASSY-001', product_name: 'Complete Engine', station_id: 'ST-05', timestamp: '10:00', parent_id: '3' },
  { id: '6', serial_no: 'ASSY-001', product_name: 'Complete Engine', station_id: 'ST-05', timestamp: '10:00', parent_id: '4' },
  { id: '7', serial_no: 'ASSY-001', product_name: 'Complete Engine', station_id: 'ST-06', timestamp: '11:00', parent_id: '5' },
];

export function Traceability() {
  const [searchSerial, setSearchSerial] = useState('');
  const [selectedSerial, setSelectedSerial] = useState<string | null>(null);
  const [view, setView] = useState<'list' | 'genealogy'>('list');

  const filteredSerials = useMemo(() => {
    if (!searchSerial) return mockSerials;
    return mockSerials.filter(s =>
      s.serial_no.toLowerCase().includes(searchSerial.toLowerCase()) ||
      s.product_name.toLowerCase().includes(searchSerial.toLowerCase()) ||
      s.lot_no.toLowerCase().includes(searchSerial.toLowerCase())
    );
  }, [searchSerial]);

  // Create genealogy tree nodes and edges
  const createGenealogyGraph = useCallback((serial: string) => {
    const filteredData = mockGenealogyData;
    
    const initialNodes: Node[] = filteredData.map((node, index) => ({
      id: node.id,
      type: 'default',
      data: {
        label: (
          <div className="p-3 text-center">
            <div className="font-bold text-sm">{node.serial_no}</div>
            <div className="text-xs text-gray-600">{node.product_name}</div>
            <div className="text-xs text-blue-600">{node.station_id}</div>
            <div className="text-xs text-gray-500">{node.timestamp}</div>
          </div>
        ),
      },
      position: { x: index % 3 * 250, y: Math.floor(index / 3) * 150 },
      style: {
        background: '#fff',
        border: '2px solid #3b82f6',
        borderRadius: '8px',
        padding: 0,
        width: 200,
      },
    }));

    const initialEdges: Edge[] = filteredData
      .filter(node => node.parent_id)
      .map(node => ({
        id: `e-${node.parent_id}-${node.id}`,
        source: node.parent_id!,
        target: node.id,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 20,
          height: 20,
          color: '#3b82f6',
        },
        style: {
          strokeWidth: 2,
          stroke: '#3b82f6',
        },
      }));

    return { nodes: initialNodes, edges: initialEdges };
  }, []);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const handleSerialSelect = (serial: string) => {
    setSelectedSerial(serial);
    setView('genealogy');
    const { nodes, edges } = createGenealogyGraph(serial);
    setNodes(nodes);
    setEdges(edges);
    toast.success(`Loaded genealogy for ${serial}`);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Production': return 'bg-yellow-100 text-yellow-800';
      case 'Completed': return 'bg-green-100 text-green-800';
      case 'Shipped': return 'bg-blue-100 text-blue-800';
      case 'Scrapped': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="flex-1 flex flex-col p-6">
        {/* Search & Toggle */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search serial number..."
                value={searchSerial}
                onChange={(e) => setSearchSerial(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-96"
              />
            </div>

            <div className="text-sm text-gray-600">
              Found: <strong>{filteredSerials.length}</strong> serials
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setView('list')}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                view === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
              }`}
            >
              <Package className="w-4 h-4" />
              Serial List
            </button>
            <button
              onClick={() => {
                if (selectedSerial) {
                  setView('genealogy');
                } else {
                  toast.warning('Please select a serial number first');
                }
              }}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                view === 'genealogy' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'
              }`}
            >
              <GitBranch className="w-4 h-4" />
              Genealogy Tree
            </button>
            <button
              onClick={() => toast.info('Export feature coming soon')}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Content */}
        {view === 'list' ? (
          <div className="flex-1 overflow-auto border rounded-lg">
            <table className="w-full">
              <thead className="bg-gray-50 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Serial Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Lot Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Current Station
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created At
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredSerials.map((serial) => (
                  <tr key={serial.serial_no} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-mono font-bold text-blue-600">{serial.serial_no}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium">{serial.product_name}</div>
                      <div className="text-sm text-gray-500">{serial.product_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-mono text-sm">{serial.lot_no}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(serial.status)}`}>
                        {serial.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${(serial.stations_completed / serial.total_stations) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600">
                          {serial.stations_completed}/{serial.total_stations}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {serial.current_station ? (
                        <span className="px-2 py-1 text-xs font-medium rounded bg-blue-50 text-blue-700">
                          {serial.current_station}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {serial.created_at}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleSerialSelect(serial.serial_no)}
                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 flex items-center gap-1"
                      >
                        <GitBranch className="w-3 h-3" />
                        View Tree
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex-1 flex flex-col">
            {selectedSerial && (
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <span className="font-medium text-blue-800">
                    Genealogy Tree for: <span className="font-mono">{selectedSerial}</span>
                  </span>
                </div>
              </div>
            )}
            <div className="flex-1 border rounded-lg bg-gray-50">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
              >
                <Background />
                <Controls />
                <MiniMap />
              </ReactFlow>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}