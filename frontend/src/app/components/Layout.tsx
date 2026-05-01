import { Link, Navigate, Outlet, useLocation } from "react-router";
import {
  AlertTriangle,
  Activity,
  BarChart3,
  Box,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Cpu,
  Factory,
  FileText,
  GitBranch,
  LayoutDashboard,
  Layers,
  Monitor,
  Package,
  PlayCircle,
  Ruler,
  ScanSearch,
  Server,
  Settings,
  ShieldAlert,
  ShieldCheck,
  Tag,
  TrendingUp,
  UserCheck,
  X,
  Lock,
  Users,
  Shield,
  LogOut,
  Database,
  Building2,
  CalendarClock,
  Eye,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useAuth } from "@/app/auth";
import { groupMenuItems, getGroupIdForPath } from "@/app/navigation/navigationGroups";
import type { GroupedMenuSection } from "@/app/navigation/navigationGroups";
import { SCREEN_STATUS_REGISTRY } from "@/app/screenStatus";
import type { ScreenPhase } from "@/app/screenStatus";

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
  if (path.startsWith("/bom")) {
    return FileText;
  }
  if (path.startsWith("/resource-requirements")) {
    return Server;
  }
  if (path.startsWith("/reason-codes")) {
    return Tag;
  }
  if (path.startsWith("/line-monitor")) {
    return Monitor;
  }
  if (path.startsWith("/station-monitor")) {
    return Monitor;
  }
  if (path.startsWith("/downtime-analysis")) {
    return BarChart3;
  }
  if (path.startsWith("/shift-summary")) {
    return CalendarClock;
  }
  if (path.startsWith("/operator-identification")) {
    return UserCheck;
  }
  if (path.startsWith("/equipment-binding")) {
    return Cpu;
  }
  if (path.startsWith("/station-session")) {
    return Layers;
  }
  if (path.startsWith("/supervisory")) {
    return Eye;
  }
  if (path.startsWith("/quality-dashboard")) {
    return ShieldAlert;
  }
  if (path.startsWith("/quality-measurements")) {
    return Ruler;
  }
  if (path.startsWith("/quality-holds")) {
    return AlertTriangle;
  }
  if (path.startsWith("/material-readiness")) {
    return Package;
  }
  if (path.startsWith("/staging-kitting")) {
    return Box;
  }
  if (path.startsWith("/wip-buffers")) {
    return Activity;
  }
  if (path.startsWith("/settings")) {
    return Settings;
  }
  return PlayCircle;
}

/** Maps nav group IDs to their sidebar section header icons. */
const GROUP_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  "home": LayoutDashboard,
  "core-operations": PlayCircle,
  "mfg-master-data": FileText,
  "quality": ShieldCheck,
  "material-wip": Package,
  "traceability": ScanSearch,
  "reporting-analytics": BarChart3,
  "planning-scheduling": CalendarClock,
  "governance-admin": Settings,
  "_other": Layers,
};

/** Looks up the screen phase for a menu item path from the SCREEN_STATUS_REGISTRY. */
function getPhaseForMenuPath(menuPath: string): ScreenPhase | null {
  const cleanPath = menuPath.split("?")[0];
  for (const entry of Object.values(SCREEN_STATUS_REGISTRY)) {
    if (!entry.routePattern.includes(":") && entry.routePattern === cleanPath) {
      return entry.phase;
    }
  }
  return null;
}

/** Small inline pill badge shown for non-connected screen phases. */
function PhaseBadge({ phase, active }: { phase: ScreenPhase; active: boolean }) {
  const config: Partial<Record<ScreenPhase, { label: string; cls: string }>> = {
    SHELL: { label: "SHELL", cls: "bg-blue-100 text-blue-700" },
    MOCK: { label: "MOCK", cls: "bg-amber-100 text-amber-700" },
    FUTURE: { label: "TBD", cls: "bg-slate-200 text-slate-600" },
    DISABLED: { label: "OFF", cls: "bg-red-100 text-red-600" },
  };
  const c = config[phase];
  if (!c) return null;
  const cls = active ? "bg-white/20 text-white/80" : c.cls;
  return (
    <span className={`ml-auto flex-shrink-0 rounded px-1 py-px text-[9px] font-bold leading-none ${cls}`}>
      {c.label}
    </span>
  );
}

export function Layout() {
  const location = useLocation();
  const { currentUser } = useAuth();
  const { effectiveRoleCode } = useImpersonation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  // Collapsible group state — auto-open the group containing the active route
  const [openGroups, setOpenGroups] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    const groupId = getGroupIdForPath(location.pathname);
    if (groupId) initial.add(groupId);
    return initial;
  });

  const toggleGroup = useCallback((groupId: string) => {
    setOpenGroups((prev) => {
      const next = new Set(prev);
      if (next.has(groupId)) next.delete(groupId);
      else next.add(groupId);
      return next;
    });
  }, []);
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
    // Auto-open the group for the new route (without closing others)
    const groupId = getGroupIdForPath(location.pathname);
    if (groupId) {
      setOpenGroups((prev) => {
        if (prev.has(groupId)) return prev;
        const next = new Set(prev);
        next.add(groupId);
        return next;
      });
    }
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

  /** Renders the flat icon-only list for the collapsed (compact) sidebar. */
  const renderCompactMenuItems = () => {
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
          className={`group mb-1 flex items-center justify-center rounded-xl px-3 py-3 transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 ${
            isActive
              ? "bg-slate-900 text-white shadow-sm"
              : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
          }`}
          title={item.label}
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
        </Link>
      );
    });
  };

  /** Renders grouped collapsible navigation sections for the expanded sidebar and mobile drawer. */
  const renderGroupedMenuItems = (onNavigate?: () => void) => {
    const sections: GroupedMenuSection[] = groupMenuItems(menuItems);
    return sections.map(({ group, items: sectionItems }) => {
      const GroupIcon = GROUP_ICONS[group.id] ?? Layers;
      const isOpen = openGroups.has(group.id);
      const hasActiveItem = sectionItems.some((item) => {
        const tp = item.to.split("?")[0];
        return location.pathname === tp || (tp !== "/" && location.pathname.startsWith(`${tp}/`));
      });
      return (
        <div key={group.id} className="mb-1">
          {/* Group header button */}
          <button
            type="button"
            onClick={() => toggleGroup(group.id)}
            aria-expanded={isOpen}
            className={`w-full flex items-center gap-2 rounded-lg px-3 py-2 text-left transition-colors hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 ${
              hasActiveItem ? "text-slate-900" : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <GroupIcon className="h-3.5 w-3.5 flex-shrink-0" />
            <span className="flex-1 text-xs font-semibold uppercase tracking-wide">
              {group.label}
            </span>
            <ChevronDown
              className={`h-3 w-3 flex-shrink-0 transition-transform duration-200 ${
                isOpen ? "rotate-0" : "-rotate-90"
              }`}
            />
          </button>

          {/* Group items */}
          {isOpen && (
            <div className="ml-1 mt-0.5 border-l border-slate-100 pl-2">
              {sectionItems.map((item) => {
                const Icon = getIconForPath(item.to);
                const targetPath = item.to.split("?")[0];
                const isActive =
                  location.pathname === targetPath ||
                  (targetPath !== "/" && location.pathname.startsWith(`${targetPath}/`));
                const phase = getPhaseForMenuPath(item.to);
                const showBadge =
                  phase !== null &&
                  phase !== "CONNECTED" &&
                  phase !== "PARTIAL" &&
                  phase !== "UNKNOWN";
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    onClick={onNavigate}
                    className={`group mb-0.5 flex items-center gap-2.5 rounded-xl px-2.5 py-2 transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 ${
                      isActive
                        ? "bg-slate-900 text-white shadow-sm"
                        : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
                    }`}
                  >
                    <span
                      className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg border transition-colors ${
                        isActive
                          ? "border-white/15 bg-white/10 text-white"
                          : "border-slate-200 bg-slate-50 text-slate-500 group-hover:border-slate-300 group-hover:bg-white group-hover:text-slate-700"
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5 flex-shrink-0 stroke-[2.25]" />
                    </span>
                    <span className="flex-1 text-sm font-medium leading-snug">{item.label}</span>
                    {showBadge && <PhaseBadge phase={phase!} active={isActive} />}
                  </Link>
                );
              })}
            </div>
          )}
        </div>
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
            <nav className="flex-1 overflow-y-auto px-3 py-4" role="navigation" aria-label="Mobile navigation">{renderGroupedMenuItems(() => setMobileSidebarOpen(false))}</nav>
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

        <nav className="flex-1 overflow-y-auto px-3 py-4">{sidebarCollapsed ? renderCompactMenuItems() : renderGroupedMenuItems()}</nav>
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
