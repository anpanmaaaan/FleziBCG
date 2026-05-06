import { useEffect, useMemo, useRef, useState, type RefObject } from "react";
import { ChevronDown, Clock, Menu } from "lucide-react";
import { useLocation, useNavigate } from "react-router";

import { useAuth } from "@/app/auth";
import { useI18n, type SupportedLocale } from "@/app/i18n";
import { useImpersonation } from "@/app/impersonation";
import { NAV_GROUPS, getGroupIdForPath } from "@/app/navigation/navigationGroups";
import { getScreenStatusMatchByRoute } from "@/app/screenStatus";
import { ImpersonationSwitcher } from "./ImpersonationSwitcher";
import { ScreenStatusBadge } from "./ScreenStatusBadge";

interface AppHeaderProps {
  currentPage: string;
  showMobileMenuButton?: boolean;
  onOpenSidebar?: () => void;
  mobileMenuOpen?: boolean;
  menuButtonRef?: RefObject<HTMLButtonElement>;
}

export function AppHeader({
  currentPage,
  showMobileMenuButton = false,
  onOpenSidebar,
  mobileMenuOpen = false,
  menuButtonRef,
}: AppHeaderProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { currentUser, logout, logoutAll } = useAuth();
  const { effectiveRoleCode } = useImpersonation();
  const { locale, setLocale, t } = useI18n();

  const [currentTime, setCurrentTime] = useState(new Date());
  const [showLangDropdown, setShowLangDropdown] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [isSigningOut, setIsSigningOut] = useState(false);

  const langRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);
  const langButtonRef = useRef<HTMLButtonElement>(null);
  const userButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setShowLangDropdown(false);
      }
      if (userRef.current && !userRef.current.contains(event.target as Node)) {
        setShowUserDropdown(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key !== "Escape") return;
      if (showUserDropdown) userButtonRef.current?.focus();
      else if (showLangDropdown) langButtonRef.current?.focus();
      setShowUserDropdown(false);
      setShowLangDropdown(false);
    }

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [showLangDropdown, showUserDropdown]);

  const domainLabel = useMemo(() => {
    const groupId = getGroupIdForPath(location.pathname);
    return NAV_GROUPS.find((group) => group.id === groupId)?.label ?? t("appHeader.domain.unknown");
  }, [location.pathname, t]);

  const statusPhase = getScreenStatusMatchByRoute(location.pathname)?.entry.phase ?? "UNKNOWN";

  const activeRole = effectiveRoleCode ?? currentUser?.role_code ?? null;
  const tenantId = currentUser?.tenant_id?.trim() || null;

  const languages: { locale: SupportedLocale; name: string }[] = [
    { locale: "en", name: "English" },
    { locale: "ja", name: "Japanese" },
  ];
  const selectedLanguage = languages.find((item) => item.locale === locale) ?? languages[0];

  const closeMenus = () => {
    setShowLangDropdown(false);
    setShowUserDropdown(false);
  };

  const handleLogout = async () => {
    if (isSigningOut) return;
    setIsSigningOut(true);
    try {
      await logout();
      navigate("/login", { replace: true });
    } finally {
      setIsSigningOut(false);
      closeMenus();
    }
  };

  const handleLogoutAll = async () => {
    if (isSigningOut) return;
    setIsSigningOut(true);
    try {
      await logoutAll();
      navigate("/login", { replace: true });
    } finally {
      setIsSigningOut(false);
      closeMenus();
    }
  };

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="flex min-h-[76px] items-center gap-3 px-3 py-2 sm:px-4 lg:px-6">
        <div className="flex min-w-0 flex-1 items-center gap-3">
          {showMobileMenuButton && (
            <button
              ref={menuButtonRef}
              type="button"
              aria-label={t("appHeader.action.openNavigation")}
              aria-expanded={mobileMenuOpen}
              aria-controls="app-mobile-navigation-drawer"
              onClick={() => {
                closeMenus();
                onOpenSidebar?.();
              }}
              className="rounded-lg border border-slate-200 p-2 text-slate-700 transition-colors hover:bg-slate-50 lg:hidden focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
            >
              <Menu className="h-5 w-5" />
            </button>
          )}

          <div className="min-w-0">
            <p className="truncate text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">
              {domainLabel}
            </p>
            <h1 className="truncate text-lg font-semibold text-slate-900 sm:text-xl">{currentPage}</h1>
          </div>
        </div>

        <div className="hidden min-w-0 flex-[1.05] items-center justify-center xl:flex">
          <div className="flex max-w-full items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700">
            <span className="rounded bg-slate-200 px-2 py-1 font-semibold text-slate-700">
              {t("appHeader.context.tenant")}
            </span>
            <span className="max-w-[10rem] truncate font-mono">{tenantId ?? t("appHeader.context.pending")}</span>
            <span className="text-slate-300">|</span>
            <span className="rounded bg-slate-200 px-2 py-1 font-semibold text-slate-700">
              {t("appHeader.context.role")}
            </span>
            <span className="font-medium">{activeRole ?? t("appHeader.context.pending")}</span>
            <span className="text-slate-300">|</span>
            <span className="rounded bg-slate-200 px-2 py-1 font-semibold text-slate-700">
              {t("appHeader.context.scope")}
            </span>
            <span>{t("appHeader.context.pending")}</span>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          <ScreenStatusBadge phase={statusPhase} size="sm" className="hidden md:inline-flex" />

          <div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 sm:flex">
            <Clock className="h-4 w-4 text-slate-500" />
            <span className="font-mono">{currentTime.toLocaleTimeString("en-US", { hour12: false })}</span>
          </div>

          <div className="hidden lg:block">
            <ImpersonationSwitcher roleCode={currentUser?.role_code} />
          </div>

          <div className="relative hidden sm:block" ref={langRef}>
            <button
              ref={langButtonRef}
              type="button"
              aria-label={t("appHeader.action.changeLanguage")}
              aria-expanded={showLangDropdown}
              aria-controls="app-header-lang-panel"
              onClick={() => {
                setShowLangDropdown((prev) => !prev);
                setShowUserDropdown(false);
              }}
              className="flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 transition-colors hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
            >
              <span className="font-semibold">{selectedLanguage.locale.toUpperCase()}</span>
              <ChevronDown className="h-4 w-4 text-slate-500" />
            </button>
            {showLangDropdown && (
              <div id="app-header-lang-panel" className="absolute right-0 z-50 mt-2 w-40 rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
                {languages.map((lang) => (
                  <button
                    key={lang.locale}
                    type="button"
                    onClick={() => {
                      setLocale(lang.locale);
                      setShowLangDropdown(false);
                    }}
                    className={`w-full px-4 py-2 text-left text-sm transition-colors hover:bg-slate-50 ${
                      locale === lang.locale ? "bg-blue-50 font-medium text-blue-700" : "text-slate-700"
                    }`}
                  >
                    {lang.name}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="relative" ref={userRef}>
            <button
              ref={userButtonRef}
              type="button"
              aria-label={t("appHeader.action.openUserMenu")}
              aria-expanded={showUserDropdown}
              aria-controls="app-header-user-panel"
              onClick={() => {
                setShowUserDropdown((prev) => !prev);
                setShowLangDropdown(false);
              }}
              className="flex h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white pl-2 pr-2 text-sm text-slate-700 transition-colors hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 font-semibold text-white shadow-sm">
                {(currentUser?.username?.[0] || t("appHeader.user.fallbackName")[0]).toUpperCase()}
              </span>
              <span className="hidden max-w-[9rem] truncate font-medium md:inline">{currentUser?.username ?? t("appHeader.user.fallbackName")}</span>
              <ChevronDown className="h-4 w-4 text-slate-500" />
            </button>

            {showUserDropdown && (
              <div id="app-header-user-panel" className="absolute right-0 z-50 mt-2 w-[min(15rem,calc(100vw-1rem))] rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
                <div className="border-b border-slate-100 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-900">{currentUser?.username ?? t("appHeader.user.fallbackName")}</p>
                  <p className="text-xs text-slate-500">{currentUser?.email ?? t("appHeader.user.fallbackEmail")}</p>
                </div>
                <button type="button" className="w-full px-4 py-2 text-left text-sm text-slate-700 transition-colors hover:bg-slate-50">
                  {t("topBar.menu.profile")}
                </button>
                <button type="button" className="w-full px-4 py-2 text-left text-sm text-slate-700 transition-colors hover:bg-slate-50">
                  {t("topBar.menu.settings")}
                </button>
                <button type="button" className="w-full px-4 py-2 text-left text-sm text-slate-700 transition-colors hover:bg-slate-50">
                  {t("topBar.menu.helpSupport")}
                </button>
                <div className="my-1 border-t border-slate-100" />
                <button
                  type="button"
                  onClick={handleLogoutAll}
                  disabled={isSigningOut}
                  className="w-full px-4 py-2 text-left text-sm text-amber-700 transition-colors hover:bg-amber-50 disabled:opacity-50"
                >
                  {t("topBar.menu.logoutAll")}
                </button>
                <button
                  type="button"
                  onClick={handleLogout}
                  disabled={isSigningOut}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 transition-colors hover:bg-red-50 disabled:opacity-50"
                >
                  {isSigningOut ? t("topBar.menu.signingOut") : t("topBar.menu.logout")}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="border-t border-slate-100 bg-slate-50/80 px-3 py-1.5 text-xs text-slate-600 sm:px-4 lg:hidden">
        <span className="font-semibold text-slate-700">{t("appHeader.context.tenant")}:</span>{" "}
        <span className="font-mono">{tenantId ?? t("appHeader.context.pending")}</span>
        <span className="mx-2 text-slate-300">|</span>
        <span className="font-semibold text-slate-700">{t("appHeader.context.role")}:</span>{" "}
        <span>{activeRole ?? t("appHeader.context.pending")}</span>
      </div>
    </header>
  );
}