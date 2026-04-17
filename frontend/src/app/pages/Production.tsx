import { useState } from "react";
import { Search, ChevronDown, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router";
import { PageHeader } from "@/app/components";

export function Production() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("BLK1");

  const viewTypes = [
    {
      id: "standard-worksheet",
      title: "Standard WorkSheet",
      image: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&h=300&fit=crop",
    },
    {
      id: "labour-assignment",
      title: "Labour Assignment",
      image: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=300&fit=crop",
    },
    {
      id: "production-tracking",
      title: "Production Tracking",
      image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop",
      onClick: () => navigate("/production/tracking"),
    },
  ];

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <PageHeader title="PRODUCTION" showBackButton={false} />

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {/* Search */}
        <div className="mb-8">
          <div className="flex items-center gap-4 max-w-4xl">
            <div className="flex-1 relative">
              <Search className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search Production Line"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-12 py-3 border rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <ChevronDown className="w-5 h-5 absolute right-4 top-1/2 -translate-y-1/2 text-gray-400" />
            </div>
            <button className="px-8 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
              Search
            </button>
          </div>
        </div>

        {/* Recent View */}
        <div>
          <h2 className="text-lg mb-4">Recent View</h2>
          
          <div className="border rounded-lg p-4 mb-8 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm text-gray-500">Production Line</span>
                <h3 className="text-xl mt-1">BLK1</h3>
              </div>
              <ChevronRight className="w-6 h-6 text-gray-400" />
            </div>
          </div>

          {/* View Types Grid */}
          <div className="grid grid-cols-3 gap-6">
            {viewTypes.map((view) => (
              <div
                key={view.id}
                onClick={view.onClick}
                className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group"
              >
                <div className="aspect-video bg-gray-100 overflow-hidden">
                  <img
                    src={view.image}
                    alt={view.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
                <div className="p-4">
                  <h3 className="text-base">{view.title}</h3>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}