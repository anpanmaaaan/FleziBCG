import { useState, useEffect, useRef } from 'react';
import { Clock, ChevronDown, Bell } from 'lucide-react';
import { useNavigate } from 'react-router';

import { useAuth } from '@/app/auth';
import { ImpersonationSwitcher } from './ImpersonationSwitcher';

interface TopBarProps {
  currentPage?: string;
}

export function TopBar({ currentPage = 'Dashboard' }: TopBarProps) {
  const navigate = useNavigate();
  const { currentUser, logout, logoutAll } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showPlantDropdown, setShowPlantDropdown] = useState(false);
  const [showLangDropdown, setShowLangDropdown] = useState(false);
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [selectedPlant, setSelectedPlant] = useState('DMES');
  const [selectedLanguage, setSelectedLanguage] = useState({ code: 'GB', name: 'English', flag: '🇬🇧' });
  const [isSigningOut, setIsSigningOut] = useState(false);

  const plantRef = useRef<HTMLDivElement>(null);
  const langRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

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
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
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
  const languages = [
    { code: 'GB', name: 'English', flag: '🇬🇧' },
    { code: 'VN', name: 'Tiếng Việt', flag: '🇻🇳' },
    { code: 'CN', name: '中文', flag: '🇨🇳' },
    { code: 'JP', name: '日本語', flag: '🇯🇵' },
  ];

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
      setShowUserDropdown(false);
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
      setShowUserDropdown(false);
    }
  };

  return (
    <div className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-20">
      {/* Left: Current Page Title */}
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold text-gray-900">{currentPage}</h1>
      </div>

      {/* Right: Controls */}
      <div className="flex items-center gap-4">
        {/* Plant/Site Selector */}
        <div className="relative" ref={plantRef}>
          <button 
            onClick={() => {
              setShowPlantDropdown(!showPlantDropdown);
              setShowLangDropdown(false);
              setShowUserDropdown(false);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <span>{selectedPlant}</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>

          {/* Plant Dropdown */}
          {showPlantDropdown && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
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
        <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 bg-gray-50 rounded-lg">
          <Clock className="w-4 h-4 text-gray-500" />
          <span className="font-mono">{formatDate(currentTime)}</span>
        </div>

        {/* Time Display */}
        <div className="flex items-center gap-2 px-3 py-2 text-sm text-white bg-brand-cta rounded-lg">
          <Clock className="w-4 h-4 text-white" />
          <span className="font-mono font-semibold">{formatTime(currentTime)}</span>
        </div>

        <ImpersonationSwitcher roleCode={currentUser?.role_code} />

        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button 
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowPlantDropdown(false);
              setShowLangDropdown(false);
              setShowUserDropdown(false);
            }}
            className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <Bell className="w-5 h-5" />
            {/* Notification Badge */}
            <span className="absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full border-2 border-white">
              2
            </span>
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
              <div className="px-4 py-2 border-b border-gray-100">
                <h3 className="font-semibold text-gray-900">Notifications</h3>
              </div>
              <div className="max-h-96 overflow-y-auto">
                <div className="px-4 py-3 hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">OEE Alert</p>
                      <p className="text-xs text-gray-600">Line 3 equipment failure detected</p>
                      <p className="text-xs text-gray-400 mt-1">5 mins ago</p>
                    </div>
                  </div>
                </div>
                <div className="px-4 py-3 hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Production Complete</p>
                      <p className="text-xs text-gray-600">PO-001 completed successfully</p>
                      <p className="text-xs text-gray-400 mt-1">15 mins ago</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="px-4 py-2 border-t border-gray-100">
                <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                  View all notifications
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Language Selector */}
        <div className="relative" ref={langRef}>
          <button 
            onClick={() => {
              setShowLangDropdown(!showLangDropdown);
              setShowPlantDropdown(false);
              setShowUserDropdown(false);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <span className="text-lg">{selectedLanguage.flag}</span>
            <span className="font-medium">{selectedLanguage.code}</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>

          {/* Language Dropdown */}
          {showLangDropdown && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    setSelectedLanguage(lang);
                    setShowLangDropdown(false);
                  }}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 transition-colors flex items-center gap-2 ${
                    selectedLanguage.code === lang.code ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
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
            onClick={() => {
              setShowUserDropdown(!showUserDropdown);
              setShowPlantDropdown(false);
              setShowLangDropdown(false);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 pl-3 pr-2 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center text-white font-semibold">
              {(currentUser?.username?.[0] || 'U').toUpperCase()}
            </div>
            <span className="font-medium">{currentUser?.username || 'User'}</span>
            <ChevronDown className="w-4 h-4 text-gray-500" />
          </button>

          {/* User Dropdown */}
          {showUserDropdown && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <div className="px-4 py-3 border-b border-gray-100">
                <p className="text-sm font-semibold text-gray-900">{currentUser?.username || 'User'}</p>
                <p className="text-xs text-gray-500">{currentUser?.email || '-'}</p>
              </div>
              <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                My Profile
              </button>
              <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                Settings
              </button>
              <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                Help & Support
              </button>
              <div className="border-t border-gray-100 my-1"></div>
              <button
                onClick={handleLogoutAll}
                disabled={isSigningOut}
                className="w-full text-left px-4 py-2 text-sm text-amber-700 hover:bg-amber-50 transition-colors disabled:opacity-50"
              >
                Logout all sessions
              </button>
              <button
                onClick={handleLogout}
                disabled={isSigningOut}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
              >
                {isSigningOut ? 'Signing out...' : 'Logout'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}