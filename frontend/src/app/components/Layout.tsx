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
  X,
  Lock,
  Users,
  Shield,
  LogOut,
  Database,
  Building2,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { useAuth } from "@/app/auth";

function getFocusableElements(container: HTMLElement | null) {
  return Array.from(
    container?.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    ) ?? []
  ).filter((el) => !el.hasAttribute('disabled') && el.getAttribute('aria-hidden') !== 'true');
}
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
  if (path.startsWith("/users")) {
    return Users;
  }
  if (path.startsWith("/roles")) {
    return Shield;
  }
  if (path.startsWith("/action-registry")) {
    return Lock;
  }
  if (path.startsWith("/scope-assignments")) {
    return Database;
  }
  if (path.startsWith("/sessions")) {
    return LogOut;
  }
  if (path.startsWith("/audit-log")) {
    return ClipboardList;
  }
  if (path.startsWith("/security-events")) {
    return AlertTriangle;
  }
  if (path.startsWith("/tenant-settings")) {
    return Building2;
  }
  if (path.startsWith("/plant-hierarchy")) {
    return Layers;
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
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const drawerRef = useRef<HTMLDivElement>(null);

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

  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [location.pathname, location.search]);

  useEffect(() => {
    if (!mobileSidebarOpen) return;

    function handleDrawerTab(event: KeyboardEvent) {
      if (event.key !== 'Tab') return;
      const focusable = getFocusableElements(drawerRef.current);
      if (!focusable.length) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      const activeEl = document.activeElement as HTMLElement;

      if (event.shiftKey && activeEl === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && activeEl === last) {
        event.preventDefault();
        first.focus();
      }
    }

    drawerRef.current?.addEventListener('keydown', handleDrawerTab);
    return () => drawerRef.current?.removeEventListener('keydown', handleDrawerTab);
  }, [mobileSidebarOpen]);

  if (!canAccessCurrentPath) {
    return <Navigate to={landing} replace />;
  }

  const renderMenuItems = (compact: boolean, onNavigate?: () => void) => {
    return menuItems.map((item) => {
      const Icon = getIconForPath(item.to);
      const targetPath = item.to.split("?")[0];
      const isActive =
        location.pathname === targetPath ||
        (targetPath !== "/" && location.pathname.startsWith(`${targetPath}/`));

      return (
        <Link
          key={item.to}
          to={item.to}
          onClick={onNavigate}
          className={`group mb-1 flex items-center gap-3 rounded-xl px-3 py-3 transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 ${
            isActive
              ? "bg-slate-900 text-white shadow-sm"
              : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
          } ${compact ? "justify-center" : ""}`}
          title={compact ? item.label : ""}
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
          {!compact && <span className="flex-1 text-sm font-medium">{item.label}</span>}
        </Link>
      );
    });
  };

  return (
    <div className="flex h-screen bg-slate-50">
      {mobileSidebarOpen && (
        <div ref={drawerRef} className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true">
          <button
            type="button"
            aria-label="Close navigation drawer"
            onClick={() => { setMobileSidebarOpen(false); menuButtonRef.current?.focus(); }}
            className="absolute inset-0 bg-slate-900/45 focus-visible:outline-0"
          />
          <aside id="app-mobile-navigation-drawer" className="relative flex h-full w-[min(20rem,85vw)] flex-col border-r border-slate-200 bg-white text-slate-700 shadow-xl">
            <div className="flex min-h-[72px] items-center justify-between border-b border-slate-200 px-4">
              <img src="/flezi-logo.png" alt="FleziBCG" className="h-12" />
              <button
                type="button"
                aria-label="Close navigation drawer"
                onClick={() => { setMobileSidebarOpen(false); menuButtonRef.current?.focus(); }}
                className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto px-3 py-4" role="navigation" aria-label="Mobile navigation">{renderMenuItems(false, () => setMobileSidebarOpen(false))}</nav>
          </aside>
        </div>
      )}

      <div
        className={`${sidebarCollapsed ? "w-20" : "w-72"} hidden lg:flex flex-col border-r border-slate-200 bg-white text-slate-700 transition-all duration-300 ease-in-out shadow-sm`}
      >
        <div className={`flex min-h-[88px] items-center border-b border-slate-200 px-4 ${sidebarCollapsed ? "justify-center" : "justify-between"}`}>
          {!sidebarCollapsed && <img src="/flezi-logo.png" alt="FleziBCG" className="h-14" />}
          <button
            type="button"
            onClick={() => setSidebarCollapsed((prev) => !prev)}
            className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
          >
            {sidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4">{renderMenuItems(sidebarCollapsed)}</nav>
      </div>

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <TopBar currentPage={currentPageTitle} showMobileMenuButton mobileMenuOpen={mobileSidebarOpen} menuButtonRef={menuButtonRef} onOpenSidebar={() => setMobileSidebarOpen(true)} />
        <ActiveImpersonationBanner />
        <RouteStatusBanner />
        <div className="min-w-0 flex-1 overflow-auto">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
