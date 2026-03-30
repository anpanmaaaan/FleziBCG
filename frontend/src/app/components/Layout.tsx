import { Outlet, Link, useLocation } from "react-router";
import { 
  ClipboardList, 
  Factory, 
  Settings, 
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  Search,
  LayoutDashboard,
  Layers,
  PlayCircle,
  CheckCircle2,
  Calendar,
  Star,
  Activity,
  BarChart3
} from "lucide-react";
import { useState } from "react";
import { TopBar } from "./TopBar";
import fleziLogo from "figma:asset/020ceccc095996a9828ea9162f539ccddf92986f.png";

export function Layout() {
  const location = useLocation();
  const [expandedMenus, setExpandedMenus] = useState({
    production: true,
    routing: true,
    quality: false,
    performance: true,
  });
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleMenu = (menu: keyof typeof expandedMenus) => {
    setExpandedMenus(prev => ({ ...prev, [menu]: !prev[menu] }));
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev);
  };

  const isActive = (path: string) => location.pathname === path;

  // Helper to render completion badge
  const CompletionBadge = ({ percent }: { percent: number }) => {
    if (sidebarCollapsed) return null;
    
    const isComplete = percent === 100;
    const color = isComplete 
      ? 'bg-emerald-500 text-white' 
      : percent >= 80 
      ? 'bg-blue-500 text-white'
      : percent >= 60
      ? 'bg-amber-500 text-white'
      : 'bg-slate-400 text-white';
    
    return (
      <span className={`ml-auto text-xs px-2 py-0.5 rounded-full font-medium ${color} flex items-center gap-1`}>
        {isComplete && <Star className="w-3 h-3 fill-current" />}
        {percent}%
      </span>
    );
  };

  // Get current page title
  const getCurrentPageTitle = () => {
    if (location.pathname === '/') return 'Execution Tracking';
    if (location.pathname === '/dashboard') return 'Dashboard';
    if (location.pathname === '/performance/oee-deep-dive') return 'OEE Deep Dive';
    if (location.pathname === '/production-orders') return 'Production Orders';
    if (location.pathname === '/dispatch') return 'Dispatch Queue';
    if (location.pathname === '/routes') return 'Route List';
    if (location.pathname === '/station-execution') return 'Station Execution';
    if (location.pathname === '/quality') return 'QC Checkpoints';
    if (location.pathname === '/defects') return 'Defect Management';
    if (location.pathname === '/traceability') return 'Traceability';
    if (location.pathname === '/scheduling') return 'APS Scheduling';
    if (location.pathname === '/settings') return 'Settings';
    if (location.pathname.startsWith('/routes/')) return 'Route Detail';
    if (location.pathname.startsWith('/production-order/')) return 'Operation List';
    return 'Dashboard';
  };

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <div 
        className={`${
          sidebarCollapsed ? 'w-20' : 'w-72'
        } bg-white text-slate-700 flex flex-col border-r border-slate-200 transition-all duration-300 ease-in-out shadow-sm`}
      >
        {/* Logo */}
        <div className={`p-6 flex items-center ${sidebarCollapsed ? 'justify-center' : 'justify-between'}`}>
          {!sidebarCollapsed && <img src={fleziLogo} alt="FleziBCG" className="h-16" />}
          <button 
            onClick={toggleSidebar}
            className="text-slate-500 hover:text-slate-700 hover:bg-slate-100 p-2 rounded-lg transition-colors"
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <ChevronLeft className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Search */}
        {!sidebarCollapsed && (
          <div className="px-4 pb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search..."
                className="w-full bg-slate-50 text-slate-700 placeholder-slate-400 rounded-lg pl-10 pr-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white border border-slate-200 transition-colors"
              />
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3">
          {/* Dashboard */}
          <Link
            to="/dashboard"
            className={`flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-slate-100 transition-all mb-1 ${
              isActive('/dashboard') ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' : 'text-slate-700'
            } ${sidebarCollapsed ? 'justify-center' : ''}`}
            title={sidebarCollapsed ? 'Dashboard' : ''}
          >
            <LayoutDashboard className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span className="flex-1">Dashboard</span>}
            <CompletionBadge percent={80} />
          </Link>

          {/* Performance Analytics */}
          <div className="mb-1">
            <button
              onClick={() => toggleMenu('performance')}
              className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center' : 'justify-between'} px-3 py-3 rounded-lg hover:bg-slate-100 transition-all ${
                location.pathname.startsWith('/performance') ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' : 'text-slate-700'
              }`}
              title={sidebarCollapsed ? 'Performance' : ''}
            >
              <div className="flex items-center gap-3">
                <BarChart3 className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && <span>Performance</span>}
              </div>
              {!sidebarCollapsed && (
                expandedMenus.performance ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )
              )}
            </button>
            {expandedMenus.performance && !sidebarCollapsed && (
              <div className="ml-8 mt-1 space-y-1">
                <Link
                  to="/performance/oee-deep-dive"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/performance/oee-deep-dive') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>OEE Deep Dive</span>
                  <CompletionBadge percent={100} />
                </Link>
              </div>
            )}
          </div>

          {/* Production Management */}
          <div className="mb-1">
            <button
              onClick={() => toggleMenu('production')}
              className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center' : 'justify-between'} px-3 py-3 rounded-lg hover:bg-slate-100 transition-all ${
                isActive('/production-orders') || isActive('/dispatch') || isActive('/') || isActive('/station-execution') ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' : 'text-slate-700'
              }`}
              title={sidebarCollapsed ? 'Production' : ''}
            >
              <div className="flex items-center gap-3">
                <Factory className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && <span>Production</span>}
              </div>
              {!sidebarCollapsed && (
                expandedMenus.production ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )
              )}
            </button>
            {expandedMenus.production && !sidebarCollapsed && (
              <div className="ml-8 mt-1 space-y-1">
                <Link
                  to="/production-orders"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/production-orders') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Production Orders</span>
                  <CompletionBadge percent={75} />
                </Link>
                <Link
                  to="/dispatch"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/dispatch') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Dispatch Queue</span>
                  <CompletionBadge percent={80} />
                </Link>
                <Link
                  to="/"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Execution Tracking</span>
                  <CompletionBadge percent={100} />
                </Link>
                <Link
                  to="/station-execution"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/station-execution') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Station Execution</span>
                  <CompletionBadge percent={100} />
                </Link>
              </div>
            )}
          </div>

          {/* Route & Operations */}
          <div className="mb-1">
            <button
              onClick={() => toggleMenu('routing')}
              className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center' : 'justify-between'} px-3 py-3 rounded-lg hover:bg-slate-100 transition-all ${
                isActive('/routes') || location.pathname.startsWith('/routes/') || location.pathname.startsWith('/production-order/') ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' : 'text-slate-700'
              }`}
              title={sidebarCollapsed ? 'Routes & Operations' : ''}
            >
              <div className="flex items-center gap-3">
                <Layers className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && <span>Routes & Operations</span>}
              </div>
              {!sidebarCollapsed && (
                expandedMenus.routing ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )
              )}
            </button>
            {expandedMenus.routing && !sidebarCollapsed && (
              <div className="ml-8 mt-1 space-y-1">
                <Link
                  to="/routes"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/routes') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Route List</span>
                  <CompletionBadge percent={85} />
                </Link>
                <Link
                  to="/production-order/PO-001"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    location.pathname.startsWith('/production-order/') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Operation List</span>
                  <CompletionBadge percent={100} />
                </Link>
              </div>
            )}
          </div>

          {/* Quality Management */}
          <div className="mb-1">
            <button
              onClick={() => toggleMenu('quality')}
              className={`w-full flex items-center ${sidebarCollapsed ? 'justify-center' : 'justify-between'} px-3 py-3 rounded-lg hover:bg-slate-100 transition-all ${
                isActive('/quality') || isActive('/defects') || isActive('/traceability') ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' : 'text-slate-700'
              }`}
              title={sidebarCollapsed ? 'Quality' : ''}
            >
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && <span>Quality</span>}
              </div>
              {!sidebarCollapsed && (
                expandedMenus.quality ? (
                  <ChevronDown className="w-4 h-4" />
                ) : (
                  <ChevronRight className="w-4 h-4" />
                )
              )}
            </button>
            {expandedMenus.quality && !sidebarCollapsed && (
              <div className="ml-8 mt-1 space-y-1">
                <Link
                  to="/quality"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/quality') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>QC Checkpoints</span>
                  <CompletionBadge percent={85} />
                </Link>
                <Link
                  to="/defects"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/defects') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Defect Management</span>
                  <CompletionBadge percent={85} />
                </Link>
                <Link
                  to="/traceability"
                  className={`flex items-center justify-between px-3 py-2 text-sm rounded-lg hover:bg-slate-100 transition-all ${
                    isActive('/traceability') ? 'bg-blue-50 text-blue-600 font-medium' : 'text-slate-600'
                  }`}
                >
                  <span>Traceability</span>
                  <CompletionBadge percent={75} />
                </Link>
              </div>
            )}
          </div>

          {/* APS Scheduling */}
          <Link
            to="/scheduling"
            className={`flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-slate-100 transition-all mb-1 ${
              isActive('/scheduling') ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' : 'text-slate-700'
            } ${sidebarCollapsed ? 'justify-center' : ''}`}
            title={sidebarCollapsed ? 'APS Scheduling' : ''}
          >
            <Calendar className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span className="flex-1">APS Scheduling</span>}
            <CompletionBadge percent={90} />
          </Link>

          {/* Settings */}
          <Link
            to="/settings"
            className={`flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-slate-100 transition-all mb-1 ${
              isActive('/settings') ? 'bg-blue-50 text-blue-600 font-medium shadow-sm' : 'text-slate-700'
            } ${sidebarCollapsed ? 'justify-center' : ''}`}
            title={sidebarCollapsed ? 'Settings' : ''}
          >
            <Settings className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span>Settings</span>}
          </Link>
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <TopBar currentPage={getCurrentPageTitle()} />
        
        {/* Page Content */}
        <div className="flex-1 overflow-auto">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
