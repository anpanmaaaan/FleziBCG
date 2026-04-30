import { Link, Navigate, Outlet, useLocation } from "react-router";
import {
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Factory,
  GitBranch,
  LayoutDashboard,
  Layers,
  Package,
  PlayCircle,
  ScanSearch,
  Settings,
  ShieldCheck,
} from "lucide-react";
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
  if (path.startsWith("/performance/oee-deep-dive")) {
    return Factory;
  }
  if (path.startsWith("/operations")) {
    return Layers;
  }
  if (path.startsWith("/production-orders")) {
    return ClipboardList;
  }
  if (path.startsWith("/work-orders")) {
    return PlayCircle;
  }
  if (path.startsWith("/products")) {
    return Package;
  }
  if (path.startsWith("/routes")) {
    return GitBranch;
  }
  if (path.startsWith("/quality")) {
    return ShieldCheck;
  }
  if (path.startsWith("/defects")) {
    return AlertTriangle;
  }
  if (path.startsWith("/traceability")) {
    return ScanSearch;
  }
  if (path.startsWith("/settings")) {
    return Settings;
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
    return "FleziBCG";
  }, [location.pathname]);

  if (!canAccessCurrentPath) {
    return <Navigate to={landing} replace />;
  }

  return (
    <div className="flex h-screen bg-slate-50">
      <div
        className={`${sidebarCollapsed ? "w-20" : "w-72"} flex flex-col border-r border-slate-200 bg-white text-slate-700 transition-all duration-300 ease-in-out shadow-sm`}
      >
        <div className={`flex min-h-[88px] items-center border-b border-slate-200 px-4 ${sidebarCollapsed ? "justify-center" : "justify-between"}`}>
          {!sidebarCollapsed && <img src="/flezi-logo.png" alt="FleziBCG" className="h-14" />}
          <button
            type="button"
            onClick={() => setSidebarCollapsed((prev) => !prev)}
            className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700"
          >
            {sidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {menuItems.map((item) => {
            const Icon = getIconForPath(item.to);
            const targetPath = item.to.split("?")[0];
            const isActive =
              location.pathname === targetPath ||
              (targetPath !== "/" && location.pathname.startsWith(`${targetPath}/`));

            return (
              <Link
                key={item.to}
                to={item.to}
                className={`group mb-1 flex items-center gap-3 rounded-xl px-3 py-3 transition-all ${
                  isActive
                    ? "bg-slate-900 text-white shadow-sm"
                    : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
                } ${sidebarCollapsed ? "justify-center" : ""}`}
                title={sidebarCollapsed ? item.label : ""}
              >
                <span
                  className={`flex h-9 w-9 items-center justify-center rounded-lg border transition-colors ${
                    isActive
                      ? "border-white/15 bg-white/10 text-white"
                      : "border-slate-200 bg-slate-50 text-slate-500 group-hover:border-slate-300 group-hover:bg-white group-hover:text-slate-700"
                  }`}
                >
                  <Icon className="h-4.5 w-4.5 flex-shrink-0 stroke-[2.25]" />
                </span>
                {!sidebarCollapsed && <span className="flex-1 text-sm font-medium">{item.label}</span>}
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
