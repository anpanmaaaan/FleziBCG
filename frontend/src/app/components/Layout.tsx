import { Link, Navigate, Outlet, useLocation } from "react-router";
import { ChevronLeft, ChevronRight, LayoutDashboard, Layers, PlayCircle } from "lucide-react";
import { useMemo, useState } from "react";

import { useAuth } from "@/app/auth";
import {
  getDefaultLandingForPersona,
  getPersonaEnforcementMode,
  getMenuItemsForPersona,
  isRouteAllowedForPersona,
  resolvePersonaFromRoleCode,
} from "@/app/persona";
import { AccessDeniedScreen } from "./AccessDeniedScreen";
import { ActiveImpersonationBanner } from "./ActiveImpersonationBanner";
import { RouteStatusBanner } from "./RouteStatusBanner";
import { TopBar } from "./TopBar";
import { useImpersonation } from "@/app/impersonation";

function getIconForPath(path: string) {
  if (path.startsWith("/dashboard")) {
    return LayoutDashboard;
  }
  if (path.startsWith("/operations")) {
    return Layers;
  }
  return PlayCircle;
}

export function Layout() {
  const location = useLocation();
  const { currentUser } = useAuth();
  const { effectiveRoleCode } = useImpersonation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const persona = resolvePersonaFromRoleCode(effectiveRoleCode ?? currentUser?.role_code ?? null);
  const enforcementMode = getPersonaEnforcementMode();

  if (persona === "DENY" && enforcementMode === "STRICT") {
    return <AccessDeniedScreen />;
  }

  const landing = getDefaultLandingForPersona(persona);
  const menuItems = getMenuItemsForPersona(persona);
  const canAccessCurrentPath = isRouteAllowedForPersona(persona, location.pathname, location.search);

  const currentPageTitle = useMemo(() => {
    if (location.pathname === "/dashboard") {
      return "Dashboard";
    }
    if (location.pathname === "/operations" || location.pathname.startsWith("/operations/")) {
      return "Global Operations";
    }
    if (location.pathname === "/station" || location.pathname === "/station-execution") {
      return "Station Execution";
    }
    if (location.pathname === "/products" || location.pathname.startsWith("/products/")) {
      return "Products";
    }
    return "MES Lite";
  }, [location.pathname]);

  if (!canAccessCurrentPath) {
    return <Navigate to={landing} replace />;
  }

  return (
    <div className="flex h-screen bg-slate-50">
      <div
        className={`${sidebarCollapsed ? "w-20" : "w-72"} bg-white text-slate-700 flex flex-col border-r border-slate-200 transition-all duration-300 ease-in-out shadow-sm`}
      >
        <div className={`p-6 flex items-center ${sidebarCollapsed ? "justify-center" : "justify-between"}`}>
          {!sidebarCollapsed && <img src="/flezi-logo.png" alt="FleziBCG" className="h-16" />}
          <button
            onClick={() => setSidebarCollapsed((prev) => !prev)}
            className="text-slate-500 hover:text-slate-700 hover:bg-slate-100 p-2 rounded-lg transition-colors"
          >
            {sidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3">
          {menuItems.map((item) => {
            const Icon = getIconForPath(item.to);
            const targetPath = item.to.split("?")[0];
            const isActive = location.pathname === targetPath;

            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-slate-100 transition-all mb-1 ${isActive ? "bg-blue-50 text-blue-600 font-medium shadow-sm" : "text-slate-700"} ${sidebarCollapsed ? "justify-center" : ""}`}
                title={sidebarCollapsed ? item.label : ""}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && <span className="flex-1">{item.label}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar currentPage={currentPageTitle} />
        <ActiveImpersonationBanner />
        <RouteStatusBanner />
        <div className="flex-1 overflow-auto">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
