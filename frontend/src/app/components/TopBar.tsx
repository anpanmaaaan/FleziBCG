import { useState, useEffect, useRef } from 'react';
import { Clock, ChevronDown, Bell, Menu, MoreHorizontal } from 'lucide-react';
import { useNavigate } from 'react-router';

import { useAuth } from '@/app/auth';
import { useI18n, type SupportedLocale } from '@/app/i18n';
import { ImpersonationSwitcher } from './ImpersonationSwitcher';

interface TopBarProps {
  currentPage?: string;
  showMobileMenuButton?: boolean;
  onOpenSidebar?: () => void;
}

export function TopBar({
  currentPage = 'Dashboard',
  showMobileMenuButton = false,
  onOpenSidebar,
}: TopBarProps) {
  const navigate = useNavigate();
  const { currentUser, logout, logoutAll } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showPlantDropdown, setShowPlantDropdown] = useState(false);
  const [showLangDropdown, setShowLangDropdown] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUtilityOverflow, setShowUtilityOverflow] = useState(false);
  const [selectedPlant, setSelectedPlant] = useState('DMES');
  const [isSigningOut, setIsSigningOut] = useState(false);
  const { locale, setLocale, t } = useI18n();

  const plantRef = useRef<HTMLDivElement>(null);
  const langRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);
  const overflowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const closeMenus = () => {
    setShowPlantDropdown(false);
    setShowLangDropdown(false);
    setShowUserDropdown(false);
    setShowNotifications(false);
    setShowUtilityOverflow(false);
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (plantRef.current && !plantRef.current.contains(event.target as Node)) {
        setShowPlantDropdown(false);
      }
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setShowLangDropdown(false);
      }
      if (userRef.current && !userRef.current.contains(event.target as Node)) {
        setShowUserDropdown(false);
      }
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (overflowRef.current && !overflowRef.current.contains(event.target as Node)) {
        setShowUtilityOverflow(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        closeMenus();
      }
    }

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatCompactTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const plants = ['DMES', 'Plant A', 'Plant B', 'Factory 1', 'Factory 2'];
  const languages: { locale: SupportedLocale; name: string; flag: string }[] = [
    { locale: 'en', name: 'English', flag: '🇬🇧' },
    { locale: 'ja', name: '日本語', flag: '🇯🇵' },
  ];
  const selectedLanguage = languages.find((l) => l.locale === locale) ?? languages[0];

  const handleLogout = async () => {
    if (isSigningOut) {
      return;
    }

    setIsSigningOut(true);
    try {
      await logout();
      navigate('/login', { replace: true });
    } finally {
      setIsSigningOut(false);
      closeMenus();
    }
  };

  const handleLogoutAll = async () => {
    if (isSigningOut) {
      return;
    }

    setIsSigningOut(true);
    try {
      await logoutAll();
      navigate('/login', { replace: true });
    } finally {
      setIsSigningOut(false);
      closeMenus();
    }
  };

  return (
    <div className="sticky top-0 z-20 flex min-h-[72px] items-center gap-2 border-b border-gray-200 bg-white px-3 py-2 sm:px-4 lg:px-6">
      {/* Left: Current Page Title */}
      <div className="flex min-w-0 flex-1 items-center gap-3">
        {showMobileMenuButton && (
          <button
            type="button"
            aria-label="Open navigation drawer"
            onClick={() => {
              closeMenus();
              onOpenSidebar?.();
            }}
            className="rounded-lg border border-gray-200 p-2 text-gray-700 transition-colors hover:bg-gray-50 lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </button>
        )}
        <div className="min-w-0">
          <p className="hidden text-xs font-semibold uppercase tracking-[0.16em] text-slate-500 sm:block">Manufacturing Operations</p>
          <h1 className="truncate text-lg font-semibold text-gray-900 sm:text-xl">{currentPage}</h1>
        </div>
      </div>

      {/* Right: Controls */}
      <div className="flex shrink-0 items-center justify-end gap-2 sm:gap-3">
        {/* Plant/Site Selector */}
        <div className="relative hidden lg:block" ref={plantRef}>
          <button 
            type="button"
            onClick={() => {
              setShowPlantDropdown(!showPlantDropdown);
              setShowLangDropdown(false);
              setShowUserDropdown(false);
              setShowNotifications(false);
              setShowUtilityOverflow(false);
            }}
            className="flex h-10 items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            <span>{selectedPlant}</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>

          {/* Plant Dropdown */}
          {showPlantDropdown && (
            <div className="absolute right-0 z-50 mt-2 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
              {plants.map((plant) => (
                <button
                  key={plant}
                  onClick={() => {
                    setSelectedPlant(plant);
                    setShowPlantDropdown(false);
                  }}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors ${
                    selectedPlant === plant ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
                  }`}
                >
                  {plant}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Date Display */}
        <div className="hidden items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-600 xl:flex">
          <Clock className="w-4 h-4 text-gray-500" />
          <span className="font-mono">{formatDate(currentTime)}</span>
        </div>

        {/* Time Display */}
        <div className="flex items-center gap-1.5 rounded-lg bg-brand-cta px-2.5 py-2 text-xs text-white shadow-sm sm:gap-2 sm:px-3 sm:text-sm">
          <Clock className="w-4 h-4 text-white" />
          <span className="font-mono font-semibold sm:hidden">{formatCompactTime(currentTime)}</span>
          <span className="hidden font-mono font-semibold sm:inline">{formatTime(currentTime)}</span>
        </div>

        <div className="hidden lg:block">
          <ImpersonationSwitcher roleCode={currentUser?.role_code} />
        </div>

        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button 
            type="button"
            aria-label="Open notifications"
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowPlantDropdown(false);
              setShowLangDropdown(false);
              setShowUserDropdown(false);
              setShowUtilityOverflow(false);
            }}
            className="relative rounded-full p-2 text-gray-600 transition-colors hover:bg-gray-100"
          >
            <Bell className="w-5 h-5" />
            {/* Notification Badge */}
            <span className="absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full border-2 border-white">
              2
            </span>
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 z-50 mt-2 w-[min(20rem,calc(100vw-1rem))] rounded-lg border border-gray-200 bg-white py-2 shadow-lg">
              <div className="px-4 py-2 border-b border-gray-100">
                <h3 className="font-semibold text-gray-900">{t("topBar.notifications.title")}</h3>
              </div>
              <div className="max-h-96 overflow-y-auto">
                <button type="button" className="w-full px-4 py-3 text-left hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">OEE Alert</p>
                      <p className="text-xs text-gray-600">Line 3 equipment failure detected</p>
                      <p className="text-xs text-gray-400 mt-1">5 mins ago</p>
                    </div>
                  </div>
                </button>
                <button type="button" className="w-full px-4 py-3 text-left hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Production Complete</p>
                      <p className="text-xs text-gray-600">PO-001 completed successfully</p>
                      <p className="text-xs text-gray-400 mt-1">15 mins ago</p>
                    </div>
                  </div>
                </button>
              </div>
              <div className="px-4 py-2 border-t border-gray-100">
                <button type="button" className="text-sm font-medium text-blue-600 hover:text-blue-700">
                  {t("topBar.notifications.viewAll")}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="relative lg:hidden" ref={overflowRef}>
          <button
            type="button"
            aria-label="Open top bar utility menu"
            onClick={() => {
              setShowUtilityOverflow(!showUtilityOverflow);
              setShowPlantDropdown(false);
              setShowLangDropdown(false);
              setShowUserDropdown(false);
              setShowNotifications(false);
            }}
            className="rounded-lg border border-gray-200 p-2 text-gray-700 transition-colors hover:bg-gray-50"
          >
            <MoreHorizontal className="h-5 w-5" />
          </button>

          {showUtilityOverflow && (
            <div className="absolute right-0 z-50 mt-2 w-[min(18rem,85vw)] rounded-xl border border-gray-200 bg-white p-3 shadow-lg">
              <div className="space-y-3">
                <div className="grid grid-cols-1 gap-2">
                  {plants.map((plant) => (
                    <button
                      key={plant}
                      type="button"
                      onClick={() => {
                        setSelectedPlant(plant);
                        setShowUtilityOverflow(false);
                      }}
                      className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                        selectedPlant === plant
                          ? 'border-blue-200 bg-blue-50 font-medium text-blue-700'
                          : 'border-gray-200 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {plant}
                    </button>
                  ))}
                </div>

                <div className="border-t border-gray-100 pt-3">
                  <div className="grid grid-cols-2 gap-2">
                    {languages.map((lang) => (
                      <button
                        key={lang.locale}
                        type="button"
                        onClick={() => {
                          setLocale(lang.locale);
                          setShowUtilityOverflow(false);
                        }}
                        className={`flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors ${
                          locale === lang.locale
                            ? 'border-blue-200 bg-blue-50 font-medium text-blue-700'
                            : 'border-gray-200 text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <span className="text-base">{lang.flag}</span>
                        <span>{lang.locale.toUpperCase()}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="border-t border-gray-100 pt-3 lg:hidden">
                  <ImpersonationSwitcher roleCode={currentUser?.role_code} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Language Selector */}
        <div className="relative hidden lg:block" ref={langRef}>
          <button 
            type="button"
            onClick={() => {
              setShowLangDropdown(!showLangDropdown);
              setShowPlantDropdown(false);
              setShowUserDropdown(false);
              setShowNotifications(false);
              setShowUtilityOverflow(false);
            }}
            className="flex h-10 items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 transition-colors hover:bg-gray-50"
          >
            <span className="text-lg">{selectedLanguage.flag}</span>
            <span className="font-medium">{selectedLanguage.locale.toUpperCase()}</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>

          {/* Language Dropdown */}
          {showLangDropdown && (
            <div className="absolute right-0 z-50 mt-2 w-48 rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
              {languages.map((lang) => (
                <button
                  key={lang.locale}
                  onClick={() => {
                    setLocale(lang.locale);
                    setShowLangDropdown(false);
                  }}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors flex items-center gap-2 ${
                    locale === lang.locale ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
                  }`}
                >
                  <span className="text-lg">{lang.flag}</span>
                  <span>{lang.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* User Profile */}
        <div className="relative" ref={userRef}>
          <button 
            type="button"
            aria-label="Open user menu"
            onClick={() => {
              setShowUserDropdown(!showUserDropdown);
              setShowPlantDropdown(false);
              setShowLangDropdown(false);
              setShowNotifications(false);
              setShowUtilityOverflow(false);
            }}
            className="flex h-10 items-center gap-2 rounded-lg border border-gray-200 bg-white pl-2 pr-2 text-sm text-gray-700 transition-colors hover:bg-gray-50"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-900 text-white font-semibold shadow-sm">
              {(currentUser?.username?.[0] || 'U').toUpperCase()}
            </div>
            <span className="hidden font-medium lg:inline">{currentUser?.username || 'User'}</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>

          {/* User Dropdown */}
          {showUserDropdown && (
            <div className="absolute right-0 z-50 mt-2 w-[min(14rem,calc(100vw-1rem))] rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-sm font-semibold text-gray-900">{currentUser?.username || 'User'}</p>
                <p className="text-xs text-gray-500">{currentUser?.email || '-'}</p>
              </div>
              <button type="button" className="w-full px-4 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-50">
                {t("topBar.menu.profile")}
              </button>
              <button type="button" className="w-full px-4 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-50">
                {t("topBar.menu.settings")}
              </button>
              <button type="button" className="w-full px-4 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-50">
                {t("topBar.menu.helpSupport")}
              </button>
              <div className="border-t border-gray-100 my-1"></div>
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
  );
}