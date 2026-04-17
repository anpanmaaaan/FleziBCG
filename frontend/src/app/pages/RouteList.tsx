import { useState } from "react";
import { Plus, Edit, Trash2, Eye, Copy, Download, Search, ArrowUpDown, Calendar, ChevronDown, Edit2 } from "lucide-react";
import { useNavigate } from "react-router";
import { routes as initialRoutes } from "@/app/data/mockData";
import { Switch } from "@/app/components/ui/switch";

export function RouteList() {
  const navigate = useNavigate();
  const [routes, setRoutes] = useState(initialRoutes);
  const [searchValues, setSearchValues] = useState({
    route: "",
    lastUpdated: "",
    status: "",
  });

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  // Toggle Active/Inactive status
  const handleToggleStatus = (routeId: string) => {
    setRoutes(prevRoutes =>
      prevRoutes.map(route =>
        route.id === routeId
          ? { ...route, status: route.status === 'Active' ? 'Inactive' as const : 'Active' as const }
          : route
      )
    );
  };

  // Navigate to route detail page
  const handleEditClick = (routeId: string) => {
    navigate(`/routes/${routeId}`);
  };

  const filteredRoutes = routes.filter(route => {
    return (
      route.name.toLowerCase().includes(searchValues.route.toLowerCase()) &&
      (searchValues.status === "" || route.status === searchValues.status)
    );
  });

  const totalPages = Math.ceil(filteredRoutes.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedRoutes = filteredRoutes.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl">Route list</h2>
          <button className="flex items-center gap-2 px-4 py-2 border rounded hover:bg-gray-50">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>

        {/* Table */}
        <div className="border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left w-1/3">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm uppercase">ROUTE</span>
                      <ArrowUpDown className="w-4 h-4" />
                    </div>
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <input
                        type="text"
                        placeholder="Search"
                        value={searchValues.route}
                        onChange={(e) => setSearchValues(prev => ({ ...prev, route: e.target.value }))}
                        className="w-full pl-9 pr-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                      />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left w-1/4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm uppercase">LAST UPDATED</span>
                      <ArrowUpDown className="w-4 h-4" />
                    </div>
                    <div className="relative">
                      <input
                        type="text"
                        placeholder="MM/DD/YYYY"
                        className="w-full pr-9 pl-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                      />
                      <Calendar className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left w-1/4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm uppercase">STATUS</span>
                      <ArrowUpDown className="w-4 h-4" />
                    </div>
                    <div className="relative">
                      <select
                        value={searchValues.status}
                        onChange={(e) => setSearchValues(prev => ({ ...prev, status: e.target.value }))}
                        className="w-full appearance-none px-3 py-2 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-focus-ring"
                      >
                        <option value="">Select</option>
                        <option value="Active">Active</option>
                        <option value="Inactive">Inactive</option>
                      </select>
                      <ChevronDown className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left w-1/6">
                    <span className="text-sm uppercase">ACTION</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedRoutes.map((route, index) => (
                  <tr key={route.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-6 py-4 font-medium">{route.name}</td>
                    <td className="px-6 py-4">{route.lastUpdated}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <Switch 
                          checked={route.status === 'Active'} 
                          onCheckedChange={() => handleToggleStatus(route.id)}
                        />
                        <span className={route.status === 'Active' ? 'text-gray-900' : 'text-gray-500'}>
                          {route.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button 
                        className="p-2 hover:bg-gray-200 rounded"
                        onClick={() => handleEditClick(route.id)}
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pagination */}
        <div className="mt-6 flex items-center justify-center gap-2">
          <span className="text-sm text-gray-600">
            Showing 1 - {Math.min(itemsPerPage, filteredRoutes.length)} of {filteredRoutes.length} results
          </span>
          <div className="flex items-center gap-1 ml-4">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              «
            </button>
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              ‹
            </button>
            <button className="px-3 py-1 border rounded bg-blue-500 text-white">
              1
            </button>
            <button
              onClick={() => setCurrentPage(2)}
              className="px-3 py-1 border rounded hover:bg-gray-50"
            >
              2
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage >= totalPages}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              ›
            </button>
            <button
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage >= totalPages}
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
            >
              »
            </button>
          </div>
          <select
            value={itemsPerPage}
            onChange={(e) => setItemsPerPage(Number(e.target.value))}
            className="ml-4 px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-focus-ring"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>
    </div>
  );
}