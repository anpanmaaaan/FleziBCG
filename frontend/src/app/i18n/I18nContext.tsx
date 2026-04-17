import { createContext, useState, useCallback, type ReactNode } from "react";
import { enRegistry } from "./registry/en";
import { jaRegistry } from "./registry/ja";
import type { I18nSemanticKey, I18nRegistry } from "./keys";
import type { SupportedLocale, I18nHook } from "./useI18n";

const LOCALE_STORAGE_KEY = "app_locale";

const registries: Record<SupportedLocale, I18nRegistry> = {
  en: enRegistry,
  ja: jaRegistry,
};

function getInitialLocale(): SupportedLocale {
  try {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (stored === "en" || stored === "ja") return stored;
  } catch {
    // localStorage unavailable
  }
  return "en";
}

function interpolate(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) => {
    return key in vars ? String(vars[key]) : match;
  });
}

export const I18nContext = createContext<I18nHook | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<SupportedLocale>(getInitialLocale);

  const setLocale = useCallback((next: SupportedLocale) => {
    setLocaleState(next);
    try {
      localStorage.setItem(LOCALE_STORAGE_KEY, next);
    } catch {
      // localStorage unavailable
    }
  }, []);

  const t = useCallback(
    (key: I18nSemanticKey, varsOrFallback?: Record<string, string | number> | string, fallback?: string): string => {
      let vars: Record<string, string | number> | undefined;
      let fb: string | undefined;
      if (typeof varsOrFallback === "string") {
        fb = varsOrFallback;
      } else {
        vars = varsOrFallback;
        fb = fallback;
      }
      const registry = registries[locale];
      const raw = registry[key] ?? enRegistry[key] ?? fb ?? key;
      return vars ? interpolate(raw, vars) : raw;
    },
    [locale],
  ) as I18nHook["t"];

  return (
    <I18nContext.Provider value={{ t, locale, setLocale }}>
      {children}
    </I18nContext.Provider>
  );
}
